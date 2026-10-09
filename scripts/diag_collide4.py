"""逐条列出碰撞 capture_id 的完整信息（含文件与 hash）。"""
import glob
import json
from pathlib import Path

targets = {"bcb9f3a0d28d", "7d03c871d2ba", "c2a590136899", "74a0bc4fbc32",
           "8386e6728aac", "e94ed642ef44"}

occ = {}
for f in sorted(glob.glob("data/categories/*.json")):
    src = json.loads(Path(f).read_text(encoding="utf-8"))
    for r in src:
        for c in (r.get("captures") or []):
            if c.get("capture_id") in targets:
                occ.setdefault(c["capture_id"], []).append(
                    (Path(f).stem, (r["product"] or {}).get("product_id"),
                     c.get("response_hash"), len(c.get("response_raw") or ""),
                     c.get("raw_ref") or ""))

for cid, items in occ.items():
    print(f"=== {cid}")
    for fn, pid, h, ln, ref in items:
        print(f"   {fn:14s} {pid:28s} hash={h} len={ln} ref={ref[:40]}")
    # 看 hash 是否相同
    hs = {i[2] for i in items}
    print(f"   -> hash 种类 {len(hs)}: {hs}")
    print()
