"""查清楚这 15 条真不一致的性质。"""
import glob
import json
import sys
from pathlib import Path

ROOT = Path(".").resolve()
sys.path.insert(0, "src")
sys.path.insert(0, "scripts")
from audit_evidence import DERIVED_FIELDS, _load_raw, jsonpath_get  # noqa: E402

found = []
for f in sorted(glob.glob("data/categories/*.json")):
    for r in json.loads(Path(f).read_text(encoding="utf-8")):
        caps = {c.get("capture_id"): c for c in (r.get("captures") or [])}
        for a in r.get("assertions") or []:
            cap = caps.get(a.get("capture_id"))
            loc = a.get("locator") or ""
            if not cap or not loc.startswith("$"):
                continue
            obj = _load_raw(cap.get("response_raw") or "", cap)
            if obj is None:
                continue
            val, err = jsonpath_get(obj, loc)
            if err:
                continue
            av, sv = str(a.get("raw_value")), str(val)
            if av == sv or a.get("attribute") in DERIVED_FIELDS:
                continue
            if isinstance(val, dict) and av == str(val.get("value")):
                continue
            if isinstance(val, str) and av == val.strip():
                continue
            found.append((f.split("/")[-1][:-5], r, a, cap, loc, av, sv))

print(f"真不一致 {len(found)} 条\n")
for fn, r, a, cap, loc, av, sv in found:
    p = r["product"]
    print(f"[{fn}] {p.get('name','')[:30]}  pid={p.get('product_id')}")
    print(f"   属性={a.get('attribute')!r}")
    printf = f"   locator={loc}"
    print(printf)
    print(f"   断言={av[:60]!r}")
    print(f"   源值={sv[:60]!r}")
    print(f"   capture={cap.get('capture_id')} url={cap.get('url','')[:70]}")
    # 看看这个 capture 的 data.product 结构
    obj = _load_raw(cap.get("response_raw") or "", cap)
    if isinstance(obj, dict):
        prod = (obj.get("data") or {}).get("product") or {}
        print(f"   data.product 键: {list(prod.keys())[:10]}")
        print(f"   data.product.name={str(prod.get('name'))[:50]!r}")
        gi = (obj.get("data") or {}).get("goodsInfo") or {}
        gl = gi.get("goodsList") or []
        if gl:
            print(f"   goodsList[0].sku/name: {str(gl[0].get('sku'))[:40]}")
    print()
