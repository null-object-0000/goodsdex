"""诊断：locator 解析失败与值不一致的真实原因。"""
import glob
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, "scripts")
def resolve(raw, locator):
    """按 locator（JSONPath 子集）取值"""
    import re
    if not locator or not locator.startswith("$"):
        raise ValueError("not a path")
    cur = json.loads(raw) if isinstance(raw, str) else raw
    for part in re.findall(r"\.([A-Za-z_][\w]*)|\[(\d+)\]", locator):
        key, idx = part
        if key:
            if not isinstance(cur, dict) or key not in cur:
                raise KeyError(f"key {key!r} missing")
            cur = cur[key]
        else:
            if not isinstance(cur, list) or int(idx) >= len(cur):
                raise KeyError(f"index {idx} missing")
            cur = cur[int(idx)]
    return cur


fails = Counter()
mismatches = []
checked = 0
for f in sorted(glob.glob("data/categories/*.json")):
    for r in json.loads(Path(f).read_text(encoding="utf-8")):
        caps = {c.get("capture_id"): c for c in (r.get("captures") or [])}
        for a in r.get("assertions") or []:
            c = caps.get(a.get("capture_id"))
            if not c:
                continue
            raw = c.get("response_raw") or ""
            if not raw:
                fails["capture 无 response_raw"] += 1
                continue
            checked += 1
            try:
                v = resolve(raw, a.get("locator"))
            except json.JSONDecodeError:
                fails["capture 非 JSON"] += 1
                continue
            except (KeyError, ValueError, TypeError) as e:
                fails[f"locator: {str(e)[:28]}"] += 1
                continue
            # 值一致性
            av = str(a.get("raw_value") if a.get("raw_value") is not None
                     else a.get("value"))
            sv = str(v)
            if av.strip() != sv.strip() and av not in sv and sv not in av:
                if len(mismatches) < 6:
                    mismatches.append((c.get("source"), a.get("locator"),
                                       av[:40], sv[:40]))
                fails["值不一致"] += 1

print(f"可检查断言 {checked}")
print()
print("失败分类：")
for k, v in fails.most_common(12):
    print(f"  {v:6d}  {k}")
print()
print("值不一致样例：")
for s, loc, want, got in mismatches:
    print(f"  [{s}] {loc[:52]}")
    print(f"      断言值={want!r}")
    print(f"      路径值={got!r}")
