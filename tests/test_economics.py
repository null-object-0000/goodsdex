"""换机经济模型测试

验收：
  - 残值是带时间戳和置信度的观测，不是常量
  - 保值换新按官方条款计算（保值率 / 实际值取高 / 补贴封顶）
  - 净支出、日均成本、盈亏平衡可复算
  - 官方 181–395 天窗口能正确判断
  - 缺数据时明确说"无法判断"，不猜
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from goodsdex.economics import (OwnedDevice, ResidualQuote, advise, break_even_days,
                                daily_cost_of_keeping, load_terms, official_trade_in,
                                render, upgrade_cost)


def test_terms_loaded_from_official():
    """条款来自官方一手页面，且带溯源信息"""
    t = load_terms()
    assert t, "官方条款文件必须存在"
    meta = t["_meta"]
    assert "mi.com" in meta["url"], "必须指向官方来源"
    assert meta.get("traceable") is True
    assert meta["source"].startswith("小米官方"), "不能是第三方解读"


def test_service_window_is_official_basis():
    """181-395 天窗口是官方基准，必须保留"""
    t = load_terms()
    w = t["benefit"]["service_window_days"]
    assert w["start"] == 181 and w["end"] == 395
    assert t["benefit"]["recycler"].startswith("转转"), "官方回收方是转转"


def test_subsidy_table_present():
    t = load_terms()
    tab = {k: v for k, v in t["trade_in_subsidy_table"].items() if not k.startswith("_")}
    assert len(tab) >= 40, "官方补贴表应覆盖 40+ 机型"
    assert tab["Xiaomi 15 Pro"] == 338
    assert tab["Xiaomi 14 Ultra"] == 398


def test_residual_is_observation_not_constant():
    """残值必须带来源和时间，否则无法判断时效"""
    q = ResidualQuote(low=2400, high=2800, kind="market",
                      source="转转 market_price", observed_at="2026-10-08",
                      confidence="medium")
    d = q.to_dict()
    assert d["mid"] == 2600
    assert d["observed_at"] and d["source"] and d["confidence"]
    # 区间只有下限时不能编造上限
    q2 = ResidualQuote(low=2000)
    assert q2.mid == 2000


def test_official_trade_in_branches_are_exclusive():
    """保值额与保底补贴是**互斥分支**，不可叠加

    Codex 评审指正：原实现把两者相加（激进且错误）。
    正确：符合保值标准 -> max(保值额, 质检额)；
         不符合标准   -> min(质检额 + 保底补贴, 保值额)。
    """
    t = load_terms()
    # 符合保值标准分支
    a = official_trade_in(5299, "Xiaomi 15 Pro", t, detected_value=3200,
                          meets_standard=True)
    assert a["guaranteed_rate"] == 0.5
    assert a["guaranteed_amount"] == round(5299 * 0.5)
    assert a["estimated_amount"] == 3200, "质检额高于保值额时取质检额"
    assert a["branch"] == "A"

    # 不符合标准分支：质检额 + 补贴，但封顶保值额
    b = official_trade_in(5299, "Xiaomi 15 Pro", t, detected_value=1000,
                          meets_standard=False)
    assert b["estimated_amount"] <= b["guaranteed_amount"], "不得超封顶"
    assert b["branch"] == "B"

    # **关键**：两者绝不能叠加
    c = official_trade_in(5299, "Xiaomi 15 Pro", t, detected_value=1000,
                          meets_standard=True)
    assert c["estimated_amount"] == round(5299 * 0.5), \
        "符合标准时不应再加补贴"


def test_unknown_condition_gives_scenarios_not_single_number():
    """成色未确认时不擅自给单一数字，要列两种情景"""
    t = load_terms()
    r = official_trade_in(5299, "Xiaomi 15 Pro", t, detected_value=0)
    assert r["estimated_amount"] is None, "成色未知不应给单一结论"
    assert "scenarios" in r
    assert set(r["scenarios"]) == {"meets_standard", "below_standard"}
    assert "requires" in r


def test_subsidy_cap():
    """保底补贴+质检额不超过 原价×保值率（仅分支 B 有补贴）"""
    t = load_terms()
    r = official_trade_in(5299, "Xiaomi 15 Pro", t, detected_value=1000,
                          meets_standard=False)
    assert r["estimated_amount"] <= r["guaranteed_amount"] + 1e-6, \
        "补贴+质检额不能超过封顶"
    # 成色未定时给情景，不给单一数字
    r2 = official_trade_in(5299, "Xiaomi 15 Pro", t, detected_value=1000)
    assert r2["estimated_amount"] is None
    assert r2["scenarios"]["below_standard"]["amount"] <= r2["guaranteed_amount"] + 1e-6


def test_rate_override():
    """机型专属保值率（60%）要生效"""
    t = load_terms()
    r = official_trade_in(3000, "Xiaomi Civi 4 Pro", t)
    assert r["guaranteed_rate"] == 0.6


def test_net_cost_math():
    assert upgrade_cost(5999, 2650, 338) == 3011
    assert upgrade_cost(5999, 2650, 338, other_fees=50) == 3061


def test_daily_cost_of_keeping():
    # (2600-1800)/365 = 2.19
    assert daily_cost_of_keeping(2600, 1800, 365) == 2.19
    assert daily_cost_of_keeping(2600, 1800, 0) == 0.0


def test_break_even():
    assert break_even_days(3011, 2.19) == 1375
    assert break_even_days(3011, 0) is None, "日均折旧为 0 时无平衡点"


def test_advise_does_not_double_count_subsidy():
    """回归：不能叠加保值额与保底补贴

    Codex 评审指正：原 test 把 5999-2650-338=3011 当正确答案，
    实际固化了错误规则（保值额 2650 与补贴 338 是互斥分支）。
    窗口内、成色未定时，回收额按市场残值算，不擅自加权益。
    """
    dev = OwnedDevice(name="Xiaomi 15 Pro", purchase_price=5299,
                      purchase_date="2026-01-15",   # 窗口内
                      residual=ResidualQuote(low=2400, high=2800, source="转转",
                                             observed_at="2026-10-08"),
                      trade_in_eligible=True)
    adv = advise(dev, new_price=5999, residual_later=1800, horizon_days=365)
    assert adv["answerable"]
    assert adv["window"]["status"] == "in_window"
    assert adv["benefit_usable"] is True
    # 成色未定 -> 不给单一金额，列情景
    assert "benefit_scenarios" in adv
    assert adv["upgrade"]["subsidy"] == 0, "不得额外叠加补贴"
    assert adv["upgrade"]["recover"] == 2600, "成色未定时按市场残值"
    assert adv["upgrade"]["net_cost"] == 3399
    # 不该再有"盈亏平衡"这个误导性标签
    assert "break_even_days" not in adv
    assert "转转" in " ".join(adv["evidence"])


def test_expired_window_disables_benefit():
    """回归：权益过期不能再享保值抵扣

    Codex 评审指正：原实现 purchase_date=2020 仍给 recover 2650 + subsidy 338，
    同时 window=expired，自相矛盾。
    """
    dev = OwnedDevice(name="Xiaomi 15 Pro", purchase_price=5299,
                      purchase_date="2020-01-01",
                      residual=ResidualQuote(low=1000, source="手动"),
                      trade_in_eligible=True)
    adv = advise(dev, new_price=5999, residual_later=500)
    assert adv["window"]["status"] == "expired"
    assert adv["benefit_usable"] is False
    assert adv["upgrade"]["recover"] == 1000, "过期后只能按市场残值"
    assert adv["upgrade"]["subsidy"] == 0
    assert any("超出" in c or "过期" in c for c in adv["caveats"])


def test_too_early_window_also_disables():
    """窗口未开始时同样不可用权益"""
    dev = OwnedDevice(name="Xiaomi 15 Pro", purchase_price=5299,
                      purchase_date="2026-09-01",   # 距今 < 181 天
                      residual=ResidualQuote(low=4000, source="手动"),
                      trade_in_eligible=True)
    adv = advise(dev, new_price=5999, residual_later=3000)
    assert adv["window"]["status"] == "too_early"
    assert adv["benefit_usable"] is False


def test_window_status():
    """官方窗口状态要能正确判断"""
    dev = OwnedDevice(name="X", purchase_price=1000, purchase_date="2026-07-18",
                      residual=ResidualQuote(low=500))
    adv = advise(dev, new_price=2000, residual_later=300)
    assert adv["window"]["status"] in ("too_early", "in_window", "expired")
    # 很久以前买的 -> 过期
    dev2 = OwnedDevice(name="X", purchase_price=1000, purchase_date="2020-01-01",
                       residual=ResidualQuote(low=100))
    adv2 = advise(dev2, new_price=2000, residual_later=50)
    assert adv2["window"]["status"] == "expired"


def test_no_residual_refuses_to_guess():
    """缺残值时必须明确拒绝判断，不能拍脑袋"""
    dev = OwnedDevice(name="未知机", purchase_price=5000)
    adv = advise(dev, new_price=6000, residual_later=2000)
    assert adv["answerable"] is False
    assert "残值" in adv["reason"] or "残值" in adv.get("action", "")


def test_render_does_not_judge_subjectively():
    """输出是数字与依据，不做主观断言，且不含误导性的"盈亏平衡" """
    dev = OwnedDevice(name="Xiaomi 15 Pro", purchase_price=5299,
                      purchase_date="2026-01-15",
                      residual=ResidualQuote(low=2400, high=2800, source="转转"),
                      trade_in_eligible=True)
    txt = render(advise(dev, new_price=5999, residual_later=1800))
    assert "净掏钱" in txt
    assert "只算钱" in txt, "必须声明模型只算钱，不含主观偏好"
    # 不再输出"盈亏平衡天数"（口径不成立，Codex 评审指正）
    assert "盈亏平衡" not in txt
    assert "互斥" in txt or "不可叠加" in txt, "必须声明分支不可叠加"


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
