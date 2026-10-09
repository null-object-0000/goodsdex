"""有效实体集合：所有消费端共享的"哪些记录该参与统计/对比"。

Codex 评审指认：多个入口（vision_params、compare_all、audit_usability）
各自只判 `kind == machine`，没有排除：
  - 已被分类形态过滤掉的记录（excluded）
  - 已拆分父记录（is_multi_model_parent，其子记录才是真实体）
  - 跨分类重复的同一 product_id

于是覆盖度分母、对比行、补采判断都被重复计数污染。

这里提供**唯一定义**，各入口统一调用。
"""
from __future__ import annotations


def is_effective_machine(rec: dict) -> bool:
    """该记录是否是一个"有效整机实体"（可参与统计与对比）"""
    p = rec.get("product") or {}
    if p.get("kind") != "machine":
        return False
    if p.get("excluded") or p.get("excluded_reason"):
        return False            # 已被分类形态过滤
    if p.get("is_multi_model_parent"):
        return False            # 已拆父记录，子记录才是真实体
    return True


def effective_machines(recs: list[dict], dedupe: bool = True) -> list[dict]:
    """筛出有效整机。

    dedupe=True 时按 product_id 去重（保留首个出现的），
    避免同一商品在多个分类下被重复计入分母。
    """
    out, seen = [], set()
    for r in recs:
        if not is_effective_machine(r):
            continue
        pid = (r.get("product") or {}).get("product_id", "")
        if dedupe and pid in seen:
            continue
        seen.add(pid)
        out.append(r)
    return out


def effective_stats(recs: list[dict]) -> dict:
    """给出口径明确的统计，便于在报告里说明分母。"""
    total = len(recs)
    machines = [r for r in recs if (r.get("product") or {}).get("kind") == "machine"]
    excluded = [r for r in machines if (r.get("product") or {}).get("excluded")]
    parents = [r for r in machines if (r.get("product") or {}).get("is_multi_model_parent")]
    children = [r for r in machines if (r.get("product") or {}).get("is_model_child")]
    eff = effective_machines(recs)
    return {
        "records": total,
        "machines_raw": len(machines),
        "excluded_by_form": len(excluded),
        "split_parents": len(parents),
        "model_children": len(children),
        "effective_unique": len(eff),
        "basis": "有效整机 = kind=machine 且未被形态过滤 且非已拆父记录，按 product_id 去重",
    }


if __name__ == "__main__":
    import glob
    import json
    import sys
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    allrecs = []
    for f in sorted(glob.glob(str(root / "data" / "categories" / "*.json"))):
        try:
            allrecs += json.loads(Path(f).read_text(encoding="utf-8"))
        except Exception:
            pass
    st = effective_stats(allrecs)
    print("口径统计：")
    for k, v in st.items():
        print(f"  {k:22s} {v}")
