from copy import deepcopy
import json
from pathlib import Path
import pytest
from goodsdex.earbuds_intake import apply_intake, DEFAULT
from goodsdex.product_sources import materialize, publisher
from goodsdex.price_semantics import comparable, validate


def manifest():
    return json.loads(DEFAULT.read_text())


def test_reviewed_cn_models_are_complete_unpriced_and_idempotent():
    old = [{'id': 'apple-a', 'brand': 'Apple', 'name': 'AirPods Max 2', 'price': 3999},
           {'id': 'apple-b', 'brand': 'Apple', 'name': 'AirPods Max 2', 'price': 3999}]
    before = deepcopy(old)
    result = apply_intake(old)
    assert old == before and result[:2] == before
    new = result[2:]
    assert len(new) == 23 and len({r['id'] for r in new}) == 23
    validate(new)
    for r in new:
        assert r['primary_source'] == r['discovered_by'] == 'earbuds_directory'
        assert r['model'] == r['id']
        assert r['name'] and r['image'].startswith('https://')
        assert r['display']['name']['source'] == r['display']['image']['source'] == 'earbuds_directory'
        assert r['price'] is None and r['price_missing'] == 'no_channel_price'
        assert r['display']['price']['missing'] == 'no_channel_price'
        assert not comparable(r) and not r.get('release_effective')
        assert sum(s['role'] == 'primary' for s in r['sources']) == 1
        assert materialize(r) == r
    assert apply_intake(result) == result
    assert apply_intake(old) == result  # fresh replay, including policy history timestamps


@pytest.mark.parametrize('change', ['region', 'host', 'model', 'price', 'date', 'duplicate'])
def test_unreviewed_inputs_fail_closed(change):
    m=manifest();r=m['items'][0]
    if change=='region':r['region']='DE'
    if change=='host':r['sources'][0]['source_url']=r['sources'][0]['source_url'].replace('cn.tws','sg.tws')
    if change=='model':r['sources'][0]['fields']['model']='miwear.headphone.foreign.g'
    if change=='price':r['price']=99
    if change=='date':r['release_date']='2026-11-06'
    if change=='duplicate':m['items'].append(deepcopy(r))
    with pytest.raises(ValueError):apply_intake([],m)


def test_secondary_channel_keeps_directory_primary_and_no_comparable_offer():
    r=manifest()['items'][0]
    r['sources'].append(dict(source='mi_store',role='secondary',kind='channel_listing',captured_at='2026-11-06T10:00:00+08:00',source_url='https://www.mi.com/shop/buy/detail?product_id=123',fields=dict(name='Official channel name',channel_price=399,price_kind='list',gid='456'),evidence=dict(method='api',verified=True)))
    r=apply_intake([],dict(schema=1,items=[r]))[0]
    assert r['primary_source']=='earbuds_directory'
    assert r['name']!='Official channel name'
    assert r['display']['channel_price']['value']==399
    assert r['price'] is None and not comparable(r)
    assert publisher('https://de.tws.wear.xiaomiwear.com/twswear/product/get_product_list') is None


def test_manifest_identity_and_images_are_from_frozen_cn_response():
    import hashlib
    import unicodedata
    doc=Path(__file__).resolve().parents[1]/'docs/earbuds-intake-20261106/evidence'
    raw=(doc/'http/response-product-list-prod-cn.json').read_bytes()
    catalog={e['model']:e for e in json.loads(raw)['result']['tw_product_list']}
    assert len(catalog)==39
    normalized=lambda s:' '.join(unicodedata.normalize('NFKC',s).split())
    for r in manifest()['items']:
        d=catalog[r['id']]
        assert r['name']==normalized(d['name'])
        assert r['image'] in [i['icon_url'] for i in d['icon_static']]
        assert r['sources'][0]['evidence']['sha256']==hashlib.sha256(raw).hexdigest()
