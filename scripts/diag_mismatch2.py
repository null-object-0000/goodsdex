"""看 ★未标派生 的 212 条到底是什么。"""
import glob
import json
import re
import sys
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


shown = 0
for f in sorted(glob.glob("data/categories/*.json")):
    for r in json.loads(Path(f).read_text(encoding="utf-8")):
        caps = {c.get("capture_id"): c for c in (r.get("captures") or [])}
        for a in r.get("assertions") or []:
            cap = caps.get(a.get("capture_id"))
            loc = a.get("locator") or ""
            attr = a.get("attribute", "")
            if not cap or not loc.startswith("$") or attr in DERIVED_FIELDS:
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
            shown += 1
            if shown <= 8:
                print(f"[{f.split('/')[-1][:-5]}] {r['product']['name'][:22]}")
                print(f"   属性={attr!r}  locator={loc[:58]}")
                print(f"   断言 raw_value={av!r}")
                print(f"   源值={sv!r}")
                print(f"   availability={a.get('availability')}")
                print()
print(f"合计 {shown} 条")
