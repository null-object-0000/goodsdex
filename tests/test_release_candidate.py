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


def observed_variant(identity, stamp, price=100, **values):
    """The real Apple snapshot shape, including the selected capture links."""
    values = dict(price=price, **values)
    capture = f'{identity}-{stamp}-{price}'
    return dict(product=dict(variant_id=identity, source='apple_cn',
                             price_fetched_at=stamp, price_status='provided'),
                fetched_at=stamp,
                captures=[dict(capture_id=capture, status='success', fetched_at=stamp)],
                assertions=[dict(assertion_id=f'{capture}-{key}', capture_id=capture,
                                 attribute=key, normalized_value=value)
                            for key, value in values.items()],
                view=dict(values=values, selected_from={key: f'{capture}-{key}'
                                                       for key in values}))


def test_category_merges_variants_and_keeps_newest_price_with_its_evidence(tmp_path):
    old = observed_variant('airpods', '2026-11-08T00:00:00Z')
    crawl = observed_variant('airpods', '2026-11-08T01:00:00Z', 101,
                             specs_table={'battery': '6 hours'})
    hourly = observed_variant('airpods', '2026-11-08T02:00:00Z', 102)
    # Hourly price refresh retained the old spec selection, rather than fetching specs.
    latest_only = observed_variant('new-hourly-SKU', '2026-11-08T02:00:00Z')
    crawl_only = observed_variant('new-crawl-SKU', '2026-11-08T01:00:00Z')
    path = tmp_path / 'data/categories/Apple_airpods.json'
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps([hourly, latest_only]))
    candidate = bundle(tmp_path, {path.relative_to(tmp_path).as_posix(): (
        json.dumps([old]).encode(), json.dumps([crawl, crawl_only]).encode())})
    merge_candidate(tmp_path, candidate)
    result = json.loads(path.read_text())
    assert [r['product']['variant_id'] for r in result] == ['airpods', 'new-hourly-SKU', 'new-crawl-SKU']
    merged = result[0]
    assert merged['view']['values'] == dict(price=102, specs_table={'battery': '6 hours'})
    assert merged['view']['selected_from']['price'] == hourly['view']['selected_from']['price']
    assert merged['product']['price_fetched_at'] == hourly['product']['price_fetched_at']
    assert merged['fetched_at'] == hourly['fetched_at']
    assert {c['capture_id'] for c in merged['captures']} >= {
        crawl['captures'][0]['capture_id'], hourly['captures'][0]['capture_id']}
    # Publish-only retries must not duplicate evidence or change the result.
    merge_candidate(tmp_path, candidate)
    assert json.loads(path.read_text()) == result


def test_category_selects_candidate_if_its_observation_is_newer():
    from release_candidate import merge_category
    old = observed_variant('airpods', '2026-11-08T00:00:00Z')
    crawl = observed_variant('airpods', '2026-11-08T10:00:00+08:00', 102)
    hourly = observed_variant('airpods', '2026-11-08T01:00:00Z', 101)
    result = merge_category([old], [crawl], [hourly], 'data/categories/Apple_airpods.json')[0]
    assert result['view']['values']['price'] == 102
    assert result['product']['price_fetched_at'] == crawl['product']['price_fetched_at']


@pytest.mark.parametrize('stamp', ['not-a-date', '2026-11-08T02:00:00', '2026-11-08T01:00:00Z'])
def test_category_rejects_unordered_or_simultaneous_contradictory_prices(stamp):
    from release_candidate import merge_category
    old = observed_variant('airpods', '2026-11-08T00:00:00Z')
    crawl = observed_variant('airpods', '2026-11-08T01:00:00Z', 101)
    hourly = observed_variant('airpods', stamp, 102)
    with pytest.raises(ValueError, match='Concurrent change'):
        merge_category([old], [crawl], [hourly], 'data/categories/Apple_airpods.json')


def test_category_rejects_duplicate_variant_ids():
    from release_candidate import merge_category
    old = observed_variant('airpods', '2026-11-08T00:00:00Z')
    crawl = observed_variant('airpods', '2026-11-08T01:00:00Z')
    hourly = observed_variant('airpods', '2026-11-08T02:00:00Z')
    with pytest.raises(ValueError, match='Ambiguous category identity'):
        merge_category([old], [crawl, crawl], [hourly], 'data/categories/Apple_airpods.json')


def test_category_rejects_rewritten_capture_before_any_file_is_written(tmp_path):
    old = observed_variant('airpods', '2026-11-08T00:00:00Z')
    crawl = observed_variant('airpods', '2026-11-08T01:00:00Z')
    hourly = copy.deepcopy(crawl)
    hourly['captures'][0]['response_hash'] = 'contradictory content under same capture ID'
    path = tmp_path / 'data/categories/Apple_airpods.json'
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps([hourly]))
    original = path.read_bytes()
    candidate = bundle(tmp_path, {
        'data/categories/new.json': (None, b'[]'),
        path.relative_to(tmp_path).as_posix(): (json.dumps([old]).encode(), json.dumps([crawl]).encode())})
    with pytest.raises(ValueError, match='Conflicting immutable evidence'):
        merge_candidate(tmp_path, candidate)
    assert not (path.parent / 'new.json').exists()
    assert path.read_bytes() == original


def test_category_unknown_list_shape_still_fails_closed():
    from release_candidate import merge_category
    with pytest.raises(ValueError, match='Ambiguous category identity'):
        merge_category([{'name': 'old'}], [{'name': 'crawl'}], [{'name': 'hourly'}],
                       'data/categories/unknown.json')


@pytest.mark.parametrize('name,field', [('data/hp/audit.json', 'fetched_at'),
                                       ('data/hp/collection-status.json', 'checked_at')])
@pytest.mark.parametrize('candidate_is_newer', [False, True])
def test_hp_reports_keep_one_complete_run_including_its_errors_and_images(tmp_path, name, field, candidate_is_newer):
    before = {field: '2026-11-08T00:00:00Z', 'images': [], 'error_count': 0}
    older = {field: '2026-11-08T01:00:00Z', 'images': [{'url': 'old', 'ok': True}],
             'requests': [{'url': 'a'}], 'error_count': 7}
    newer = {field: '2026-11-08T10:00:00+08:00', 'images': [{'url': 'new', 'ok': False}],
             'requests': [{'url': 'b'}], 'error_count': 1}
    after, latest = (newer, older) if candidate_is_newer else (older, newer)
    path = tmp_path / name
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(latest))
    candidate = bundle(tmp_path, {name: (json.dumps(before).encode(), json.dumps(after).encode())})
    merge_candidate(tmp_path, candidate)
    assert json.loads(path.read_text()) == newer
    merge_candidate(tmp_path, candidate)
    assert json.loads(path.read_text()) == newer


@pytest.mark.parametrize('stamp', ['invalid', '2026-11-08T01:00:00', '2026-11-08T01:00:00Z'])
def test_hp_report_conflicting_or_unordered_observations_still_fail(stamp):
    from release_candidate import merge_run_report
    with pytest.raises(ValueError, match='no unambiguous report order'):
        merge_run_report({'fetched_at': '2026-11-08T00:00:00Z'},
                         {'fetched_at': '2026-11-08T01:00:00Z', 'error_count': 1},
                         {'fetched_at': stamp, 'error_count': 2}, 'data/hp/audit.json')


def test_candidate_reads_logical_baselines_from_compressed_git_storage(tmp_path):
    import gzip
    import subprocess
    from release_candidate import pack
    before = {'public/goods.json': b'[{"id":"same","name":"old"}]\n',
              'data/categories/家电.json': b'[{"product":{"variant_id":"same","name":"old"}}]\n'}
    subprocess.run(['git', 'init', '-q', str(tmp_path)], check=True)
    for name, raw in before.items():
        path = tmp_path / (name + '.gz')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(gzip.compress(raw, mtime=0))
    subprocess.run(['git', '-C', str(tmp_path), 'add', '-A'], check=True)
    subprocess.run(['git', '-C', str(tmp_path), '-c', 'user.email=t@t', '-c', 'user.name=t',
                    'commit', '-qm', 'compressed baseline'], check=True)
    for name, raw in before.items():
        (tmp_path / name).write_bytes(raw.replace(b'old', b'new'))
    candidate = tmp_path / 'candidate.json'
    pack(tmp_path, 'all', candidate)
    files = json.loads(candidate.read_text())['files']
    assert set(files) == set(before)
    for name, raw in before.items():
        assert base64.b64decode(files[name]['before']) == raw
        assert base64.b64decode(files[name]['after']) == raw.replace(b'old', b'new')
        (tmp_path / name).write_bytes(raw)
    merge_candidate(tmp_path, candidate)
    for name, raw in before.items():
        assert json.loads((tmp_path / name).read_bytes()) == json.loads(raw.replace(b'old', b'new'))
    assert not allowed_path('data/categories/家电.json.gz')
