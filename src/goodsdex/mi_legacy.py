"""从可追溯的官方旧产品页补采型号与详情，不把无货认成停售。"""

from __future__ import annotations
import hashlib
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

from .apple import write_json
from .facts import Capture, Assertion, now_iso
from .pipeline import collect_one
from .sources.apple_cn import externalize

SEEDS = Path(__file__).resolve().parents[2] / "data/official/mi_legacy_seeds.json"
VERSION = "mi-legacy-v1"


def official_url(url, script=False):
    p = urllib.parse.urlsplit(url)
    host = "cdn.cnbj1.fds.api.mi-img.com" if script else "www.mi.com"
    if p.scheme != "https" or p.hostname != host or p.port or p.username:
        raise ValueError("非官方旧产品资料链接")
    if script and not p.path.startswith("/mi.com-assets/shop/pro/js/product/"):
        raise ValueError("只读取产品页实际引用的产品脚本")
    return url


def fetch(url):
    official_url(url, urllib.parse.urlsplit(url).hostname != "www.mi.com")

    class Redirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            official_url(newurl)
            return super().redirect_request(req, fp, code, msg, headers, newurl)

    with urllib.request.build_opener(Redirect()).open(
        urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=25
    ) as res:
        return Capture.make(
            "mi_cn_legacy", res.url, res.read().decode("utf-8"), parser_version=VERSION
        )


def page_info(body):
    m = re.search(r"var\s+\$GLOBAL_PAGE_INFO\s*=\s*", body)
    if not m:
        raise ValueError("官方页产品身份缺失")
    info = json.JSONDecoder().raw_decode(body[m.end() :])[0].get("product_info") or {}
    if not re.fullmatch(r"\d+", str(info.get("product_id", ""))) or not info.get(
        "name"
    ):
        raise ValueError("官方页没有有效 product_id/name")
    return info


def script_links(body):
    return sorted(
        {
            official_url(urllib.parse.urljoin("https://www.mi.com", u), True)
            for u in re.findall(r'(?:src|href)=["\']([^"\']+)["\']', body)
            if "/js/product/" in u and re.search(r"/index\.[\w]+\.js$", u)
        }
    )


def specs(body):
    result = []
    for array in re.finditer(r"(specsArray\d*)\s*:\s*\[(.*?)\]", body, re.S):
        for pair in re.finditer(
            r'\{name:("(?:\\.|[^"\\])*"),specs:("(?:\\.|[^"\\])*")\}', array[2]
        ):
            result.append(
                (
                    json.loads(pair[1]),
                    json.loads(pair[2]),
                    f"js:{array[1]}@{array.start() + pair.start()}",
                )
            )
    return result


def crawl(
    out=Path("data/categories"),
    raw=Path("data/mi-legacy/raw"),
    seeds=None,
    transport=fetch,
    collect=collect_one,
    pause=2.1,
):
    out, raw = Path(out), Path(raw)
    seeds = json.loads(SEEDS.read_text()) if seeds is None else seeds
    path = out / "Mi_legacy.json"
    old = json.loads(path.read_text()) if path.exists() else []
    merged = {r["product"]["product_id"]: r for r in old}
    report = {
        "fetched_at": now_iso(),
        "scope": "verified official legacy page seeds; not exhaustive",
        "errors": [],
        "updated": [],
    }
    for seed in seeds:
        try:
            if seed.get("type") == "reviewed_pdf_component":
                rec = manual_component(seed, raw)
                merged[rec["product"]["product_id"]] = rec
                report["updated"].append(rec["product"]["product_id"])
                continue
            cap = transport(official_url(seed["url"]))
            info = page_info(cap.response_raw)
            rows, captures = [], [cap]
            for url in script_links(cap.response_raw):
                time.sleep(pause)
                script = transport(url)
                rows.extend(
                    (label, value, locator, script)
                    for label, value, locator in specs(script.response_raw)
                )
                captures.append(script)
            model_rows = [r for r in rows if r[0] in ("产品型号", "型号")]
            if len(model_rows) != 1:
                raise ValueError("产品脚本中型号不唯一或缺失")
            time.sleep(pause)
            rec = collect(
                str(info["product_id"]),
                name_hint=info["name"],
                category=seed["category"],
            )
            if not any(c["status"] == "success" for c in rec["captures"]):
                raise ValueError("详情采集失败，保留旧记录")
            p = rec["product"]
            p.update(
                name=info["name"],
                source="mi_cn",
                brand="小米",
                market="CN",
                record_level="model_reference",
                catalog_scope="legacy_seed",
                sale_status="unverified",
                source_url=seed["url"],
                model=model_rows[0][1],
                lookup_keys=[model_rows[0][1]],
                price_kind="not_applicable",
            )
            values = rec["view"]["values"]
            values["name"] = info["name"]
            for key in ("price", "market_price", "pc_price", "pc_market_price"):
                values.pop(key, None)
                rec["view"].get("selected_from", {}).pop(key, None)
            values["price"] = None
            for label, value, locator, evidence in rows:
                aid = hashlib.sha256(
                    f"{evidence.capture_id}|{label}".encode()
                ).hexdigest()[:16]
                rec["assertions"].append(
                    Assertion(
                        aid,
                        p["product_id"],
                        evidence.capture_id,
                        "mi_cn_legacy",
                        label,
                        value,
                        locator=locator,
                        parser_version=VERSION,
                    ).to_dict()
                )
                values[label] = value
                rec["view"].setdefault("selected_from", {})[label] = aid
            values["model"] = p["model"]
            previous_caps = []
            for entry in rec["captures"]:
                evidence = Capture(**entry)
                if evidence.raw_ref and evidence.response_raw.startswith(
                    "<externalized:"
                ):
                    evidence.response_raw = Path(evidence.raw_ref).read_text()
                externalize(evidence, raw)
                previous_caps.append(evidence.to_dict())
            rec["captures"] = previous_caps
            for evidence in captures:
                externalize(evidence, raw)
                rec["captures"].append(evidence.to_dict())
            merged[p["product_id"]] = rec
            report["updated"].append(p["product_id"])
        except (ValueError, OSError, KeyError, TypeError) as exc:
            report["errors"].append({"url": seed["url"], "error": str(exc)})
    if merged:
        write_json(path, list(merged.values()))
    write_json(raw.parent / "report.json", report)
    return report


def publish_legacy(cats, out):
    from collections import Counter
    from .publish import to_public

    out = Path(out)
    path = out / "goods.json"
    items = json.loads(path.read_text())
    incoming = [
        to_public(r) for r in json.loads((Path(cats) / "Mi_legacy.json").read_text())
    ]
    ids = {r["id"] for r in incoming}
    merged = [r for r in items if r["id"] not in ids] + incoming
    merged.sort(key=lambda r: r["id"])
    write_json(path, merged)
    write_json(
        out / "meta.json",
        {
            "generated_at": now_iso(),
            "count": len(merged),
            "by_kind": dict(Counter(r.get("kind", "unknown") for r in merged)),
            "with_price": sum(r.get("price") is not None for r in merged),
            "note": "包含独立标记的旧款机型资料；旧款参考不提供现价。",
        },
    )
    return {"count": len(merged), "legacy": len(incoming)}


def manual_component(seed, raw, read=None):
    """人工逐列核验的官方说明书事实；只在 PDF 原件哈希一致时使用。"""
    import base64

    url = seed["url"]
    p = urllib.parse.urlsplit(url)
    if (
        p.scheme != "https"
        or p.netloc != "cdn.cnbj1.fds.api.mi-img.com"
        or not re.fullmatch(r"/iotweb-product-center/[a-zA-Z0-9_]+\.pdf", p.path)
        or p.query
    ):
        raise ValueError("说明书来源不合法")
    if read is None:

        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *args):
                return None

        with urllib.request.build_opener(NoRedirect()).open(url, timeout=30) as res:
            body = res.read()
    else:
        body = read(url)
    digest = hashlib.sha256(body).hexdigest()
    if digest != seed["sha256"]:
        raise ValueError("官方 PDF 版本变化，待重新逐列核验；保留原资料")
    cap = Capture.make(
        "mi_cn_manual",
        url,
        "base64:" + base64.b64encode(body).decode(),
        parser_version="reviewed-pdf-v1",
    )
    externalize(cap, Path(raw))
    pid = "CN:mi_cn:reference:" + seed["model"]
    assertions = []
    for label, value in seed["facts"].items():
        assertions.append(
            Assertion(
                hashlib.sha256(f"{cap.capture_id}|{label}".encode()).hexdigest()[:16],
                pid,
                cap.capture_id,
                "mi_cn_manual",
                label,
                value,
                locator=f"pdf:page={seed['pdf_page']};printed_page={seed['printed_page']};table=全能基座;row={label}",
                qualifiers={
                    "binary_sha256": digest,
                    "reviewed_at": seed["reviewed_at"],
                    "extraction": "manual_visual_review",
                },
                parser_version="reviewed-pdf-v1",
            ).to_dict()
        )
    return {
        "product": {
            "product_id": pid,
            "name": seed["name"],
            "source": "mi_cn",
            "brand": "小米",
            "market": "CN",
            "category": seed["category"],
            "kind": "accessory",
            "record_level": "model_reference",
            "catalog_scope": "component_manual",
            "sale_status": "unverified",
            "source_url": url,
            "model": seed["model"],
            "lookup_keys": [seed["model"]],
        },
        "fetched_at": cap.fetched_at,
        "captures": [cap.to_dict()],
        "assertions": assertions,
        "view": {
            "values": {**seed["facts"], "model": seed["model"], "price": None},
            "selected_from": {a["attribute"]: a["assertion_id"] for a in assertions},
        },
    }
