"""清尾 2：重采含 classParameters 商品的分类（locator 精确到 .value）。"""
import glob
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(".").resolve()
EXT_RE = re.compile(r"<externalized:sha256=([0-9a-f]{64})")
sys.path.insert(0, "src")
sys.path.insert(0, "scripts")
from goodsdex import pipeline  # noqa: E402


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


def jp_get(obj, path):
    cur = obj
    for key, idx in re.findall(r"\.([^.[\]]+)|\[(\d+)\]", path[1:]):
        if idx:
            if not isinstance(cur, list) or int(idx) >= len(cur):
                return None, False
            cur = cur[int(idx)]
        else:
            if not isinstance(cur, dict) or key not in cur:
                return None, False
            cur = cur[key]
    return cur, True


def coarse_locators(recs):
    """统计 locator 指向容器、断言值取 .value 的条数（旧写法）"""
    caps = {}
    for r in recs:
        for c in r.get("captures") or []:
            caps.setdefault(c.get("capture_id"), c)
    n = 0
    for r in recs:
        for a in r.get("assertions") or []:
            loc = a.get("locator") or ""
            if not loc.endswith("classParameters.list") and \
               not re.search(r"classParameters\.list\[\d+\]$", loc):
                continue
            cap = caps.get(a.get("capture_id"))
            if not cap:
                continue
            obj = load_cap(cap)
            if obj is None:
                continue
            val, ok = jp_get(obj, loc)
            if ok and isinstance(val, dict) and val.get("value") == a.get("raw_value"):
                n += 1
    return n


stale = []
for f in sorted(glob.glob("data/categories/*.json")):
    try:
        recs = json.loads(Path(f).read_text(encoding="utf-8"))
    except Exception:
        continue
    n = coarse_locators(recs)
    if n:
        stale.append((Path(f).stem, n))

print(f"待清尾 {len(stale)} 个分类（locator 指向容器）", flush=True)
for c, n in stale[:8]:
    print(f"   {c}  {n} 条", flush=True)

ok = err = 0
for i, (cat, _n) in enumerate(stale, 1):
    name = "毛巾/浴巾" if cat == "毛巾_浴巾" else cat
    try:
        recs = pipeline.run_category(name, limit=0, max_pages=20, workers=2,
                                     outdir=Path("data/categories"), verbose=False)
        print(f"[{i}/{len(stale)}] ✓ {name[:20]:22s} {len(recs):4d} 款 "
              f"残留 {coarse_locators(recs)}", flush=True)
        ok += 1
    except Exception as e:
        print(f"[{i}/{len(stale)}] ✗ {name[:20]:22s} {type(e).__name__}: {e}",
              flush=True)
        err += 1
    time.sleep(1.5)
print(f"\n完成 {ok} 成功 {err} 失败", flush=True)
