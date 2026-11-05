"""把 data/archive-history 里确认下架的机型号，转成公开商品集里的一行（record_level=model_reference）。

用法：python3 scripts/merge_history_rows.py --archive data/archive-history --out /tmp/history-rows.json
只读归档，不发起任何网络请求。
"""
import argparse, glob, json, os, re

from goodsdex.legacy_catalog import category_of

def params_of(rec):
    out = {}
    for p in rec.get("params") or []:
        label = (p.get("label") or p.get("name") or "").strip()
        value = (p.get("value") or "").strip()
        if label and value and label not in out:
            out[label] = value
    return out

def to_row(rec):
    pid = str(rec.get("product_id") or "").strip()
    name = (rec.get("name") or "").strip()
    if not pid or not name:
        return None
    return {
        "id": f"CN:mi_cn:product:{pid}",
        "name": name,
        "kind": "machine" if rec.get("params_count") else "unknown",
        "category": category_of(name) or "待人工",
        "category_review_required": category_of(name) is None,
        "status": "retired",
        "price_missing": "page_no_price",
        "image_missing": "page_no_image",
        "captured_at": (rec.get("source") or {}).get("fetched_at"),
        "captured_at_unknown": not bool((rec.get("source") or {}).get("fetched_at")),
        "price": None,
        "market_price": None,
        "gid": None,
        "image": None,
        "record_level": "model_reference",
        "discontinued": True,
        "discontinued_source": (rec.get("status_source") or {}).get("url"),
        "params": params_of(rec),
        "source": "goods_supplements:xiaomi_archive_history",
        "catalog_identity": "goods_supplements:archive_history:model_reference",
        "fetched_at": (rec.get("source") or {}).get("fetched_at"),
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive", default="data/archive-history")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rows, skipped = [], 0
    for path in sorted(glob.glob(os.path.join(a.archive, "*.json"))):
        try:
            rec = json.load(open(path, encoding="utf-8"))
        except Exception:
            skipped += 1
            continue
        if not rec.get("discontinued"):
            skipped += 1
            continue
        row = to_row(rec)
        if row:
            rows.append(row)
        else:
            skipped += 1
    seen, unique = set(), []
    for r in rows:
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        unique.append(r)
    json.dump(unique, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    with_params = sum(1 for r in unique if r["params"])
    print(f"归档文件: {len(glob.glob(os.path.join(a.archive,'*.json')))} 条, 转出 {len(unique)} 行, 跳过 {skipped}")
    print(f"带参数: {with_params} ({with_params*100//max(len(unique),1)}%)")

if __name__ == "__main__":
    main()
