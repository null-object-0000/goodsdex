"""覆盖度统计 —— 让指标对应下游价值。

Codex 评审指出：
  "33 字段""0 冲突"没有质量保证：图片和内部 ID 能撑高字段数，
  误并、漏接源又能降低冲突数。

所以按品类定义决策关键属性，分别统计：
  采集成功率 / 参数覆盖率 / 身份确认率 / 可定位证据率 /
  可比条件覆盖率 / 未解决关系数

分母来自版本化的比较 schema，不是本次响应恰好出现的键。
"""
from __future__ import annotations
import json
from typing import Optional

from .resolve import CATEGORY_RULES, guess_category

SCHEMA_VERSION = "attr-schema-v1"

# 通用元数据（固定 schema，用于统计 meta 覆盖率）
META_ATTRS = ["name", "price", "market_price", "colors", "img_url", "carousel"]


def coverage_report(records: list[dict], category: str = "") -> dict:
    """统计一个品类下多商品的覆盖度"""
    cat = category if category in CATEGORY_RULES else guess_category(category)
    if not cat and records:
        cat = guess_category(records[0].get("product", {}).get("name", ""))
    key_attrs = [d.attr_id for d in CATEGORY_RULES.get(cat, {}).get("attrs", [])]

    per_product = {}
    capture_ok = capture_total = 0
    locatable = total_assertions = 0
    unresolved = 0

    for r in records:
        name = r["product"].get("name") or r["product"]["product_id"]
        v = r.get("view") or {}
        vals = v.get("values") or {}
        avail = v.get("availability") or {}

        # 元数据覆盖率
        meta_hit = sum(1 for a in META_ATTRS if a in vals)
        # 关键属性覆盖率（分母是 schema 定义，不是实际出现的键）
        keys_hit = sum(1 for a in key_attrs if a in vals)
        # 身份确认率
        conf = r["product"].get("identity_confidence", "unverified")

        caps = r.get("captures") or []
        capture_total += len(caps)
        capture_ok += sum(1 for c in caps if c.get("status") == "success")

        asserts = r.get("assertions") or []
        total_assertions += len(asserts)
        locatable += sum(1 for a in asserts if a.get("locator"))

        unresolved += len(v.get("relations") or [])

        per_product[name] = {
            "meta": {"covered": meta_hit, "total": len(META_ATTRS)},
            "key_attrs": {"covered": keys_hit, "total": len(key_attrs)},
            "identity_confidence": conf,
            "captures_ok": sum(1 for c in caps if c.get("status") == "success"),
            "captures_total": len(caps),
            "assertions": len(asserts),
            "gaps": len(v.get("gaps") or []),
            "relations": len(v.get("relations") or []),
        }

    n = max(len(records), 1)
    return {
        "schema_version": SCHEMA_VERSION,
        "category": cat,
        "products": len(records),
        "meta": {"attrs": META_ATTRS},
        "params": {"key_attrs": key_attrs, "schema_version": SCHEMA_VERSION},
        "key_attrs": {"per_product": {k: v["key_attrs"] for k, v in per_product.items()},
                      "total": len(key_attrs)},
        "summary": {
            "capture_success_rate": round(capture_ok / max(capture_total, 1), 3),
            "locatable_evidence_rate": round(locatable / max(total_assertions, 1), 3),
            "identity_verified_rate": round(
                sum(1 for v in per_product.values()
                    if v["identity_confidence"] == "verified") / n, 3),
            "key_attr_coverage_avg": round(
                sum(v["key_attrs"]["covered"] for v in per_product.values())
                / max(sum(v["key_attrs"]["total"] for v in per_product.values()), 1), 3),
            "unresolved_relations": unresolved,
        },
        "per_product": per_product,
    }


def render_report(rep: dict) -> str:
    s = rep["summary"]
    lines = [
        f"品类: {rep['category']}  |  商品数: {rep['products']}  |  schema: {rep['schema_version']}",
        "",
        f"采集成功率        {s['capture_success_rate']:.0%}",
        f"可定位证据率      {s['locatable_evidence_rate']:.0%}",
        f"身份确认率        {s['identity_verified_rate']:.0%}",
        f"关键属性覆盖率    {s['key_attr_coverage_avg']:.0%}  (分母={rep['key_attrs']['total']} 项 schema 属性)",
        f"未解决关系数      {s['unresolved_relations']}",
        "",
        f"{'商品':28s}{'关键属性':>10s}{'缺口':>6s}{'断言':>6s}{'身份':>8s}",
    ]
    for name, d in rep["per_product"].items():
        ka = f"{d['key_attrs']['covered']}/{d['key_attrs']['total']}"
        lines.append(f"{name[:26]:28s}{ka:>10s}{d['gaps']:>6d}{d['assertions']:>6d}"
                     f"{d['identity_confidence']:>8s}")
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    fp = sys.argv[1] if len(sys.argv) > 1 else "data/耳机.json"
    cat = sys.argv[2] if len(sys.argv) > 2 else ""
    print(render_report(coverage_report(json.load(open(fp, encoding="utf-8")), cat)))
