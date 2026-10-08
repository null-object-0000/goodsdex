"""数据模型：字段级溯源。

设计要点：
- 每个字段独立携带来源，不做"整条记录一个来源"
- 冲突不覆盖，全部保留
- 值可为标量/列表/字典，来源信息始终可追
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Optional
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))


def now_iso() -> str:
    return datetime.now(CST).isoformat(timespec="seconds")


@dataclass
class Provenance:
    """一个字段的来源"""

    source: str                      # 源标识，如 "mi_cn_mobile"
    site: str = ""                   # 站点，如 "m.mi.com"
    page: str = ""                   # 页面说明，如 "移动端商品详情页价格区"
    ui_location: str = ""            # 用户在页面上看到的位置，如 "现价"
    api: str = ""                    # 接口，如 "POST /mtop/xiaomishop/product/info"
    json_path: str = ""              # JSON 路径
    url: str = ""                    # 人类可访问的页面地址
    raw_field: str = ""              # 原始字段名（归一化前）
    fetched_at: str = field(default_factory=now_iso)

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v not in (None, "")}


@dataclass
class Conflict:
    """跨源冲突，全部变体保留"""

    field: str
    kind: str                        # "表述差异" | "数据矛盾"
    variants: list[dict] = field(default_factory=list)
    picked: Any = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Record:
    """一个商品"""

    key: str                         # 商品唯一键（product_id）
    name: str = ""
    category: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    provenance: dict[str, Provenance] = field(default_factory=dict)
    conflicts: list[Conflict] = field(default_factory=list)
    dropped: list[str] = field(default_factory=list)   # 被剔除的空值/垃圾字段
    sources_used: list[str] = field(default_factory=list)
    source_urls: dict[str, str] = field(default_factory=dict)
    fetched_at: str = field(default_factory=now_iso)

    def set(self, key: str, value: Any, prov: Provenance) -> None:
        self.data[key] = value
        self.provenance[key] = prov

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "name": self.name,
            "category": self.category,
            "data": self.data,
            "provenance": {k: v.to_dict() for k, v in self.provenance.items()},
            "conflicts": [c.to_dict() for c in self.conflicts],
            "dropped": self.dropped,
            "sources_used": self.sources_used,
            "source_urls": self.source_urls,
            "fetched_at": self.fetched_at,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Record":
        r = cls(key=d.get("key", ""), name=d.get("name", ""), category=d.get("category", ""),
                data=d.get("data", {}), dropped=d.get("dropped", []),
                sources_used=d.get("sources_used", []),
                source_urls=d.get("source_urls", {}),
                fetched_at=d.get("fetched_at", now_iso()))
        r.provenance = {k: Provenance(**v) for k, v in (d.get("provenance") or {}).items()}
        r.conflicts = [Conflict(**c) for c in (d.get("conflicts") or [])]
        return r


# ---------------- 源注册表（含信源等级） ----------------

SOURCE_LEVELS = {
    "mi_cn_mobile": 1,   # 官方
    "mi_cn_pc": 1,       # 官方
    "baike": 3,          # 第三方
    "zol": 3,            # 第三方
    "audio52": 3,        # 第三方
}

SOURCE_META = {
    "mi_cn_mobile": {"site": "m.mi.com", "page": "移动端商品详情页"},
    "mi_cn_pc": {"site": "www.mi.com", "page": "PC 商品详情页"},
    "baike": {"site": "baike.baidu.com", "page": "百度百科词条"},
    "zol": {"site": "detail.zol.com.cn", "page": "ZOL 参数页"},
    "audio52": {"site": "www.52audio.com", "page": "我爱音频网拆解"},
}

# 字段 -> 源优先级（前面的优先）
FIELD_PRIORITY: dict[str, list[str]] = {
    "发布日期": ["baike", "zol", "mi_cn_mobile"],   # 百科精确到日
    "上市日期": ["zol", "baike", "mi_cn_mobile"],
    "型号": ["mi_cn_mobile", "zol"],
}
DEFAULT_PRIORITY = ["mi_cn_mobile", "mi_cn_pc", "baike", "zol", "audio52"]
