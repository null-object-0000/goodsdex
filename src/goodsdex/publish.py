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

import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from goodsdex.supplements import DEFAULT_SUPPLEMENTS, publish
from goodsdex.public_fields import normalize_public_row

CST = timezone(timedelta(hours=8))

# data/categories/ 混放的非商品快照文件后缀（审计报告、设备目录、发现集、人工待审队列）。
_NON_SNAPSHOT_SUFFIXES = (
    "-report.json",
    "-directory.json",
    "-discovery.json",
    "-review-queue.json",
)


def is_category_snapshot_file(path: Path) -> bool:
    """判断路径是否为商品分类快照文件名（排除审计报告与目录/发现/待审队列）。"""
    name = Path(path).name
    return name.endswith(".json") and not name.endswith(_NON_SNAPSHOT_SUFFIXES)


def iter_category_files(cats_dir: Path | str):
    """集中枚举分类商品快照文件并解析记录列表。

    排除规则统一收口于此：
      - 跳过 `*-report.json` / `*-directory.json` / `*-discovery.json` / `*-review-queue.json`
      - 跳过无法解析或顶层不是 list 的 JSON（如目录型 dict）
      - 仅产出顶层 list，由调用方或 `iter_category_records` 消费
    """
    cats_path = Path(cats_dir)
    if not cats_path.exists():
        return
    for f in sorted(cats_path.glob("*.json")):
        if not is_category_snapshot_file(f):
            continue
        try:
            recs = json.loads(f.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"[publish] skip unreadable {f.name}: {exc}", file=sys.stderr)
            continue
        if not isinstance(recs, list):
            continue
        yield f, recs


def record_id(rec: dict) -> str | None:
    """提取内部商品快照记录的唯一身份（variant_id 优先，其次 product_id）。"""
    if not isinstance(rec, dict):
        return None
    p = rec.get("product")
    if not isinstance(p, dict):
        return None
    vid = p.get("variant_id") or p.get("product_id")
    return vid if isinstance(vid, str) and vid.strip() else None

# view.values 里**不属于商品属性**的键。
# 分三类：
#   ① 未公开的展示素材（不导出整组图片与详情）
#   ② 提升到顶层或由顶层身份/价格字段替代的原始字段（避免重复）
#   ③ 内部标记（下划线开头，另行处理）
_NOISE = {
    # ① 未公开的展示素材；主图 img_url 另以顶层 image 输出
    "carousel", "pc_imgs", "buyer_imgs", "qa_items", "pc_tabs",
    "desc", "attrs", "colors", "sell_points", "review_tags",
    "buy_options", "official_main_image",
    # ② 顶层字段的原始来源；img_url 对应顶层 image
    "name", "short_title", "price", "market_price", "pc_price",
    "pc_market_price", "gid", "sku", "commodity_id", "img_url",
}


def to_public(rec: dict, *, source_file: str | None = None, row_index: int | None = None) -> dict:
    """把一条内部记录转成发布条目（保留可核对性）。

    契约：必须拥有非空字符串身份（product.variant_id 或 product.product_id），
    绝不允许产出 id=None 的行。
    """
    rid = record_id(rec)
    if not rid:
        loc = f" ({source_file}#{row_index})" if source_file is not None else ""
        raise ValueError(f"to_public: record missing product.product_id/variant_id{loc}")
    p = rec.get("product") or {}
    v = (rec.get("view") or {}).get("values") or {}
    item = {
        "id": rid,
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
    if str(item.get("id") or "").startswith("CN:mi_cn:product:"):
        # Cached source records already have full names in their resolved view.
        source = p.get("name_source") or {}
        item["name"] = p.get("name") if isinstance(source, dict) and source.get("kind") == "official_page_title" else v.get("name") or p.get("name")
        if p.get("name_source"):
            item["name_source"] = p["name_source"]
            if isinstance(source, dict) and source.get("kind") == "official_page_title":
                item["source_url"] = source["url"]
        # Only a successful mobile business response proves current availability;
        # failed captures may still contain a cached product identity.
        if any(c.get("source") == "mi_cn_mobile" and c.get("status") == "success"
               for c in rec.get("captures", [])):
            item["on_sale"] = True
        from goodsdex.accessories import classify
        item["is_accessory"] = classify(item)["accessory"]
        if item["is_accessory"]:
            item["kind"] = "accessory"
    # 溯源标记：容器展开来的、或本身是容器
    if p.get("is_container"):
        item["is_container"] = True
    if p.get("from_container"):
        item["from_container"] = True
    # 去掉空值与内部标记
    item["params"] = {k: val for k, val in item["params"].items()
                      if not str(k).startswith("_") and val not in (None, "", [])}
    from goodsdex.xiaomi_covers import record_cover
    item = record_cover(rec, item)
    from goodsdex.manual_params import apply_public_params
    return apply_public_params([normalize_public_row(item)])[0][0]


def collect_public(cats_dir):
    """Use the same source projection for absence checks and publication."""
    items = []
    skipped_non_dict = 0
    skipped_no_id = 0
    for f, recs in iter_category_files(cats_dir):
        for idx, r in enumerate(recs):
            if not isinstance(r, dict):
                skipped_non_dict += 1
                continue
            if not record_id(r):
                skipped_no_id += 1
                print(f"[publish] skip record without product id at {f.name}#{idx}", file=sys.stderr)
                continue
            items.append(to_public(r, source_file=f.name, row_index=idx))

    if skipped_non_dict or skipped_no_id:
        print(f"[publish] skipped {skipped_non_dict} non-dict rows and {skipped_no_id} missing-id rows",
              file=sys.stderr)
    items.sort(key=lambda x: str(x.get("id")))
    return items


def build(cats_dir: Path = Path("data/categories"),
          out_dir: Path = Path("public"), supplements: Path = DEFAULT_SUPPLEMENTS) -> dict:
    items = collect_public(cats_dir)
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
