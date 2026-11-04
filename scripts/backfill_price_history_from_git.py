"""Recover real price observations from Git, with bounded snapshot memory.

The public directory is a detached data checkout. No goods or publishing code is
modified. SQLite holds identities on disk; only one JSON row is decoded at once.
Existing OSS history manifest descriptors are refreshed without rebuilding goods.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timedelta, timezone
import gzip
import hashlib
import io
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from goodsdex.price_history import CST, encode, instant, observation


def stream_array(stream, chunk_size=65536):
    """Strict incremental top-level JSON array parser (one row plus a chunk)."""
    decoder = json.JSONDecoder()
    buf, pos, eof = '', 0, False

    def more():
        nonlocal buf, pos, eof
        buf = buf[pos:]
        pos = 0
        block = stream.read(chunk_size)
        eof = not block
        buf += block

    def char():
        nonlocal pos
        while True:
            while pos < len(buf) and buf[pos].isspace():
                pos += 1
            if pos < len(buf) or eof:
                return buf[pos:pos + 1]
            more()

    if char() != '[':
        raise ValueError('Expected goods array')
    pos += 1
    if char() != ']':
        while True:
            while True:
                try:
                    row, end = decoder.raw_decode(buf, pos)
                    break
                except json.JSONDecodeError:
                    if eof:
                        raise
                    more()
                    char()
            if not isinstance(row, dict):
                raise ValueError('Expected goods object')
            pos = end
            yield row
            delimiter = char()
            if delimiter == ']':
                break
            if delimiter != ',':
                raise ValueError('Expected comma')
            pos += 1
            char()
    pos += 1
    if char():
        raise ValueError('Trailing JSON content')


def recover(row, sha, committed_at):
    at = row.get('fetched_at') or committed_at
    event = observation(row, at=at, backfilled=True)
    event.update(time_source='fetched_at' if row.get('fetched_at') else 'commit',
                 git_commit=sha, revision=sha, market_price=row.get('market_price'),
                 price_kind=row.get('price_kind'), raw_price=row.get('price'),
                 original_missing_status=row.get('missing_status'))
    if row.get('missing_status') in ('no_price', 'unavailable'):
        event.update(price=None, missing_status=row['missing_status'])
    return flag_suspicious(event)


def flag_suspicious(event):
    # Retain questionable input verbatim, but never expose it as an accepted price.
    raw = event.get('raw_price', event.get('price'))
    if raw is not None:
        try:
            valid = not isinstance(raw, bool) and 0 < float(raw) < 200000
        except (TypeError, ValueError, OverflowError):
            valid = False
        if not valid:
            event = dict(event, raw_price=raw, price=None, suspicious=True,
                         suspicious_reason='price_outside_0_200000_or_non_numeric')
            if event['missing_status'] == 'ok':
                event['missing_status'] = 'no_price'
    return event


def digest(path):
    sha = hashlib.sha256()
    with path.open('rb') as fp:
        for block in iter(lambda: fp.read(65536), b''):
            sha.update(block)
    return sha.hexdigest()


def update_meta(public, index):
    meta_path = public / 'meta.json'
    meta = json.loads(meta_path.read_bytes())
    files = {}
    entries = [('price-history/index.json', index['observation_count'])]
    entries += [(d['path'], d['count']) for d in index['files'] + index['archived_files']]
    for path in sorted((public / 'prices').glob('*.jsonl')):
        with path.open('rb') as fp:
            count = sum(bool(line.strip()) for line in fp)
        entries.append((path.relative_to(public).as_posix(), count))
    for name, count in entries:
        path = public / name
        files[name] = dict(sha256=digest(path), bytes=path.stat().st_size, count=count)
    meta.setdefault('price_history', {}).update({k:index[k] for k in ('observation_count', 'earliest', 'latest', 'months', 'backfilled_count')})
    meta['price_history']['files'] = files
    meta_path.write_bytes(encode(meta))


def backfill(repo, ref, public, report):
    report.mkdir(parents=True, exist_ok=True)
    tip = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', ref], text=True).strip()
    commits = subprocess.check_output(['git', '-C', str(repo), 'log', '--reverse',
        '--format=%H %cI', tip, '--', 'public/goods.json'], text=True).splitlines()
    history = public / 'price-history'
    history.mkdir(parents=True, exist_ok=True)
    index_path = history / 'index.json'
    old = json.loads(index_path.read_bytes()) if index_path.exists() else {}
    stats = Counter()
    with tempfile.TemporaryDirectory(prefix='goodsdex-history-') as tmp, \
            (report / 'conflicts.jsonl').open('wb') as conflicts:
        db = sqlite3.connect(str(Path(tmp) / 'events.sqlite'))
        db.execute('CREATE TABLE events (gid TEXT, at TEXT, month TEXT, payload TEXT, priority INT, PRIMARY KEY(gid,at))')
        db.execute('CREATE INDEX events_time ON events(month,at)')

        def add(event, existing=False):
            if existing:
                event.setdefault('time_source', 'fetched_at')
            event = flag_suspicious(event)
            stamp = instant(event['at'])
            at = stamp.isoformat()
            month = stamp.astimezone(CST).strftime('%Y-%m')
            priority = int(event.get('time_source', 'fetched_at' if existing else 'commit') == 'fetched_at')
            previous = db.execute('SELECT payload,priority FROM events WHERE gid=? AND at=?', (event['gid'], at)).fetchone()
            if previous:
                before = json.loads(previous[0])
                if any(before.get(k) != event.get(k) for k in ('price', 'missing_status', 'raw_price') if k != 'raw_price' or 'raw_price' in before):
                    stats['conflicts'] += 1
                    conflicts.write(encode(dict(gid=event['gid'], at=at, retained=event if priority > previous[1] else before,
                                                rejected=before if priority > previous[1] else event)))
                if priority <= previous[1]:
                    stats['duplicates'] += 1
                    return
                stats['replaced_commit_time'] += 1
            db.execute('INSERT OR REPLACE INTO events VALUES (?,?,?,?,?)',
                       (event['gid'], at, month, json.dumps(event, ensure_ascii=False), priority))

        for descriptor in old.get('files', []) + old.get('archived_files', []):
            path = public / descriptor['path']
            if digest(path) != descriptor['sha256']:
                raise ValueError(f'History digest mismatch: {path}')
            count = 0
            with gzip.open(path, 'rt') as fp:
                for line in fp:
                    add(json.loads(line), existing=True)
                    count += 1
            if count != descriptor['count']:
                raise ValueError(f'History count mismatch: {path}')
            stats['existing'] += count
        for i, commit in enumerate(commits, 1):
            sha, at = commit.split(' ', 1)
            proc = subprocess.Popen(['git', '-C', str(repo), 'show', f'{sha}:public/goods.json'], stdout=subprocess.PIPE)
            try:
                with io.TextIOWrapper(proc.stdout, encoding='utf-8') as fp:
                    for row in stream_array(fp):
                        add(recover(row, sha, at))
                        stats['snapshot_rows'] += 1
            finally:
                if proc.poll() is None:
                    proc.terminate() if sys.exc_info()[0] else None
                code = proc.wait()
            if code:
                raise RuntimeError(f'git show failed: {sha}')
            db.commit()
            if i % 20 == 0 or i == len(commits):
                print(f'{i}/{len(commits)} snapshots; {stats["snapshot_rows"]} rows', flush=True)

        # Legacy importer supports snapshots. Merge per identity/time, including
        # keys missing from an existing timestamp (never skip a whole timestamp).
        legacy_missing = 0
        months = [r[0] for r in db.execute('SELECT DISTINCT month FROM events ORDER BY month')]
        for month in months:
            path = public / 'prices' / f'{month}.jsonl'
            # Disk staging keeps snapshots bounded by one timestamp.
            db.execute('CREATE TABLE IF NOT EXISTS legacy (at TEXT PRIMARY KEY, payload TEXT)')
            db.execute('DELETE FROM legacy')
            if path.exists():
                with path.open() as fp:
                    for line in fp:
                        snap = json.loads(line)
                        at = instant(snap['fetched_at']).isoformat()
                        previous = db.execute('SELECT payload FROM legacy WHERE at=?', (at,)).fetchone()
                        if previous:
                            prior = json.loads(previous[0])
                            prior['prices'].update(snap['prices'])
                            snap = prior
                        db.execute('INSERT OR REPLACE INTO legacy VALUES (?,?)', (at, json.dumps(snap)))
            for (at,) in db.execute('SELECT DISTINCT at FROM events WHERE month=? ORDER BY at', (month,)).fetchall():
                previous = db.execute('SELECT payload FROM legacy WHERE at=?', (at,)).fetchone()
                snap = json.loads(previous[0]) if previous else dict(fetched_at=at, prices={})
                for (payload,) in db.execute('SELECT payload FROM events WHERE at=? AND month=?', (at, month)):
                    event = json.loads(payload)
                    if event['gid'] not in snap['prices']:
                        snap['prices'][event['gid']] = dict(price=event['price'], missing_status=event['missing_status'])
                        legacy_missing += 1
                db.execute('INSERT OR REPLACE INTO legacy VALUES (?,?)', (at, json.dumps(snap)))
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.with_suffix('.tmp').open('wb') as fp:
                for (payload,) in db.execute('SELECT payload FROM legacy ORDER BY at'):
                    fp.write(encode(json.loads(payload)))
            path.with_suffix('.tmp').replace(path)

        cutoff = datetime.now(timezone.utc) - timedelta(days=old.get('retention_days', 90))
        files, archived = [], []
        for month in months:
            name = f'{month}.jsonl.gz'
            path = history / name
            count, start, end = 0, None, None
            with path.with_suffix('.tmp').open('wb') as raw, gzip.GzipFile(fileobj=raw, mode='wb', filename='', mtime=0) as fp:
                for (payload,) in db.execute('SELECT payload FROM events WHERE month=? ORDER BY at,gid', (month,)):
                    event = json.loads(payload)
                    fp.write(encode(event))
                    count += 1
                    start = start or event['at']
                    end = event['at']
            path.with_suffix('.tmp').replace(path)
            descriptor = dict(month=month, path=f'price-history/{name}', sha256=digest(path),
                              count=count, bytes=path.stat().st_size, start=start, end=end, backfilled=True)
            (files if instant(end) >= cutoff else archived).append(descriptor)
        counts = Counter(r[0] for r in db.execute('SELECT count(*) FROM events GROUP BY gid'))
        summary = dict(observation_count=sum(n * k for n, k in counts.items()), gid_count=sum(counts.values()),
                       observations_per_gid=dict(sorted(counts.items())), gids_with_at_least_3=sum(v for k, v in counts.items() if k >= 3))
        summary.update(earliest=json.loads(db.execute('SELECT payload FROM events ORDER BY at LIMIT 1').fetchone()[0])['at'],
                       latest=json.loads(db.execute('SELECT payload FROM events ORDER BY at DESC LIMIT 1').fetchone()[0])['at'])
        suspicious = 0
        backfilled = 0
        sources = Counter()
        with (report / 'suspicious.jsonl').open('wb') as fp:
            for (payload,) in db.execute('SELECT payload FROM events ORDER BY at,gid'):
                event = json.loads(payload)
                sources[event.get('time_source', 'existing_fetched_at')] += 1
                backfilled += bool(event.get('backfilled'))
                if event.get('suspicious'):
                    suspicious += 1
                    fp.write(encode(event))
        revision = json.loads((public / 'meta.json').read_bytes())['revision']
        index = dict(old, schema=1, revision=revision, backfill_completed=True, backfilled=True, backfilled_count=backfilled,
                     files=files, archived_files=archived, months=len(months), detail_cutoff=cutoff.isoformat(),
                     git_backfill=dict(ref=ref, tip=tip, commit_count=len(commits), first_commit=commits[0], last_commit=commits[-1]),
                     **{k:summary[k] for k in ('observation_count', 'earliest', 'latest')})
        index_path.write_bytes(encode(index))
        update_meta(public, index)
        # Choose changing, well-covered series first, deterministically.
        first_day = instant(commits[0].split(' ', 1)[1]).date().isoformat()
        last_day = instant(commits[-1].split(' ', 1)[1]).date().isoformat()
        selected = db.execute("SELECT gid FROM events GROUP BY gid HAVING count(*)>=3 AND min(at)<? AND max(at)>=? ORDER BY count(DISTINCT json_extract(payload,'$.price')) DESC,count(*) DESC,gid LIMIT 10",
                              (first_day + 'T23:59:59+00:00', last_day)).fetchall()
        with (report / 'sequences.md').open('w') as fp:
            fp.write('# 十个 gid 的完整序列（CNY；null 表示缺价或隔离）\n\n')
            for (gid,) in selected:
                fp.write(f'## {gid}\n\n|时间|价格|原始异常价|时间来源|\n|---|---:|---:|---|\n')
                for (payload,) in db.execute('SELECT payload FROM events WHERE gid=? ORDER BY at', (gid,)):
                    event = json.loads(payload)
                    fp.write(f"|{event['at']}|{event['price']}|{event.get('raw_price') if event.get('suspicious') else ''}|{event.get('time_source', 'existing_fetched_at')}|\n")
                if gid != selected[-1][0]:
                    fp.write('\n')
        result = dict(**summary, **stats, suspicious_count=suspicious, time_sources=dict(sources), legacy_added=legacy_missing,
                      git_backfill=index['git_backfill'], index_sha256=digest(index_path), sample_gids=[r[0] for r in selected])
        (report / 'statistics.json').write_bytes(encode(result))
        db.close()
        return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    parser.add_argument('--ref', default='origin/data')
    parser.add_argument('--public', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(backfill(args.repo, args.ref, args.public, args.report), ensure_ascii=False, indent=2))
