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
    assert history['image'] == 'https://spend-good.oss-cn-shanghai.aliyuncs.com/goods/c1116b822a2e678c45d7316abf02e24ca6866c77.jpg'
    assert history['image_status'] == 'available'
    assert history['image_source'] == history['image_source_type'] == 'official_archive'
    assert history['image_source_url'].startswith('https://web.archive.org/web/20220401000000id_/')
    assert history['image_captured_at'] == '2022-04-01'
    assert history['image_note'] == '2022 年官网首页预售 banner 图，时光灰；非当前在售款'
    assert history['image_scope'] == 'series'
    assert history['detail_images'] == [{'url': 'https://spend-good.oss-cn-shanghai.aliyuncs.com/goods/c1116b822a2e678c45d7316abf02e24ca6866c77.jpg', 'kind': 'exterior', 'width': 1920, 'height': 974}, {'url': 'https://spend-good.oss-cn-shanghai.aliyuncs.com/goods/c7aeef0c9fc9519fd1f05794500d73d1e4f3df83.jpg', 'kind': 'interior', 'width': 1920, 'height': 785}, {'url': 'https://spend-good.oss-cn-shanghai.aliyuncs.com/goods/b890768eee82d3bd1ecf0a2e564c2d70d61c0f3f.jpg', 'kind': 'interior', 'width': 1667, 'height': 806}]
    assert len(history['trims']) == 5
    assert all(t['image'] == history['image'] and t['image_scope'] == 'series' and t['image_source'] == 'official_archive' and t['range_std'] == 'NEDC' for t in history['trims'])
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
    row=deepcopy(raw[0]);row['model_year']='unknown'
    with pytest.raises(ValueError, match='model_year'): migrate([row])


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
    assert row['image_status']=='available'
    assert row['image_source']=='official_archive'
    assert row['image_source_url'].startswith('https://web.archive.org/')
    assert row['image_scope']=='series'
    assert len(row['trims']) == 5
    assert 'source_record' not in row['trims'][0]
    detail = json.loads((tmp_path/'detail/08.json').read_text())[row['id']]
    assert detail['detail_images'] == next(r for r in result if r['id'] == row['id'])['detail_images']
    assert len(detail['detail_images']) == 3


def test_existing_daily_and_history_publishers_do_not_reintroduce_configuration_rows():
    import sys
    sys.path.insert(0, str(ROOT/'scripts'))
    from publish_cars import prepare, prepare_history
    previous=migrate(sources())
    refreshed, _=prepare(previous)
    assert len(refreshed)==11
    assert len(mappings(refreshed))==48
    assert all(r['schema']=='car-product-v2' for r in refreshed)
    repeated, _=prepare_history(refreshed)
    assert repeated==refreshed


def test_history_without_image_still_has_unavailable_placeholder():
    raw = sources()
    for row in raw:
        if row.get('model_year') == 2022:
            row['image'] = None
    history = next(r for r in migrate(raw) if r['model_year'] == 2022)
    assert history['image'] is None and history['image_status'] == 'official_unavailable'
    assert all(t['image'] is None for t in history['trims'])


def test_archive_image_amendment_only_changes_exact_han_product_and_is_idempotent():
    import sys
    sys.path.insert(0, str(ROOT/'scripts'))
    from apply_han_archive_image import apply, TARGET, AMENDED
    rows = migrate(sources())
    old = deepcopy(rows)
    parent = next(r for r in old if r['id'] == TARGET)
    for trim in parent['trims']:
        trim['source_record'] = {k:v for k,v in trim['source_record'].items() if k not in AMENDED}
        trim['source_record']['image'] = None
    old_parent = migrate([t['source_record'] for t in parent['trims']])[0]
    old = [old_parent if r['id'] == TARGET else r for r in old]
    result = apply(old)
    assert sum(a != b for a,b in zip(old,result)) == 1
    assert [r for r in old if r['id'] != TARGET] == [r for r in result if r['id'] != TARGET]
    assert apply(result) == result
    damaged = deepcopy(old)
    next(r for r in damaged if r['id'] == TARGET)['trims'][0]['source_record']['price'] = 1
    with pytest.raises(ValueError, match='configuration evidence'):
        apply(damaged)


def test_finalized_category_projection_survives_canonical_migration():
    rows = migrate(sources())
    for product in rows:
        product['categories'] = [product['category']]
        for trim in product['trims']:
            trim['source_record']['categories'] = [trim['source_record']['category']]
    assert migrate(rows) == rows


def test_finalized_archive_product_survives_daily_and_history_publication():
    import sys
    sys.path.insert(0, str(ROOT/'scripts'))
    from publish_cars import prepare, prepare_history
    rows = migrate(sources())
    for product in rows:
        product['categories'] = [product['category']]
        for trim in product['trims']:
            trim['source_record']['categories'] = [trim['source_record']['category']]
    history = next(r for r in rows if r['model_year'] == 2022)
    daily, _ = prepare(rows)
    repeated, _ = prepare_history(daily)
    assert next(r for r in repeated if r['model_year'] == 2022) == history


def test_daily_round_trip_with_pcauto_supplements_never_splits_products():
    import sys
    sys.path.insert(0, str(ROOT/'scripts'))
    from publish_cars import prepare, prepare_history
    from goodsdex.supplements import DEFAULT_SUPPLEMENTS
    third_party = [r for r in json.loads(DEFAULT_SUPPLEMENTS.read_text())
                   if r.get('schema') == 'car-product-v2' and r.get('source') == 'pcauto']
    expected = migrate(sources()) + third_party
    raw = expand_sources(expected)
    grouped = migrate(raw)
    assert len(grouped) == len(expected) == 17
    assert len({r['id'] for r in grouped}) == 17
    assert_preserved(raw, grouped)
    refreshed, _ = prepare(expected, append_only=True)
    historical, _ = prepare_history(refreshed)
    assert {r['id']:r for r in historical} == {r['id']:r for r in expected}
    assert len(historical) == 17


def test_duplicate_product_or_trim_ids_are_release_errors():
    from goodsdex.car_structure import assert_unique_car_ids
    rows = migrate(sources())
    assert_unique_car_ids(rows)
    with pytest.raises(ValueError, match='Duplicate car product'):
        assert_unique_car_ids(rows + [deepcopy(rows[0])])
    rows[0]['trims'].append(deepcopy(rows[0]['trims'][0]))
    with pytest.raises(ValueError, match='Duplicate car trim'):
        assert_unique_car_ids(rows)
