"""重采断言悬空的分类（按内容判断，不靠 mtime）。"""
import glob
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, "scripts")
from goodsdex import pipeline


def dangling_ratio(recs):
    t = b = 0
    for r in recs:
        cids = {c.get("capture_id") for c in (r.get("captures") or [])}
        for a in r.get("assertions") or []:
            t += 1
            if a.get("capture_id") not in cids:
                b += 1
    return (b / t) if t else 0.0


stale = []
for f in sorted(glob.glob("data/categories/*.json")):
    try:
        recs = json.loads(Path(f).read_text(encoding="utf-8"))
    except Exception:
        continue
    if dangling_ratio(recs) > 0.10:
        stale.append(Path(f).stem)

print(f"待重采 {len(stale)} 个分类（悬空率 >10%）", flush=True)
ok = err = 0
for i, cat in enumerate(stale, 1):
    name = "毛巾/浴巾" if cat == "毛巾_浴巾" else cat
    try:
        recs = pipeline.run_category(name, limit=0, max_pages=20, workers=2,
                                     outdir=Path("data/categories"), verbose=False)
        r = dangling_ratio(recs) if recs else 0
        print(f"[{i}/{len(stale)}] ✓ {name[:20]:22s} {len(recs):4d} 款 悬空 {r:.0%}",
              flush=True)
        ok += 1
    except Exception as e:
        print(f"[{i}/{len(stale)}] ✗ {name[:20]:22s} {type(e).__name__}: {e}",
              flush=True)
        err += 1
    time.sleep(1.5)
print(f"\n完成 {ok} 成功 {err} 失败", flush=True)
