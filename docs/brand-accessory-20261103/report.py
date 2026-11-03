"""Reproduce acceptance counts from exact before/after export and archive snapshots."""
import argparse
from collections import Counter
import gzip
import json
from pathlib import Path

from goodsdex.brands import audit_brands, distribution, normalize_brands


def load(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


def report(before, after, archive, old_archive):
    old_ids = {r['id'] for r in old_archive}
    new = [r for r in archive if r['id'] not in old_ids]
    excluded_ids = {r['id'] for r in new}
    kept_before = [r for r in before if r['id'] not in excluded_ids]
    # Keep ordering and conflicting duplicate IDs; no dict-by-ID data loss.
    strip = lambda row: {k: v for k, v in row.items() if k not in ('brand', 'brand_source')}
    assert list(map(strip, kept_before)) == list(map(strip, after)), 'Unrelated product fields changed'
    assert all(r.get('brand_source') == 'id_prefix' for r in after)
    assert not any(r['id'] in excluded_ids for r in after)
    old_by_id = {r['id']: r for r in old_archive}
    assert all(r == old_by_id[r['id']] for r in archive if r['id'] in old_ids), 'Prior archive changed'
    normalized = normalize_brands(before)
    brands = audit_brands(before, normalized)
    brands['after_filter'] = distribution(after)
    brands['before_unknown_ratio'] = sum(not r.get('brand') for r in before) / len(before)
    cats_before = Counter(r.get('category') for r in before)
    cats_after = Counter(r.get('category') for r in after)
    categories = [dict(category=k, before=cats_before[k], excluded=cats_before[k]-cats_after[k], after=cats_after[k]) for k in sorted(cats_before)]
    # All 11 newly discovered records + 9 historical real accessory records.
    samples = [dict(id=r['id'], name=r['name'], category=r.get('category'),
                    excluded_reason=r['excluded_reason'], batch='new') for r in new]
    for word in ('保护膜', '充电器', '数据线', '电池', '保护壳', '滤芯', '拖布', '桨叶', '收纳包'):
        r = next((r for r in old_archive if word in r['name']), None)
        if r and not any(s['id'] == r['id'] for s in samples):
            samples.append(dict(id=r['id'], name=r['name'], category=r.get('category'), excluded_reason=r['excluded_reason'], batch='historical'))
    assert len(samples) == 20
    return dict(before_count=len(before), after_count=len(after), brand=brands,
                newly_excluded_count=len(new), historical_excluded_count=len(old_archive),
                total_archived=len(archive), excluded_samples20=samples,
                new_exclusions=new, categories=categories,
                retained_fields_unchanged=True, historical_archive_unchanged=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--before', required=True)
    ap.add_argument('--after', required=True)
    ap.add_argument('--archive', required=True)
    ap.add_argument('--old-archive', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    result = report(load(a.before), load(a.after), load(a.archive), load(a.old_archive))
    Path(a.out).write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('categories','new_exclusions','excluded_samples20')}, ensure_ascii=False))
