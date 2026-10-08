"""视觉参数提取的共享逻辑（被 scripts 与包内共用）。"""
from __future__ import annotations
import json

# 元数据字段：不算"产品参数"
META_FIELDS = {
    "name", "short_title", "sell_points", "gid", "commodity_id", "sku",
    "price", "market_price", "img_url", "carousel", "attrs", "colors",
    "evaluate_total", "evaluate_real", "review_tags", "buyer_imgs",
    "qa_total", "qa_items", "desc", "buy_options", "pc_price",
    "pc_market_price", "pc_tabs", "pc_imgs", "_params_empty", "product_id",
    "kind", "category_match", "excluded_reason",
}


def count_real_params(rec: dict) -> int:
    """统计真实参数数（排除元数据与内部字段）。

    这是判断"是否需要视觉提取"的正确依据 ——
    用视图值总数会把元数据算进去，实测导致 12 台冰箱被误跳过。
    """
    vals = (rec.get("view") or {}).get("values") or {}
    return sum(1 for k in vals if k not in META_FIELDS and not k.startswith("_"))


def tab_signature(rec: dict) -> list[str]:
    """该商品的 tab 名列表（用于判断参数是否分型号存放）"""
    out = []
    for c in rec.get("captures") or []:
        if c.get("source") != "mi_cn_pc":
            continue
        try:
            j = json.loads(c.get("response_raw") or "")
        except Exception:
            continue
        tabs = ((j.get("data") or {}).get("extend_info") or {}).get("desc_tabs_view") or []
        out += [t.get("name") or "" for t in tabs]
    return out
