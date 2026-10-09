"""查 6 个真碰撞的 capture 来自哪个分类、是不是旧数据。"""
import glob
import json
from collections import defaultdict
from pathlib import Path

targets = {"bcb9f3a0d28d", "7d03c871d2ba", "c2a590136899", "74a0bc4fbc32",
           "8386e6728aac", "e94ed642ef44"}

for f in sorted(glob.glob("data/categories/*.json")):
    for r in json.loads(Path(f).read_text(encoding="utf-8")):
        pid = (r.get("product") or {}).get("product_id")
        for c in (r.get("captures") or []):
            if c.get("capture_id") in targets:
                print(f"[{Path(f).stem}] {pid} {r['product'].get('name','')[:26]}")
                print(f"   cid={c['capture_id']} src={c.get('source')} "
                      f"status={c.get('status')} url={c.get('url','')[:60]}")
                print(f"   raw前80={ (c.get('response_raw') or '')[:80]!r}")
                print()
