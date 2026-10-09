"""快速确认：共用 capture_id 的内容是否相同。"""
import glob
import json
from collections import defaultdict
from pathlib import Path

# capture_id -> {内容标识}
content = defaultdict(set)
owners = defaultdict(set)

for f in glob.glob("data/categories/*.json"):
    for r in json.loads(Path(f).read_text(encoding="utf-8")):
        pid = (r.get("product") or {}).get("product_id")
        for c in (r.get("captures") or []):
            cid = c.get("capture_id")
            # 内容标识：优先 hash，其次 raw 长度+前80字符
            ident = c.get("response_hash") or f"len{len(c.get('response_raw') or '')}"
            content[cid].add(ident)
            owners[cid].add(pid)

shared = [cid for cid, o in owners.items() if len(o) > 1]
print(f"被多个商品引用的 capture_id: {len(shared)}")
collide = [cid for cid in shared if len(content[cid]) > 1]
print(f"其中内容不同（真碰撞）: {len(collide)}")
print(f"内容相同（合法共用同一份证据）: {len(shared) - len(collide)}")
for cid in collide[:8]:
    print(f"   ❌ {cid}: {len(owners[cid])} 商品, {len(content[cid])} 种内容")
for cid in shared[:5]:
    if cid not in collide:
        print(f"   ✓ {cid}: {len(owners[cid])} 商品共用同一响应")
