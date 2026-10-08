"""采集事实层：不丢证据的采集闭环。

核心原则（来自 Codex 评审）：
  **底层保留事实断言，Record 只是查询/导出的视图。**

三层结构：
  Capture     一次采集请求的完整证据（原响应 + 状态 + 时间）
  Assertion   「谁对哪个实体、哪个属性、在什么条件下声明了什么」
  View        按策略从断言选出的展示值（可重建，非事实）

关键点：
  - 适配器返回 **断言列表**，不是用属性名去重的字典
  - 同值多源时，两个来源都是独立佐证，都要保留
  - 采集失败不伪装成字段，走独立状态
  - 原响应保存，定位相对于原始响应，不相对解析后的临时 dict
  - 归一化不刷新采集时间
"""
from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Optional

CST = timezone(timedelta(hours=8))


def now_iso() -> str:
    return datetime.now(CST).isoformat(timespec="seconds")


class CaptureStatus(str, Enum):
    """采集任务状态"""

    SUCCESS = "success"                  # 完整成功
    PARTIAL = "partial"                  # 部分成功（如降级）
    TRANSPORT_ERROR = "transport_error"
    RATE_LIMITED = "rate_limited"      # 被限流（429）—— 与"源未提供"完全不同   # 网络/HTTP 失败
    SOURCE_ERROR = "source_error"         # 业务错误码
    PARSE_ERROR = "parse_error"           # 解析失败
    NOT_FOUND = "not_found"
    UNSUPPORTED = "unsupported"


class Availability(str, Enum):
    """数据可用性（与采集状态分开）"""

    PROVIDED = "provided"                    # 有值
    SOURCE_EMPTY = "source_empty"            # 源明确返回空（是有效结果）
    ABSENT = "absent"                        # 源里没有这个字段
    EXPLICITLY_UNKNOWN = "explicitly_unknown"  # 明确表示"未知/未公布"
    NOT_APPLICABLE = "not_applicable"        # 该品类无此属性
    NOT_COLLECTED = "not_collected"          # 采集失败，未取到


@dataclass
class Capture:
    """一次采集的完整证据"""

    capture_id: str
    source: str
    url: str
    method: str = "GET"
    request_headers: dict = field(default_factory=dict)   # 敏感头需脱敏
    request_body: Optional[str] = None
    status: CaptureStatus = CaptureStatus.SUCCESS
    http_status: Optional[int] = None
    error: str = ""
    response_raw: str = ""              # 原响应（保存证据）
    response_hash: str = ""             # 内容哈希，用于去重/变更检测
    parser_version: str = "v1"
    fetched_at: str = field(default_factory=now_iso)
    declared_at: str = ""               # 源声明的有效时间（如价格生效时间）

    def to_dict(self) -> dict:
        d = asdict(self)
        d["status"] = self.status.value if isinstance(self.status, CaptureStatus) else self.status
        return d

    @classmethod
    def make(cls, source: str, url: str, response_raw: str = "",
             status: CaptureStatus = CaptureStatus.SUCCESS, **kw) -> "Capture":
        cid = hashlib.sha1(f"{source}|{url}|{now_iso()}".encode()).hexdigest()[:12]
        h = hashlib.sha256(response_raw.encode()).hexdigest()[:16] if response_raw else ""
        return cls(capture_id=cid, source=source, url=url, response_raw=response_raw,
                   response_hash=h, status=status, **kw)


@dataclass
class Assertion:
    """一条事实断言：谁、对哪个属性、在什么条件下、声明了什么"""

    assertion_id: str
    subject_id: str                     # 实体（product/variant）
    capture_id: str                     # 来源采集
    source: str
    attribute: str                       # 原始属性名（未归一化）
    raw_value: Any                       # 原始值（字符串/数字/列表，未清洗）
    locator: str = ""                    # 相对于**原始响应**的定位
    ui_location: str = ""                # 用户在页面上的位置
    page: str = ""                       # 页面说明
    qualifiers: dict = field(default_factory=dict)   # 条件：{"anc": "off", "mode": "..."}
    canonical: str = ""                  # 归一化后的属性 ID（由 normalize 填）
    normalized_value: Any = None         # 归一化后的值（数量+单位）
    value_type: str = ""                 # text/quantity/enum/list/...
    availability: Availability = Availability.PROVIDED
    parser_version: str = "v1"
    normalization_rule_version: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["availability"] = self.availability.value if isinstance(self.availability, Availability) else self.availability
        return d


@dataclass
class Subject:
    """实体：产品 / 变体"""

    subject_id: str
    kind: str = "product"                # product | variant
    name: str = ""
    market: str = "CN"
    parent_id: str = ""                  # 变体指向产品
    external_ids: dict = field(default_factory=dict)   # {"mi_cn_mobile.gid": "..."}
    attributes: dict = field(default_factory=dict)     # 颜色、容量等

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Bundle:
    """一个商品的完整采集产物：证据 + 断言（未选值）"""

    subject: Subject
    captures: list[Capture] = field(default_factory=list)
    assertions: list[Assertion] = field(default_factory=list)
    discovery: dict = field(default_factory=dict)   # 发现信息（query/页数/total/是否完整）
    fetched_at: str = field(default_factory=now_iso)

    def add_capture(self, cap: Capture) -> None:
        self.captures.append(cap)

    def add_assertions(self, items: list[Assertion]) -> None:
        self.assertions.extend(items)

    def to_dict(self) -> dict:
        return {
            "subject": self.subject.to_dict(),
            "captures": [c.to_dict() for c in self.captures],
            "assertions": [a.to_dict() for a in self.assertions],
            "discovery": self.discovery,
            "fetched_at": self.fetched_at,
        }
