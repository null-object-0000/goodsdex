"""检查 capture_id 是否全局唯一（审计用全局 map，碰撞会配错）。"""
import glob
import json
from collections import Counter, defaultdict
from pathlib import Path

owner = defaultdict(set)
for f in sorted(glob.glob("data/categories/*.json")):
    for r in json.loads(Path(f).read_text(encoding="utf-8")):
        pid = (r.get("product") or {}).get("product_id")
        for c in (r.get("captures") or []):
            owner[c.get("capture_id")].add(pid)

dups = {k: v for k, v in owner.items() if len(v) > 1}
print(f"capture_id 总数 {len(owner)}，被多个 product 共用的 {len(dups)}")
for k, v in list(dups.items())[:6]:
    print(f"   {k} -> {len(v)} 个商品: {list(v)[:3]}")

# 同一 capture_id 的内容是否不同？
diffs = 0
by_id = defaultdict(set)
for f in sorted(glob.glob("data/categories/*.json")):
    for r in json.loads(Path(f).read_text(encoding="utf-8")):
        for c in (r.get("captures") or []):
            raw = (c.get("response_raw") or "")
            by_id[c.get("capture_id")].add(hash(raw))
differ = {k: v for k, v in by_id.items() if len(v) > 1}
print(f"\n同 id 但内容不同: {len(differ)} 个")
for k, v in list(differ.items())[:5]:
    print(f"   {k}: {len(v)} 种不同内容")
