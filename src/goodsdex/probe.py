"""CDP 三路并查探测器 —— GoodsDex 的核心工具，独立可用。

抓任何页面前先跑这个：
  ① raw HTML      服务端返回了什么
  ② 渲染后 DOM     JS 注入后又有什么
  ③ 网络请求       XHR/Script/Document 里的隐藏数据接口

实战价值：小米商城 PC 商品页的 raw HTML 是空壳，真正的数据在
api2.order.mi.com/product/view —— 只看 HTML 会误判「没有数据」。
"""
from __future__ import annotations
import json
import re
import socket
import subprocess
import time
import urllib.request
from pathlib import Path

DEFAULT_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# 判定为"可能含数据"的请求特征
DATA_HINTS = ("api", "json", "xhr", "graphql", ".ajax", "mtop", "/v1/", "/v2/",
              "product", "detail", "search", "list", "query")


def _wait_port(port: int, timeout: float = 40) -> bool:
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), 1):
                return True
        except OSError:
            time.sleep(0.3)
    return False


def raw_fetch(url: str, ua: str = DEFAULT_UA, timeout: int = 25):
    """① curl 等价：原始 HTML"""
    hdr = {"User-Agent": ua, "Accept": "text/html,application/xhtml+xml,*/*"}
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=hdr), timeout=timeout)
        return r.read().decode("utf-8", "ignore"), r.status
    except Exception as e:
        return "", f"ERR {e}"


class Probe:
    """复用单个无头浏览器实例（冷启动约 40s，复用后每页约 3s）"""

    def __init__(self, port: int = 9340, ua: str = DEFAULT_UA, width: int = 1400,
                 height: int = 2400):
        self.port = port
        self.ua = ua
        self._proc = subprocess.Popen([
            "google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox",
            "--disable-dev-shm-usage", f"--remote-debugging-port={port}",
            "--remote-allow-origins=*", f"--user-agent={ua}",
            f"--window-size={width},{height}", "about:blank",
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if not _wait_port(port):
            raise RuntimeError("chrome devtools port not ready")
        tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{port}/json").read())
        page = next(t for t in tabs if t["type"] == "page")
        import websocket  # 需要 websocket-client
        self._ws = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=60)
        self._mid = 0
        self._send("Page.enable")
        self._send("Runtime.enable")
        self._send("Network.enable", {"maxTotalBufferSize": 300_000_000,
                                      "maxResourceBufferSize": 30_000_000,
                                      "maxPostDataSize": 10_000_000})

    def _send(self, method: str, params: dict | None = None, timeout: float = 30):
        self._mid += 1
        mid = self._mid
        self._ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
        t0 = time.time()
        while time.time() - t0 < timeout:
            try:
                self._ws.settimeout(2)
                msg = json.loads(self._ws.recv())
            except Exception:
                continue
            if msg.get("id") == mid:
                return msg
        return {}

    def inspect(self, url: str, wait: float = 4.0, settle: float = 25.0) -> dict:
        """访问页面，采集 ② 渲染后 DOM + ③ 网络请求"""
        self._send("Page.navigate", {"url": url}, timeout=40)
        reqs: dict[str, dict] = {}
        bodies: dict[str, str] = {}
        deadline = time.time() + settle
        first = time.time() + wait
        while time.time() < deadline:
            try:
                self._ws.settimeout(2)
                msg = json.loads(self._ws.recv())
            except Exception:
                if time.time() > first and reqs:
                    # 首屏已过且无新消息，可提前结束
                    break
                continue
            m, p = msg.get("method"), msg.get("params") or {}
            if m == "Network.requestWillBeSent":
                req = p["request"]
                reqs[p["requestId"]] = {
                    "url": req["url"], "method": req["method"], "type": p.get("type"),
                    "postData": req.get("postData"), "headers": req.get("headers", {}),
                }
            elif m == "Network.responseReceived":
                r = reqs.get(p["requestId"])
                if r:
                    r["status"] = p["response"]["status"]
                    r["mime"] = p["response"].get("mimeType", "")
                    r["size"] = p["response"].get("encodedDataLength") or 0
                    if any(k in r["mime"] for k in ("json", "javascript", "text")) \
                            and "image" not in r["mime"]:
                        try:
                            b = self._send("Network.getResponseBody",
                                           {"requestId": p["requestId"]}, 20)
                            body = (b.get("result") or {}).get("body") or ""
                            if body and len(body) < 3_000_000:
                                bodies[p["requestId"]] = body
                        except Exception:
                            pass

        dom = self._eval("document.documentElement.outerHTML")
        text = self._eval("document.body ? document.body.innerText : ''")
        by_type: dict[str, int] = {}
        for r in reqs.values():
            t = r.get("type") or "?"
            by_type[t] = by_type.get(t, 0) + 1

        data_reqs = []
        for rid, r in reqs.items():
            if any(k in r["url"].lower() for k in DATA_HINTS) or \
                    r.get("mime", "").startswith("application/json"):
                data_reqs.append({**{k: v for k, v in r.items() if k != "headers"},
                                  "body": bodies.get(rid, "")[:200_000]})
        return {"url": url, "rendered_dom": dom, "visible_text": text,
                "requests": [r for r in reqs.values()],
                "by_type": by_type, "data_requests": data_reqs}

    def _eval(self, expr: str) -> str:
        r = self._send("Runtime.evaluate", {"expression": expr, "returnByValue": True})
        return ((r.get("result") or {}).get("result") or {}).get("value") or ""

    def fetch(self, url: str, wait: float = 3.0) -> dict:
        """轻量抓取：只要 ② 渲染后 DOM"""
        self._send("Page.navigate", {"url": url}, timeout=40)
        time.sleep(wait)
        dom = self._eval("document.documentElement.outerHTML")
        text = self._eval("document.body ? document.body.innerText : ''")
        m = re.search(r"<title[^>]*>(.*?)</title>", dom, re.S)
        return {"url": url, "html": dom, "text": text,
                "title": (m.group(1).strip() if m else "")}

    def close(self):
        try:
            self._ws.close()
        except Exception:
            pass
        self._proc.terminate()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


def probe(url: str, outdir: str | Path, prefix: str = "probe") -> dict:
    """完整三路并查，把所有产物落盘"""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    result = {"url": url}

    raw, status = raw_fetch(url)
    result["raw"] = {"status": status, "len": len(raw)}
    (outdir / f"{prefix}_raw.html").write_text(raw, encoding="utf-8")

    p = Probe()
    try:
        r = p.inspect(url)
    finally:
        p.close()

    result["rendered"] = {"len": len(r["rendered_dom"]),
                          "text_len": len(r["visible_text"]),
                          "delta_vs_raw": len(r["rendered_dom"]) - len(raw)}
    result["requests"] = {"total": len(r["requests"]), "by_type": r["by_type"],
                          "data_requests": [
                              {k: v for k, v in d.items() if k != "body"}
                              for d in r["data_requests"]]}

    (outdir / f"{prefix}_rendered.html").write_text(r["rendered_dom"], encoding="utf-8")
    (outdir / f"{prefix}_text.txt").write_text(r["visible_text"], encoding="utf-8")
    (outdir / f"{prefix}_requests.json").write_text(
        json.dumps(r["requests"], ensure_ascii=False, indent=1), encoding="utf-8")
    (outdir / f"{prefix}_bodies.json").write_text(
        json.dumps({d["url"]: d["body"] for d in r["data_requests"]}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    return result


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python3 probe.py <url> [前缀]")
        raise SystemExit(1)
    url = sys.argv[1]
    prefix = sys.argv[2] if len(sys.argv) > 2 else re.sub(r"[^a-zA-Z0-9]", "_", url)[-30:]
    res = probe(url, Path("probe_out"), prefix)
    print(f"URL: {res['url']}")
    print(f"① raw HTML   : {res['raw']['status']} / {res['raw']['len']} 字节")
    print(f"② 渲染后 DOM : {res['rendered']['len']} 字节 "
          f"(可见文本 {res['rendered']['text_len']}, 相对 raw {res['rendered']['delta_vs_raw']:+d})")
    req = res["requests"]
    print(f"③ 网络请求   : {req['total']} 个 {req['by_type']}")
    if req["data_requests"]:
        print(f"\n   可能含数据的请求 {len(req['data_requests'])} 个:")
        for d in req["data_requests"][:20]:
            print(f"     [{d.get('status')}] {d.get('method','?'):4s} "
                  f"{d.get('type','?'):9s} {d['url'][:100]}")
    print(f"\n产物: {Path('probe_out')}/")
