from copy import deepcopy

import pytest

from goodsdex.retirement import reconcile, counts


def test_three_brands_missing_pages_preserve_history_and_first_observation():
    previous = [dict(id=str(i), brand=brand, name='完整型号', params={'CPU': '旧配置'},
                     image='https://official.example/image.png', source_url='https://official.example/p')
                for i, brand in enumerate(['惠普', 'Apple', '小米'])]
    baseline = deepcopy(previous)
    observations = [dict(id=r['id'], state='missing', source_url=r['source_url'],
                         observed_at='2026-11-05T00:00:00Z', reason='http_410') for r in previous]
    rows = reconcile(previous, [], observations)
    assert len(rows) == 3
    for row, before in zip(rows, previous):
        assert {k: row[k] for k in before} == before
        assert row['status'] == 'retired'
        assert row['retired_at'] == '2026-11-05T00:00:00Z'
    assert reconcile(rows, [], [dict(o, observed_at='2026-11-06T00:00:00Z') for o in observations]) == rows
    assert counts(rows) == {'retired_count': 3, 'retired_by_brand': {'惠普': 1, 'Apple': 1, '小米': 1}}
    assert previous == baseline


@pytest.mark.parametrize('state', ['timeout', 'challenge', 'parse_error', 'unavailable'])
def test_errors_never_infer_retirement(state):
    previous = [dict(id='1', name='产品')]
    assert reconcile(previous, previous, [dict(id='1', state=state)]) == previous
    # Losing an unverified row stays visible to the publisher's no-lost-IDs gate.
    assert reconcile(previous, [], [dict(id='1', state=state)]) == []


def test_reappearance_requires_explicit_success_and_keeps_history():
    old = [dict(id='1', status='retired', retired_at='first', retirement_evidence={'reason': 'http_404'})]
    assert reconcile(old, [dict(id='1')])[0]['status'] == 'retired'
    row = reconcile(old, [dict(id='1')], [dict(id='1', state='available', observed_at='again')])[0]
    assert row['status'] == 'available'
    assert 'retired_at' not in row
    assert row['retirement_history'][0]['retired_at'] == 'first'


def test_missing_observation_requires_provenance():
    with pytest.raises(ValueError, match='requires'):
        reconcile([dict(id='1')], [], [dict(id='1', state='missing')])


def test_legacy_hp_delisting_migrates_original_timestamp():
    row = dict(id='1', sale_status='delisted', delisted_at='first',
               delisted_evidence={'reason': 'sku_redirected_to_catalogue'})
    result = reconcile([], [row])[0]
    assert result['retired_at'] == 'first'
    assert result['status'] == 'retired'
    assert result['retirement_evidence'] == row['delisted_evidence']


def test_complete_snapshot_retains_selected_brand_only():
    from goodsdex.retirement import completed_snapshot
    previous = [dict(id='hp', brand='惠普', source_url='https://www.hp.com/p'),
                dict(id='mi', brand='小米', source_url='https://www.mi.com/p')]
    rows = completed_snapshot(previous, [], brands={'惠普'}, observed_at='first',
                              snapshot_url='https://www.hp.com/catalogue')
    assert [r['id'] for r in rows] == ['hp']
    assert rows[0]['status'] == 'retired'
    assert rows[0]['source_url'] == previous[0]['source_url']


def test_completed_discovery_archive_drives_public_retirement(tmp_path):
    import json
    from goodsdex.archive import merge_archive
    from goodsdex.retirement import archive_observations
    previous = [dict(id='x', brand='小米', source_url='https://www.mi.com/p',
                     name='完整商品', image='https://www.mi.com/image.png', params={'容量': '256GB'})]
    records = [dict(product={'product_id': 'x', 'name': '完整商品'}, view={'values': {}})]
    archive = tmp_path / 'archive'
    merge_archive('手机', records, archive_dir=archive, now_iso='2026-11-01T00:00:00Z')
    merge_archive('手机', [], archive_dir=archive, now_iso='2026-11-02T00:00:00Z',
                  discovery={'completeness': 'partial', 'stop_reason': 'timeout'})
    assert archive_observations(tmp_path, previous) == []
    merge_archive('手机', [], archive_dir=archive, now_iso='2026-11-03T00:00:00Z',
                  discovery={'completeness': 'complete', 'stop_reason': 'empty_page',
                             'total_reported': 0, 'found': 0})
    observations = archive_observations(tmp_path, previous)
    rows = reconcile(previous, [], observations)
    assert rows[0]['retired_at'] == '2026-11-03T00:00:00Z'
    assert rows[0]['image'] == previous[0]['image']
    assert rows[0]['params'] == previous[0]['params']
    # A later partial discovery preserves the last complete missing event.
    merge_archive('手机', [], archive_dir=archive, now_iso='2026-11-04T00:00:00Z')
    assert archive_observations(tmp_path, previous) == observations


def test_retiring_duplicate_id_variants_retains_every_configuration():
    previous = [dict(id='shared', name='容量A', params={'容量': '128GB'}),
                dict(id='shared', name='容量B', params={'容量': '256GB'})]
    observation = dict(id='shared', state='missing', observed_at='first',
                       source_url='https://official.example/product', reason='http_410')
    rows = reconcile(previous, [], [observation])
    assert len(rows) == 2
    assert [r['params'] for r in rows] == [r['params'] for r in previous]
    assert all(r['status'] == 'retired' for r in rows)


def test_newer_sighting_in_another_category_prevents_false_retirement(tmp_path):
    import json
    from goodsdex.retirement import archive_observations
    archive = tmp_path/'archive'
    archive.mkdir()
    old = dict(id='x', source_url='https://official.example/product')
    (archive/'a.json').write_text(json.dumps({'items': {'x': {
        'missing_since': '2026-11-01T00:00:00Z', 'last_seen_at': '2026-10-31T00:00:00Z'}}}))
    (archive/'b.json').write_text(json.dumps({'items': {'x': {
        'last_seen_at': '2026-11-02T08:00:00+08:00'}}}))
    assert archive_observations(tmp_path, [old]) == []
    assert archive_observations(tmp_path, [dict(old, status='retired', retired_at='2026-11-03T00:00:00Z')]) == []
    # A fresh SKU observation also prevents replaying an older absence event.
    (archive/'b.json').unlink()
    assert archive_observations(tmp_path, [dict(old, fetched_at='2026-11-02T00:00:00Z')]) == []


def test_rebuild_consumes_fresh_complete_archive_before_lost_id_gate(tmp_path):
    import json, subprocess, sys
    from pathlib import Path
    from goodsdex.archive import merge_archive
    from goodsdex.publish import build
    public = tmp_path/'public'
    public.mkdir()
    cats = tmp_path/'categories'
    cats.mkdir()
    archive = tmp_path/'source-archive'
    previous = dict(id='test-retired-product', name='测试整机', brand='测试',
                    kind='machine', source='test_official', price=99,
                    image='https://official.example/photo.png',
                    source_url='https://official.example/product',
                    params={'容量': '1TB'}, fetched_at='2026-11-01T00:00:00Z')
    (public/'goods.json').write_text(json.dumps([previous]))
    extras = tmp_path/'extras.json'
    extras.write_text('[]')
    records = [dict(product={'product_id': previous['id'], 'name': previous['name']},
                    view={'values': {}})]
    merge_archive('测试', records, archive_dir=archive, now_iso='2026-11-01T00:00:00Z')
    merge_archive('测试', [], archive_dir=archive, now_iso='2026-11-05T00:00:00Z',
                  discovery={'completeness': 'complete', 'stop_reason': 'empty_page',
                             'total_reported': 0, 'found': 0})
    script = Path(__file__).resolve().parents[1]/'scripts/ci_publish_archive.py'
    subprocess.run([sys.executable, str(script), '--archive', str(archive),
                    '--out', str(public/'archive')], check=True, capture_output=True)
    meta = build(cats, public, extras)
    rows = json.loads((public/'goods.json').read_text())
    assert len(rows) == 1
    assert {k: rows[0][k] for k in previous} == previous
    assert rows[0]['status'] == 'retired'
    assert rows[0]['retired_at'] == '2026-11-05T00:00:00Z'
    assert meta['retired_count'] == 1
