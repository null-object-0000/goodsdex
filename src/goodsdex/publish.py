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
        "id": p.get("product_id"),
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
    # 溯源标记：容器展开来的、或本身是容器
    if p.get("is_container"):
        item["is_container"] = True
    if p.get("from_container"):
        item["from_container"] = True
    # 去掉空值与内部标记
    item["params"] = {k: val for k, val in item["params"].items()
                      if not str(k).startswith("_") and val not in (None, "", [])}
    return item


def build(cats_dir: Path = Path("data/categories"),
          out_dir: Path = Path("public")) -> dict:
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

    (out_dir / "goods.json").write_text(
        json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")

    kinds: dict = {}
    for it in items:
        k = it.get("kind") or "unknown"
        kinds[k] = kinds.get(k, 0) + 1
    withprice = sum(1 for it in items if it.get("price") is not None)

    meta = {
        "generated_at": datetime.now(CST).isoformat(timespec="seconds"),
        "count": len(items),
        "by_kind": kinds,
        "with_price": withprice,
        "note": ("发布集是派生视图：含身份/价格/主图链接/参数。"
                 "原始响应与逐字段证据保留在采集端，用于审计。"),
    }
    (out_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    return meta


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--cats", default="data/categories")
    ap.add_argument("--out", default="public")
    a = ap.parse_args()
    print(json.dumps(build(Path(a.cats), Path(a.out)),
                     ensure_ascii=False, indent=1))
