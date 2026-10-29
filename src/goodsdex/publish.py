"""发布集导出：把内部采集数据转成**可公开**的派生视图。

为什么要分层（内部数据 vs 发布集）：
  - 内部数据 343 MB，含 captures/assertions（原响应快照 + 逐字段证据），
    是溯源审计用的；直接入 git 会撑爆仓库。
  - 发布集约 2 MB，含身份/价格/主图链接/参数 —— 这才是对外的数据集。
  - **但两者不是简单裁剪**：发布集必须能指回证据（保留 record 的
    id 与抓取时间），否则公开数据就成了不可核对的孤证。

产出：
  public/goods.json      全量发布集（2 MB）
  public/meta.json       统计与生成时间
  public/prices/*.jsonl  价格时间序列（按月，追加不覆盖）
"""
from __future__ import annotations

import glob
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from goodsdex.supplements import DEFAULT_SUPPLEMENTS, publish
from goodsdex.public_fields import normalize_public_row

CST = timezone(timedelta(hours=8))

# view.values 里**不属于商品属性**的键。
# 分三类：
#   ① 未公开的展示素材（不导出整组图片与详情）
#   ② 提升到顶层或由顶层身份/价格字段替代的原始字段（避免重复）
#   ③ 内部标记（下划线开头，另行处理）
_NOISE = {
    # ① 未公开的展示素材；主图 img_url 另以顶层 image 输出
    "carousel", "pc_imgs", "buyer_imgs", "qa_items", "pc_tabs",
    "desc", "attrs", "colors", "sell_points", "review_tags",
    "buy_options",
    # ② 顶层字段的原始来源；img_url 对应顶层 image
    "name", "short_title", "price", "market_price", "pc_price",
    "pc_market_price", "gid", "sku", "commodity_id", "img_url",
}


def to_public(rec: dict) -> dict:
    """把一条内部记录转成发布条目（保留可核对性）"""
    p = rec.get("product") or {}
    v = (rec.get("view") or {}).get("values") or {}
    item = {
        "id": p.get("variant_id") or p.get("product_id"),
        "name": p.get("name"),
        "kind": p.get("kind"),
        "category": p.get("category"),
        "price": v.get("price"),
        "market_price": v.get("market_price"),
        "gid": v.get("gid"),
        "image": v.get("img_url") or None,
        "fetched_at": rec.get("fetched_at"),
        "params": {k: val for k, val in v.items() if k not in _NOISE},
    }
    if p.get("source") in ("apple_cn", "apple_support"):
        item.update({key:p.get(key) for key in ("source","brand","market","product_id","variant_id","part_number","source_url","currency","price_kind","price_status","price_fetched_at","variant_attrs")})
        if p.get("source") == "apple_support":
            item.update({key: p.get(key) for key in (
                "family", "record_level", "catalog_scope", "sale_status",
                "document_locale", "source_docs_url")})
        if v.get("img_url"): item["image_url"] = v["img_url"]
    if p.get("record_level") == "model_reference":
        item.update({key:p.get(key) for key in ("source", "brand", "market", "record_level", "catalog_scope", "sale_status", "source_url", "model", "lookup_keys") if p.get(key) is not None})
        item["price"] = None
        item["market_price"] = None
    # 溯源标记：容器展开来的、或本身是容器
    if p.get("is_container"):
        item["is_container"] = True
    if p.get("from_container"):
        item["from_container"] = True
    # 去掉空值与内部标记
    item["params"] = {k: val for k, val in item["params"].items()
                      if not str(k).startswith("_") and val not in (None, "", [])}
    return normalize_public_row(item)


def build(cats_dir: Path = Path("data/categories"),
          out_dir: Path = Path("public"), supplements: Path = DEFAULT_SUPPLEMENTS) -> dict:
    items = []
    for f in sorted(glob.glob(str(Path(cats_dir) / "*.json"))):
        try:
            recs = json.loads(Path(f).read_text(encoding="utf-8"))
        except Exception:
            continue
        for r in recs:
            items.append(to_public(r))

    items.sort(key=lambda x: str(x.get("id")))
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    previous_path = out_dir / "goods.json"
    previous = json.loads(previous_path.read_text(encoding="utf-8")) if previous_path.exists() else []
    return publish(items, out_dir, previous, supplements)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--cats", default="data/categories")
    ap.add_argument("--out", default="public")
    a = ap.parse_args()
    print(json.dumps(build(Path(a.cats), Path(a.out)),
                     ensure_ascii=False, indent=1))
