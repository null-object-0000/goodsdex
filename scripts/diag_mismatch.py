"""查清剩余 212 条"值不一致"的性质。"""
import glob
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(".").resolve()
EXT_RE = re.compile(r"<externalized:sha256=([0-9a-f]{64})")

sys.path.insert(0, "scripts")
from audit_evidence import DERIVED_FIELDS, jsonpath_get  # noqa: E402


def load_cap(cap):
    raw = (cap.get("response_raw") or "").strip()
    m = EXT_RE.match(raw)
    if m:
        ref = cap.get("raw_ref") or ""
        p = Path(ref) if ref else None
        if not p or not p.exists():
            p = ROOT / "data" / "raw" / m.group(1)[:2] / f"{m.group(1)}.txt"
        if not p.exists():
            return None
        raw = p.read_text(encoding="utf-8")
    try:
        return json.loads(raw)
    except Exception:
        return None


by_attr = Counter()
detail = []
for f in sorted(glob.glob("data/categories/*.json")):
    for r in json.loads(Path(f).read_text(encoding="utf-8")):
        caps = {c.get("capture_id"): c for c in (r.get("captures") or [])}
        for a in r.get("assertions") or []:
            cap = caps.get(a.get("capture_id"))
            loc = a.get("locator") or ""
            if not cap or not loc.startswith("$"):
                continue
            obj = load_cap(cap)
            if obj is None:
                continue
            val, err = jsonpath_get(obj, loc)
            if err:
                continue
            av, sv = str(a.get("raw_value")), str(val)
            if av == sv or av in sv or sv in av:
                continue
            attr = a.get("attribute", "")
            by_attr[(attr, attr in DERIVED_FIELDS)] += 1
            if len(detail) < 10:
                detail.append((attr, loc, av[:60], sv[:60]))

print("值不一致按属性分：")
for (attr, is_der), n in by_attr.most_common(20):
    tag = "已标派生" if is_der else "★未标派生"
    print(f"  {n:4d}  {attr[:28]:30s} {tag}")
print()
print("样例：")
for attr, loc, av, sv in detail:
    print(f"  [{attr}] {loc[:56]}")
    print(f"       断言={av!r}")
    print(f"       源值={sv!r}")
