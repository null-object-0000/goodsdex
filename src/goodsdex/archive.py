"""商品档案：累积历史，下架不丢。

## 为什么需要

原来的落盘是**整分类覆盖**（`pipeline.run_category` 用原子替换写
`<分类>.json`）。后果：某商品下架后，下次采集它不在结果里，
**旧记录被覆盖 = 永久丢失**——与"持续积累、下架也留档"的目标冲突。

## 做法

采集结果与**档案**分开：
  data/categories/<分类>.json   本次采集的**快照**（可覆盖，反映当下）
  data/archive/<分类>.json      **累积档案**（只增不减，记录每个商品
                                最后见到的时刻与状态）

档案合并规则（关键）：
  - 本次见到的商品  -> 更新 last_seen_at / last_seen_price / times_seen
  - 本次没见到的    -> **保留**，标 missing_since（若之前是在售）
  - 曾标记下架的    -> 若又出现，清掉 missing_since（复活）

这样"从某一刻开始持续积累"才有意义：档案是单调增长的，
任何时刻的商品状态都能回溯。
"""
from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

CST = timezone(timedelta(hours=8))


def _now() -> str:
    return datetime.now(CST).isoformat(timespec="seconds")


def _slim(rec: dict) -> dict:
    """档案里存精简条目（身份 + 价格 + 参数），不含原始证据。

    原始证据在 data/categories 的 captures 里（体量大、可按需重采）；
    档案要长期累积，只留可对比的字段。
    """
    p = rec.get("product") or {}
    v = (rec.get("view") or {}).get("values") or {}
    noise = {"carousel", "pc_imgs", "buyer_imgs", "qa_items", "pc_tabs",
             "desc", "attrs", "colors", "sell_points", "review_tags",
             "buy_options", "name", "short_title", "price", "market_price",
             "pc_price", "pc_market_price", "gid", "sku", "commodity_id",
             "img_url"}
    return {
        "id": p.get("product_id"),
        "name": p.get("name"),
        "kind": p.get("kind"),
        "price": v.get("price"),
        "market_price": v.get("market_price"),
        "gid": v.get("gid"),
        "params": {k: val for k, val in v.items()
                   if k not in noise and not str(k).startswith("_")
                   and val not in (None, "", [])},
    }


def merge_archive(category: str, records: list[dict],
                  archive_dir: Path = Path("data/archive"),
                  seen_at: Optional[str] = None,
                  now_iso: Optional[str] = None) -> dict:
    """把一次采集结果并入档案，返回统计。

    幂等：同一批记录重复并入不会重复计数（按 id 更新）。
    """
    stamp = now_iso or _now()
    archive_dir = Path(archive_dir)
    archive_dir.mkdir(parents=True, exist_ok=True)
    fp = archive_dir / f"{category}.json"

    arch: dict = {}
    if fp.exists():
        try:
            arch = json.loads(fp.read_text(encoding="utf-8"))
        except Exception:
            arch = {}
    items: dict = arch.get("items") or {}

    seen_ids = set()
    added = updated = revived = 0
    for r in records:
        e = _slim(r)
        pid = e.get("id")
        if not pid:
            continue
        seen_ids.add(pid)
        old = items.get(pid)
        if old is None:
            items[pid] = {**e, "first_seen_at": stamp, "last_seen_at": stamp,
                          "times_seen": 1}
            added += 1
        else:
            was_missing = bool(old.get("missing_since"))
            old.update(e)                      # 刷新为最新观测值
            old["last_seen_at"] = stamp
            old["times_seen"] = int(old.get("times_seen") or 0) + 1
            if was_missing:
                old.pop("missing_since", None)
                revived += 1
            updated += 1

    # 本次没见到的：保留，标 missing_since（首次缺席时记录）
    went_missing = 0
    for pid, old in items.items():
        if pid in seen_ids:
            continue
        if not old.get("missing_since"):
            old["missing_since"] = stamp
            went_missing += 1

    out = {
        "category": category,
        "updated_at": stamp,
        "count": len(items),
        "present": len(seen_ids),
        "missing": len(items) - len(seen_ids),
        "items": items,
    }
    tmp = fp.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(out, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    tmp.replace(fp)
    return {"category": category, "total": len(items),
            "present": len(seen_ids), "missing": out["missing"],
            "added": added, "updated": updated,
            "went_missing": went_missing, "revived": revived}


def archive_stats(archive_dir: Path = Path("data/archive")) -> dict:
    """档案总览：多少商品、多少已下架。"""
    archive_dir = Path(archive_dir)
    total = present = missing = 0
    cats = 0
    for f in sorted(archive_dir.glob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        cats += 1
        for it in (d.get("items") or {}).values():
            total += 1
            if it.get("missing_since"):
                missing += 1
            else:
                present += 1
    return {"categories": cats, "total": total,
            "present": present, "missing": missing}


if __name__ == "__main__":
    import sys
    print(json.dumps(archive_stats(), ensure_ascii=False, indent=1))
