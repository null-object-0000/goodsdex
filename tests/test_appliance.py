"""家电日成本模型测试。

核心是**口径正确性**：换新对比必须两边同口径，
不能只算"省下的电费"而忽略新机本身的支出。
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from goodsdex.appliance import (  # noqa: E402
    Appliance, Tariff, compare_replace, daily_cost, parse_energy_kwh,
)


# ------------------------------------------------------------ 解析

def test_parse_official_formats():
    """官方耗电量的各种写法都要能解析"""
    assert parse_energy_kwh("0.75kW·h/24h") == 0.75
    assert parse_energy_kwh("0.58kW·h/24h") == 0.58
    assert parse_energy_kwh("0.93kWh/24h") == 0.93
    assert parse_energy_kwh("1.2度/天") == 1.2


def test_parse_refuses_to_guess():
    """没有时间维度的数字不能当"每天"用 —— 宁可缺，不可猜"""
    assert parse_energy_kwh("220V") is None
    assert parse_energy_kwh("0.75kWh") is None      # 无 /24h，不知道是一天还是一年
    assert parse_energy_kwh(None) is None
    assert parse_energy_kwh("") is None


# ------------------------------------------------------------ 电价

def test_tariff_blended_weighting():
    """全天运行设备用时间加权电价，介于谷峰之间"""
    t = Tariff()
    assert t.offpeak < t.blended < t.peak
    # 峰 16h + 谷 8h（blended 保留 4 位小数用于展示，容差取 1e-4）
    assert abs(t.blended - (0.617 * 16 + 0.307 * 8) / 24) < 1e-4


# ------------------------------------------------------------ 日成本

def test_daily_cost_components():
    """日成本 = 电费 + 折旧，且分别可核"""
    d = Appliance(name="测试冰箱", price=3650, energy=0.75)
    cb = daily_cost(d, lifespan_years=10, tariff=Tariff())
    assert abs(cb.electricity_per_day - 0.75 * Tariff().blended) < 1e-6
    assert abs(cb.depreciation_per_day - 3650 / 3650) < 1e-6   # 1 元/天
    assert abs(cb.total_per_day - (cb.electricity_per_day + 1.0)) < 1e-6


def test_missing_energy_is_flagged_not_guessed():
    """缺耗电量时必须标注"算不了"，不能当 0 悄悄算成只折旧"""
    cb = daily_cost(Appliance(name="无参数机", price=3000, energy=None))
    assert cb.electricity_per_day == 0.0
    assert any("未标注耗电量" in c for c in cb.caveats)
    assert cb.total_per_day > 0        # 折旧部分仍算出来


def test_assumptions_are_exposed():
    """电价与寿命是假设，必须写出来"""
    cb = daily_cost(Appliance(name="x", price=1000, energy=1.0))
    joined = " ".join(cb.assumptions) + " ".join(cb.caveats)
    assert "电价" in joined and "寿命" in joined


def test_price_is_fully_amortized():
    """折旧总额应等于购机价（不重不漏）"""
    d = Appliance(name="x", price=2199, energy=0.5)
    cb = daily_cost(d, lifespan_years=8)
    assert abs(cb.depreciation_per_day * 8 * 365 - 2199) < 0.5


# ------------------------------------------------------------ 换新对比

def test_compare_uses_same_horizon():
    """两方案必须在同一时间窗内比 —— 不能拿旧机剩余年限比新机完整寿命"""
    old = Appliance(name="旧冰箱", price=2000, energy=1.2)
    new = Appliance(name="新冰箱", price=3000, energy=0.6)
    r = compare_replace(old, new, lifespan_years=10, old_age_years=8,
                        horizon_years=5)
    assert r["horizon_years"] == 5
    # 换新一侧必须含购机支出，不能只算电费
    assert r["new"]["total"] >= new.price
    # 继续用一侧只有电费
    assert abs(r["old"]["total"] - r["old"]["electricity"]) < 0.01
    assert r["electricity_saving_per_day"] > 0


def test_compare_does_not_use_mismatched_depreciation():
    """回归：旧机折旧率不能因为"剩余年限短"而虚高

    旧写法用 old.price/(剩余年限) 与 new.price/(完整寿命) 相减，
    旧机分母小 -> 折旧虚高 -> 显得"换新更省"，是假结论。
    新写法固定观察窗，窗内旧机只计电费。
    """
    old = Appliance(name="旧", price=2000, energy=0.8)
    new = Appliance(name="新", price=2000, energy=0.8)   # 完全同规格
    r = compare_replace(old, new, lifespan_years=10, old_age_years=9,
                        horizon_years=5)
    # 同规格时换新必然更贵（多花一台机器的钱）
    # delta = 继续用 − 换新，此处应为负（换新支出更高）
    assert r["delta"] < 0, f"同规格换新不该更省钱，得到 delta={r['delta']}"
    assert r["electricity_saving_per_day"] == 0


def test_compare_reports_payback_from_electricity_only():
    """回本天数只能基于"省下的电费" —— 这是可核的口径"""
    old = Appliance(name="旧", price=1000, energy=1.0)
    new = Appliance(name="新", price=2000, energy=0.5)
    r = compare_replace(old, new, lifespan_years=10, old_age_years=9)
    assert r["payback_days"] is not None
    expected = int(round(2000 / r["electricity_saving_per_day"]))
    assert r["payback_days"] == expected


def test_no_electricity_saving_means_no_payback():
    """新机不省电就不能靠省电回本 —— 不能编一个数字出来"""
    old = Appliance(name="旧", price=1000, energy=0.5)
    new = Appliance(name="新", price=2000, energy=0.6)
    r = compare_replace(old, new, lifespan_years=10)
    assert r["electricity_saving_per_day"] < 0
    assert r["payback_days"] is None


def test_missing_residual_not_invented():
    """没有残值数据时明确写"未计"，不臆造一个回收价"""
    old = Appliance(name="旧", price=1000, energy=1.0)
    new = Appliance(name="新", price=2000, energy=0.5)
    r = compare_replace(old, new)
    assert any("未计旧机回收残值" in c for c in r["caveats"])


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    ok = 0
    for fn in fns:
        try:
            fn()
            print(f"  ✓ {fn.__name__}")
            ok += 1
        except AssertionError as e:
            print(f"  ✗ {fn.__name__}: {e}")
    print(f"\n{ok}/{len(fns)} 通过")
