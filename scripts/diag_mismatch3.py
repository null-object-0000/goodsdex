"""用最新审计口径查看剩余 mismatch。"""
import glob
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(".").resolve()
sys.path.insert(0, "src")
sys.path.insert(0, "scripts")
from audit_evidence import DERIVED_FIELDS, _load_raw, jsonpath_get  # noqa: E402

# 重新实现判定（与 audit_evidence 一致）
cnt = Counter()
detail = []
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
            if av == sv:
                continue
            if a.get("attribute") in DERIVED_FIELDS:
                continue
            if isinstance(val, dict) and av == str(val.get("value")):
                continue
            cnt[a.get("attribute")] += 1
            if len(detail) < 8:
                detail.append((f.split("/")[-1][:-5], r["product"]["name"][:20],
                               a.get("attribute"), loc, av[:50], sv[:50]))

print("剩余 mismatch 按属性：")
for k, v in cnt.most_common(15):
    print(f"  {v:4d}  {k}")
print()
for fn, pn, attr, loc, av, sv in detail:
    print(f"[{fn}] {pn}")
    print(f"   属性={attr!r} locator={loc[:56]}")
    print(f"   断言={av!r}")
    print(f"   源值={sv!r}")
