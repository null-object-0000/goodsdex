"""诊断：为什么补采没写进去？"""
import json
import sys
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, "scripts")
from goodsdex import pipeline


def dangling(rs):
    t = b = 0
    for r in rs:
        cids = {c.get("capture_id") for c in (r.get("captures") or [])}
        for a in r.get("assertions") or []:
            t += 1
            if a.get("capture_id") not in cids:
                b += 1
    return t, b


cat = sys.argv[1] if len(sys.argv) > 1 else "扫地机器人"
old = json.loads(Path(f"data/categories/{cat}.json").read_text(encoding="utf-8"))
recs = pipeline.run_category(cat, limit=0, max_pages=20, workers=2,
                             outdir=Path("/tmp/gd-check"), verbose=False)
print(f"旧数据 {len(old)} 条  vs  新采集 {len(recs)} 条")
print(f"触发防清空保护（新 < 旧*0.5）? {len(recs) < len(old) * 0.5}")
t1, b1 = dangling(old)
t2, b2 = dangling(recs)
print(f"旧: 断言 {t1} 悬空 {b1} ({b1/max(t1,1):.0%})")
print(f"新: 断言 {t2} 悬空 {b2} ({b2/max(t2,1):.0%})")
