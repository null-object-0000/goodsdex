"""Collect the 28 audited products serially, then combine with archive rows.

python3 scripts/merge_history_rows.py --out /tmp/history.json
python3 scripts/build_goods_supplements.py --history /tmp/history.json
Reruns replay persisted responses. To recollect use a new --evidence directory.
Every dispatch (including failures) consumes the durable 200-request budget.
"""
from __future__ import annotations

import argparse
import csv
import fcntl
import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from goodsdex.kind import classify_product_kind
from goodsdex.sources.mi_cn import MTOP_HEADERS, MTOP_URL


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    tmp.replace(path)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        return None


class Collector:
    def __init__(self, directory):
        self.directory = directory
        directory.mkdir(parents=True, exist_ok=True)
        self.lock = (directory / ".lock").open("a")
        fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self.state = directory / "requests.json"
        self.events = json.loads(self.state.read_text()) if self.state.exists() else []
        self.opener = urllib.request.build_opener(NoRedirect())

    def call(self, pid, gid=None):
        body = [{}, {"productId": pid, **({"gid": gid} if gid else {})}]
        for event in reversed(self.events):
            if event["body"] == body and event.get("status") == 200:
                raw = (self.directory / event["file"]).read_bytes()
                if hashlib.sha256(raw).hexdigest() != event["sha256"]:
                    raise ValueError("Evidence checksum mismatch")
                return json.loads(raw), event
        if len(self.events) >= 200:
            raise RuntimeError("200 request hard limit exhausted")
        # A persisted unfinished dispatch also imposes a recovery wait.
        previous = max((r.get("ended", r["started"] + 30) for r in self.events), default=0)
        time.sleep(max(0, previous + 2.12 - time.time()))
        event = dict(body=body, url=MTOP_URL, started=time.time(), file=f"{len(self.events)+1:04d}.json")
        self.events.append(event)
        write(self.state, self.events)  # reserve before dispatch, including interrupted requests
        req = urllib.request.Request(MTOP_URL, data=json.dumps(body).encode(), headers=MTOP_HEADERS)
        try:
            with self.opener.open(req, timeout=25) as response:
                raw, event["status"] = response.read(), response.status
        except urllib.error.HTTPError as error:
            raw, event["status"] = error.read(), error.code
        except OSError as error:
            event.update(ended=time.time(), error=repr(error))
            write(self.state, self.events)
            raise
        event.update(ended=time.time(), sha256=hashlib.sha256(raw).hexdigest())
        (self.directory / event["file"]).write_bytes(raw)
        write(self.state, self.events)
        print(f"request {len(self.events)}/200: {pid} {gid or ''} HTTP {event['status']}", flush=True)
        if event["status"] != 200:
            raise ValueError(f"HTTP {event['status']}; stop, no unbudgeted retries")
        return json.loads(raw), event


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--history", type=Path, required=True)
    ap.add_argument("--evidence", type=Path, default=ROOT / "data/supplement-refresh-20261027")
    ap.add_argument("--out", type=Path, default=ROOT / "data/supplements/goods-supplements.json")
    args = ap.parse_args()
    client = Collector(args.evidence)
    with (ROOT / "docs/分类覆盖差集-20261026-missing.csv").open(newline="", encoding="utf-8") as source:
        candidates = list(csv.DictReader(source))
    rows = []
    for candidate in candidates:
        pid = candidate["product_id"]
        detail, _ = client.call(pid)
        if detail.get("code") != 0:
            raise ValueError(f"{pid}: API code {detail.get('code')}")
        gid = detail["data"]["product"].get("defaultGid")
        if not gid:
            raise ValueError(f"{pid}: no defaultGid")
        detail, event = client.call(pid, gid)
        if detail.get("code") != 0:
            raise ValueError(f"{pid}: API code {detail.get('code')}")
        data = detail["data"]
        product = data["product"]
        goods = data["goodsInfo"]["goodsList"][0]
        if str(product["productId"]) != pid or str(goods["productId"]) != pid:
            raise ValueError(f"{pid}: identity mismatch; no borrowed child params")
        category = (candidate["supplement_categories"] or candidate["tree_categories"]).split(" / ")[0]
        name = product["name"].strip()
        kind = classify_product_kind(name, category)
        if any(word in name for word in ("滤芯", "悬浮键盘")):
            kind = "accessory"
        elif any(word in name for word in ("鼠标", "键鼠", "机械键盘", "饮水机", "喂食器")):
            kind = "machine"
        params = {p["name"]: p["value"] for p in (goods.get("classParameters") or {}).get("list", [])
                  if p.get("name") and p.get("value")}
        images = goods.get("carouselList") or []
        rows.append(dict(id=f"CN:mi_cn:product:{pid}", name=name, kind=kind, category=category,
                         price=goods.get("price"), market_price=goods.get("marketPrice"), gid=gid,
                         image=images[0].get("imgUrl") if images else goods.get("imgUrl"), params=params,
                         fetched_at=datetime.fromtimestamp(event["ended"], timezone.utc).isoformat(),
                         source="goods_supplements:xiaomi_mobile_official",
                         catalog_identity="goods_supplements:category_coverage_20261026",
                         source_url=MTOP_URL, source_sha256=event["sha256"]))
    history = json.loads(args.history.read_text(encoding="utf-8"))
    combined = sorted(history + rows, key=lambda r: r["id"])
    if len({r["id"] for r in combined}) != len(combined):
        raise ValueError("Duplicate supplemental IDs")
    write(args.out, combined)
    audit = dict(history=len(history), category_rows=len(rows), requests=len(client.events),
                 min_gap_seconds=min((b["started"] - a["ended"] for a, b in zip(client.events, client.events[1:])), default=None),
                 concurrency=1, request_limit=200,
                 responses=[dict(id=r["id"], sha256=r["source_sha256"]) for r in rows])
    write(args.out.parent / "collection-audit.json", audit)
    print(json.dumps(audit, ensure_ascii=False))


if __name__ == "__main__":
    main()
