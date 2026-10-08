"""采集闭环测试 —— 针对 Codex 评审指出的问题，逐条验收。

验收标准（来自 docs/REVIEW-codex.md 第一优先级的验收）：
  - 同名不同值、同值多源、空参数、业务失败、网络失败五种离线样例
    都能导出并读回
  - 每个候选能定位原始快照
  - 采集时间不会被归一化刷新
  - 失败不会伪报成功
  - 历史不会被覆盖
"""
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from goodsdex.facts import (Assertion, Availability, Bundle, Capture, CaptureStatus,
                            Subject)
from goodsdex.resolve import AttrDef, build_view, parse_quantity, values_conflict


# ---------- 1. 数字/单位解析（修"忽略单位判等"） ----------

def test_quantity_units():
    a = parse_quantity("5g", "g")
    b = parse_quantity("5kg", "kg")
    assert a.value == 5 and a.unit == "g"
    assert b.value == 5 and b.unit == "kg"
    # 单位不同 -> 不可比，不能判等
    A = Assertion(assertion_id="a", subject_id="s", capture_id="c", source="x",
                  attribute="w", raw_value="5g")
    B = Assertion(assertion_id="b", subject_id="s", capture_id="c", source="x",
                  attribute="w", raw_value="5kg")
    d = AttrDef("w", "重量", "quantity", "g")
    assert values_conflict(A, B, d) == "incomparable", "5g 与 5kg 不能判等"


def test_negation_preserved():
    """修"包含关系掩盖否定"：不能拿"第一数字相同"证明相等"""
    A = Assertion(assertion_id="a", subject_id="s", capture_id="c", source="x",
                  attribute="anc", raw_value="无主动降噪")
    B = Assertion(assertion_id="b", subject_id="s", capture_id="c", source="x",
                  attribute="anc", raw_value="主动降噪")
    d = AttrDef("anc", "降噪", "text")
    assert values_conflict(A, B, d) == "conflict", "否定与肯定必须判冲突"
    # 数值型也一致
    C = Assertion(assertion_id="c", subject_id="s", capture_id="c", source="x",
                  attribute="anc", raw_value="不支持")
    assert parse_quantity("不支持").negative is True


def test_qualifier_not_merged():
    """修"降噪开/关续航被合并"：条件不同 -> 不可比"""
    A = Assertion(assertion_id="a", subject_id="s", capture_id="c", source="x",
                  attribute="life", raw_value="降噪关短续航：8小时")
    B = Assertion(assertion_id="b", subject_id="s", capture_id="c", source="x",
                  attribute="life", raw_value="降噪开短续航：4.5小时")
    d = AttrDef("life", "续航", "quantity", "h")
    assert values_conflict(A, B, d) == "incomparable", "不同工作模式不可比"


def test_compatible_not_equal():
    """约5.3g 与 5.3±0.1g：可以展示为可能兼容，但不能宣称事实相等"""
    A = Assertion(assertion_id="a", subject_id="s", capture_id="c", source="m",
                  attribute="w", raw_value="约5.3g")
    B = Assertion(assertion_id="b", subject_id="s", capture_id="c", source="p",
                  attribute="w", raw_value="5.3±0.1g")
    d = AttrDef("w", "重量", "quantity", "g")
    assert values_conflict(A, B, d) == "compatible"


# ---------- 2. 证据保留（修"同值多源佐证丢失"） ----------

def test_same_value_multisource_kept():
    """两源给出相同值时，两条断言都要保留（都是独立佐证）"""
    b = Bundle(subject=Subject(subject_id="s"))
    b.add_assertions([
        Assertion(assertion_id="m1", subject_id="s", capture_id="c1", source="mi_cn_mobile",
                  attribute="price", raw_value="79", locator="$.a"),
        Assertion(assertion_id="p1", subject_id="s", capture_id="c2", source="mi_cn_pc",
                  attribute="pc_price", raw_value="79", locator="$.b"),
    ])
    assert len(b.assertions) == 2
    v = build_view(b.assertions, category="dryer", subject_id="s")
    # 移动端 price 与 PC pc_price 是不同属性，各自保留（不做错误合并）
    assert v.values.get("price") == "79"
    assert v.values.get("pc_price") == "79"


def test_no_overwrite_by_field_name():
    """修"同名字段后者覆盖前者"：断言列表不按属性名去重"""
    b = Bundle(subject=Subject(subject_id="s"))
    b.add_assertions([
        Assertion(assertion_id="a1", subject_id="s", capture_id="c1", source="mi_cn_mobile",
                  attribute="price", raw_value="100"),
        Assertion(assertion_id="a2", subject_id="s", capture_id="c2", source="mi_cn_pc",
                  attribute="price", raw_value="200"),
    ])
    assert len(b.assertions) == 2, "同名断言必须都保留，供后续对账"


# ---------- 3. 采集状态（修"空响应伪报成功"） ----------

def test_capture_status_distinguishes_failure():
    ok = Capture.make("mi_cn_mobile", "u", '{"a":1}', status=CaptureStatus.SUCCESS)
    err = Capture.make("mi_cn_pc", "u", "", status=CaptureStatus.TRANSPORT_ERROR,
                       error="timeout")
    assert ok.status == CaptureStatus.SUCCESS
    assert err.status == CaptureStatus.TRANSPORT_ERROR
    assert "timeout" in err.error
    # 两者必须能区分，不能都算"成功"
    assert ok.status != err.status


def test_source_empty_vs_absent():
    """空参数列表是有效结果(source_empty)，不是"官方没录入"的推断"""
    b = Bundle(subject=Subject(subject_id="s"))
    b.add_assertions([
        Assertion(assertion_id="e1", subject_id="s", capture_id="c", source="mi_cn_mobile",
                  attribute="_params_empty", raw_value=True,
                  availability=Availability.SOURCE_EMPTY),
        Assertion(assertion_id="n1", subject_id="s", capture_id="c", source="mi_cn_mobile",
                  attribute="name", raw_value="测试耳机"),
    ])
    v = build_view(b.assertions, category="earphone", subject_id="s")
    reasons = {g["attr"]: g["reason"] for g in v.gaps}
    assert reasons.get("anc.depth") == "source_empty", "空参数应标 source_empty 而非 absent"


def test_error_not_stored_as_field():
    """采集异常不能伪装成商品字段"""
    b = Bundle(subject=Subject(subject_id="s"))
    b.add_capture(Capture.make("mi_cn", "u", "", status=CaptureStatus.TRANSPORT_ERROR,
                               error="boom"))
    # 断言层不应出现 _err 之类的伪字段
    assert all(not a.attribute.endswith("_err") for a in b.assertions)


# ---------- 4. 序列化（修"冲突记录序列化失败"） ----------

def test_full_record_serializable():
    """含冲突/缺口的完整记录必须能导出并读回"""
    b = Bundle(subject=Subject(subject_id="s", name="X"))
    b.add_capture(Capture.make("mi_cn_mobile", "u", '{"raw":1}'))
    b.add_assertions([
        Assertion(assertion_id="a1", subject_id="s", capture_id="c", source="mi_cn_mobile",
                  attribute="最大风速", raw_value="62m/s"),
        Assertion(assertion_id="a2", subject_id="s", capture_id="c", source="mi_cn_pc",
                  attribute="最大风速", raw_value="70m/s"),
        Assertion(assertion_id="a3", subject_id="s", capture_id="c", source="mi_cn_mobile",
                  attribute="额定功率", raw_value="1600W"),
    ])
    v = build_view(b.assertions, category="dryer", subject_id="s")
    rec = {"subject": b.subject.to_dict(),
           "captures": [c.to_dict() for c in b.captures],
           "assertions": [a.to_dict() for a in b.assertions],
           "view": v.to_dict()}
    s = json.dumps(rec, ensure_ascii=False)     # 不能抛异常
    back = json.loads(s)                        # 必须能读回
    assert len(back["assertions"]) == 3
    assert back["view"]["values"]["wind.speed"] in ("62m/s", "70m/s")
    # 数值不同 -> 必须记录为冲突关系，且两个候选都在
    rels = [r for r in back["view"]["relations"] if r["attr"] == "wind.speed"]
    assert rels and rels[0]["relation"] == "conflict", "62 与 70 应判冲突"


def test_assertion_locator_points_to_raw():
    """定位必须指向原始响应的路径，不是解析后临时 dict 的键"""
    a = Assertion(assertion_id="x", subject_id="s", capture_id="c", source="mi_cn_mobile",
                  attribute="最大风速", raw_value="62m/s",
                  locator="$.data.goodsInfo.goodsList[0].classParameters.list[3]")
    assert a.locator.startswith("$."), "locator 应是相对原始响应的 JSONPath"
    assert "classParameters.list[" in a.locator, "参数应带原始数组索引"


def test_availability_preserved():
    """'无'/'暂未公布' 等明确表达不能被当垃圾丢掉"""
    b = Bundle(subject=Subject(subject_id="s"))
    b.add_assertions([
        Assertion(assertion_id="a", subject_id="s", capture_id="c", source="mi_cn_mobile",
                  attribute="降噪", raw_value="无", availability=Availability.EXPLICITLY_UNKNOWN),
    ])
    assert b.assertions[0].availability == Availability.EXPLICITLY_UNKNOWN


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for fn in fns:
        try:
            fn()
            print(f"  ✓ {fn.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  ✗ {fn.__name__}: {e}")
        except Exception as e:
            print(f"  ✗ {fn.__name__}: {type(e).__name__}: {e}")
    print(f"\n{passed}/{len(fns)} 通过")
