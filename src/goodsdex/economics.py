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
                      detected_value: float = 0.0) -> dict:
    """按官方条款算保值换新能拿到的钱。

    规则：保值金额 = 原零售价 × 保值率，与实际质检金额取高；
        若不满足保值标准，则 实际质检金额 + 保底补贴，但总额封顶 原价×保值率。
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
    # 二者取高
    if detected_value > 0:
        amount = max(guaranteed, detected_value)
        basis = "实际质检金额高于保值金额" if detected_value > guaranteed else "保值金额"
    else:
        amount = guaranteed
        basis = "保值金额（未提供质检金额）"
    # 保底补贴封顶
    cap = guaranteed
    if detected_value <= guaranteed:
        amount = min(amount, cap)

    win = terms.get("benefit", {}).get("service_window_days", {})
    return {
        "available": True,
        "model": model_name,
        "original_retail_price": original_retail_price,
        "guaranteed_rate": rate,
        "guaranteed_amount": guaranteed,
        "subsidy_amount": subsidy,
        "estimated_amount": amount,
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
           planned_use_days: int = 730) -> dict:
    """给出换机建议（含依据与置信度，不下断言式结论）"""
    terms = terms or load_terms()
    r = device.residual
    if not r:
        return {"answerable": False, "reason": "缺少当前残值观测",
                "action": "需要先获取残值（转转 market_price / recycle_valuation，或手动输入）"}

    res_now = r.mid
    keep_daily = daily_cost_of_keeping(res_now, residual_later, horizon_days)

    ti = {}
    if device.trade_in_eligible:
        ti = official_trade_in(device.purchase_price, device.name, terms,
                               detected_value=res_now)
    subsidy = ti.get("subsidy_amount", 0) if ti.get("available") else 0
    # 保值换新权益下的回收额取高
    recover = max(res_now, ti.get("estimated_amount", 0)) if ti.get("available") else res_now

    net = upgrade_cost(new_price, recover, subsidy)
    new_daily = round(net / planned_use_days, 2) if planned_use_days else 0.0
    be = break_even_days(net, keep_daily)

    out = {
        "answerable": True,
        "device": device.name,
        "residual_observation": r.to_dict(),
        "keep": {"residual_now": res_now, "residual_later": residual_later,
                 "horizon_days": horizon_days, "daily_cost": keep_daily},
        "upgrade": {"new_price": new_price, "recover": recover, "subsidy": subsidy,
                    "net_cost": net, "planned_use_days": planned_use_days,
                    "daily_cost": new_daily},
        "break_even_days": be,
        "confidence": r.confidence,
        "evidence": [r.source] + ([ti.get("recycler", "")] if ti.get("available") else []),
        "caveats": [
            "残值为区间估计，实际以检测为准",
            "换机决策还取决于新机是否带来你在意的能力提升，本模型只算钱",
        ],
    }
    # 时间窗判断（官方 181-395 天）
    win = terms.get("benefit", {}).get("service_window_days", {}) if terms else {}
    if device.purchase_date and win:
        from datetime import date
        try:
            y, m, d = (int(x) for x in device.purchase_date.split("-")[:3])
            age = (date.today() - date(y, m, d)).days
            lo, hi = win.get("start", 181), win.get("end", 395)
            if age < lo:
                out["window"] = {"age_days": age, "status": "too_early",
                                 "message": f"使用 {age} 天，官方保值换新窗口从第 {lo} 天开始，"
                                            f"还有 {lo - age} 天"}
            elif age <= hi:
                out["window"] = {"age_days": age, "status": "in_window",
                                 "message": f"使用 {age} 天，正在官方保值换新窗口内"
                                            f"（{lo}–{hi} 天），剩 {hi - age} 天"}
            else:
                out["window"] = {"age_days": age, "status": "expired",
                                 "message": f"使用 {age} 天，已超出官方保值换新窗口"
                                            f"（{hi} 天），走高保值率的路已关闭"}
        except Exception:
            pass
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
    if adv.get("break_even_days"):
        L.append("")
        L.append(f"  盈亏平衡        {adv['break_even_days']} 天 —— 不换的话，"
                 f"旧机要贬掉这么多钱需要这么久")
    if adv.get("window"):
        w = adv["window"]
        L.append("")
        L.append(f"  官方窗口        {w['message']}")
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
