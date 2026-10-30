"""Reviewed non-product tombstones; no inferred or category-wide deletions."""
from types import MappingProxyType

ALLOWED_DELETIONS = MappingProxyType({
    "CN:mi_cn:product:25077": "空壳：名称空、无型号、无参数、无图、无价",
    "CN:mi_cn:product:18032": "空壳：名称空、无型号、无参数、无图、无价",
    "CN:mi_cn:product:18034": "空壳：名称空、无型号、无参数、无图、无价",
    "CN:mi_cn:product:21403": "空壳：名称空、无型号、无参数、无图、无价",
    "CN:mi_cn:product:21404": "空壳：名称空、无型号、无参数、无图、无价",
    "CN:mi_cn:product:25078": "空壳：名称空、无型号、无参数、无图、无价",
    "GLOBAL:apple_support:model:111980": "macOS Big Sur：操作系统页面，非商品机型",
    "GLOBAL:apple_support:model:111988": "macOS Sierra：操作系统页面，非商品机型",
    "GLOBAL:apple_support:model:112591": "Mac OS X v10.6 Snow Leopard：操作系统页面，非商品机型",
    "GLOBAL:apple_support:model:112593": "Mac OS X v10.5 Leopard：操作系统页面，非商品机型",
})


def remove_reviewed_non_goods(rows):
    return [row for row in rows if row.get("id") not in ALLOWED_DELETIONS]


def allowed_deletions(previous, current):
    missing = {r["id"] for r in previous} - {r["id"] for r in current}
    return {key: ALLOWED_DELETIONS[key] for key in sorted(missing & ALLOWED_DELETIONS.keys())}


def assert_no_lost_ids(previous, current, retained_ids=()):
    retained = {r["id"] for r in current} | set(retained_ids)
    missing = {r["id"] for r in previous} - retained - ALLOWED_DELETIONS.keys()
    if missing:
        raise ValueError(f"Publication would drop {len(missing)} IDs: {sorted(missing)}")


def assert_no_empty_shells(rows):
    # Check Xiaomi public records, including future IDs. 0 is a valid price/value.
    def present(value):
        if isinstance(value, str):
            return bool(value.strip())
        if isinstance(value, dict):
            return any(present(v) for v in value.values())
        if isinstance(value, (list, tuple)):
            return any(present(v) for v in value)
        return value is not None

    invalid = sorted({r["id"] for r in rows
        if (r.get("source") == "mi_cn" or r.get("id", "").startswith("CN:mi_cn:"))
        and not any(present(r.get(k)) for k in (
            "name", "params", "image", "image_url", "price", "market_price", "historical_price"))})
    if invalid:
        raise ValueError(f"Empty Xiaomi records cannot be published: {invalid}")
