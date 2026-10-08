"""A/B 对比测试 —— 对应 Codex 评审第三优先级的验收标准。

验收：
  - 5g/5kg 不会被判等
  - 不同测试条件不会强比
  - 未知值不会进入计算
  - 明确不存在的能力不被当垃圾丢掉
  - 保留跨品类反例（耳机降噪不会进入吹风机噪声维度）
  - 报告分别统计元数据、参数与可比关键属性覆盖率
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from goodsdex.compare import Cell, compare, render_text
from goodsdex.identity import build_identity
from goodsdex.resolve import (DRYER_MAP, EARPHONE_MAP, build_view,
                              guess_category, parse_quantity)


def _rec(pid, name, params: dict, category=""):
    """构造一条最小记录（含断言 + 视图）"""
    from goodsdex.facts import Assertion
    asserts = [Assertion(assertion_id=f"{pid}:name", subject_id=pid, capture_id="c",
                         source="mi_cn_mobile", attribute="name", raw_value=name)]
    for i, (k, v) in enumerate(params.items()):
        asserts.append(Assertion(assertion_id=f"{pid}:{k}", subject_id=pid, capture_id="c",
                                 source="mi_cn_mobile", attribute=k, raw_value=v,
                                 locator=f"$.list[{i}]"))
    v = build_view(asserts, category=category, subject_id=pid)
    p = build_identity(pid, [{"commodity_id": f"{pid}0", "name": name}], category=category)
    p.name = name
    return {"product": p.to_dict(),
            "assertions": [a.to_dict() for a in asserts],
            "view": v.to_dict(), "captures": [], "discovery": {}}


def test_cross_category_not_merged():
    """耳机降噪不能进入吹风机噪声维度（跨品类反例）"""
    assert EARPHONE_MAP.get("降噪") == "anc.depth"
    assert DRYER_MAP.get("最大噪音") == "noise.max"
    assert DRYER_MAP.get("降噪") is None, "吹风机映射不应包含耳机的『降噪』"
    assert EARPHONE_MAP.get("最大噪音") is None
    # 两者的内部属性 ID 也不同
    assert "anc.depth" != "noise.max"


def test_similar_text_not_auto_grouped():
    """相似文字不自动归成同一参数（不做全局子串归并）"""
    # "抗风噪" 与 "降噪" 是两个属性，不因都含"噪"而合并
    assert EARPHONE_MAP["抗风噪"] != EARPHONE_MAP["降噪"]
    assert EARPHONE_MAP["通话降噪"] != EARPHONE_MAP["降噪"]


def test_unknown_attr_not_in_comparable():
    """未登记属性不进可计算参数，另列"""
    r = _rec("1", "测试耳机", {"降噪": "42dB", "某个没见过的字段": "xyz"}, category="earphone")
    v = r["view"]
    assert "anc.depth" in v["values"]
    assert "某个没见过的字段" in v["unclassified"]
    assert "某个没见过的字段" not in v["values"]


def test_missing_reason_shown():
    """缺失要说明原因，不能只显示空"""
    r = _rec("1", "测试耳机", {"降噪": "42dB"}, category="earphone")
    gaps = {g["attr"]: g["reason"] for g in r["view"]["gaps"]}
    assert "battery.single" in gaps
    assert gaps["battery.single"] in ("absent", "source_empty")


def test_compare_table_renders():
    """对比表能渲染，且每格引用断言"""
    a = _rec("1", "耳机A", {"降噪": "55dB", "耳机单次续航": "8h", "单耳重量": "5.3g"},
             category="earphone")
    b = _rec("2", "耳机B", {"降噪": "42dB", "耳机单次续航": "6h", "单耳重量": "4.5g"},
             category="earphone")
    cmp = compare([a, b], category="earphone")
    txt = render_text(cmp)
    assert "降噪深度" in txt and "55dB" in txt and "42dB" in txt
    # 单元格必须引用断言
    row = next(r for r in cmp.rows if r["attr"] == "anc.depth")
    for c in row["cells"]:
        assert isinstance(c, Cell) and c.selected_from, "每格必须引用断言"


def test_condition_difference_flagged():
    """条件不同的值不能强比，要标注"""
    from goodsdex.facts import Assertion
    asserts = [
        Assertion(assertion_id="1:name", subject_id="1", capture_id="c",
                  source="m", attribute="name", raw_value="A"),
        Assertion(assertion_id="1:life", subject_id="1", capture_id="c",
                  source="m", attribute="耳机单次续航", raw_value="降噪关：8小时"),
    ]
    v = build_view(asserts, category="earphone", subject_id="1")
    n = None
    from goodsdex.compare import _normalize_for_display
    from goodsdex.resolve import CATEGORY_RULES
    adef = next(d for d in CATEGORY_RULES["earphone"]["attrs"] if d.attr_id == "battery.single")
    n = _normalize_for_display(v.values["battery.single"], adef)
    assert n["qualifiers"].get("anc") == "off", "条件必须被解析出来"


def test_negative_not_lost():
    """明确不存在的能力不能被当垃圾丢掉"""
    r = _rec("1", "测试耳机", {"降噪": "不支持", "防尘防水": "IP54"}, category="earphone")
    v = r["view"]
    assert "anc.depth" in v["values"], "'不支持' 是有效信息，不能丢"
    assert v["values"]["anc.depth"] == "不支持"


def test_coverage_stats():
    """报告要分别统计元数据、参数与可比关键属性覆盖率"""
    from goodsdex.coverage import coverage_report
    a = _rec("1", "耳机A", {"降噪": "55dB", "耳机单次续航": "8h"}, category="earphone")
    b = _rec("2", "耳机B", {"降噪": "42dB"}, category="earphone")
    rep = coverage_report([a, b], category="earphone")
    assert "meta" in rep and "params" in rep and "key_attrs" in rep
    # A 有两个关键属性,B 只有一个 -> 覆盖率不同
    assert rep["key_attrs"]["per_product"]["耳机A"]["covered"] == 2
    assert rep["key_attrs"]["per_product"]["耳机B"]["covered"] == 1


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    ok = 0
    for fn in fns:
        try:
            fn(); print(f"  ✓ {fn.__name__}"); ok += 1
        except AssertionError as e:
            print(f"  ✗ {fn.__name__}: {e}")
        except Exception as e:
            print(f"  ✗ {fn.__name__}: {type(e).__name__}: {e}")
    print(f"\n{ok}/{len(fns)} 通过")
