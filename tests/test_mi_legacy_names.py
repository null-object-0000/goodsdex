import gzip
import hashlib
import json
from pathlib import Path
import pytest
from goodsdex.mi_legacy_names import apply_legacy_names, DEFAULT
from goodsdex.shards import build_shards

ROOT = Path(__file__).resolve().parents[1]

def targets():
    return json.loads((ROOT / 'docs/xiaomi-legacy-names-20261105/targets.json').read_text())

def test_all_twelve_evidence_and_identity_links_are_real():
    manifest = json.loads(DEFAULT.read_text())
    assert len(manifest['items']) == 12
    for item in manifest['items']:
        pid = item['id'].rsplit(':', 1)[-1]
        for e in [*item['name_evidence'], item['historical_price_evidence'], item['retirement_evidence']]:
            raw = gzip.decompress((ROOT / e['capture_file']).read_bytes())
            assert hashlib.sha256(raw).hexdigest() == e['sha256']
            if e.get('selector'):
                assert f'data-stat-productid="{pid}"' in raw.decode()
        assert str(item['historical_price']) in item['historical_price_evidence']['quote']
        assert '该产品已下架' in item['retirement_evidence']['quote']

def test_replay_preserves_ids_prices_dates_and_unrelated_records():
    before = targets() + [dict(id='CN:other:1', name='13.3" 未知机型', price=None)]
    result = apply_legacy_names(before)
    assert before == targets() + [dict(id='CN:other:1', name='13.3" 未知机型', price=None)]
    assert [r['id'] for r in result] == [r['id'] for r in before]
    assert result[-1] == before[-1]
    for row in result[:-1]:
        assert row['status'] == 'retired' and row['is_historical']
        assert row['price'] is None and row['price_missing']
        assert row['name'].startswith('小米')
        assert not row.get('release')
    assert apply_legacy_names(result) == result


def test_live_offer_supersedes_frozen_retired_reference():
    row = dict(targets()[0], status='available', discontinued=False, price=100)
    assert apply_legacy_names([row]) == [row]


def test_repair_rejects_cross_identity_and_unofficial_evidence():
    manifest = json.loads(DEFAULT.read_text())
    manifest['items'][0]['name_evidence'][0]['source_url'] = 'https://example.com/product'
    with pytest.raises(ValueError): apply_legacy_names(targets(), manifest)
    manifest = json.loads(DEFAULT.read_text())
    manifest['items'][0]['name_evidence'] = [e for e in manifest['items'][0]['name_evidence'] if not e.get('selector')]
    with pytest.raises(ValueError): apply_legacy_names(targets(), manifest)


def test_light_indexes_keep_retired_semantics(tmp_path):
    rows = apply_legacy_names(targets())
    (tmp_path/'goods.json').write_text(json.dumps(rows))
    build_shards(tmp_path)
    index = json.loads((tmp_path/'index/mi_cn.json').read_text())['items']
    assert len(index) == 12
    assert all(r['status'] == 'retired' and r['is_historical'] and r['price_missing'] for r in index)
    assert all('历史标价' in r['historical_price_note'] for r in index)
