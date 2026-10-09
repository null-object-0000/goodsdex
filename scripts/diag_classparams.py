"""找有参数的手机商品，看 classParameters 的真实结构。"""
import glob
import json
import sys
from pathlib import Path

sys.path.insert(0, "src")


def walk(o, path="$"):
    """找出所有 dict 里 key 为 classParameters 的位置"""
    hits = []
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "classParameters":
                hits.append((f"{path}.{k}", v))
            hits += walk(v, f"{path}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o[:5]):
            hits += walk(v, f"{path}[{i}]")
    return hits


found = 0
for f in sorted(glob.glob("data/categories/*.json")):
    for r in json.loads(Path(f).read_text(encoding="utf-8")):
        for c in (r.get("captures") or []):
            raw = c.get("response_raw") or ""
            if "classParameters" not in raw:
                continue
            try:
                d = json.loads(raw)
            except Exception:
                continue
            for p, v in walk(d):
                if isinstance(v, dict) and v.get("list"):
                    print(f"文件: {f.split('/')[-1]}")
                    print(f"  路径: {p}")
                    print(f"  类型: dict, keys={list(v.keys())}")
                    print(f"  list 长度: {len(v['list'])}")
                    print(f"  list[0]: {json.dumps(v['list'][0], ensure_ascii=False)[:200]}")
                    found += 1
                    break
        if found >= 3:
            break
    if found >= 3:
        break

if not found:
    print("全库未找到 classParameters.list 非空的结构 —— 说明 locator 假设错了")
    # 打印一个真实含 classParameters 的结构
    for f in sorted(glob.glob("data/categories/*.json")):
        for r in json.loads(Path(f).read_text(encoding="utf-8")):
            for c in (r.get("captures") or []):
                raw = c.get("response_raw") or ""
                if "classParameters" not in raw:
                    continue
                d = json.loads(raw)
                for p, v in walk(d):
                    print(f"  路径 {p} -> {json.dumps(v, ensure_ascii=False)[:220]}")
                    break
                raise SystemExit
