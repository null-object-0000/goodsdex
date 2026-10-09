"""批量价格刷新：用 dynamicv2 一次查多个商品的价格。

**参数从官方 shop JS 里挖出来的，不是猜的**：
  GET api2.order.mi.com/product/dynamicv2
    goods_ids=<逗号分隔的 gid>
    type=price,act,coupon,favorite
    address_id/province_id/city_id/district_id/area_id 可为空

实测：批量 60 个 ≈ 1.1s，全库 3477 个 ≈ 63s（58 批）。
比全量采集（26 分钟）轻 25 倍，足够支撑小时级刷新。

价格是**时间序列**：每次刷新按 <日期> 追加观测，不覆盖历史。
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Iterable, Optional

CST = timezone(timedelta(hours=8))
DYNAMIC_URL = "https://api2.order.mi.com/product/dynamicv2"
UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
      "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148")
BATCH = 60          # 实测 60 个/请求稳定
PAUSE = 0.4         # 批间停顿，避免触发限流


def fetch_prices(gids: Iterable[str], timeout: int = 20) -> dict:
    """批量取价 -> {gid: {"price": int, "market_price": int, ...}}

    失败时返回已成功的部分，并把失败原因放在 "__error__" 键下
    —— 不把"没取到"伪装成"没有价格"。
    """
    ids = [str(g) for g in gids if g]
    out: dict = {}
    errors = []
    for i in range(0, len(ids), BATCH):
        chunk = ids[i:i + BATCH]
        params = {
            "goods_ids": ",".join(chunk),
            "type": "price,act,coupon,favorite",
            "address_id": "", "province_id": "", "city_id": "",
            "district_id": "", "area_id": "",
        }
        url = f"{DYNAMIC_URL}?{urllib.parse.urlencode(params)}"
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": UA, "Referer": "https://m.mi.com/",
                "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                d = json.loads(r.read().decode("utf-8", "ignore"))
        except Exception as e:
            errors.append(f"batch@{i}: {type(e).__name__}: {e}")
            continue
        if d.get("code") != 200:
            errors.append(f"batch@{i}: code={d.get('code')} {d.get('msg')}")
            continue
        data = d.get("data") or {}
        for gid, entry in data.items():
            if not isinstance(entry, dict):
                continue
            # 结构：{gid: {"first": {"price": {"price": {...}}}}}
            first = entry.get("first") or {}
            pinfo = (first.get("price") or {}).get("price") or {}
            if pinfo:
                out[str(gid)] = {
                    "price": pinfo.get("price"),
                    "market_price": pinfo.get("market_price"),
                    "min_price": pinfo.get("min_price"),
                    "max_price": pinfo.get("max_price"),
                }
        if i + BATCH < len(ids):
            time.sleep(PAUSE)
    if errors:
        out["__error__"] = errors
    return out


def now_iso() -> str:
    return datetime.now(CST).isoformat(timespec="seconds")


def refresh(gids: list[str], store: Path, stamp: Optional[str] = None) -> dict:
    """刷新价格并按时间追加观测（不覆盖历史）。

    产出：
      <store>/prices/latest.json      最新快照
      <store>/prices/<YYYY-MM>.jsonl  按月追加的时间序列
    """
    stamp = stamp or now_iso()
    prices = fetch_prices(gids)
    errs = prices.pop("__error__", [])

    store = Path(store)
    (store / "prices").mkdir(parents=True, exist_ok=True)

    snap = {"fetched_at": stamp, "count": len(prices), "prices": prices}
    (store / "prices" / "latest.json").write_text(
        json.dumps(snap, ensure_ascii=False, indent=1), encoding="utf-8")

    # 时间序列按**小时**追加（同小时内重跑不重复写）
    month = stamp[:7]
    fp = store / "prices" / f"{month}.jsonl"
    hour = stamp[:13]
    seen = set()
    if fp.exists():
        for old in fp.read_text(encoding="utf-8").splitlines():
            try:
                seen.add(str(json.loads(old).get("fetched_at"))[:13])
            except Exception:
                pass
    if hour not in seen:
        line = json.dumps({"fetched_at": stamp, "prices": prices},
                          ensure_ascii=False)
        with fp.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    return {"fetched_at": stamp, "updated": len(prices),
            "requested": len(gids), "errors": errs}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--store", default="data")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()

    # 从分类文件收集 gid
    gids = []
    for f in sorted(Path("data/categories").glob("*.json")):
        for r in json.loads(f.read_text(encoding="utf-8")):
            v = (r.get("view") or {}).get("values") or {}
            if v.get("gid"):
                gids.append(str(v["gid"]))
    if a.limit:
        gids = gids[:a.limit]
    print(f"待刷新 {len(gids)} 个商品")
    res = refresh(gids, Path(a.store))
    print(json.dumps(res, ensure_ascii=False, indent=1))
