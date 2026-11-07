"""Confirmed removal stays a full published row; transport failures fail closed."""
from copy import deepcopy
import json
import threading
import time

import pytest

from goodsdex.delisted import (ARCHIVE_NAME, URL, apply_archive, confirm_delisted,
                              prepare)
from goodsdex.publish import build
from goodsdex.release_policy import assert_no_lost_ids
from goodsdex.supplements import merge

NOW = '2026-11-07T12:00:00+08:00'
IDS = [f'CN:mi_cn:product:{pid}' for pid in (20905, 21697, 21698, 22580, 22581)]


def row(key):
    return dict(id=key, name='历史完整商品', price=199, source='mi_cn',
                params={'型号': '保留原型号'}, image='https://example.com/product.jpg')


def removed(key, timeout):
    assert timeout == 10
    return dict(code=400480502, message='该产品已下架')


@pytest.mark.parametrize('scenario', ['delisted', 'available', 'timeout', '500', '429'])
def test_only_explicit_delisting_marks(scenario):
    calls = []

    def fetch(key, timeout):
        calls.append((key, timeout))
        if scenario == 'timeout':
            raise TimeoutError('timed out')
        if scenario == 'delisted':
            return removed(key, timeout)
        return dict(code={'available': 0, '500': 500, '429': 429}[scenario], message='ok')

    previous = [row(IDS[0])]
    baseline = deepcopy(previous)
    archive, report = prepare(previous, [], {}, fetch, NOW)
    result = apply_archive([], archive)
    assert previous == baseline
    if scenario == 'delisted':
        assert len(result) == 1
        assert result[0]['on_sale'] is False
        assert result[0]['delisted_at'] == '2026-11-07'
        assert result[0]['delisted_evidence'] == dict(code=400480502,
                message='该产品已下架', probed_at=NOW, url=URL)
        assert all(result[0][key] == value for key, value in previous[0].items())
        assert_no_lost_ids(previous, result)
    else:
        if scenario == 'available':
            # Listed upstream but absent from this round's crawl: keep the full
            # row, flagged as carried, so the gate is not tripped by a miss.
            assert len(result) == 1
            assert result[0]['carry_reason'] == 'crawl_missed_but_listed'
            assert result[0]['carried_forward_at'] == NOW
            assert result[0]['on_sale'] is True
            assert all(result[0][key] == value for key, value in previous[0].items())
            assert report['counts'] == dict(confirmed=0, unknown=0, revived=0, carried=1)
            assert len(report['carried']) == 1
            assert_no_lost_ids(previous, result)
        else:
            assert result == []
            assert report['counts'] == dict(confirmed=0, unknown=1, revived=0, carried=0)
            assert report['unknown'][IDS[0]]['reason']
            with pytest.raises(ValueError, match='Publication would drop'):
                assert_no_lost_ids(previous, result)
    assert len(calls) == (1 if scenario in ('available', 'delisted') else 2)


def test_crawl_miss_on_listed_item_is_carried_and_flagged():
    miss, lost = 'CN:mi_cn:product:20545', 'CN:mi_cn:product:20071'
    previous = [row(key) for key in IDS + [miss, lost]]

    def fetch(key, timeout):
        if key == lost:
            raise TimeoutError('probe failed')
        return dict(code=0, message='ok') if key == miss else removed(key, timeout)

    archive, report = prepare(previous, [], {}, fetch, NOW)
    result = apply_archive([], archive)
    assert report['counts'] == dict(confirmed=5, unknown=1, revived=0, carried=1)
    carried = [r for r in result if r['id'] == miss]
    assert carried and carried[0]['carry_reason'] == 'crawl_missed_but_listed'
    assert carried[0]['carried_forward_at'] == NOW and carried[0]['on_sale'] is True
    # The carried row is still a full record, so the gate passes for it; the id
    # whose liveness could not be confirmed still fails the gate.
    current = [row('CN:mi_cn:product:20833')] + result
    rows, _ = merge(current, [], previous[:-1], apply_backfills=False)
    assert {r['id'] for r in rows} >= set(IDS) | {miss}
    with pytest.raises(ValueError, match=lost):
        merge(current, [], previous, apply_backfills=False)


def test_wholesale_crawl_miss_refuses_to_carry():
    previous = [row(f'CN:mi_cn:product:{9000 + i}') for i in range(80)]

    def fetch(key, timeout):
        return dict(code=0, message='ok')

    with pytest.raises(ValueError, match='Too many listed-but-missed'):
        prepare(previous, [], {}, fetch, NOW)


def test_revival_and_unknown_preserve_previous_delisting():
    previous = [row(IDS[0])]
    archive, _ = prepare(previous, [], {}, removed, NOW)
    delisted = apply_archive([], archive)

    def timeout(*args, **kwargs):
        raise TimeoutError('network')

    unchanged, report = prepare(delisted, previous, archive, timeout, NOW)
    assert apply_archive(previous, unchanged) == delisted
    assert report['counts']['revived'] == 0
    recovered, report = prepare(delisted, previous, unchanged,
                               lambda *a, **kw: dict(code=0, message='ok'), NOW)
    result = apply_archive(previous, recovered)
    assert result[0]['on_sale'] is True
    assert not any(k.startswith('delisted_') for k in result[0])
    assert report['counts']['revived'] == 1
    assert apply_archive(result, recovered) == result
    # Successful detail response without a newly collected full row cannot
    # manufacture a restored product or remove its archive.
    waiting, report = prepare(delisted, [], archive,
                             lambda *a, **kw: dict(code=0, message='ok'), NOW)
    assert apply_archive([], waiting) == delisted
    assert report['counts']['revived'] == 0


def test_message_confirmation_retry_and_identity_scope():
    attempts = []

    def fetch(key, timeout):
        attempts.append(key)
        if len(attempts) == 1:
            raise TimeoutError()
        return dict(code=123, message='该商品已下架')

    unknown = {}
    found = confirm_delisted([IDS[0], 'CN:other:product:20905'], fetch, NOW, unknown=unknown)
    assert set(found) == {IDS[0]}
    assert len(attempts) == 2
    assert unknown['CN:other:product:20905']['reason'] == 'unsupported_identity'
    assert not confirm_delisted(IDS, lambda *a, **k: dict(code=0, message='已下架'), NOW)


def test_concurrency_is_capped():
    lock = threading.Lock()
    active = peak = 0

    def fetch(key, timeout):
        nonlocal active, peak
        with lock:
            active += 1
            peak = max(peak, active)
        time.sleep(.01)
        with lock:
            active -= 1
        return removed(key, timeout)

    assert len(confirm_delisted(IDS * 2, fetch, NOW, workers=100)) == 5
    assert 1 < peak <= 4


def test_build_reads_archive_before_gate(tmp_path, monkeypatch):
    """Collector archive -> ci publication -> real build/publish no-loss gate."""
    from goodsdex import backfill
    monkeypatch.setattr(backfill, 'apply_default', lambda rows: (rows, {}))
    previous = [row(key) for key in IDS]
    archive, _ = prepare(previous, [], {}, removed, NOW)
    cats = tmp_path / 'categories'
    cats.mkdir()
    (cats / 'current.json').write_text(json.dumps([{
        'product': dict(product_id='CN:mi_cn:product:20833', name='在售对照'),
        'view': {'values': {'price': 100}},
    }]))
    public = tmp_path / 'public'
    (public / 'archive').mkdir(parents=True)
    import subprocess
    import sys
    from pathlib import Path
    source_archive = tmp_path / 'source-archive'
    source_archive.mkdir()
    (source_archive / ARCHIVE_NAME).write_text(json.dumps(archive))
    subprocess.run([sys.executable, str(Path(__file__).resolve().parents[1] /
                    'scripts/ci_publish_archive.py'), '--archive', str(source_archive),
                    '--out', str(public / 'archive')], check=True, capture_output=True)
    (public / 'goods.json').write_text(json.dumps(previous))
    supplements = tmp_path / 'supplements.json'
    supplements.write_text('[]')
    build(cats, public, supplements)
    result = json.loads((public / 'goods.json').read_text())
    assert {r['id'] for r in result} >= set(IDS)
    assert all(r['on_sale'] is False for r in result if r['id'] in IDS)


def test_http_errors_never_confirm_even_with_delisting_body(monkeypatch):
    from urllib.error import HTTPError
    from goodsdex import delisted
    calls = []

    def fail(request, timeout):
        calls.append(timeout)
        raise HTTPError(URL, 500, '该产品已下架', {}, None)

    monkeypatch.setattr(delisted.urllib.request, 'urlopen', fail)
    unknown = {}
    assert confirm_delisted([IDS[0]], now=NOW, unknown=unknown) == {}
    assert calls == [10, 10]
    assert 'HTTPError' in unknown[IDS[0]]['reason']


def test_stale_revival_evidence_does_not_override_later_unknown():
    previous = [row(IDS[0])]
    archive, _ = prepare(previous, [], {}, removed, NOW)
    retired = apply_archive([], archive)
    revived, _ = prepare(retired, previous, archive,
                         lambda *a, **kw: dict(code=0, message='ok'), NOW)
    available = apply_archive(previous, revived)
    archive, report = prepare(available, [], revived,
                             lambda *a, **kw: dict(code=500, message='error'), NOW)
    assert not archive['items']
    assert not apply_archive([], archive)
    with pytest.raises(ValueError):
        assert_no_lost_ids(available, apply_archive([], archive))


def test_successful_collection_projects_on_sale():
    from goodsdex.publish import to_public
    record = dict(product=dict(product_id=IDS[0], name='商品'),
                  captures=[dict(source='mi_cn_mobile', status='success')])
    assert to_public(record)['on_sale'] is True
    record['captures'][0]['status'] = 'transport_error'
    assert 'on_sale' not in to_public(record)


def test_confirmed_delisting_keeps_full_row_over_failed_capture_shell():
    previous = [row(IDS[0])]
    archive, _ = prepare(previous, [], {}, removed, NOW)
    expected = apply_archive([], archive)
    assert apply_archive([dict(id=IDS[0], name=None, params={})], archive) == expected
    # Losing the collector-side file must not erase previously published evidence.
    archive, report = prepare(expected, [], {},
                             lambda *a, **kw: dict(code=500), NOW)
    assert report['counts']['unknown'] == 1
    assert apply_archive([], archive) == expected


def test_unverified_archive_cannot_carry_an_id():
    for evidence in (dict(code=500), dict(code=400480502),
                     dict(code=400480502, probed_at=NOW, url='https://example.com')):
        archive = dict(items={IDS[0]: dict(row=row(IDS[0]), state='delisted', evidence=evidence)})
        assert apply_archive([], archive) == []


def test_apply_archive_tolerates_rows_without_identity():
    """Category snapshots can carry auxiliary rows with no id; annotating must skip them."""
    archive, _ = prepare([row(IDS[0])], [], {}, removed, NOW)
    rows = [{'name': '辅助行，无 id'}, {'id': None, 'name': '空 id'}, 'raw-string', row(IDS[0])]
    out = apply_archive(rows, archive)
    assert out[0] == rows[0] and out[1] == rows[1] and out[2] == 'raw-string'
    assert out[3]['on_sale'] is False and out[3]['delisted_at'] == '2026-11-07'
