"""商品身份模型：产品 / 地区版本 / 销售变体。

来自实际数据的层次关系（小米商城）：

    product_id = 25526
      ├─ commodity_id 1230809265  Xiaomi 18 Pro Max 12GB+256GB   ¥6999
      ├─ commodity_id 1230809266  Xiaomi 18 Pro Max 12GB+512GB   ¥7999
      ├─ commodity_id 1230809267  Xiaomi 18 Pro Max 16GB+512GB   ¥8999
      ├─ commodity_id 1230809268  Xiaomi 18 Pro Max 16GB+1TB     ¥9999
      └─ commodity_id 1230809269  Xiaomi 18 Pro Max 16GB+1TB 特别版 ¥10999

    另一个例子（同价颜色变体）：
    product_id = 22137
      ├─ 1230805246  REDMI Buds 8 Pro 冰釉白  ¥369
      ├─ 1230805247  REDMI Buds 8 Pro 玄悟黑  ¥369
      └─ 1230805248  REDMI Buds 8 Pro 薄雾蓝  ¥369

层次：
  Product       产品（跨地区、跨销售变体的稳定实体）
  MarketVersion 地区版本（国行 / 港版 / 全球版……型号体系不同，不可混比）
  Variant       销售变体（容量/颜色/套装，价格和规格可能不同）

原则：
  - 参数属于 Product 或 Variant，取决于该参数是否随变体变化
    （如"最大风速"属于产品，"机身颜色"属于变体）
  - 价格必须挂在 Variant 上，且带时间戳（价格是时间序列，不是永久属性）
  - 跨源匹配必须先确认是同一个 Variant，否则比较无意义
"""
from __future__ import annotations
import hashlib
import re
from dataclasses import dataclass, field, asdict
from typing import Optional

# 变体属性识别（从商品名解析）
CAPACITY_RE = re.compile(r"(\d+)\s*(GB|TB)\s*\+\s*(\d+)\s*(GB|TB)", re.I)
COLOR_WORDS = ("黑", "白", "蓝", "绿", "紫", "灰", "金", "粉", "青", "红", "银", "钛",
               "冰釉", "玄悟", "薄雾", "雪山", "幻影", "山岚", "迷雾", "岩石", "贝母",
               "暮", "脂", "萃", "曜石", "云棉", "海浪", "迷雾", "朋克", "月光")
EDITION_WORDS = ("青春版", "活力版", "特别版", "典藏版", "限定版", "礼盒", "套装",
                 "至尊版", "纪念版", "探索版", "典藏套装", "电竞版", "Pro版")


def parse_variant_attrs(name: str) -> dict:
    """从商品名解析变体属性（容量/颜色/版本）"""
    attrs = {}
    m = CAPACITY_RE.search(name or "")
    if m:
        attrs["ram"] = f"{m.group(1)}{m.group(2).upper()}"
        attrs["rom"] = f"{m.group(3)}{m.group(4).upper()}"
    else:
        m2 = re.search(r"\b(\d+)\s*(GB|TB)\b", name or "", re.I)
        if m2:
            attrs["storage"] = f"{m2.group(1)}{m2.group(2).upper()}"
    for w in EDITION_WORDS:
        if w in (name or ""):
            attrs["edition"] = w

    # 颜色：剥掉容量/版本后，取**最后一个空格分隔的中文片段**（颜色通常在名称末尾）
    base = CAPACITY_RE.sub("", name or "")
    base = re.sub(r"\b\d+\s*(GB|TB)\b", "", base, flags=re.I)
    for w in EDITION_WORDS:
        base = base.replace(w, "")
    tokens = [t for t in re.split(r"\s+", base.strip()) if t]
    color = ""
    for t in reversed(tokens):
        # 纯中文、2-6 字，且不是产品名的一部分
        if re.fullmatch(r"[\u4e00-\u9fff]{2,6}", t):
            color = t
            break
    # 回退：整串里出现的最长颜色词
    if not color:
        best = ""
        for c in COLOR_WORDS:
            if c in base and len(c) > len(best):
                best = c
        color = best
    if color:
        attrs["color"] = color
    return attrs


def _is_color_token(tok: str) -> bool:
    """判断一个 token 是否是颜色（纯中文 2-6 字，且含颜色字）。

    必须排除**版本词** —— "青春版"含"青"字，会被误判成颜色而剥掉，
    导致「REDMI Buds 6 青春版」和「REDMI Buds 6」同名（实测踩过）。
    """
    if not re.fullmatch(r"[\u4e00-\u9fff]{2,6}", tok or ""):
        return False
    if any(w in tok for w in EDITION_WORDS):
        return False
    return any(c in tok for c in COLOR_WORDS)


def product_name(name: str) -> str:
    """去掉变体后缀（颜色/容量），得到产品名。

    注意：**版本词（青春版/活力版/Pro）必须保留** ——
    「REDMI Buds 6 青春版」和「REDMI Buds 6」是两个不同产品，
    去掉版本词会让两者同名，对比时混为一谈（实测踩过）。
    只剥离颜色与容量这类**销售变体**。
    """
    s = name or ""
    s = CAPACITY_RE.sub("", s)
    s = re.sub(r"\b\d+\s*(GB|TB)\b", "", s, flags=re.I)
    toks = s.split()
    while toks and _is_color_token(toks[-1]):
        toks.pop()
    return " ".join(toks).strip()


@dataclass
class Variant:
    """销售变体（可购买的最小单位）"""

    variant_id: str
    product_id: str
    name: str = ""
    attrs: dict = field(default_factory=dict)        # {ram, rom, color, edition}
    external_ids: dict = field(default_factory=dict)  # {"mi_cn.commodity_id": ...}

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Product:
    """产品实体（跨变体的稳定身份）"""

    product_id: str
    name: str = ""
    market: str = "CN"
    brand: str = ""
    category: str = ""
    variants: list[Variant] = field(default_factory=list)
    external_ids: dict = field(default_factory=dict)  # {"mi_cn.product_id": ...}
    identity_evidence: dict = field(default_factory=dict)  # 身份判定依据（供复核）
    identity_confidence: str = "unverified"  # verified | inferred | unverified

    def add_variant(self, v: Variant) -> None:
        if not any(x.variant_id == v.variant_id for x in self.variants):
            self.variants.append(v)

    def to_dict(self) -> dict:
        return {**{k: v for k, v in asdict(self).items() if k != "variants"},
                "variants": [v.to_dict() for v in self.variants]}


def make_product_id(market: str, source: str, source_product_id: str) -> str:
    """内部产品 ID（带地区命名空间）。

    地区必须显式写入 —— 不同地区的型号体系不同，混比会出错。
    """
    return f"{market}:{source}:product:{source_product_id}"


def make_variant_id(market: str, source: str, commodity_id: str) -> str:
    return f"{market}:{source}:commodity:{commodity_id}"


def build_identity(source_product_id: str, variants_raw: list[dict],
                   market: str = "CN", source: str = "mi_cn",
                   brand: str = "", category: str = "") -> Product:
    """从搜索结果的变体列表构建产品身份。

    variants_raw: [{commodity_id, name, price, market_price}, ...]
    """
    p = Product(
        product_id=make_product_id(market, source, source_product_id),
        market=market, brand=brand, category=category,
        external_ids={f"{source}.product_id": source_product_id},
    )
    names = []
    for v in variants_raw:
        cid = v.get("commodity_id")
        if not cid:
            continue
        nm = v.get("name") or ""
        names.append(nm)
        attrs = parse_variant_attrs(nm)
        p.add_variant(Variant(
            variant_id=make_variant_id(market, source, str(cid)),
            product_id=p.product_id, name=nm, attrs=attrs,
            external_ids={f"{source}.commodity_id": str(cid),
                          **({f"{source}.sku": str(v["sku"])} if v.get("sku") else {})},
        ))
    # 产品名：取所有变体名的公共前缀（去掉变体后缀后最长的一个）
    cleaned = [product_name(n) for n in names if n]
    if cleaned:
        p.name = max(cleaned, key=len) if len(set(cleaned)) == 1 else _common_prefix(cleaned)
    # 身份判定依据
    p.identity_evidence = {
        "variant_count": len(p.variants),
        "variant_names": names[:6],
        "basis": "同一 product_id 下的 commodity 列表",
        "scope": f"{market} 市场，{source} 源",
    }
    p.identity_confidence = "verified" if len(p.variants) >= 1 else "unverified"
    return p


def _common_prefix(names: list[str]) -> str:
    if not names:
        return ""
    s = names[0]
    for n in names[1:]:
        while s and not n.startswith(s):
            s = s[:-1]
    return s.strip()


def same_product(a: Product, b: Product) -> Optional[bool]:
    """判定两个产品是否同一实体。

    名称完全一致**只能作为候选筛选，不是同一性证明** ——
    同名可能不同地区、年份或套装。
    """
    # 地区不同 -> 明确不同
    if a.market != b.market:
        return False
    # 外部 ID 命中 -> 确定同一
    for k, v in a.external_ids.items():
        if b.external_ids.get(k) == v:
            return True
    # 型号一致（若都有）-> 同一
    ma, mb = a.external_ids.get("model"), b.external_ids.get("model")
    if ma and mb:
        return ma == mb
    return None       # 无法判定，需人工核查
