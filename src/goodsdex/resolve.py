"""解析层：断言 -> 视图。

与旧 normalize.py 的区别：
  - 输入是**断言列表**（保留全部来源），不是去重字典
  - 不做全局子串自动归并（那会制造语义错误）
  - 数量先解析单位；文本否定保留；不同条件不强合
  - 冲突保留全部候选 + 各自证据

映射按 `source + category + raw_attribute` 定义，不是全局名字匹配。
"""
from __future__ import annotations
import json
import re
from dataclasses import dataclass, field
from typing import Any, Optional

from .facts import Assertion, Availability

# ---------------- 属性定义（按品类） ----------------
# 只有在这里显式登记的属性才进入"可计算参数"；其余原样保留为 unclassified。


@dataclass(frozen=True)
class AttrDef:
    attr_id: str                 # 内部属性 ID
    label: str                   # 展示名
    value_type: str              # quantity | enum | text | bool
    unit: str = ""               # 期望单位
    qualifiers: tuple = ()       # 需要区分的条件维度


# 耳机的决策关键属性
EARPHONE_ATTRS = [
    AttrDef("anc.depth", "降噪深度", "quantity", "dB"),
    AttrDef("anc.call", "通话降噪", "text"),
    AttrDef("anc.wind", "抗风噪", "text"),
    AttrDef("battery.single", "单次续航", "quantity", "h", ("anc", "codec")),
    AttrDef("battery.total", "总续航", "quantity", "h", ("anc", "codec")),
    AttrDef("weight.single", "单耳重量", "quantity", "g"),
    AttrDef("weight.total", "整机重量", "quantity", "g"),
    AttrDef("water.ip", "防水等级", "enum"),
    AttrDef("bt.version", "蓝牙版本", "text"),
    AttrDef("bt.codecs", "音频编码", "text"),
    AttrDef("driver", "发声单元", "text"),
    AttrDef("charge.time", "充电时间", "quantity", "min"),
    AttrDef("release.date", "发布日期", "text"),
    AttrDef("weight.case", "充电盒重量", "quantity", "g"),
    AttrDef("charge.fast", "快充", "text"),
    AttrDef("form", "佩戴方式", "enum"),
]

# 吹风机 / 家电
DRYER_ATTRS = [
    AttrDef("power.rated", "额定功率", "quantity", "W"),
    AttrDef("wind.speed", "最大风速", "quantity", "m/s"),
    AttrDef("wind.volume", "最大风量", "quantity", "m³/min"),
    AttrDef("motor.rpm", "马达转速", "quantity", "rpm"),
    AttrDef("noise.max", "最大噪音", "quantity", "dB"),
    AttrDef("heat.levels", "温度挡位", "quantity", "挡"),
    AttrDef("speed.levels", "风速挡位", "quantity", "挡"),
    AttrDef("care.ion", "护发因子", "text"),
    AttrDef("release.date", "发布日期", "text"),
]

# 手机的决策关键属性（换机最常看的几项）
PHONE_ATTRS = [
    AttrDef("cpu", "处理器", "text"),
    AttrDef("cpu.clock", "CPU主频", "text"),
    AttrDef("screen.size", "屏幕尺寸", "quantity", "英寸"),
    AttrDef("screen.res", "屏幕分辨率", "text"),
    AttrDef("screen.type", "屏幕类型", "text"),
    AttrDef("cam.rear", "后置摄像头", "text"),
    AttrDef("cam.front", "前置摄像头", "text"),
    AttrDef("ram", "运行内存", "text"),
    AttrDef("rom", "存储容量", "text"),
    AttrDef("battery", "电池容量", "quantity", "mAh"),
    AttrDef("charge.wired", "有线快充", "quantity", "W"),
    AttrDef("charge.wireless", "无线快充", "quantity", "W"),
    AttrDef("thickness", "机身厚度", "quantity", "mm"),
    AttrDef("weight", "机身重量", "quantity", "g"),
    AttrDef("nfc", "NFC", "enum"),
    AttrDef("ir", "红外遥控", "enum"),
    AttrDef("fingerprint", "指纹识别", "text"),
    AttrDef("network", "网络类型", "text"),
    AttrDef("sim", "网络模式", "text"),
    AttrDef("port", "数据接口", "text"),
    AttrDef("release.date", "发布日期", "text"),
]

PHONE_MAP = {
    "CPU型号": "cpu", "处理器": "cpu", "CPU": "cpu",
    "CPU主频": "cpu.clock",
    "屏幕尺寸": "screen.size",
    "屏幕分辨率": "screen.res", "分辨率": "screen.res",
    "屏幕": "screen.type", "屏幕类型": "screen.type",
    "后置摄像头": "cam.rear", "后置相机": "cam.rear",
    "前置摄像头": "cam.front", "前置相机": "cam.front",
    "运行内存": "ram", "内存": "ram",
    "存储容量": "rom", "机身存储": "rom", "存储": "rom",
    "电池容量": "battery", "电池": "battery",
    "有线快充": "charge.wired", "有线充电": "charge.wired",
    "无线快充": "charge.wireless", "无线充电": "charge.wireless",
    "机身厚度": "thickness", "厚度": "thickness",
    "机身重量": "weight", "重量": "weight",
    "NFC": "nfc",
    "红外遥控": "ir",
    "指纹识别": "fingerprint",
    "网络类型": "network",
    "网络模式": "sim",
    "数据接口": "port", "接口": "port",
    "发布日期": "release.date", "上市时间": "release.date", "发布时间": "release.date",
}


# 原始字段名 -> 内部属性 ID（按品类；只做**精确**匹配，不做子串）
EARPHONE_MAP = {
    "降噪": "anc.depth", "降噪深度": "anc.depth", "主动降噪": "anc.depth",
    "通话降噪": "anc.call", "麦克风降噪": "anc.call",
    "抗风噪": "anc.wind", "风噪": "anc.wind",
    "耳机单次续航": "battery.single", "单次续航": "battery.single",
    "整体续航": "battery.total", "总续航": "battery.total", "续航时间": "battery.total",
    "单耳重量": "weight.single", "单耳机净重": "weight.single",
    "整机重量": "weight.total", "含充电盒总重": "weight.total",
    "产品净重（含充电盒）": "weight.total", "产品净重(含充电盒)": "weight.total",
    "充电盒重量": "weight.case",
    "防尘防水": "water.ip", "防水防尘": "water.ip", "防护等级": "water.ip",
    "蓝牙版本": "bt.version", "蓝牙": "bt.version", "蓝牙版连接": "bt.version",
    "音频协议": "bt.codecs", "蓝牙编解码": "bt.codecs", "音频编码": "bt.codecs",
    "蓝牙功能": "bt.codecs",
    "发音单元": "driver", "驱动单元": "driver", "发声单元": "driver",
    "充电时间": "charge.time", "快充": "charge.fast",
    "发布日期": "release.date", "上市时间": "release.date", "发布时间": "release.date",
    "佩戴方式": "form", "产品形态": "form",
}

DRYER_MAP = {
    "额定功率": "power.rated",
    "最大风速": "wind.speed", "风速": "wind.speed",
    "最大风量": "wind.volume", "风量": "wind.volume",
    "马达转速": "motor.rpm", "转速": "motor.rpm", "电机转速": "motor.rpm",
    "最大噪音": "noise.max", "噪音": "noise.max",
    "温度挡位": "heat.levels", "风温挡位": "heat.levels",
    "风速挡位": "speed.levels",
    "护发因子": "care.ion", "负离子": "care.ion",
    "发布日期": "release.date", "上市时间": "release.date",
}

CATEGORY_RULES = {
    "earphone": {"attrs": EARPHONE_ATTRS, "map": EARPHONE_MAP},
    "dryer": {"attrs": DRYER_ATTRS, "map": DRYER_MAP},
    "phone": {"attrs": PHONE_ATTRS, "map": PHONE_MAP},
}


def guess_category(text: str) -> str:
    t = text or ""
    if re.search(r"耳机|buds|earphone|headphone", t, re.I):
        return "earphone"
    if re.search(r"吹风机|电吹风|dryer", t, re.I):
        return "dryer"
    # 手机：官方机型名（Xiaomi 数字系列 / REDMI K / Note / Turbo / MIX / Civi）
    if re.search(r"Xiaomi\s*\d|小米\s*\d|REDMI\s*(K|Note|Turbo|\d)|Redmi\s*(K|Note|Turbo|\d)"
                 r"|MIX\s*(Fold|Flip|\d)|Civi\s*\d|红米\s*(K|Note)", t, re.I):
        return "phone"
    return ""


# ---------------- 值解析 ----------------

# 单位换算（同量纲）
UNIT_ALIASES = {
    "h": "h", "小时": "h", "hour": "h",
    "min": "min", "分钟": "min",
    "g": "g", "克": "g",
    "kg": "kg", "千克": "kg", "公斤": "kg",
    "mg": "mg", "毫克": "mg",
    "db": "dB", "分贝": "dB",
    "w": "W", "瓦": "W",
    "kw": "kW",
    "m/s": "m/s", "米/秒": "m/s",
    "rpm": "rpm", "r/min": "rpm",
    "mah": "mAh", "毫安时": "mAh",
    "m³/min": "m³/min", "立方米/分钟": "m³/min",
    "mm": "mm", "毫米": "mm",
    "cm": "cm", "厘米": "cm",
}

# 单位必须按长度降序尝试，否则 "kg" 会被 "g" 抢先匹配
_UNIT_RE = "|".join(sorted((re.escape(u) for u in UNIT_ALIASES), key=len, reverse=True))


@dataclass
class Quantity:
    value: Optional[float] = None
    unit: str = ""
    raw: str = ""
    range_max: Optional[float] = None      # 如 "10小时" vs "42小时" 中的长续航
    negative: bool = False                 # 否定（如"无主动降噪"）
    qualifiers: dict = field(default_factory=dict)   # {"anc": "off"}
    unresolved: str = ""                   # 无法解析时说明原因


NEGATION = re.compile(r"^\s*(无|没有|不支持|不含|非)\s*")


def parse_quantity(raw: Any, expect_unit: str = "") -> Quantity:
    """解析数量：单位、范围、否定。不做"第一数字相同就判等"这种猜测。"""
    s = str(raw or "").strip()
    q = Quantity(raw=s)
    if not s:
        q.unresolved = "empty"
        return q
    if NEGATION.match(s):
        q.negative = True
        rest = NEGATION.sub("", s, count=1)
        if not rest.strip():
            return q
        s = rest
    # 条件限定：降噪关/开
    if re.search(r"降噪\s*关", s):
        q.qualifiers["anc"] = "off"
    elif re.search(r"降噪\s*开", s):
        q.qualifiers["anc"] = "on"
    # 取数值 + 单位（单位按长度降序，避免 "kg" 被 "g" 抢先匹配）
    m = re.search(rf"(\d+(?:\.\d+)?)\s*({_UNIT_RE})?", s, re.I)
    if not m:
        q.unresolved = "no_number"
        return q
    q.value = float(m.group(1))
    if m.group(2):
        u = m.group(2)
        q.unit = UNIT_ALIASES.get(u.lower(), UNIT_ALIASES.get(u, u))
    elif expect_unit:
        # 文本里没写单位时，用属性定义的期望单位；但这属于**推断**，标记出来
        q.unit = expect_unit
        q.qualifiers["unit_inferred"] = True
    # 范围："4.5h（耳机单次使用）" vs "23h（耳机+充电盒）" —— 取第二个大数作为 max
    nums = re.findall(rf"(\d+(?:\.\d+)?)\s*({_UNIT_RE})?", s, re.I)
    if len(nums) > 1:
        try:
            q.range_max = max(float(n[0]) for n in nums if n[0])
        except ValueError:
            pass
    return q


def values_conflict(a: Assertion, b: Assertion, attr_def: Optional[AttrDef]) -> str:
    """判定两条断言的关系。

    返回：same | compatible | conflict | incomparable
      - same        值等价
      - compatible  可能兼容（如 约5.3g 与 5.3±0.1g），但**不证明事实相等**
      - conflict    互斥
      - incomparable 条件不同或类型不同，不可比
    """
    if attr_def and attr_def.value_type == "quantity":
        qa = parse_quantity(a.raw_value, attr_def.unit)
        qb = parse_quantity(b.raw_value, attr_def.unit)
        # 条件不同 -> 不可比（如降噪开 vs 降噪关）
        # 注：unit_inferred 是解析时的标注，不参与条件比较
        ca = {k: v for k, v in qa.qualifiers.items() if k != "unit_inferred"}
        cb = {k: v for k, v in qb.qualifiers.items() if k != "unit_inferred"}
        if ca != cb:
            return "incomparable"
        # 否定不一致 -> 冲突（一个说不支持，一个说支持）
        if qa.negative != qb.negative:
            return "conflict"
        if qa.negative and qb.negative:
            return "same"
        # 单位不同 -> 不可比（如 g vs kg，实际相差千倍，绝不能判等）
        if qa.unit and qb.unit and qa.unit != qb.unit:
            return "incomparable"
        if qa.value is None or qb.value is None:
            return "incomparable"
        if abs(qa.value - qb.value) < 1e-9:
            return "compatible"      # 数值相同但精度/表述可能不同，不宣称"事实相等"
        return "conflict"
    # 文本
    sa, sb = str(a.raw_value).strip(), str(b.raw_value).strip()
    if sa == sb:
        return "same"
    na, nb = bool(NEGATION.match(sa)), bool(NEGATION.match(sb))
    if na != nb:
        return "conflict"            # 一个否定一个肯定，不能算"表述差异"
    if (sa in sb) or (sb in sa):
        return "compatible"
    return "conflict"


# ---------------- 视图 ----------------

@dataclass
class View:
    """解析视图：按策略从断言选出展示值。可重建，非事实本身。"""

    subject_id: str
    values: dict = field(default_factory=dict)         # attr_id -> 选定值
    selected_from: dict = field(default_factory=dict)  # attr_id -> assertion_id
    candidates: dict = field(default_factory=dict)     # attr_id -> [assertion_id]
    relations: list = field(default_factory=list)      # 断言间关系
    unclassified: dict = field(default_factory=dict)   # 未登记属性，原样保留
    availability: dict = field(default_factory=dict)   # attr_id -> Availability
    gaps: list = field(default_factory=list)           # 缺失及其原因

    def to_dict(self) -> dict:
        return {
            "subject_id": self.subject_id, "values": self.values,
            "selected_from": self.selected_from, "candidates": self.candidates,
            "relations": self.relations, "unclassified": self.unclassified,
            "availability": {k: (v.value if isinstance(v, Availability) else v)
                             for k, v in self.availability.items()},
            "gaps": self.gaps,
        }


# 未登记但属于结构性的字段，直接透传到视图
STRUCTURAL_KEEP = {
    "name", "short_title", "sell_points", "price", "market_price", "pc_price",
    "pc_market_price", "desc", "colors", "attrs", "carousel", "img_url", "buyer_imgs",
    "review_tags", "qa_items", "qa_total", "evaluate_total", "evaluate_real",
    "buy_options", "pc_tabs", "pc_imgs", "gid", "sku", "commodity_id", "goods_id",
}


def build_view(assertions: list[Assertion], category: str = "",
               subject_id: str = "") -> View:
    """从断言列表构建视图"""
    # category 可能是中文分类名（如"吹风机"）或内部标识（如"dryer"），统一解析
    cat = category if category in CATEGORY_RULES else guess_category(category)
    if not cat:
        cat = guess_category(" ".join(str(a.raw_value) for a in assertions[:40]))
    rules = CATEGORY_RULES.get(cat, {})
    amap: dict = rules.get("map", {})
    adefs = {d.attr_id: d for d in rules.get("attrs", [])}
    v = View(subject_id=subject_id or (assertions[0].subject_id if assertions else ""))

    by_attr: dict[str, list[Assertion]] = {}
    for a in assertions:
        # 品类映射：只做精确匹配，不做子串
        attr_id = amap.get(a.attribute)
        if attr_id:
            a.canonical = attr_id
            by_attr.setdefault(attr_id, []).append(a)
        elif a.attribute in STRUCTURAL_KEEP or a.attribute.startswith("_"):
            v.values[a.attribute] = a.raw_value
            v.availability[a.attribute] = a.availability
        else:
            # 未登记属性：原样保留，不自动进入可计算参数
            v.unclassified.setdefault(a.attribute, []).append(a.raw_value)

    for attr_id, items in by_attr.items():
        adef = adefs.get(attr_id)
        v.candidates[attr_id] = [a.assertion_id for a in items]
        # 选值：官方优先，其次按值完整性；**全部候选都保留**
        picked = items[0]
        v.values[attr_id] = picked.raw_value
        v.selected_from[attr_id] = picked.assertion_id
        v.availability[attr_id] = picked.availability
        # 关系判定
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                rel = values_conflict(items[i], items[j], adef)
                if rel != "same":
                    v.relations.append({
                        "attr": attr_id, "relation": rel,
                        "a": {"id": items[i].assertion_id, "source": items[i].source,
                              "value": items[i].raw_value, "locator": items[i].locator},
                        "b": {"id": items[j].assertion_id, "source": items[j].source,
                              "value": items[j].raw_value, "locator": items[j].locator},
                    })

    # 缺口：登记了但没值的属性，说明原因
    for attr_id, adef in adefs.items():
        if attr_id not in by_attr:
            empty = [a for a in assertions if a.attribute == "_params_empty"]
            reason = "source_empty" if empty else "absent"
            v.gaps.append({"attr": attr_id, "label": adef.label, "reason": reason})
            v.availability[attr_id] = (Availability.SOURCE_EMPTY if empty
                                       else Availability.ABSENT)
    return v
