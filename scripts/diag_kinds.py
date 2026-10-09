"""查：配件/服务记录是被"丢弃"还是被"标记保留"。"""
import json
import glob
from collections import Counter

bak = Counter()
bak_excl = Counter()
for f in glob.glob("/tmp/gd-cats-backup-1015/*.json"):
    for r in json.load(open(f)):
        p = r.get("product") or {}
        k = p.get("kind", "?")
        bak[k] += 1
        if p.get("excluded"):
            bak_excl[k] += 1

cur = Counter()
for f in glob.glob("data/categories/*.json"):
    for r in json.load(open(f)):
        cur[(r.get("product") or {}).get("kind", "?")] += 1

print("备份（重采前，10:15）:")
for k, v in bak.most_common():
    print(f"   {k:12s} {v:5d}   其中 excluded={bak_excl.get(k,0)}")
print()
print("现在（重采后）:")
for k, v in cur.most_common():
    print(f"   {k:12s} {v:5d}")
print()
print("配件/服务样本（备份里）:")
n = 0
for f in glob.glob("/tmp/gd-cats-backup-1015/*.json"):
    for r in json.load(open(f)):
        p = r.get("product") or {}
        if p.get("kind") in ("accessory", "service") and n < 5:
            print(f"   [{p.get('kind')}] {p.get('name','')[:34]}  "
                  f"excluded={p.get('excluded')}  "
                  f"reason={p.get('excluded_reason')}")
            n += 1
