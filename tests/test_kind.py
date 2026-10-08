"""商品类型与分类过滤测试

这些规则的依据全部来自实跑观察，不是拍脑袋：
  - 搜「壁挂空调」89 条里混着保养服务、滤网、检测服务
  - 搜「壁挂空调/立式空调/中央空调」返回 92/92/91 条高度重叠
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from goodsdex.kind import classify_product_kind, split_kinds
from goodsdex.category_filter import filter_category, matches_category


# ---------- 类型分流 ----------

def test_service_detected():
    assert classify_product_kind("空调清洁保养服务") == "service"
    assert classify_product_kind("空调检测服务") == "service"
    assert classify_product_kind("小米手机保值换新服务") == "service"


def test_accessory_detected():
    assert classify_product_kind("米家除醛滤网（中央空调）") == "accessory"
    assert classify_product_kind("米家新风空调滤芯 （挂机）") == "accessory"
    assert classify_product_kind("米家驱蚊滤网（挂机）") == "accessory"


def test_machine_detected():
    assert classify_product_kind("巨省电 1.5匹新一级能效 小米空调") == "machine"
    assert classify_product_kind("米家高速吹风机") == "machine"
    assert classify_product_kind("Xiaomi 15 Pro") == "machine"
    assert classify_product_kind("REDMI Buds 8 Pro") == "machine"
    assert classify_product_kind("米家扫地机器人") == "machine"


def test_service_and_accessory_are_not_machines():
    """服务与耗材没有换代意义，绝不能进代际表"""
    for n in ("空调清洁保养服务", "米家除醛滤网（中央空调）", "空调检测服务"):
        assert classify_product_kind(n) != "machine", f"{n} 不该被判为整机"


def test_split_kinds_counts():
    recs = [{"product": {"name": "小米空调"}},
            {"product": {"name": "空调清洁保养服务"}},
            {"product": {"name": "米家除醛滤网"}}]
    s = split_kinds(recs)
    assert s["counts"]["machine"] == 1
    assert s["counts"]["service"] == 1
    assert s["counts"]["accessory"] == 1
    assert len(s["machines"]) == 1


# ---------- 分类过滤 ----------

def test_wall_mounted_excludes_floor_standing():
    """壁挂空调分类要排除立式/柜机/中央空调"""
    ok, _ = matches_category("巨省电 1.5匹新一级能效 小米空调", "壁挂空调")
    assert ok
    ok2, reason2 = matches_category("双出风 立式3匹新一级能效 米家空调", "壁挂空调")
    assert not ok2, "立式空调不该出现在壁挂空调分类"
    assert "立式" in reason2


def test_floor_standing_excludes_wall():
    ok, _ = matches_category("双出风 立式3匹新一级能效 米家空调", "立式空调")
    assert ok
    ok2, _ = matches_category("巨省电 1.5匹新一级能效 小米空调", "立式空调")
    assert not ok2


def test_central_ac_excludes_wall_and_floor():
    ok, _ = matches_category("米家中央空调 巨省电 风管机 大3匹超一级能效", "中央空调Pro")
    assert ok
    assert not matches_category("巨省电 1.5匹 小米空调", "中央空调Pro")[0]
    assert not matches_category("双出风 立式3匹 米家空调", "中央空调Pro")[0]


def test_front_load_vs_top_load():
    assert matches_category("米家滚筒洗衣机 10kg", "滚筒洗衣机")[0]
    assert not matches_category("米家波轮洗衣机 10kg", "滚筒洗衣机")[0]
    assert matches_category("米家波轮洗衣机 10kg", "波轮洗衣机")[0]


def test_no_rule_keeps_everything():
    """没定义的分类不过滤，避免误杀"""
    ok, reason = matches_category("随便什么商品", "不存在的分类")
    assert ok and reason == "no_rule"


def test_filter_marks_not_drops():
    """被排除的不能静默丢弃，要带原因保留供复核"""
    recs = [{"product": {"name": "巨省电 1.5匹 小米空调"}},
            {"product": {"name": "双出风 立式3匹 米家空调"}}]
    kept, dropped = filter_category(recs, "壁挂空调")
    assert len(kept) == 1 and len(dropped) == 1
    assert dropped[0]["product"]["excluded_reason"], "必须记录排除原因"


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
