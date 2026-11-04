import gzip
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from goodsdex.price_history import observation, stage, finalize, encode
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from release_candidate import merge_candidate
import base64

NOW = datetime(2026, 11, 4, tzinfo=timezone.utc)


def row(price=99, at='2026-11-04T09:00:00+08:00'):
    return dict(id='CN:mi_cn:product:10000292', gid='10000292', fetched_at=at, price=price)


def setup(tmp_path, rows=None):
    public = tmp_path / 'public'
    public.mkdir()
    (public / 'goods.json').write_text(json.dumps(rows if rows is not None else [row()]))
    (public / 'meta.json').write_text('{}')
    return public


def read(public):
    index = json.loads((public / 'price-history/index.json').read_bytes())
    events = []
    for d in index['files'] + index['archived_files']:
        raw = (public / d['path']).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == d['sha256']
        lines = gzip.decompress(raw).splitlines()
        assert len(lines) == d['count']
        events += [json.loads(line) for line in lines]
    return index, events


def test_backfill_real_times_three_points_and_replay(tmp_path):
    public = setup(tmp_path)
    for at in ('2026-11-04T10:00:00+08:00', '2026-11-04T11:00:00+08:00'):
        stage(public, [observation(row(98, at))])
    stats = finalize(public, 'release-1', now=NOW)
    index, events = read(public)
    assert stats['added'] == 3 and stats['backfilled'] == 1
    assert [e['price'] for e in events] == [99, 98, 98]
    assert all(e['revision'] == index['revision'] == 'release-1' for e in events)
    assert events[0]['backfilled'] is True
    original = (public / index['files'][0]['path']).read_bytes()
    stage(public, [observation(row(98, '2026-11-04T02:00:00Z'))])
    assert finalize(public, 'release-2', now=NOW)['added'] == 0
    assert (public / index['files'][0]['path']).read_bytes() == original
    stage(public, [observation(row(97, '2026-11-04T02:00:00Z'))])
    with pytest.raises(ValueError, match='Conflicting'):
        finalize(public, 'release-3', now=NOW)


@pytest.mark.parametrize('price', [None, '', 0, '0', -1, 'NaN', False])
def test_missing_never_zero_or_skipped(tmp_path, price):
    public = setup(tmp_path, [row(price)])
    finalize(public, 'r', now=NOW)
    _, events = read(public)
    assert len(events) == 1
    assert events[0]['price'] is None and events[0]['missing_status'] == 'no_price'


def test_retained_price_is_not_a_new_quote():
    assert observation(dict(row(), price_status='stale'))['price'] is None
    assert observation(dict(row(), sale_status='delisted'))['missing_status'] == 'unavailable'
    with pytest.raises(ValueError, match='timezone'):
        observation(row(at='2026-11-04T00:00:00'))


def test_split_archive_and_digests(tmp_path):
    public = setup(tmp_path, [])
    stage(public, [observation(row(1, at)) for at in (
        '2026-06-01T00:00:00Z', '2026-11-01T00:00:00Z', '2026-11-16T00:00:00Z')])
    finalize(public, 'r', now=NOW, max_bytes=1)
    index, events = read(public)
    assert {d['path'] for d in index['files']} == {'price-history/2026-11-a.jsonl.gz', 'price-history/2026-11-b.jsonl.gz'}
    assert len(index['archived_files']) == 1 and len(events) == 3
    assert index['months'] == 2 and index['retention_days'] == 90
    assert index['observation_count'] == 3
    assert json.loads((public / 'meta.json').read_text())['price_history']['revision'] == 'r'


def test_concurrent_candidates_keep_every_gid_at_same_time(tmp_path):
    public = setup(tmp_path, [])
    events = [observation(dict(row(), id=f'CN:mi_cn:product:{n}')) for n in (1, 2)]
    raw = b''.join(encode(e) for e in events)
    path = tmp_path / 'candidate.json'
    path.write_text(json.dumps(dict(schema=1, scope='prices', base='r', files={
        'data/price-observations/run.jsonl': dict(before=None, after=base64.b64encode(raw).decode())})))
    merge_candidate(tmp_path, path)
    merge_candidate(tmp_path, path)
    finalize(public, 'r', now=NOW)
    assert len(read(public)[1]) == 2


def test_batch_absent_and_network_failure_are_distinct(monkeypatch):
    from goodsdex import prices
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self): return b'{"code":200,"data":{}}'
    monkeypatch.setattr(prices.urllib.request, 'urlopen', lambda *a, **k: Response())
    assert prices.fetch_prices(['1'])['1'] == dict(price=None, missing_status='no_price')
    def fail(*a, **k): raise TimeoutError('timeout')
    monkeypatch.setattr(prices.urllib.request, 'urlopen', fail)
    assert prices.fetch_prices(['1'])['1'] == dict(price=None, missing_status='unavailable')


def test_compatibility_projection_uses_actual_observation_times(tmp_path):
    public = setup(tmp_path)
    finalize(public, 'r', now=NOW)
    snapshots = [json.loads(line) for line in (public / 'prices/2026-11.jsonl').read_bytes().splitlines()]
    assert snapshots == [dict(fetched_at='2026-11-04T09:00:00+08:00', prices={row()['id']: dict(price=99, missing_status='ok')})]


def test_same_gid_same_time_conflict_is_rejected_before_persist(tmp_path):
    public = setup(tmp_path, [])
    stage(public, [observation(row(99)), observation(row(100))])
    with pytest.raises(ValueError, match='Conflicting'):
        finalize(public, 'r', now=NOW)
    assert not (public / 'price-history/index.json').exists()
    assert list((tmp_path / 'data/price-observations').glob('*.jsonl'))


def test_candidate_does_not_silently_drop_conflicting_duplicate(tmp_path):
    setup(tmp_path, [])
    raw = b''.join(encode(observation(row(price))) for price in (99, 100))
    candidate = tmp_path / 'candidate.json'
    candidate.write_text(json.dumps(dict(schema=1, scope='prices', base='r', files={
        'data/price-observations/run.jsonl': dict(before=None, after=base64.b64encode(raw).decode())})))
    with pytest.raises(ValueError, match='Conflicting candidate'):
        merge_candidate(tmp_path, candidate)
    assert not (tmp_path / 'data/price-observations/run.jsonl').exists()


def test_history_descriptors_do_not_extend_catalog_file_allowlist(tmp_path):
    from goodsdex.dedupe import finalize_public
    from goodsdex.shards import build_shards
    public = setup(tmp_path, [])
    finalize_public(public)
    revision = json.loads((public/'meta.json').read_text())['revision']
    stage(public, [observation(row())])
    finalize(public, revision, now=NOW)
    meta = build_shards(public)
    assert 'price-history/index.json' not in meta['files']
    assert not any(name.startswith('prices/') for name in meta['files'])
    assert meta['price_history']['files']['price-history/index.json']['count'] == 1
    assert 'prices/2026-11.jsonl' in meta['price_history']['files']


def test_shared_raw_gid_projects_every_canonical_identity(tmp_path, monkeypatch):
    from goodsdex import prices
    monkeypatch.setattr(prices, 'fetch_prices', lambda gids: {'1': {'price': 99}})
    prices.refresh(['1'], tmp_path, stamp='2026-11-04T09:00:00+08:00', identities={'1': ['CN:mi_cn:product:a', 'CN:mi_cn:product:b']})
    snapshot = json.loads((tmp_path/'prices/2026-11.jsonl').read_text())
    assert set(snapshot['prices']) == {'1', 'CN:mi_cn:product:a', 'CN:mi_cn:product:b'}
