"""确认剩余共用 capture_id 是否为"内容相同"（合法）还是碰撞（bug）。"""
import glob
import json
from collections import defaultdict
from pathlib import Path

by_id = defaultdict(set)
for f in glob.glob("data/categories/*.json"):
    for r in json.loads(Path(f).read_text(encoding="utf-8")):
        pid = (r.get("product") or {}).get("product_id")
        for c in (r.get("captures") or []):
            by_id[c.get("capture_id")].add(c.get("response_hash") or "")

shared = {k: v for k, v in by_id.items() if len(v) == 1 and "" in v}
multi = defaultdict(set)
for f in glob.glob("data/categories/*.json"):
    for r in json.loads(Path(f).read_text(encoding="utf-8")):
        for c in (r.get("captures") or []):
            multi[c.get("capture_id")].add(c.get("response_hash") or c.get("response_raw", "")[:60])

collide = 0
ok = 0
for cid, hashes in multi.items():
    owners = set()
    for f in glob.glob("data/categories/*.json"):
        for r in json.loads(Path(f).read_text(encoding="utf-8")):
            if any(c.get("capture_id") == cid for c in (r.get("captures") or [])):
                owners.add((r.get("product") or {}).get("product_id"))
    if len(owners) > 1:
        if len(hashes) > 1:
            collide += 1
            print(f"❌ 碰撞 {cid}: {len(owners)} 商品, {len(hashes)} 种内容")
        else:
            ok += 1
print(f"\n共用 id：内容相同（合法共用证据）{ok} 个，真碰撞 {collide} 个")
