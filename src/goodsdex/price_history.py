"""Append-only, per-product price observations. Finalized only under the release lock."""
from __future__ import annotations
import gzip
import hashlib
import json
import math
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

CST = timezone(timedelta(hours=8))
MAX_BYTES = 200 * 1024 * 1024


def encode(value):
    return (json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n').encode()


def instant(at):
    value = datetime.fromisoformat(at.replace('Z', '+00:00'))
    if value.tzinfo is None:
        raise ValueError(f'Observation requires timezone: {at}')
    return value.astimezone(timezone.utc)


def numeric(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        n = float(value)
    except (ValueError, TypeError):
        return None
    return (int(n) if n.is_integer() else n) if math.isfinite(n) and n > 0 else None


def observation(row, *, at=None, status=None, backfilled=False):
    # Public id is the canonical cross-brand gid; raw Xiaomi gid is only an API key.
    gid = row.get('id') or row.get('gid')
    at = at or row.get('fetched_at')
    if not gid or not at:
        raise ValueError('Observation requires identity and actual collection time')
    at = instant(at).astimezone(CST).isoformat()
    price = numeric(row.get('price'))
    unavailable = row.get('price_status') == 'stale' or row.get('sale_status') in ('delisted', 'unavailable')
    status = status or ('unavailable' if unavailable else ('ok' if price is not None else 'no_price'))
    if status not in ('ok', 'no_price', 'unavailable') or (status == 'ok' and price is None):
        raise ValueError('Invalid observation status/price')
    return dict(gid=str(gid), at=at, price=price if status == 'ok' else None,
                price_type='price', currency=row.get('currency') or 'CNY',
                missing_status=status, source=str(gid).split(':')[1] if ':' in str(gid) else row.get('source', 'mi_cn'),
                **({'backfilled': True} if backfilled else {}))


def stage(public, events):
    events = list(events)
    if not events:
        return
    folder = Path(public).parent / 'data/price-observations'
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f'{uuid4().hex}.jsonl').write_bytes(b''.join(encode(e) for e in events))


def key(event):
    return event['gid'], instant(event['at'])


def signature(event):
    return tuple(event.get(k) for k in ('price', 'price_type', 'currency', 'missing_status', 'source'))


def finalize(public, revision, previous=None, *, now=None, max_bytes=MAX_BYTES):
    public = Path(public)
    folder = public / 'price-history'
    folder.mkdir(parents=True, exist_ok=True)
    index_path = folder / 'index.json'
    old = json.loads(index_path.read_bytes()) if index_path.exists() else {}
    # All archives remain available, including those outside default hot reads.
    descriptors = old.get('files', []) + old.get('archived_files', [])
    by_month, seen = defaultdict(list), {}
    for d in descriptors:
        raw = (public / d['path']).read_bytes()
        if hashlib.sha256(raw).hexdigest() != d['sha256']:
            raise ValueError(f'History digest mismatch: {d["path"]}')
        for line in gzip.decompress(raw).splitlines():
            event = json.loads(line)
            k = key(event)
            if k in seen:
                raise ValueError(f'Duplicate persisted observation: {k}')
            seen[k] = event
            by_month[d['month']].append(event)
    additions, backfilled = 0, 0
    def add(event, backfill=False):
        nonlocal additions, backfilled
        normalized = observation(dict(event, id=event['gid']), at=event['at'], status=event['missing_status'])
        if signature(event) != signature(normalized):
            raise ValueError('Malformed observation price/status/source')
        k = key(event)
        if k in seen:
            if signature(seen[k]) != signature(event):
                raise ValueError(f'Conflicting observation: {k}')
            return
        event = dict(event, revision=revision)
        seen[k] = event
        month = instant(event['at']).astimezone(CST).strftime('%Y-%m')
        by_month[month].append(event)
        additions += 1
        backfilled += bool(event.get('backfilled'))
    # One initial observation per actual goods timestamp. Missing prices are explicit too.
    if not old.get('backfill_completed'):
        for row in previous if previous is not None else json.loads((public / 'goods.json').read_bytes()):
            if row.get('fetched_at') and (row.get('id') or row.get('gid')):
                add(observation(row, backfilled=True), backfill=True)
    pending = public.parent / 'data/price-observations'
    for file in sorted(pending.glob('*.jsonl')):
        for line in file.read_bytes().splitlines():
            add(json.loads(line))
    cutoff = (now or datetime.now(timezone.utc)) - timedelta(days=90)
    files, archived = [], []
    def write(month, suffix, rows):
        if not rows:
            return
        name = f'{month}{suffix}.jsonl.gz'
        raw = gzip.compress(b''.join(encode(e) for e in rows), mtime=0)
        path = folder / name
        if not path.exists() or path.read_bytes() != raw:
            tmp = path.with_suffix('.tmp'); tmp.write_bytes(raw); tmp.replace(path)
        d = dict(month=month, path=f'price-history/{name}', sha256=hashlib.sha256(raw).hexdigest(),
                 count=len(rows), bytes=len(raw), start=min(e['at'] for e in rows), end=max(e['at'] for e in rows))
        (files if max(instant(e['at']) for e in rows) >= cutoff else archived).append(d)
    for month, rows in sorted(by_month.items()):
        # Preserve original order; append new events without changing existing observations.
        raw = gzip.compress(b''.join(encode(e) for e in rows), mtime=0)
        split = any((folder / f'{month}-{part}.jsonl.gz').exists() for part in ('a', 'b')) or len(raw) > max_bytes
        if split:
            write(month, '-a', [e for e in rows if instant(e['at']).astimezone(CST).day <= 15])
            write(month, '-b', [e for e in rows if instant(e['at']).astimezone(CST).day > 15])
        else:
            write(month, '', rows)
    summary = dict(months=len(by_month), observation_count=len(seen),
                   earliest=min((e['at'] for e in seen.values()), default=None),
                   latest=max((e['at'] for e in seen.values()), default=None))
    index = dict(schema=1, revision=revision, retention_days=90, detail_cutoff=cutoff.isoformat(),
                 backfill_completed=True, backfilled_count=old.get('backfilled_count', 0) + backfilled,
                 files=files, archived_files=archived, **summary)
    index_path.write_bytes(encode(index))
    meta_path = public / 'meta.json'
    meta = json.loads(meta_path.read_bytes())
    meta['price_history'] = dict(**summary, revision=revision, index='price-history/index.json',
                                 backfilled_count=index['backfilled_count'], retention_days=90)
    meta_path.write_bytes(encode(meta))
    # A compatibility projection for the deployed snapshot-only importer; no invented prices.
    # Do not replace existing legacy history. Add only new timestamps not already represented.
    for month, rows in by_month.items():
        legacy = public / 'prices' / f'{month}.jsonl'
        legacy.parent.mkdir(parents=True, exist_ok=True)
        stamps = set()
        if legacy.exists():
            for line in legacy.read_bytes().splitlines():
                stamps.add(instant(json.loads(line)['fetched_at']))
        snapshots = defaultdict(dict)
        for e in rows:
            if instant(e['at']) not in stamps:
                snapshots[e['at']][e['gid']] = dict(price=e['price'], missing_status=e['missing_status'])
        with legacy.open('ab') as fp:
            for at, prices in sorted(snapshots.items()):
                fp.write(encode(dict(fetched_at=at, prices=prices)))
    for file in pending.glob('*.jsonl'):
        file.unlink()
    return dict(added=additions, backfilled=backfilled, **summary)
