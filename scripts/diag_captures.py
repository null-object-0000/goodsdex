"""诊断：哪些 capture 的 response_raw 不是 JSON。"""
import glob
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, "src")

kinds = Counter()
samples = {}
scanned = 0
for f in sorted(glob.glob("data/categories/*.json")):
    for r in json.loads(Path(f).read_text(encoding="utf-8")):
        for c in (r.get("captures") or []):
            raw = c.get("response_raw") or ""
            if not raw:
                continue
            scanned += 1
            try:
                json.loads(raw)
                kinds["可解析"] += 1
                continue
            except Exception:
                pass
            head = raw[:60].replace("\n", " ")
            if head.startswith("<"):
                k = "<HTML>"
            elif head.startswith("<externalized"):
                k = "<外置引用>"
            elif raw.strip().startswith("cb(") or raw.strip().startswith("callback"):
                k = "JSONP 未剥离"
            elif not raw.strip():
                k = "空"
            else:
                k = f"其他: {head[:32]}"
            kinds[k] += 1
            samples.setdefault(k, (f.split("/")[-1], c.get("source"),
                                   c.get("status"), head[:100]))

print(f"扫描 capture {scanned}")
print()
for k, v in kinds.most_common(12):
    print(f"  {v:6d}  {k}")
print()
print("样例：")
for k, (fn, src, st, head) in samples.items():
    print(f"  [{k}] {fn} source={src} status={st}")
    print(f"      {head!r}")
