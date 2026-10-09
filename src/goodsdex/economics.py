"""残值与换机经济：回答「继续用 vs 换新」哪个划算。

核心不是参数对比，是**钱**：

  继续用：边际日均成本 = (当前残值 − N 月后残值) / 天数
  换新：  净支出 = 新机价 − 旧机回收价 − 补贴
          日均成本 = 净支出 / 计划使用天数

盈亏平衡点 = 换新的净支出，摊到「继续用能撑多久」上，与继续用的贬值速度相等的那一天。

官方一手依据（小米保值换新条款，见 data/official/mi_trade_in_terms.json）：
  - 服务窗口：生效后第 181–395 天
  - 保值：原零售价 ×50%（部分 60%），与实际质检金额取高
  - 保底补贴：机型相关 ¥138–598，且补贴+质检额 ≤ 原价×保值率
  - 回收方：转转循环科技（所以转转估价是官方同源数据）

**所有价格都是区间/估计，不是承诺值**；模型输出的结论必须带置信度与依据。
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

TERMS_PATH = Path(__file__).resolve().parents[2] / "data" / "official" / "mi_trade_in_terms.json"


def load_terms(path: Optional[Path] = None) -> dict:
    p = path or TERMS_PATH
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


# ---------- 残值来源 ----------

@dataclass
class ResidualQuote:
    """一次残值观测。

    残值不是常量，是**带时间戳的观测**，且各有置信度 ——
    二手行情、平台估价、官方保值是三种不同性质的数。
    """

    low: float                      # 最低价（元）
    high: float = 0.0               # 最高价；0 表示未给区间
    kind: str = "market"            # market | platform_recycle | official_guarantee | user_input
    source: str = ""                # 来源标识
    observed_at: str = ""           # ISO 日期
    confidence: str = "medium"      # high | medium | low
    url: str = ""
    note: str = ""

    @property
    def mid(self) -> float:
        return (self.low + self.high) / 2 if self.high else self.low

    def to_dict(self) -> dict:
        d = asdict(self)
        d["mid"] = self.mid
        return d


# ---------- 官方保值换新 ----------

def official_trade_in(original_retail_price: float, model_name: str,
                      terms: Optional[dict] = None,
                      detected_value: float = 0.0,
                      meets_standard: Optional[bool] = None) -> dict:
    """按官方条款算保值换新能拿到的钱。

    **官方条款有两条互斥分支**（Codex 评审指正，此前实现错误地叠加了）：

      分支 A —— 符合保值回收标准（全新/99新/95新/9新 且功能正常）：
        拿 max(原零售价 × 保值率, 实际质检金额) 的现金券
        例：原价 5299、保值率 50%、质检 2600 -> 拿 2649.5（不是 2649.5+338）

      分支 B —— 不符合保值标准：
        拿「实际质检金额 + 保底补贴」，但总额封顶「原零售价 × 保值率」
        且此时**拿不到**保值额

    meets_standard=None 时两种情景都算出来，不擅自选一个当结论。
    """
    terms = terms or load_terms()
    if not terms:
        return {"available": False, "reason": "terms_not_loaded"}

    rate = terms.get("guaranteed_rate_overrides", {}).get(model_name)
    if rate is None:
        rate = terms.get("benchmark_rate") or terms.get("guaranteed_rate", {}).get("default", 0.5)

    table = terms.get("trade_in_subsidy_table", {})
    subsidy = 0
    for k, v in table.items():
        if k.startswith("_"):
            continue
        if model_name and (model_name in k or k in model_name):
            subsidy = v
            break

    guaranteed = round(original_retail_price * rate)
    win = terms.get("benefit", {}).get("service_window_days", {})

    # 分支 A：符合保值标准
    branch_a = max(guaranteed, detected_value) if detected_value > 0 else guaranteed

    # 分支 B：不符合标准 -> 质检额 + 保底补贴，封顶保值额
    branch_b = min(detected_value + subsidy, guaranteed) if detected_value > 0 else subsidy
    branch_b = min(branch_b, guaranteed)

    if meets_standard is True:
        amount, basis, branch = branch_a, "符合保值标准：保值额与质检额取高", "A"
    elif meets_standard is False:
        amount, basis, branch = branch_b, "不符合保值标准：质检额+保底补贴（封顶保值额）", "B"
    else:
        # 未判定成色时不擅自下结论，两个情景都给出
        return {
            "available": True, "model": model_name,
            "original_retail_price": original_retail_price,
            "guaranteed_rate": rate, "guaranteed_amount": guaranteed,
            "subsidy_amount": subsidy,
            "scenarios": {
                "meets_standard": {"amount": branch_a, "branch": "A",
                                   "basis": "保值额与质检额取高"},
                "below_standard": {"amount": branch_b, "branch": "B",
                                   "basis": "质检额+保底补贴，封顶保值额"},
            },
            "estimated_amount": None,       # 成色未知，不给单一数字
            "requires": "需确认成色（准新/99新/95新/9新 且功能正常与否）",
            "service_window_days": win,
            "recycler": terms.get("benefit", {}).get("recycler", ""),
            "caveat": "以实际检测为准，非承诺值；保值额与保底补贴不可叠加",
        }

    return {
        "available": True,
        "model": model_name,
        "original_retail_price": original_retail_price,
        "guaranteed_rate": rate,
        "guaranteed_amount": guaranteed,
        "subsidy_amount": subsidy,
        "estimated_amount": amount,
        "branch": branch,
        "basis": basis,
        "service_window_days": win,
        "recycler": terms.get("benefit", {}).get("recycler", ""),
        "caveat": "以实际检测为准，非承诺值",
    }


# ---------- 换机经济 ----------

@dataclass
class OwnedDevice:
    """手上这台设备"""

    name: str
    purchase_price: float                   # 购入价（原零售价）
    purchase_date: str = ""                 # ISO 日期
    residual: Optional[ResidualQuote] = None
    trade_in_eligible: bool = False          # 是否买过保值换新服务


def daily_cost_of_keeping(residual_now: float, residual_later: float,
                          days: int) -> float:
    """继续用的边际日均成本 —— 只是「折旧」，不含已经沉没的购机款"""
    if days <= 0:
        return 0.0
    return round((residual_now - residual_later) / days, 2)


def upgrade_cost(new_price: float, residual_now: float,
                 subsidy: float = 0.0, other_fees: float = 0.0) -> float:
    """换新净支出 = 新机价 − 旧机回收 − 补贴 + 其它费用"""
    return round(new_price - residual_now - subsidy + other_fees, 2)


def break_even_days(net_cost: float, daily_cost_keeping: float) -> Optional[int]:
    """盈亏平衡：继续用多少天后，其累计折旧等于换新的净支出。

    也就是「如果不换，这些钱要多久才'贬'回来」。
    """
    if daily_cost_keeping <= 0:
        return None
    return int(round(net_cost / daily_cost_keeping))


def advise(device: OwnedDevice, new_price: float, residual_later: float,
           horizon_days: int = 365, terms: Optional[dict] = None,
           planned_use_days: int = 730,
           meets_standard: Optional[bool] = None) -> dict:
    """给出换机成本情景（含依据与置信度，不下断言式结论）。

    **两个重要约束**（Codex 评审指正）：

    ① 权益窗口必须**先判定**。原实现在算完净支出后才加个文字标签，
       于是 purchase_date=2020 的设备仍得到 recover 2650 + subsidy 338，
       同时 window=expired —— 自相矛盾。窗口无效则权益不可用。

    ② **不再叠加保值额与保底补贴** —— 官方是两条互斥分支
       （见 official_trade_in）。

    另外：不再输出"盈亏平衡天数"。原实现把旧机折旧线性外推多年、
    未计新机折旧，不是真正的平衡点（净支出甚至可能超过当前残值）。
    改为只给可复算的净支出与情景对比。
    """
    terms = terms or load_terms()
    r = device.residual
    if not r:
        return {"answerable": False, "reason": "缺少当前残值观测",
                "action": "需要先获取残值（转转 market_price / recycle_valuation，或手动输入）"}

    res_now = r.mid
    keep_daily = daily_cost_of_keeping(res_now, residual_later, horizon_days)

    # ① 先判定窗口 —— 权益是否可用取决于此
    win = terms.get("benefit", {}).get("service_window_days", {}) if terms else {}
    window_status = "unknown"
    age = None
    if device.purchase_date and win:
        from datetime import date
        try:
            y, m, d = (int(x) for x in device.purchase_date.split("-")[:3])
            age = (date.today() - date(y, m, d)).days
            lo, hi = win.get("start", 181), win.get("end", 395)
            if age < lo:
                window_status = "too_early"
            elif age <= hi:
                window_status = "in_window"
            else:
                window_status = "expired"
        except Exception:
            pass

    benefit_usable = device.trade_in_eligible and window_status in ("in_window",)
    if not device.trade_in_eligible:
        window_status = window_status if window_status != "unknown" else "not_enrolled"

    # ② 权益计算（仅在可用时）
    ti = {}
    if benefit_usable:
        ti = official_trade_in(device.purchase_price, device.name, terms,
                               detected_value=0.0, meets_standard=meets_standard)
    recover = res_now                     # 权益不可用时只有市场残值
    subsidy = 0
    scenarios = None
    if ti.get("available"):
        if ti.get("estimated_amount") is not None:
            recover = max(res_now, ti["estimated_amount"])
        else:
            scenarios = ti.get("scenarios")
            recover = res_now              # 成色未定 -> 先用市场残值，情景另给

    net = upgrade_cost(new_price, recover, subsidy)
    new_daily = round(net / planned_use_days, 2) if planned_use_days else 0.0

    out = {
        "answerable": True,
        "device": device.name,
        "residual_observation": r.to_dict(),
        "keep": {"residual_now": res_now, "residual_later": residual_later,
                 "horizon_days": horizon_days, "daily_cost": keep_daily,
                 "note": "旧机折旧，机会成本口径；不含维修等支出"},
        "upgrade": {"new_price": new_price, "recover": recover, "subsidy": subsidy,
                    "net_cost": net, "planned_use_days": planned_use_days,
                    "daily_cost": new_daily,
                    "note": "净现金支出；两种方案未在同一期限比较期末净资产"},
        "benefit_usable": benefit_usable,
        "window": {"age_days": age, "status": window_status,
                   "window_days": [win.get("start"), win.get("end")] if win else None},
        "confidence": r.confidence,
        "evidence": [r.source] + ([ti.get("recycler", "")] if ti.get("available") else []),
        "caveats": [
            "残值为区间估计，实际以检测为准",
            "保值额与保底补贴是互斥分支，不可叠加",
            "换机决策还取决于新机是否带来你在意的能力提升，本模型只算钱",
        ],
    }
    if scenarios:
        out["benefit_scenarios"] = scenarios
        out["caveats"].append("成色未确认，权益金额按两种情景分别给出")
    if window_status == "expired" and device.trade_in_eligible:
        out["caveats"].append(
            f"已超出官方保值换新窗口（第 {win.get('start')}-{win.get('end')} 天），"
            f"当前只能按市场残值计算")
    elif window_status == "too_early":
        out["caveats"].append(
            f"尚未进入官方窗口（第 {win.get('start')} 天起），当前按市场残值计算")
    return out


def render(adv: dict) -> str:
    if not adv.get("answerable"):
        return f"无法判断：{adv.get('reason')}\n{adv.get('action','')}"
    k, u = adv["keep"], adv["upgrade"]
    L = [f"设备：{adv['device']}   (残值置信度：{adv['confidence']})", ""]
    L.append(f"  当前残值        ¥{k['residual_now']:.0f}"
             + (f"（区间 ¥{adv['residual_observation']['low']:.0f}–"
                f"{adv['residual_observation']['high']:.0f}）"
                if adv['residual_observation'].get('high') else ""))
    L.append(f"  继续用日均      ¥{k['daily_cost']:.2f}/天"
             f"   （{k['horizon_days']} 天贬值到 ¥{k['residual_later']:.0f}）")
    L.append("")
    L.append(f"  新机价          ¥{u['new_price']:.0f}")
    L.append(f"  旧机回收        −¥{u['recover']:.0f}")
    if u["subsidy"]:
        L.append(f"  换机补贴        −¥{u['subsidy']:.0f}")
    L.append(f"  净掏钱          ¥{u['net_cost']:.0f}")
    L.append(f"  换新日均        ¥{u['daily_cost']:.2f}/天（按 {u['planned_use_days']} 天摊）")
    if adv.get("benefit_scenarios"):
        L.append("")
        L.append("  保值换新权益（成色未确认，两种情景）：")
        for name, sc in adv["benefit_scenarios"].items():
            label = "符合保值标准" if name == "meets_standard" else "不符合标准"
            L.append(f"    {label}    可抵 ¥{sc['amount']:.0f}   ({sc['basis']})")
    if adv.get("window"):
        w = adv["window"]
        L.append("")
        st = {"in_window": "在窗口内", "too_early": "尚未开始",
              "expired": "已过期", "not_enrolled": "未购买该服务",
              "unknown": "未知"}.get(w.get("status"), w.get("status"))
        L.append(f"  官方窗口        {st}"
                 + (f"（已用 {w['age_days']} 天）" if w.get("age_days") else ""))
    if adv.get("caveats"):
        L.append("")
        for c in adv["caveats"]:
            L.append(f"  注：{c}")
    return "\n".join(L)


if __name__ == "__main__":
    terms = load_terms()
    print("官方条款已加载:", bool(terms),
          "| 机型补贴表:", len(terms.get("trade_in_subsidy_table", {})), "项"
          if terms else "")
    # 示例：Xiaomi 15 Pro，原价 5299
    dev = OwnedDevice(
        name="Xiaomi 15 Pro", purchase_price=5299, purchase_date="2026-01-15",
        residual=ResidualQuote(low=2400, high=2800, kind="market",
                               source="转转 market_price", observed_at="2026-10-08",
                               confidence="medium"),
        trade_in_eligible=True,
    )
    adv = advise(dev, new_price=5999, residual_later=1800, horizon_days=365)
    print(render(adv))
