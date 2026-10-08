"""归一化与冲突判定测试"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from goodsdex.normalize import canon, is_junk, classify_conflict, flatten, normalize_record
from goodsdex.model import Provenance


def test_canon():
    assert canon("release_date") == "发布日期"
    assert canon("发布日期") == "发布日期"
    assert canon("蓝牙版本") == "蓝牙版本"
    assert canon("Weight of a single earbud") == "单耳重量"
    # 三个降噪必须是独立字段（不能合并）
    assert canon("降噪") == "降噪"
    assert canon("通话降噪") == "通话降噪"
    assert canon("抗风噪") == "抗风噪"


def test_junk():
    for v in ["", "无", "—", None, [], {}]:
        assert is_junk(v), v
    for v in ["5.3g", "IP54", ["a"]]:
        assert not is_junk(v), v


def test_conflict_kind():
    # 表述差异：数值相同
    assert classify_conflict([{"value": "约5.3g"}, {"value": "5.3±0.1g"}]) == "表述差异"
    # 表述差异：包含关系
    assert classify_conflict([{"value": "入耳式"}, {"value": "入耳式耳机"}]) == "表述差异"
    # 数据矛盾：数值不同
    assert classify_conflict([{"value": "34.5g"}, {"value": "43.4g"}]) == "数据矛盾"


def test_flatten():
    p = Provenance(source="mi_cn_mobile", raw_field="params")
    data = {"name": "X", "params": {"最大风速": "25m/s", "马达转速": "20000rpm"}}
    flat, fprov = flatten(data, {"name": p, "params": p})
    assert flat["最大风速"] == "25m/s"
    assert "params" not in flat
    assert fprov["最大风速"].raw_field == "params.最大风速"


def test_normalize_no_wrong_merge():
    """降噪三兄弟不能被合并"""
    P = lambda s: Provenance(source=s)
    rec = {"data": {"降噪": "42dB", "通话降噪": "双麦AI", "抗风噪": "6m/s"},
           "provenance": {"降噪": P("m"), "通话降噪": P("m"), "抗风噪": P("m")}}
    out = normalize_record(rec)
    assert "降噪" in out["data"] and "通话降噪" in out["data"] and "抗风噪" in out["data"]
    assert out["conflicts"] == []


if __name__ == "__main__":
    for fn in [test_canon, test_junk, test_conflict_kind, test_flatten, test_normalize_no_wrong_merge]:
        fn()
        print(f"  ✓ {fn.__name__}")
    print("全部通过")
