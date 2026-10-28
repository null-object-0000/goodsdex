"""Append-only supplemental release rows and fail-closed publication checks."""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from goodsdex.cars import is_car

DEFAULT_SUPPLEMENTS = Path(__file__).resolve().parents[2] / "data/supplements/goods-supplements.json"


def indexed(rows, label, unique=False):
    result = {}
    for row in rows:
        key = row.get("id")
        if not isinstance(key, str) or not key or (unique and key in result):
            raise ValueError(f"{label}: missing/duplicate id: {key!r}")
        result[key] = row
    return result


def merge(rebuilt, supplements, previous):
    # Other publishers cannot drop cars; only the separate daily job refreshes them.
    present = {r['id'] for r in rebuilt}
    rebuilt = rebuilt + [r for r in previous if is_car(r) and r['id'] not in present]
    existing = indexed(rebuilt, "rebuilt")
    extra = indexed(supplements, "supplements", unique=True)
    old = indexed(previous, "previous")
    for key, row in extra.items():
        if not row.get("source") or not row.get("catalog_identity"):
            raise ValueError(f"supplement lacks provenance: {key}")
        if key in existing:
            print(f"supplement conflict (keep rebuilt): {key}")
    added = [row for key, row in extra.items() if key not in existing]
    result = rebuilt + added
    missing = sorted(old.keys() - indexed(result, "merged").keys())
    if missing:
        raise ValueError(f"Publication would drop {len(missing)} IDs: {json.dumps(missing, ensure_ascii=False)}")
    if len(result) != len(rebuilt) + len(added):
        raise ValueError("count != rebuilt_count + added_count")
    audit = dict(previous_count=len(previous), rebuilt_count=len(rebuilt),
                 added_count=len(added), count=len(result), missing_ids=missing,
                 added_ids=[r["id"] for r in added], conflicts=sorted(extra.keys() & existing.keys()))
    print(json.dumps(audit, ensure_ascii=False))
    return result, audit


def publish(rebuilt, out_dir, previous, supplements=DEFAULT_SUPPLEMENTS):
    # Validate before writing either release file. Missing supplements fail closed.
    result, audit = merge(rebuilt, json.loads(Path(supplements).read_text(encoding="utf-8")), previous)
    out_dir = Path(out_dir)
    meta_path = out_dir / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    meta = metadata(result, meta)
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, value in (("goods.json", result), ("meta.json", meta), ("merge-audit.json", audit)):
        path = out_dir / name
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(value, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        tmp.replace(path)
    return meta


def metadata(result, meta=None):
    meta = dict(meta or {})
    meta.update(generated_at=datetime.now(timezone.utc).isoformat(), count=len(result),
                brands=dict(Counter(r.get("brand") or ("小米" if r["id"].startswith("CN:mi_cn:") else "未知") for r in result)),
                with_price=sum(r.get("price") is not None for r in result),
                by_kind=dict(Counter(r.get("kind") or "unknown" for r in result)))
    return meta
