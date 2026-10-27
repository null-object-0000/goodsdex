"""把 data/archive-history 里确认下架的机型号，转成公开商品集里的一行（record_level=model_reference）。

用法：python3 scripts/merge_history_rows.py --archive data/archive-history --out /tmp/history-rows.json
只读归档，不发起任何网络请求。
"""
import argparse, glob, json, os, re

# 名称 → 分类。命中不到就给「旧款机型」，不硬猜。
CATEGORY_HINTS = [
    ("显示器", "显示器"), ("电视", "电视"), ("空调", "空调"), ("冰箱", "冰箱"), ("洗衣机", "洗衣机"),
    ("扫地", "扫地机器人"), ("扫拖", "扫地机器人"), ("吸尘", "吸尘器"), ("净化器", "空气净化器"),
    ("路由器", "路由器"), ("音箱", "音箱"), ("耳机", "耳机"), ("手环", "手环"), ("手表", "手表"),
    ("平板", "平板"), ("笔记本", "笔记本"), ("手机", "手机"), ("电饭煲", "电饭煲"), ("电水壶", "电水壶"),
    ("台灯", "台灯"), ("插座", "插座"), ("摄像头", "摄像头"), ("门锁", "门锁"), ("体重秤", "体重秤"),
    ("体脂秤", "体重秤"), ("风扇", "风扇"), ("加湿器", "加湿器"), ("微波炉", "微波炉"), ("烤箱", "烤箱"),
    ("电磁炉", "电磁炉"), ("剃须刀", "剃须刀"), ("吹风机", "吹风机"), ("牙刷", "电动牙刷"), ("净水", "净水器"),
    ("电蚊", "驱蚊"), ("被子", "床品"), ("枕头", "床品"), ("背包", "箱包"), ("旅行箱", "箱包"),
]

def category_of(name):
    for key, cat in CATEGORY_HINTS:
        if key in name:
            return cat
    return "旧款机型"

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
        "category": category_of(name),
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
