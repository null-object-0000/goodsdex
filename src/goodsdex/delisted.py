"""Explicit Xiaomi delisting evidence; absent/failed requests never imply delisting.

Fetcher contract: fetcher(public_id, timeout=10) -> decoded business response.
HTTP errors must raise (as the default urllib fetcher does). At most four requests
run concurrently, each with one retry. Only confirmed rows bypass absence by
remaining full records in current; the publication gate is unchanged.
"""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import urllib.request

URL = 'https://m.mi.com/mtop/xiaomishop/product/info'
ARCHIVE_NAME = '_delisted.json'
ID_PATTERN = re.compile(r'CN:mi_cn:product:([0-9]+)\Z')


def fetch_product(key, timeout=10):
    from goodsdex.sources.mi_cn import MTOP_HEADERS
    pid = int(ID_PATTERN.fullmatch(key).group(1))
    request = urllib.request.Request(URL, data=json.dumps([{}, {'productId': pid}]).encode(),
                                     headers=MTOP_HEADERS)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read())


def is_delisted(response):
    return response.get('code') != 0 and (response.get('code') == 400480502 or
                                         '已下架' in str(response.get('message', '')))


def confirm_delisted(ids, fetcher=fetch_product, now=None, *, unknown=None,
                     available=None, workers=4):
    """Return only explicit delistings. Optional sinks retain audit diagnostics.

    code:0 always means available, even if an inconsistent message says otherwise.
    Unsupported identities are unknown and never sent to the Xiaomi endpoint.
    """
    stamp = now or datetime.now(timezone.utc).isoformat(timespec='seconds')
    if isinstance(stamp, datetime):
        stamp = stamp.isoformat(timespec='seconds')

    def probe(key):
        if not ID_PATTERN.fullmatch(key):
            return key, 'unknown', dict(reason='unsupported_identity', attempts=0)
        for attempt in range(1, 3):
            try:
                response = fetcher(key, timeout=10)
                if not isinstance(response, dict):
                    raise ValueError('Response is not an object')
                evidence = dict(code=response.get('code'), message=response.get('message'),
                                probed_at=stamp, url=URL)
                if is_delisted(response):
                    return key, 'confirmed', evidence
                if response.get('code') == 0:
                    return key, 'available', evidence
                reason = 'non_delisted_response'
            except Exception as exc:
                evidence = dict(probed_at=stamp, url=URL)
                reason = f'{type(exc).__name__}: {exc}'
        return key, 'unknown', dict(evidence, reason=reason, attempts=2)

    confirmed = {}
    with ThreadPoolExecutor(max_workers=max(1, min(workers, 4))) as pool:
        for key, state, value in pool.map(probe, sorted(set(ids))):
            if state == 'confirmed':
                confirmed[key] = value
            else:
                if unknown is not None:
                    unknown[key] = dict(value, reason=value.get('reason', 'available_response'))
                if state == 'available' and available is not None:
                    available[key] = value
    return confirmed


def prepare(previous, current, archive, fetcher=fetch_product, now=None):
    """Build collector-side full-row archive plus this round's audit report."""
    old = {r['id']: r for r in previous}
    present = {r['id'] for r in current}
    # Availability is a one-round event; never replay it over a later failure.
    items = {key: deepcopy(entry) for key, entry in archive.get('items', {}).items()
             if entry.get('state') == 'delisted'}
    for key, row in old.items():
        evidence = row.get('delisted_evidence', {})
        if (ID_PATTERN.fullmatch(key) and row.get('on_sale') is False
                and is_delisted(evidence) and evidence.get('url') == URL
                and evidence.get('probed_at')):
            items.setdefault(key, dict(row=deepcopy(row), state='delisted',
                                       evidence=deepcopy(evidence)))
    candidates = (old.keys() - present) | {key for key, r in old.items()
                                         if r.get('delisted_evidence') and ID_PATTERN.fullmatch(key)}
    unknown, available = {}, {}
    confirmed = confirm_delisted(candidates, fetcher, now, unknown=unknown, available=available)
    revived = {}
    for key, evidence in confirmed.items():
        items[key] = dict(row=deepcopy(old[key]), state='delisted', evidence=evidence)
    for key, evidence in available.items():
        if key in present and (old[key].get('delisted_evidence') or
                               items.get(key, {}).get('state') == 'delisted'):
            items[key] = dict(state='available', evidence=evidence)
            revived[key] = evidence
            unknown.pop(key, None)
    report = dict(confirmed=confirmed, unknown=unknown, revived=revived,
                  counts=dict(confirmed=len(confirmed), unknown=len(unknown), revived=len(revived)))
    return dict(schema=1, items=items), report


def apply_archive(current, archive):
    """Replay only explicit evidence, keeping full archived rows for absent IDs."""
    rows = deepcopy(current)
    items = archive.get('items', {})
    present = {r['id'] for r in rows}
    confirmed = {}
    for key, entry in items.items():
        evidence = entry.get('evidence', {})
        if (ID_PATTERN.fullmatch(key) and entry.get('state') == 'delisted'
                and is_delisted(evidence) and evidence.get('url') == URL
                and evidence.get('probed_at')):
            if entry['row']['id'] != key:
                raise ValueError('Delisted archive identity mismatch')
            confirmed[key] = entry
    # A failed detail capture may leave a shell in categories. Keep the last
    # complete published record for confirmed delistings, including its params.
    rows = [deepcopy(confirmed[r['id']]['row']) if r['id'] in confirmed else r
            for r in rows]
    rows.extend(deepcopy(entry['row']) for key, entry in confirmed.items() if key not in present)
    for row in rows:
        entry = items.get(row['id'], {})
        evidence = entry.get('evidence', {})
        if not ID_PATTERN.fullmatch(row['id']) or evidence.get('url') != URL or not evidence.get('probed_at'):
            continue
        if entry.get('state') == 'delisted' and is_delisted(evidence):
            row.update(on_sale=False, delisted_at=evidence['probed_at'][:10],
                       delisted_evidence=deepcopy(evidence))
        elif entry.get('state') == 'available' and evidence.get('code') == 0:
            row['on_sale'] = True
            for key in list(row):
                if key.startswith('delisted_'):
                    row.pop(key)
            # A fresh successful product response also supersedes old catalogue
            # absence state, otherwise retirement.reconcile would revive it later.
            if row.get('status') == 'retired':
                from goodsdex.retirement import reconcile
                revived = reconcile([row], [row], [dict(id=row['id'], state='available',
                                    observed_at=evidence['probed_at'], source_url=URL)])[0]
                row.clear()
                row.update(revived)
            if row.get('sale_status') == 'delisted':
                row.pop('sale_status')
    return rows


def load_archive(public):
    path = Path(public) / 'archive' / ARCHIVE_NAME
    return json.loads(path.read_text()) if path.exists() else {}
