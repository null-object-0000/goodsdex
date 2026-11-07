"""Lost updates, independent brands, fail-closed conflicts, append-only history."""
import base64
import copy
import json
from pathlib import Path
import sys

import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from release_candidate import merge_goods, merge_candidate, allowed_path


def row(key, source, price):
    return dict(id=key, source=source, name=key, price=price, params={'cpu': 'kept'})


def test_stale_collectors_keep_other_brand_and_unrelated_fields():
    base = [row('mi', 'mi_cn', 100), row('hp', 'hp_cn', 200)]
    price = copy.deepcopy(base)
    price[0]['price'] = 101
    hp = copy.deepcopy(base)
    hp[1]['price'] = 201
    hp[0]['params']['cpu'] = 'newer daily crawl'
    result = merge_goods(base, price, hp, 'prices')
    assert result[0]['price'] == 101
    assert result[0]['params']['cpu'] == 'newer daily crawl'
    assert result[1] == hp[1]
    assert merge_goods(base, price, result, 'prices') == result # publish-only re-run


def test_same_field_conflict_never_rolls_back_new_price():
    base = [row('hp', 'hp_cn', 100)]
    candidate = [dict(base[0], price=101)]
    latest = [dict(base[0], price=102)]
    with pytest.raises(ValueError, match='Concurrent change'):
        merge_goods(base, candidate, latest, 'hp')
    assert latest[0]['price'] == 102


def test_collector_cannot_edit_other_brand_or_drop_ids():
    base = [row('hp', 'hp_cn', 100)]
    with pytest.raises(ValueError, match='another responsibility'):
        merge_goods(base, [dict(base[0], price=101)], base, 'apple')
    with pytest.raises(ValueError, match='drop'):
        merge_goods(base, [], base, 'hp')


def encode(value):
    return base64.b64encode(value).decode() if value is not None else None


def bundle(tmp_path, files):
    p = tmp_path / 'candidate.json'
    p.write_text(json.dumps(dict(schema=1, scope='prices', base='test', files={
        k: dict(before=encode(b), after=encode(a)) for k, (b, a) in files.items()})))
    return p


def test_append_observations_preserves_newer_published_history(tmp_path):
    p = tmp_path / 'public/prices/month.jsonl'
    p.parent.mkdir(parents=True)
    lines = [(json.dumps(dict(fetched_at=f'2026-10-31T{h}:00:00+08:00', prices={}))+'\n').encode() for h in ('01','02','03')]
    p.write_bytes(lines[0]+lines[2])
    c = bundle(tmp_path, {'public/prices/month.jsonl': (lines[0], lines[0]+lines[1])})
    merge_candidate(tmp_path, c)
    assert p.read_bytes() == lines[0]+lines[2]+lines[1]
    merge_candidate(tmp_path, c)
    assert p.read_bytes() == lines[0]+lines[2]+lines[1]


def test_invalid_delta_does_not_partially_write(tmp_path):
    p = tmp_path / 'data/categories/a.json'
    p.parent.mkdir(parents=True)
    p.write_text('{"value": 3}')
    c = bundle(tmp_path, {'data/categories/new.json': (None, b'[]'), 'data/categories/a.json': (b'{"value": 1}', b'{"value": 2}')})
    with pytest.raises(ValueError, match='Concurrent change'):
        merge_candidate(tmp_path, c)
    assert not (p.parent/'new.json').exists()
    assert json.loads(p.read_text()) == {'value': 3}


@pytest.mark.parametrize('name', ['../public/goods.json', '/public/goods.json', 'public/meta.json', 'public/index/hp_cn.json', 'public/detail/00.json', '.github/workflows/evil.yml'])
def test_candidate_never_contains_generated_shards_or_unsafe_paths(name):
    assert not allowed_path(name)


def test_apple_history_preserves_each_product_observation(tmp_path):
    p = tmp_path / 'public/prices/apple/month.jsonl'
    p.parent.mkdir(parents=True)
    events = [dict(id=key, fetched_at='2026-10-31T01:02:03Z', price=100) for key in ('a','b','c')]
    lines = [(json.dumps(e)+'\n').encode() for e in events]
    p.write_bytes(lines[0])
    c = bundle(tmp_path, {'public/prices/apple/month.jsonl': (lines[0], b''.join(lines))})
    merge_candidate(tmp_path, c)
    assert p.read_bytes() == b''.join(lines)
    merge_candidate(tmp_path, c)
    assert p.read_bytes() == b''.join(lines)


def test_shared_publication_does_not_replay_foreign_field_backfills(monkeypatch):
    from goodsdex import backfill, supplements
    base = [row('hp', 'hp_cn', 100), row('apple', 'apple_support', None)]
    monkeypatch.setattr(backfill, 'apply_default', lambda rows: (_ for _ in ()).throw(AssertionError('No global field replay during brand publication')))
    result, audit = supplements.merge(base, [], base, apply_backfills=False)
    assert result == base
    assert audit['count'] == len(base)
    result, audit = supplements.merge(base[:1], [], base, apply_backfills=False)
    assert result == base
    assert audit['carried_ids'] == ['apple']
    assert audit['carried_sources'] == ['apple_support']
    # Once the source is represented, losing another row must still fail.
    with pytest.raises(ValueError, match='drop'):
        supplements.merge(base, [], base + [row('apple2', 'apple_support', None)],
                          apply_backfills=False)


def test_other_brand_ambiguous_rows_keep_original_positions():
    base = [row('ambiguous', 'mi_cn', 100), row('hp', 'hp_cn', 200), row('ambiguous', 'mi_cn', 101)]
    candidate = copy.deepcopy(base)
    candidate[1]['price'] = 201
    assert merge_goods(base, candidate, base, 'hp') == candidate


def test_non_ascii_archive_name_is_allowed_and_unquoted(tmp_path):
    """Chinese category names (e.g. 'REDMI 系列.json') must survive the allowlist.

    git quotes non-ASCII paths by default ("data/archive/REDMI \\347\\263\\273..."),
    which used to fail the prefix check and abort the whole crawl run.
    """
    import subprocess
    from release_candidate import git
    assert allowed_path('data/archive/REDMI 系列.json')
    subprocess.run(['git', 'init', '-q', str(tmp_path)], check=True)
    (tmp_path / 'data' / 'archive').mkdir(parents=True)
    target = tmp_path / 'data' / 'archive' / 'REDMI 系列.json'
    target.write_text('[]', encoding='utf-8')
    subprocess.run(['git', '-C', str(tmp_path), 'add', '-f', '--', 'data/archive'], check=True)
    names = git(tmp_path, 'diff', '--cached', '--name-only').decode().splitlines()
    assert names == ['data/archive/REDMI 系列.json']
    assert all(allowed_path(n) for n in names)


def test_pack_skips_throttle_logs_instead_of_staging_them(tmp_path):
    """采集日志不能进候选包；旧实现先暂存再校验，导致整轮发布失败。"""
    import subprocess
    from release_candidate import pack
    root = tmp_path
    subprocess.run(['git', 'init', '-q', str(root)], check=True)
    (root / 'docs/release-coverage/L5/throttle').mkdir(parents=True)
    (root / 'docs/release-coverage/L5/throttle/requests.jsonl').write_text('{"a":1}\n', encoding='utf-8')
    (root / 'data/categories').mkdir(parents=True)
    (root / 'data/categories/phones.json').write_text('[]', encoding='utf-8')
    subprocess.run(['git', '-C', str(root), 'add', '-A'], check=True)
    subprocess.run(['git', '-C', str(root), '-c', 'user.email=t@t', '-c', 'user.name=t',
                    'commit', '-qm', 'init'], check=True)
    (root / 'docs/release-coverage/L5/throttle/requests.jsonl').write_text('{"a":2}\n', encoding='utf-8')
    out = tmp_path / 'cand.json'
    pack(root, 'release_dates', out)
    bundle = json.loads(out.read_text())
    assert not any(n.endswith('.jsonl') for n in bundle['files'])


def test_timestamp_only_conflict_does_not_force_a_rerun():
    """并发发布只改了 updated_at 时，取最新即可，不必整轮重采。"""
    from release_candidate import merge_value
    before = {'id': 'x', 'price': 1, 'updated_at': '2026-11-01'}
    after = {'id': 'x', 'price': 2, 'updated_at': '2026-11-07T00:00:00'}
    latest = {'id': 'x', 'price': 1, 'updated_at': '2026-11-07T01:00:00'}
    out = merge_value(before, after, latest, 'data/archive/x.json')
    assert out['price'] == 2
    assert out['updated_at'] == '2026-11-07T01:00:00'


def test_last_seen_at_conflict_does_not_force_a_rerun():
    """Apple 目录用 last_seen_at 记「最后一次看到」，它和 updated_at 一样不是数据。"""
    from release_candidate import merge_value
    before = {'id': 'x', 'price': 1, 'last_seen_at': '2026-11-06T00:00:00'}
    after = {'id': 'x', 'price': 2, 'last_seen_at': '2026-11-07T00:00:00'}
    latest = {'id': 'x', 'price': 1, 'last_seen_at': '2026-11-07T01:00:00'}
    out = merge_value(before, after, latest, 'data/archive/Apple_airpods.json')
    assert out['price'] == 2
    assert out['last_seen_at'] == '2026-11-07T01:00:00'


def test_real_field_conflict_still_fails():
    """真正改了数据字段（价格）时仍然要报，不能顺手放过。"""
    import pytest
    from release_candidate import merge_value
    before = {'id': 'x', 'price': 1}
    after = {'id': 'x', 'price': 2}
    latest = {'id': 'x', 'price': 3}
    with pytest.raises(ValueError, match='Concurrent change'):
        merge_value(before, after, latest, 'data/archive/x.json')


def test_times_seen_counter_merges_to_the_larger_value():
    """times_seen 是观测次数，两条采集线各记各的，取较大值而不是报冲突。"""
    from release_candidate import merge_value
    before = {'id': 'x', 'price': 1, 'times_seen': 12}
    after = {'id': 'x', 'price': 2, 'times_seen': 13}
    latest = {'id': 'x', 'price': 1, 'times_seen': 15}
    out = merge_value(before, after, latest, 'data/archive/Apple_airpods.json.items.CN:apple_cn:commodity:MKFW4CH/A')
    assert out['price'] == 2
    assert out['times_seen'] == 15


def test_counter_field_cannot_swallow_a_real_price_change():
    """计数器放行不等于整行放行：价格变了仍然要报。"""
    import pytest
    from release_candidate import merge_value
    before = {'id': 'x', 'price': 1, 'times_seen': 12}
    after = {'id': 'x', 'price': 2, 'times_seen': 13}
    latest = {'id': 'x', 'price': 3, 'times_seen': 15}
    with pytest.raises(ValueError, match='Concurrent change'):
        merge_value(before, after, latest, 'data/archive/Apple_airpods.json')
