"""家电持有成本模型：「这台每天花你多少钱」。

与手机不同，家电没有保值换新体系，它的日常成本由两块构成：

  ① 电费   —— 官方标注的耗电量（kW·h/24h）× 电价
  ② 折旧   —— 购机价 ÷ 预期寿命

**关键设计约束**（沿用本项目一贯原则）：

- 电价、预期寿命都是**假设**，必须显式暴露并可覆盖，
  不能悄悄内嵌一个数字假装是事实。
- 耗电量是**官方标注值**（实验室工况），实际随环境/使用习惯浮动，
  必须标注来源与不确定性，不能当成实测。
- 换新判断要**两边同口径**：拿"继续用旧机的日成本"对比
  "换新机的日成本（含摊到寿命的新机价）"，
  而不是只算省下的电费 —— 那会忽略新机本身的支出。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------- 电价

# 上海居民阶梯电价（第一档，一户一表，分时）
# 来源：上海市发改委《关于本市居民生活用电试行阶梯电价实施方案的通知》
#   https://fgw.sh.gov.cn/ys-szgyjcssfw-1.4.2-h5/20240819/...
#   峰时段（6:00-22:00）0.617 元/度；谷时段（22:00-次日6:00）0.307 元/度
SH_TIER1_PEAK = 0.617
SH_TIER1_OFFPEAK = 0.307

# 冰箱等全天运行设备按时间加权：峰 16h + 谷 8h
_BLEND = (SH_TIER1_PEAK * 16 + SH_TIER1_OFFPEAK * 8) / 24


@dataclass
class Tariff:
    """电价假设。默认用上海居民第一档分时的**时间加权**值。"""

    peak: float = SH_TIER1_PEAK
    offpeak: float = SH_TIER1_OFFPEAK
    peak_hours: int = 16
    source: str = ("上海市发改委：居民阶梯电价第一档（峰 0.617 / 谷 0.307 元·度）")
    note: str = ("第一档上限 3120 度/户·年；超出后进入第二/三档，"
                 "电价上升。本估算按第一档计，可能偏低。")

    @property
    def blended(self) -> float:
        """全天运行设备的时间加权电价"""
        total = self.peak_hours + (24 - self.peak_hours)
        if total <= 0:
            return self.peak
        return round((self.peak * self.peak_hours
                      + self.offpeak * (24 - self.peak_hours)) / total, 4)


# ---------------------------------------------------------------- 解析

def parse_energy_kwh(value) -> Optional[float]:
    """把官方耗电量文本解析成 度/天。

    官方写法实测有：
      "0.75kW·h/24h"、"0.58kW·h/24h"
      "0.75度/天"、"0.75kWh"
    解析不出返回 None —— 宁可缺，不可猜。
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    import re
    s = str(value).strip().lower()
    if not s:
        return None
    m = re.search(r"(\d+(?:\.\d+)?)", s)
    if not m:
        return None
    n = float(m.group(1))
    # 明显是"每天"的量纲才接受
    if any(k in s for k in ("/24h", "24h", "每天", "/天", "·h/24")):
        return round(n, 3)
    # 纯 kWh/kW·h 无时间维度 -> 不猜，返回 None
    if "kwh" in s or "kw·h" in s or "度" in s:
        return None
    return None


# ---------------------------------------------------------------- 模型

@dataclass
class Appliance:
    """一台家电"""

    name: str
    price: float                              # 购机价
    energy: Optional[float] = None            # 官方耗电量 度/天
    category: str = ""
    purchase_date: str = ""
    # 官方标注耗电量的出处（用于溯源）
    energy_source: str = ""


# 预期寿命假设：家电的常见设计寿命（年）。
# 这是**假设**，不是采集事实；用户可覆盖。
DEFAULT_LIFESPAN_YEARS = 10.0


@dataclass
class CostBreakdown:
    """一台家电的日成本构成"""

    device: str
    energy_kwh_day: Optional[float]
    electricity_per_day: float
    depreciation_per_day: float
    total_per_day: float
    lifespan_years: float
    tariff_source: str
    assumptions: list[str] = field(default_factory=list)
    caveats: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "device": self.device,
            "energy_kwh_day": self.energy_kwh_day,
            "electricity_per_day": round(self.electricity_per_day, 3),
            "depreciation_per_day": round(self.depreciation_per_day, 3),
            "total_per_day": round(self.total_per_day, 3),
            "lifespan_years": self.lifespan_years,
            "tariff_source": self.tariff_source,
            "assumptions": self.assumptions,
            "caveats": self.caveats,
        }


def daily_cost(dev: Appliance, lifespan_years: float = DEFAULT_LIFESPAN_YEARS,
               tariff: Optional[Tariff] = None) -> CostBreakdown:
    """算一台家电每天花多少钱（电费 + 折旧）"""
    tariff = tariff or Tariff()
    assum = [f"预期寿命按 {lifespan_years:.0f} 年（假设，非采集值）",
             f"电价按 {tariff.blended} 元/度（{tariff.source}）"]
    caveats = []

    elec = 0.0
    if dev.energy is not None:
        elec = dev.energy * tariff.blended
    else:
        caveats.append("官方未标注耗电量，电费无法计算 —— "
                       "这里只体现折旧，实际日成本更高")

    days = lifespan_years * 365
    dep = dev.price / days if days > 0 else 0.0

    return CostBreakdown(
        device=dev.name,
        energy_kwh_day=dev.energy,
        electricity_per_day=elec,
        depreciation_per_day=dep,
        total_per_day=elec + dep,
        lifespan_years=lifespan_years,
        tariff_source=tariff.source,
        assumptions=assum,
        caveats=caveats + [
            "耗电量为官方标注值（实验室工况），实际随环境与使用习惯浮动",
            tariff.note,
        ],
    )


def compare_replace(old: Appliance, new: Appliance,
                    lifespan_years: float = DEFAULT_LIFESPAN_YEARS,
                    tariff: Optional[Tariff] = None,
                    old_age_years: float = 0.0,
                    horizon_years: float = 5.0) -> dict:
    """换新值不值：**同一时间窗**内比总支出。

    两组常犯的错误口径（都要避开）：

    ① 只比电费 —— 忽略新机本身的支出，等于白送。
    ② 拿"旧机剩余年限的折旧"比"新机完整寿命的折旧" ——
       旧机 2 年摊完 vs 新机 10 年摊完，分母不同，不可比。
       （旧机折旧率天然更高，会显得"换新更省"，是假的。）

    正确做法：固定一个**观察窗**（默认 5 年），算这个窗内
    两个方案各自要花多少现金：
      - 继续用：窗内电费（假设旧机还能撑满窗口）
      - 换新  ：新机价 + 窗内电费 − 旧机残值（有则计，无则标 0）
    再比窗内总支出。残值缺失时不臆造，只明确标注。
    """
    tariff = tariff or Tariff()
    cb_old = daily_cost(old, lifespan_years, tariff)
    cb_new = daily_cost(new, lifespan_years, tariff)
    days = max(horizon_years * 365, 1)

    def elec_of(cb: CostBreakdown) -> float:
        return cb.electricity_per_day * days

    old_elec = elec_of(cb_old)
    new_elec = elec_of(cb_new)

    old_total = old_elec                      # 继续用：窗内只有电费
    new_total = new.price + new_elec          # 换新：购机 + 窗内电费
    delta = round(old_total - new_total, 2)   # 正 = 继续用更省

    save_elec = round(cb_old.electricity_per_day - cb_new.electricity_per_day, 3)

    out = {
        "horizon_years": horizon_years,
        "old": {"name": old.name, "electricity": round(old_elec, 2),
                "total": round(old_total, 2),
                "per_day_elec": round(cb_old.electricity_per_day, 3),
                "age_years": old_age_years},
        "new": {"name": new.name, "price": new.price,
                "electricity": round(new_elec, 2),
                "total": round(new_total, 2),
                "per_day_elec": round(cb_new.electricity_per_day, 3)},
        "delta": delta,
        "electricity_saving_per_day": save_elec,
        "payback_days": None,
        "assumptions": [
            f"观察窗 {horizon_years:.0f} 年（两方案同窗比较）",
            f"电价 {tariff.blended} 元/度（{tariff.source}）",
            f"旧机已用 {old_age_years:.1f} 年",
            f"新机预期寿命 {lifespan_years:.0f} 年（假设）",
        ],
        "caveats": [
            "未计旧机回收残值（缺数据，不臆造）—— 有残值则换新更划算",
            "假设旧机能撑满观察窗；若中途报废，继续用的一侧会低估",
            "只算钱，不含能力差异（容量/保鲜/静音等）",
        ],
    }
    if save_elec > 0:
        # 单靠省电回本：新机价 ÷ 每天省下的电费
        out["payback_days"] = int(round(new.price / save_elec))
    return out


def render_cost(cb: CostBreakdown) -> str:
    L = [f"{cb.device}", ""]
    if cb.energy_kwh_day is not None:
        L.append(f"  电费    ¥{cb.electricity_per_day:6.2f}/天"
                 f"   （官方耗电 {cb.energy_kwh_day} 度/天）")
    else:
        L.append("  电费        无法计算（官方未标注耗电量）")
    L.append(f"  折旧    ¥{cb.depreciation_per_day:6.2f}/天"
             f"   （购机 ¥{cb.depreciation_per_day*cb.lifespan_years*365:.0f}"
             f" ÷ {cb.lifespan_years:.0f} 年）")
    L.append(f"  ─────────────────────")
    L.append(f"  合计    ¥{cb.total_per_day:6.2f}/天"
             f"   ≈ ¥{cb.total_per_day*30:.0f}/月"
             f" ≈ ¥{cb.total_per_day*365:.0f}/年")
    if cb.caveats:
        L.append("")
        for c in cb.caveats:
            L.append(f"  · {c}")
    return "\n".join(L)


def render_compare(res: dict) -> str:
    o, n = res["old"], res["new"]
    h = res["horizon_years"]
    L = [f"换新对比（同 {h:.0f} 年观察窗内总支出）", ""]
    L.append(f"  继续用  {o['name'][:26]}")
    L.append(f"     窗内电费 ¥{o['electricity']:.0f}"
             f"（¥{o['per_day_elec']:.2f}/天）")
    L.append(f"     合计    ¥{o['total']:.0f}")
    L.append(f"  换新    {n['name'][:26]}")
    L.append(f"     购机    ¥{n['price']:.0f}")
    L.append(f"     窗内电费 ¥{n['electricity']:.0f}"
             f"（¥{n['per_day_elec']:.2f}/天）")
    L.append(f"     合计    ¥{n['total']:.0f}")
    L.append("")
    d = res["delta"]
    # delta = 继续用总支出 − 换新总支出
    #   > 0  -> 换新更省（继续用的支出更高）
    #   < 0  -> 继续用更省（换新要多掏钱）
    if d > 0:
        L.append(f"  → {h:.0f} 年内，换新比继续用省 ¥{d:.0f}（未计旧机残值）")
    else:
        L.append(f"  → {h:.0f} 年内，继续用比换新省 ¥{abs(d):.0f}")
    sv = res["electricity_saving_per_day"]
    L.append(f"  电费差：{'省' if sv > 0 else '多花'} ¥{abs(sv):.2f}/天")
    if res.get("payback_days"):
        L.append(f"  单靠省电回本需 {res['payback_days']} 天"
                 f"（≈{res['payback_days']/365:.1f} 年）")
    else:
        L.append("  电费并无节省 —— 换新不会靠省电回本")
    L.append("")
    for c in res["caveats"]:
        L.append(f"  · {c}")
    return "\n".join(L)
