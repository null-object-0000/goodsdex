"""Keep official product history; unavailability is never retirement evidence."""
from copy import deepcopy
from collections import Counter
import json
from pathlib import Path
from datetime import datetime


def event_time(value):
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00')).timestamp()
    except (ValueError, AttributeError):
        return float('-inf')


def archive_observations(public, previous):
    """Bridge the existing complete-discovery archives into public lifecycle state.

    archive.merge_archive sets missing_since only after completeness validation;
    partial/failed rounds cannot create that event. Use the full published row
    for retention, never recreate a product from the old slim archive.
    """
    known = {r['id']: r for r in previous}
    result = {}
    for path in sorted((Path(public) / 'archive').glob('*.json')):
        if path.name == '_delisted.json':
            continue  # Separate explicit API evidence, consumed by delisted.apply_archive.
        archive = json.loads(path.read_text())
        if not isinstance(archive, dict) or not isinstance(archive.get('items'), dict):
            continue
        for key, item in archive['items'].items():
            row = known.get(key)
            if not row or not row.get('source_url'):
                continue
            missing = item.get('missing_since')
            last_seen = item.get('last_seen_at')
            if missing:
                obs = dict(id=key, state='missing', observed_at=missing,
                           source_url=row['source_url'],
                           reason='absent_from_completed_official_catalogue',
                           archive_path='archive/' + path.name)
            elif last_seen:
                obs = dict(id=key, state='available', observed_at=last_seen,
                           source_url=row['source_url'])
            else:
                continue
            old = result.get(key, {})
            rank = (event_time(obs['observed_at']), obs['state'] == 'available')
            old_rank = (event_time(old.get('observed_at')), old.get('state') == 'available')
            if rank > old_rank:
                result[key] = obs
    # Seeing a product in any newer category overrides an older category's
    # absence. Consider those sightings even before it has ever been retired;
    # otherwise the first finalize falsely retires it and the next revives it.
    return [obs for key, obs in result.items()
            if (obs['state'] == 'available' and known[key].get('status') == 'retired'
                and event_time(obs['observed_at']) >= event_time(known[key].get('retired_at')))
            or (obs['state'] == 'missing' and
                event_time(obs['observed_at']) >= event_time(known[key].get('fetched_at')))]


def completed_snapshot(previous, current, *, brands, observed_at, snapshot_url):
    """Compare a successfully completed authoritative inventory for selected brands.

    Never call on partial listings or a failed collection. Keep the full prior
    record when it leaves that inventory; this means catalogue withdrawal, not
    hardware end-of-life. Non-selected brands remain subject to no-lost-ID gates.
    """
    if not observed_at or not snapshot_url or not brands:
        raise ValueError('Completed snapshot needs scope, URL and observation time')
    present = {r['id'] for r in current}
    observations = [dict(id=r['id'], state='missing', source_url=r.get('source_url'),
                         observed_at=observed_at, reason='absent_from_completed_official_catalogue',
                         snapshot_url=snapshot_url)
                    for r in previous if r.get('brand') in brands and r['id'] not in present]
    return reconcile(previous, current, observations)


def reconcile(previous, current, observations=()):
    """Reconcile a completed crawl using explicit per-product observations.

    Collectors must distinguish a confirmed missing page (404/410 or a validated
    catalogue redirect) from timeouts, challenges and partial discovery. Merely
    being absent from a search/listing is not enough. Reappearances require an
    explicit available observation, so an old retained row cannot revive itself.
    """
    evidence = {e['id']: e for e in observations}
    rows = deepcopy(current)
    present = {r['id'] for r in rows}
    for row in previous:
        obs = evidence.get(row['id'], {})
        if row['id'] not in present and (row.get('status') == 'retired' or
                                        obs.get('state') == 'missing'):
            rows.append(deepcopy(row))
            # Keep all legitimate variants of an absent ID. The existing
            # publication contract permits protected duplicate-ID variants.
    old = {r['id']: r for r in previous}
    for row in rows:
        prior = old.get(row['id'], {})
        obs = evidence.get(row['id'], {})
        # Do not replay a past missing-page event after a later verified revival.
        reappeared_at = max((h.get('reappeared_at', '') for h in prior.get('retirement_history', [])), default='')
        if reappeared_at and obs.get('observed_at', '') <= reappeared_at:
            obs = {}
        if obs.get('state') == 'missing':
            if not obs.get('source_url') or not obs.get('observed_at') or not obs.get('reason'):
                raise ValueError('Retirement requires URL, observation time and reason')
            row.update(status='retired',
                       retired_at=prior.get('retired_at') or obs['observed_at'],
                       retirement_evidence=prior.get('retirement_evidence') or deepcopy(obs))
        elif obs.get('state') == 'available':
            row['status'] = 'available'
            if prior.get('retired_at'):
                row.setdefault('retirement_history', []).append({
                    'retired_at': prior['retired_at'], 'evidence': prior.get('retirement_evidence'),
                    'reappeared_at': obs['observed_at']})
            row.pop('retired_at', None)
            row.pop('retirement_evidence', None)
            if row.get('sale_status') == 'delisted':
                row.pop('sale_status', None)
                row.pop('delisted_at', None)
                row.pop('delisted_evidence', None)
        elif prior.get('status') == 'retired':
            for key in ('status', 'retired_at', 'retirement_evidence'):
                if key in prior:
                    row[key] = deepcopy(prior[key])
        # Migrate previously verified HP delistings without changing first-seen time.
        if row.get('sale_status') == 'delisted' and row.get('delisted_evidence'):
            row['status'] = 'retired'
            row.setdefault('retired_at', row['delisted_at'])
            row.setdefault('retirement_evidence', deepcopy(row['delisted_evidence']))
    return rows


def counts(rows):
    retired = [r for r in rows if r.get('status') == 'retired']
    return dict(retired_count=len(retired),
                retired_by_brand=dict(Counter(r.get('brand') or '未知' for r in retired)))
