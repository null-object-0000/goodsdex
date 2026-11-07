"""Release exclusion contract. Recomputed from observations, never the last view."""
from collections import Counter
from copy import deepcopy
import json
import sys

from goodsdex.accessories import classify, exclusion_reason
from goodsdex.brands import normalize_brands
from goodsdex.release_policy import ALLOWED_DELETIONS

# Closed enumeration: additions require updating README and the contract document.
REASONS = (
    'accessory:sticker', 'accessory:screen_film', 'accessory:cleaning_consumable',
    'accessory:category', 'accessory:name', 'apparel', 'preorder_deposit', 'service:installation', 'service:other', 'container', 'duplicate', 'invalid', 'manual',
)
# Reviewed identities, not inference from the human-readable deletion text.
DELETION_REASONS = {key: ('invalid' if key.startswith('CN:mi_cn:') else 'manual')
                    for key in ALLOWED_DELETIONS}


def reviewed_observations(public, rows, previous):
    """Recover old tombstones from source snapshots; persist full observations."""
    path = public / 'archive/non-goods.json'
    observations = {r['id']: r for r in json.loads(path.read_text())} if path.exists() else {}
    # Source categories retain reviewed records removed by older publishers.
    from goodsdex.publish import to_public
    for source in sorted((public.parent / 'data/categories').glob('*.json')):
        try:
            records = json.loads(source.read_text())
        except Exception as exc:
            print(f'[exclusions] skip unreadable {source.name}: {exc}', file=sys.stderr)
            continue
        if isinstance(records, dict):
            # Auxiliary reports live next to category snapshots; only mapping
            # payloads can carry product records.
            records = [v for v in records.values() if isinstance(v, dict)]
        if not isinstance(records, list):
            print(f'[exclusions] skip non-list {source.name}', file=sys.stderr)
            continue
        skipped = 0
        for record in records:
            if not isinstance(record, dict):
                skipped += 1
                continue
            p = record.get('product') or {}
            key = p.get('variant_id') or p.get('product_id')
            if key in ALLOWED_DELETIONS:
                observations[key] = to_public(record)
        if skipped:
            print(f'[exclusions] {source.name}: skipped {skipped} non-object entries',
                  file=sys.stderr)
    for row in [*(previous or []), *rows]:
        if row['id'] in ALLOWED_DELETIONS:
            observations[row['id']] = deepcopy(row)
    return list(observations.values())


def build_excluded(rows, published, accessory_archive, reviewed, duplicate_rows,
                   generated_at, revision):
    """One main reason per row; observed categories and evidence stay intact.

    The release universe is current input plus archived excluded identities absent
    from that input. Safe duplicate reductions count as rows, like meta.count.
    """
    published_ids = {r['id'] for r in published}
    candidates = {r['id']: r for r in [*accessory_archive, *reviewed]}
    for row in rows:
        if row['id'] not in published_ids:
            candidates[row['id']] = row
    items = []
    def append(row, reason, evidence):
        if reason not in REASONS:
            raise ValueError(f'Unknown exclusion reason: {reason}')
        entry = deepcopy(row)
        entry.update(excluded_reason=reason, excluded_at=generated_at, exclusion=evidence,
                     matched_rule=evidence.get('matched_rule', reason.split(':')[0]),
                     matched_text=evidence.get('matched_text', evidence.get('matched')))
        # Categories are source labels, not inferred from a rule or a name.
        entry['category_l1'] = row.get('category_l1')
        entry['category_l2'] = row.get('category_l2', row.get('category'))
        for key in ('name', 'brand', 'price', 'image', 'source_url'):
            entry.setdefault(key, None)
        items.append(entry)
    for key, row in sorted(candidates.items()):
        if key in published_ids:
            continue
        if key in DELETION_REASONS:
            append(row, DELETION_REASONS[key], dict(basis='reviewed_id', matched=ALLOWED_DELETIONS[key]))
        else:
            from goodsdex.services import classify_non_goods
            from goodsdex.apparel import classify_apparel
            service = classify_non_goods(row) or classify_apparel(row)
            reason = service['reason'] if service else exclusion_reason(row)
            if reason is None:
                raise ValueError(f'Archived exclusion no longer justified; review identity: {key}')
            append(row, reason, service or classify(row))
    for row in duplicate_rows:
        append(row, 'duplicate', dict(basis='safe_merge', matched=row['id']))
    items = normalize_brands(items)
    counts = Counter(r['excluded_reason'] for r in items)
    return dict(generatedAt=generated_at, revision=revision, total=len(items),
                reasons={r: counts[r] for r in REASONS}, items=items)


def excluded_by_rule(excluded):
    counts = Counter('apparel' if r['excluded_reason'] == 'apparel' else r['matched_rule']
                     for r in excluded['items'])
    return {rule: counts[rule] for rule in dict.fromkeys(r.split(':')[0] for r in REASONS)}


def validate_excluded(meta, excluded, published):
    if excluded['revision'] != meta['revision'] or excluded['generatedAt'] != meta['generated_at']:
        raise ValueError('Exclusion view belongs to another release')
    items = excluded['items']
    if excluded['total'] != len(items) or meta['total_excluded'] != len(items):
        raise ValueError('Exclusion total mismatch')
    counts = Counter(r['excluded_reason'] for r in items)
    if set(excluded['reasons']) != set(REASONS) or any(r not in REASONS for r in counts):
        raise ValueError('Unknown exclusion reason')
    if excluded['reasons'] != {r: counts[r] for r in REASONS}:
        raise ValueError('Exclusion reason counts mismatch')
    if meta['excluded_by_rule'] != excluded_by_rule(excluded):
        raise ValueError('Exclusion rule counts mismatch')
    if meta['total_published'] != len(published) or meta['total_all'] != len(published) + len(items):
        raise ValueError('Release total mismatch')
    ids = {r['id'] for r in published}
    if any(r['id'] in ids and r['excluded_reason'] != 'duplicate' for r in items):
        raise ValueError('Excluded identity leaked into goods')
    if any(r['excluded_at'] != excluded['generatedAt'] for r in items):
        raise ValueError('Stale exclusion decision')
