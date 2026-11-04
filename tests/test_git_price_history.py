import gzip
import io
import json
from pathlib import Path
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from backfill_price_history_from_git import backfill, recover, stream_array


@pytest.mark.parametrize('size', [1, 2, 17, 65536])
def test_stream_boundaries(size):
    class Bounded(io.StringIO):
        def read(self, n=-1):
            assert 0 < n <= 65536
            return super().read(n)
    rows = [{'id': '中文', 'params': {'text': 'a\\"b' * 100}}, {'price': 123}]
    assert list(stream_array(Bounded(json.dumps(rows, ensure_ascii=False)), size)) == rows
    assert list(stream_array(io.StringIO(' [ ] \n'), size)) == []
    for text in ('[{},]', '[{}', '[{}]x', '{}', '[{} {}]'):
        with pytest.raises(ValueError):
            list(stream_array(io.StringIO(text), size))


def test_times_and_suspicious():
    base = dict(id='CN:mi_cn:product:1', fetched_at='2026-10-27T08:00:00Z', price=12)
    event = recover(base, 'sha', '2026-11-04T00:00:00Z')
    assert event['at'] == '2026-10-27T16:00:00+08:00'
    assert event['time_source'] == 'fetched_at'
    assert recover(dict(base, fetched_at=None), 'sha', '2026-11-04T00:00:00Z')['time_source'] == 'commit'
    for price in (0, -1, 200000, 999999, 'nan', True, 'bad'):
        event = recover(dict(base, price=price), 'sha', '2026-11-04T00:00:00Z')
        assert event['suspicious'] and event['raw_price'] == price
        assert event['price'] is None and event['missing_status'] == 'no_price'
    assert 'suspicious' not in recover(dict(base, price=None), 'sha', base['fetched_at'])


def test_git_merge_keeps_live_observations_and_missing_legacy_keys(tmp_path):
    repo = tmp_path / 'repo'
    repo.mkdir()
    def git(*args):
        return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()
    git('init')
    git('config', 'user.email', 'test@example.com')
    git('config', 'user.name', 'Test')
    public = repo / 'public'
    public.mkdir()
    at = '2026-10-27T08:00:00+08:00'
    rows = [dict(id='CN:mi_cn:product:1', fetched_at=at, price=99),
            dict(id='CN:mi_cn:product:2', fetched_at=at, price=0)]
    for n in range(3):
        (public / 'goods.json').write_text(json.dumps(rows))
        git('add', '.')
        git('commit', '--allow-empty', '-m', str(n))
    (public / 'meta.json').write_text('{"revision":"live"}')
    history = public / 'price-history'
    history.mkdir()
    live = recover(dict(rows[0], price=88), 'live-sha', at)
    live.pop('backfilled')
    # A commit-time placeholder must lose to an actual fetched_at on the same key.
    placeholder = recover(dict(rows[1], price=77, fetched_at=None), 'placeholder', at)
    raw = gzip.compress(('\n'.join(map(json.dumps, [live, placeholder])) + '\n').encode())
    (history / '2026-10.jsonl.gz').write_bytes(raw)
    import hashlib
    (history / 'index.json').write_text(json.dumps(dict(revision='live', files=[dict(path='price-history/2026-10.jsonl.gz', sha256=hashlib.sha256(raw).hexdigest(), count=2)])))
    (public / 'prices').mkdir()
    legacy = public / 'prices/2026-10.jsonl'
    legacy.write_text(json.dumps(dict(fetched_at=at, prices={live['gid']: dict(price=88)})) + '\n')
    before = (public / 'goods.json').read_bytes()
    result = backfill(repo, 'HEAD', public, tmp_path / 'report')
    assert result['observation_count'] == 2
    assert result['replaced_commit_time'] == 1
    events = [json.loads(line) for line in gzip.open(history / '2026-10.jsonl.gz', 'rt')]
    assert events[0]['price'] == 88 and not events[0].get('backfilled')
    assert events[1]['suspicious'] and events[1]['raw_price'] == 0
    snap = json.loads(legacy.read_text())
    assert len(snap['prices']) == 2 and snap['prices'][live['gid']]['price'] == 88
    assert (public / 'goods.json').read_bytes() == before
    again = backfill(repo, 'HEAD', public, tmp_path / 'report2')
    assert again['observation_count'] == 2 and again['legacy_added'] == 0
