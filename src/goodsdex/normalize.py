"""字段归一化：跨源同义字段合并 + 冲突判定。

两条规则来自实战：
1. 嵌套参数（如 params 字典）要展开到顶层，否则无法跨源比对
2. 相似字段名不等于同一字段 —— 「降噪」「通话降噪」「抗风噪」是三个东西，
   错误合并比漏合并更危险（会掩盖真实差异）
"""
from __future__ import annotations
import json
import re

# canonical -> 各源写法（归一化后比较：去空格/大小写）
ALIAS: dict[str, list[str]] = {
    "name": ["name", "pc_name", "名称", "商品名", "产品名称"],
    "型号": ["model", "型號", "型号", "产品型号", "货号"],
    "价格": ["price", "pc_price", "现价", "售价"],
    "划线价": ["market_price", "pc_market_price", "原价", "划线价", "建议零售价"],
    "发布日期": ["发布日期", "上市时间", "上市日期", "release_date", "release date",
                 "发布时间", "国内发布时间"],
    "形态": ["form", "佩戴方式", "产品形态", "产品类型", "产品定位"],
    "颜色": ["color", "顏色", "颜色", "产品颜色", "机身颜色", "可选颜色"],
    "简介": ["desc", "product_desc", "商品简介", "特色简介"],

    # 耳机
    "单耳重量": ["weight of a single earbud", "每邊耳機的重量", "单耳重量", "单耳机净重"],
    "充电盒重量": ["weight of charging case", "充電盒重量", "充电盒重量"],
    "整机重量": ["total weight", "總重量", "整机重量", "含充电盒总重", "产品净重（含充电盒）"],
    "电池容量": ["battery capacity", "電池容量", "电池容量", "蓝牙版电池容量", "耳机电池容量"],
    "充电接口": ["charging port", "充電連接埠", "充电接口", "充电连接口"],
    "蓝牙版本": ["wireless connection", "無線連接", "蓝牙版本", "蓝牙", "蓝牙版连接"],
    "蓝牙协议": ["bluetooth protocols", "藍牙協議", "蓝牙编解码", "音频协议", "蓝牙功能"],
    "通讯距离": ["communication range", "通訊範圍", "工作距离", "通讯距离", "传输范围"],
    "降噪": ["降噪", "anc", "降噪功能", "主动降噪"],
    "通话降噪": ["通话降噪", "麦克风降噪"],
    "抗风噪": ["抗风噪", "风噪"],
    "续航_单次": ["耳机单次续航", "单次续航", "降噪关短续航", "降噪开短续航"],
    "续航_总": ["整体续航", "總續航", "续航时间", "降噪关长续航", "降噪开长续航"],
    "防水": ["防尘防水", "ip rating", "防水防尘", "防护等级"],
    "频响范围": ["频响范围", "频率响应范围", "frequency response"],
    "发声单元": ["发音单元", "驱动单元", "扬声器单元", "喇叭单元"],

    # 吹风机 / 家电
    "额定功率": ["额定功率", "power", "功率"],
    "最大风速": ["最大风速", "max wind speed", "风速"],
    "最大风量": ["最大风量", "max airflow", "风量"],
    "马达转速": ["马达转速", "motor speed", "转速", "电机转速"],
    "最大噪音": ["最大噪音", "噪音", "noise", "噪声"],
    "温度挡位": ["温度挡位", "风温挡位", "heat levels", "热风挡位"],
    "风速挡位": ["风速挡位", "speed levels", "风量挡位"],
    "护发因子": ["护发因子", "负离子", "纳米水离子"],
    "机身尺寸": ["产品尺寸", "机身尺寸", "size"],
    "净重": ["产品净重", "净重", "重量", "weight"],
}

# 结构性子对象（不做别名映射，原样保留）
STRUCTURAL = {
    "pc_", "buy_options", "carousel", "buyer_imgs", "qa_", "evaluate_", "img_url",
    "gid", "sku", "commodity_id", "goods_id", "sell_points", "review_tags", "attrs",
    "detail_imgs", "desc_imgs", "short_title",
}

JUNK = {"", "无", "—", "-", "/", "n/a", "na", "null", "none", "见详情", "详见产品页",
        "暂未公布", "暂无", "以实际为准"}


def _norm(s: str) -> str:
    return re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "", (s or "").lower())


def is_junk(v) -> bool:
    if v is None:
        return True
    if isinstance(v, str):
        s = v.strip()
        if s in JUNK or not s:
            return True
        if re.fullmatch(r"[\s\-—/、,，。.·]+", s):
            return True
    if isinstance(v, (list, dict)) and not v:
        return True
    return False


def canon(field: str) -> str:
    f = _norm(field)
    if not f:
        return field
    for k in ALIAS:
        if _norm(k) == f:
            return k
    for k, aliases in ALIAS.items():
        for a in aliases:
            if _norm(a) == f:
                return k
    for k, aliases in ALIAS.items():
        for a in aliases:
            na = _norm(a)
            if len(na) >= 4 and na in f:
                return k
    return field


def _first_num(v):
    m = re.search(r"\d+(?:\.\d+)?", str(v))
    return m.group(0) if m else None


def _nums(v):
    return re.findall(r"\d+(?:\.\d+)?", str(v))


def classify_conflict(variants: list[dict]) -> str:
    """表述差异 vs 数据矛盾"""
    vals = [str(v["value"]) for v in variants]
    ne = [s for s in (_nums(t) for t in vals) if s]
    if ne and all(ne[0] == s for s in ne):
        return "表述差异"
    firsts = [_first_num(t) for t in vals]
    if all(firsts) and len(set(firsts)) == 1:
        return "表述差异"
    if any((a in b or b in a) for a in vals for b in vals if a != b):
        return "表述差异"
    return "数据矛盾"


def flatten(data: dict, prov: dict, holders=("params", "参数")) -> tuple[dict, dict]:
    """嵌套参数字典展开到顶层，保留来源"""
    flat, fprov = dict(data), dict(prov)
    for h in holders:
        sub = data.get(h)
        if isinstance(sub, dict):
            src = getattr(prov.get(h), "source", None) or (prov.get(h) or {}).get("source")
            for k, v in sub.items():
                if k not in flat:
                    flat[k] = v
                    p = prov.get(h)
                    if p is not None:
                        if hasattr(p, "to_dict"):
                            np = type(p)(source=p.source, site=p.site, page=p.page,
                                         ui_location=p.ui_location, api=p.api,
                                         json_path=f"{p.json_path}.{k}", url=p.url,
                                         raw_field=f"{h}.{k}")
                        else:
                            np = {**p, "raw_field": f"{h}.{k}"}
                        fprov[k] = np
            flat.pop(h, None)
            fprov.pop(h, None)
    return flat, fprov


def normalize_record(rec) -> dict:
    """把各源字段归一到 canonical，检测冲突。返回 {data, provenance, conflicts, dropped}"""
    data, prov = rec.get("data") or {}, rec.get("provenance") or {}
    data, prov = flatten(data, prov)

    norm, nprov, conflicts, dropped = {}, {}, [], []
    groups: dict[str, list] = {}

    for f, v in data.items():
        if is_junk(v):
            dropped.append(f)
            continue
        if any(str(f).startswith(p) or str(f) == p for p in STRUCTURAL):
            norm[f] = v
            nprov[f] = prov.get(f)
            continue
        groups.setdefault(canon(f), []).append((f, v, prov.get(f)))

    for c, items in groups.items():
        norm[c] = items[0][1]
        nprov[c] = items[0][2]
        if len({json.dumps(v, ensure_ascii=False, default=str) for _, v, _ in items}) > 1:
            variants = [{"raw_field": f, "value": v,
                         "source": getattr(p, "source", None) or (p or {}).get("source")}
                        for f, v, p in items]
            conflicts.append({"field": c, "kind": classify_conflict(variants),
                              "variants": variants, "picked": items[0][1]})

    return {"data": norm, "provenance": nprov, "conflicts": conflicts, "dropped": dropped}
