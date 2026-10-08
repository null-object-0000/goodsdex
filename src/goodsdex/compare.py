"""A/B 对比：按类型化属性对齐，输出可核查的对比表。

关键原则（Codex 评审）：
  - 比较键是「属性 ID + 实体层级 + 条件」，不是中文字段名，也不是单位
  - 同品类比较取内部属性集合的并集；原始未知字段另列
  - 单元格引用断言，显示缺失原因、证据和冲突状态
  - 条件不同则并排展示，不强行判优劣
  - 跨品类只在显式定义的共同维度上比较，不自动把相似文字归成同一参数
  - 没有统一测试条件的官方最大值，只能做"厂商标称值对照"
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from typing import Optional

from .resolve import AttrDef, CATEGORY_RULES, build_view, parse_quantity, guess_category


@dataclass
class Cell:
    """对比表的一格"""

    attr: str
    label: str
    value: Optional[str] = None
    normalized: Optional[dict] = None      # {"value":..,"unit":..,"qualifiers":{..}}
    source_product: str = ""
    selected_from: str = ""                # assertion_id
    candidates: list = field(default_factory=list)
    status: str = "ok"                     # ok | missing | not_comparable | conflict
    missing_reason: str = ""               # source_empty | absent | not_collected
    note: str = ""

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v not in (None, "", [], {})}


@dataclass
class Comparison:
    """A/B 对比结果"""

    category: str
    products: list = field(default_factory=list)     # [{product_id, name}]
    rows: list = field(default_factory=list)         # [{"attr","label","cells":[...]}]
    unclassified: dict = field(default_factory=dict)
    warnings: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"category": self.category, "products": self.products,
                "rows": [{"attr": r["attr"], "label": r["label"],
                          "cells": [c.to_dict() for c in r["cells"]]} for r in self.rows],
                "unclassified": self.unclassified, "warnings": self.warnings}


def _normalize_for_display(raw, adef: Optional[AttrDef]) -> Optional[dict]:
    if adef and adef.value_type == "quantity":
        q = parse_quantity(raw, adef.unit)
        return {"value": q.value, "unit": q.unit, "range_max": q.range_max,
                "negative": q.negative, "raw_text": str(raw),
                "qualifiers": {k: v for k, v in q.qualifiers.items()
                               if k != "unit_inferred"}}
    return {"text": str(raw)}


def compare(records: list[dict], category: str = "", attrs: Optional[list[AttrDef]] = None) -> Comparison:
    """对同品类多个商品做 A/B 对比。

    records: pipeline 输出的记录列表（含 product / view）
    """
    if not records:
        return Comparison(category=category)

    cat = category if category in CATEGORY_RULES else guess_category(category)
    if not cat and records:
        cat = guess_category(records[0]["product"].get("name", ""))
    rules = CATEGORY_RULES.get(cat, {})
    adefs = attrs or rules.get("attrs", [])
    adef_by_id = {d.attr_id: d for d in adefs}

    cmp = Comparison(category=cat)
    cmp.products = [{"product_id": r["product"]["product_id"],
                     "name": r["product"].get("name")} for r in records]

    # 每个商品的视图
    views = {}
    for r in records:
        pid = r["product"]["product_id"]
        views[pid] = r.get("view") or {}

    # 按属性并集逐行输出
    for adef in adefs:
        cells = []
        for r in records:
            pid = r["product"]["product_id"]
            v = views[pid]
            vals = v.get("values") or {}
            sel = v.get("selected_from") or {}
            cands = v.get("candidates") or {}
            avail = v.get("availability") or {}
            gaps = {g["attr"]: g["reason"] for g in (v.get("gaps") or [])}

            if adef.attr_id in vals:
                cell = Cell(attr=adef.attr_id, label=adef.label,
                            value=str(vals[adef.attr_id]),
                            normalized=_normalize_for_display(vals[adef.attr_id], adef),
                            source_product=pid,
                            selected_from=sel.get(adef.attr_id, ""),
                            candidates=cands.get(adef.attr_id, []))
            else:
                reason = gaps.get(adef.attr_id) or avail.get(adef.attr_id) or "absent"
                cell = Cell(attr=adef.attr_id, label=adef.label, source_product=pid,
                            status="missing", missing_reason=str(reason))
            cells.append(cell)
        cmp.rows.append({"attr": adef.attr_id, "label": adef.label, "cells": cells})

    # 条件不同 / 冲突 的提示
    for row in cmp.rows:
        quals = set()
        for c in row["cells"]:
            if isinstance(c, Cell) and c.normalized and c.normalized.get("qualifiers"):
                quals.add(json.dumps(c.normalized["qualifiers"], sort_keys=True, ensure_ascii=False))
        if len(quals) > 1:
            for c in row["cells"]:
                if isinstance(c, Cell):
                    c.status = c.status if c.status != "ok" else "not_comparable"
                    c.note = "各商品测量条件不同，不可直接比优劣"

    # 未分类字段另列（不自动进入可比参数）
    unc = {}
    for r in records:
        pid = r["product"]["product_id"]
        u = (views[pid].get("unclassified") or {})
        for k, val in u.items():
            unc.setdefault(k, {})[pid] = val
    cmp.unclassified = unc

    cmp.warnings.append("官方标称值：无统一测试条件，仅作厂商标称对照，不代表实测优劣")
    return cmp


def _fmt_num(v) -> str:
    """数值格式化：整数不带小数点"""
    try:
        f = float(v)
        return str(int(f)) if f == int(f) else str(f)
    except (TypeError, ValueError):
        return str(v)


def render_text(cmp: Comparison, max_width: int = 30) -> str:
    """渲染为文本对比表"""
    lines = []
    names = [p["name"] or p["product_id"] for p in cmp.products]
    header = "属性".ljust(16) + "".join(n[:max_width].ljust(max_width + 2) for n in names)
    lines.append(header)
    lines.append("-" * len(header))
    for row in cmp.rows:
        cells = row["cells"]
        def fmt(c):
            if not isinstance(c, Cell):
                return "?"
            if c.status == "missing":
                return {"source_empty": "源未提供", "absent": "—",
                        "not_collected": "采集失败"}.get(c.missing_reason, "—")
            n = c.normalized or {}
            # 数值型：显示归一化后的数值（可比较），原始描述另存
            if n.get("value") is not None:
                v = f"{_fmt_num(n['value'])}{n.get('unit','')}"
                if n.get("negative"):
                    v = "不支持"
            else:
                v = c.value or ""
            if n.get("qualifiers"):
                qs = ",".join(f"{k}={vv}" for k, vv in n["qualifiers"].items())
                v = f"{v} ({qs})"
            if c.status == "not_comparable":
                v += " ⚠条件不同"
            return v
        lines.append(row["label"].ljust(16) +
                     "".join(fmt(c)[:max_width].ljust(max_width + 2) for c in cells))
    if cmp.warnings:
        lines.append("")
        for w in cmp.warnings:
            lines.append(f"注：{w}")
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    fp = sys.argv[1] if len(sys.argv) > 1 else "data/耳机.json"
    recs = json.load(open(fp, encoding="utf-8"))
    cat = sys.argv[2] if len(sys.argv) > 2 else ""
    c = compare(recs, category=cat)
    print(render_text(c))
    if c.unclassified:
        print(f"\n未归类字段（不参与对比）：{list(c.unclassified.keys())}")
