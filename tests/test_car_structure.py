import json
from pathlib import Path
from copy import deepcopy
import pytest
from goodsdex.car_structure import migrate, mappings, expand_sources, assert_preserved
from goodsdex.cars import merge_cars
ROOT = Path(__file__).resolve().parents[1]


def sources():
    return json.loads((ROOT/'data/official/car-catalog.json').read_text())['rows'] + json.loads((ROOT/'data/car-history-20261029/byd-verified.json').read_text())


def test_every_configuration_and_non_car_object_survives_idempotent_migration():
    raw = sources()
    other = [{'id': 'CN:mi_cn:keep', 'params': {'untouched': [1, None]}}, {'id': 'CN:hp_cn:keep', 'opaque': True}]
    result = migrate(other + raw)
    assert_preserved(other + raw, result)
    assert result[:2] == other
    assert migrate(result) == result
    assert len(result) == 13
    assert len(mappings(result)) == 48
    assert {r['id']:r for r in expand_sources(result)[2:]} == {r['id']:r for r in raw}
    assert len({m['old_id'] for m in mappings(result)}) == 48


def test_year_provenance_and_no_image_substitution():
    result = migrate(sources())
    history = next(r for r in result if r['model_year'] == 2022)
    assert history['model_year_source'] == 'pcauto'
    assert history['model_year_confidence'] == 'third_party'
    assert history['image'] is None
    assert history['image_status'] == 'official_unavailable'
    assert len(history['trims']) == 5
    assert all(t['image'] is None and t['range_std'] == 'NEDC' for t in history['trims'])
    assert history['trims'][0]['name'] == '121KM 尊贵型'
    for r in result:
        assert r['model_year'] is None or isinstance(r['model_year'], int)
        assert all('DM-i' not in t['name'] for t in r['trims'])
        if r['brand'] == '小米汽车':
            assert r['model_year'] is None and r['image_scope'] == 'series'
    su7=next(r for r in result if r['series']=='SU7')
    assert su7['name']=='小米汽车 新一代 SU7'
    assert len(su7['trims']) == 3


def test_refresh_updates_only_reviewed_trims_and_preserves_historical_snapshot():
    raw=sources()
    previous=migrate(raw)
    incoming=deepcopy(raw[:43])
    incoming[0]['price'] += 100
    result=merge_cars(previous,incoming,raw[:43])
    expanded={r['id']:r for r in expand_sources(result)}
    assert expanded[raw[0]['id']]['price'] == incoming[0]['price']
    assert all(expanded[r['id']]==r for r in raw[43:])
    assert len(mappings(result)) == 48


def test_corrupted_migration_and_unreviewed_products_fail_closed():
    raw=sources()
    result=migrate(raw)
    result[0]['trims'].pop()
    with pytest.raises(ValueError): assert_preserved(raw,result)
    row=deepcopy(raw[0]);row['id']='CN:byd:car:goods-999:unknown:attr-1'
    with pytest.raises(ValueError): migrate([row])


def test_shards_retain_nested_search_and_image_metadata(tmp_path):
    from goodsdex.shards import build_shards
    import base64, gzip
    result=migrate(sources())
    (tmp_path/'goods.json').write_text(json.dumps(result))
    build_shards(tmp_path)
    data=json.loads((tmp_path/'index/byd.json').read_text())
    queries=json.loads(gzip.decompress(base64.b64decode(data['query_gzip'])))
    index=next(i for i,r in enumerate(data['items']) if r['model_year']==2022)
    assert '121KM' in queries[index]['search_text'].upper()
    row=data['items'][index]
    assert row['image_status']=='official_unavailable'
    assert len(row['trims']) == 5
    assert 'source_record' not in row['trims'][0]
