from copy import deepcopy
import pytest
from goodsdex.product_sources import materialize, migrate_row, upsert_source, coverage


def obs(source='mihome_directory', **fields):
    hosts={'mihome_directory':'home.mi.com','mi_store':'www.mi.com','hp_support':'support.hp.com','youpin':'www.xiaomiyoupin.com'}
    return dict(source=source, captured_at='2026-11-06T00:00:00Z', source_url='https://'+hosts.get(source,'example.org')+'/product/1',
                fields=fields, evidence={'method':'page_fetch'})


def test_discovery_no_price_then_store_promotion_and_history():
    first=materialize({'id':'device'},observations=[obs(name='设备',model='vendor.device.a')])
    assert first['primary_source']==first['discovered_by']=='mihome_directory'
    assert first['price'] is None and first['price_missing']
    promoted=upsert_source(first,obs('mi_store',name='官方 商品',price=599))
    assert promoted['primary_source']=='mi_store'
    assert sum(s['role']=='primary' for s in promoted['sources'])==1
    assert promoted['source_history'][0]['from']=='mihome_directory'
    assert promoted['source_history'][0]['to']=='mi_store'
    assert promoted['discovered_by']=='mihome_directory'
    assert materialize(promoted)==promoted


def test_default_priority_display_independent_and_configurable():
    sources=[obs(name='目录名',category='加湿器',icon='device.png'),obs('hp_support',name='支持名'),obs('mi_store',name='商城名',category='家电',image='photo.png')]
    r=materialize({'id':'p'},observations=sources)
    assert r['primary_source']=='mi_store'
    assert r['name']=='商城名' and r['category']=='加湿器'
    assert r['display']['category']['source']=='mihome_directory'
    assert r['display']['image']['type']=='product_photo'
    configured=materialize(r,rules={'name':['mihome_directory']})
    assert configured['primary_source']=='mi_store' and configured['name']=='目录名'
    assert next(s for s in r['sources'] if s['source']=='mi_store')['fields']['category']=='家电'


def test_observations_remain_separate_and_latest_null_clears_price():
    a=obs('mi_store',name='产品',price=599);r=materialize({'id':'p'},observations=[a])
    b=obs('mi_store',price=None);b['captured_at']='2026-11-07T00:00:00Z'
    after=upsert_source(r,b)
    assert len(after['sources'])==1 and len(after['sources'][0]['observations'])==2
    assert after['name']=='产品' and after['price'] is None and after['price_missing']
    assert r['price']==599
    assert materialize(after)==after


def test_legacy_directory_never_becomes_store_and_no_icon_photo():
    legacy=dict(id='mihome:1',name='旧目录',source='mihome',source_url='https://home.mi.com/product/1',
                name_mihome='旧目录',mihome_model='brand.device.a',image_mihome={'url':'icon.png'},price=None)
    before=deepcopy(legacy);r=migrate_row(legacy)
    assert legacy==before and r['primary_source']=='mihome_directory'
    assert r['image'] is None and r['sources'][0]['fields']['icon']=='icon.png'
    assert r['sources'][0]['evidence']['capture_time_missing']
    assert set(legacy)<=set(r)


def test_evidence_and_media_cannot_supply_identity():
    for bad in [obs('mi_store',name='fake'),obs('media',name='reported')]:
        if bad['source']=='mi_store':bad['source_url']='https://example.org/product/1'
        with pytest.raises(ValueError):materialize({'id':'p'},observations=[bad])
    missing=obs(name='x');missing.pop('evidence')
    with pytest.raises(ValueError):upsert_source({'id':'p'},missing)


def test_refreshed_legacy_price_mirrors_latest_and_retains_evidence():
    first=migrate_row(dict(id='p',name='产品',price=599,source_url='https://www.mi.com/product/1',fetched_at='2026-11-06T00:00:00Z'))
    fresh=deepcopy(first);fresh.update(price=499,price_fetched_at='2026-11-07T00:00:00Z')
    second=migrate_row(fresh,first)
    assert second['price']==second['display']['price']['value']==499
    assert len(second['sources'][0]['observations'])==2
    assert coverage([first,second])['primary_only']==2
    assert migrate_row(second)==second


def test_snapshot_rollback_restores_exact_legacy_release(tmp_path):
    from scripts.migrate_product_sources import snapshot, restore
    public=tmp_path/'public';public.mkdir();(public/'detail').mkdir()
    (public/'goods.json').write_bytes(b'[{"id":"legacy","price":null}]\n')
    (public/'meta.json').write_bytes(b'{"schema":1}\n')
    (public/'detail/00.json').write_bytes(b'{}\n')
    before={p.relative_to(public):p.read_bytes() for p in public.rglob('*') if p.is_file()}
    backup=tmp_path/'backup.tar.gz';snapshot(public,backup)
    (public/'goods.json').write_bytes(b'[]');(public/'new.json').write_bytes(b'{}')
    restore(public,backup)
    assert before=={p.relative_to(public):p.read_bytes() for p in public.rglob('*') if p.is_file()}
    with pytest.raises(ValueError):snapshot(public,backup)


def test_collector_without_new_columns_uses_price_capture_time_and_preserves_discovery():
    old=migrate_row(dict(id='p',name='产品',price=599,source_url='https://www.mi.com/product/1',fetched_at='2026-11-05T00:00:00Z',price_fetched_at='2026-11-06T00:00:00Z'))
    raw=dict(id='p',name='产品',price=499,source_url='https://www.mi.com/product/1',fetched_at='2026-11-05T00:00:00Z',price_fetched_at='2026-11-07T00:00:00Z')
    new=migrate_row(raw,old)
    assert new['price']==499 and new['display']['price']['captured_at']=='2026-11-07T00:00:00Z'


def test_display_price_recomputes_comparison_eligibility():
    row=dict(id='car',price=None,price_kind='full',price_comparable=False)
    result=materialize(row,observations=[obs('mi_store',name='产品',price=599,price_kind='full')])
    from goodsdex.price_semantics import validate
    validate([result])
    assert result['price_comparable'] is True
    cleared=obs('mi_store',price=None,price_kind='full')
    cleared['captured_at']='2026-11-07T00:00:00Z'
    result=upsert_source(result,cleared)
    validate([result])
    assert result['price_comparable'] is False


def test_schema_migration_preserves_reviewed_exclusion_decisions(tmp_path, monkeypatch):
    import json
    from goodsdex.dedupe import finalize_public
    from goodsdex.exclusions import REASONS
    row=dict(id='CN:mi_cn:product:test',name='设备',price=None,price_kind='unknown',price_comparable=False,category='设备',params={},source_url='https://www.mi.com/product/test')
    (tmp_path/'goods.json').write_text(json.dumps([row]))
    excluded=dict(total=1,reasons={r:int(r=='manual') for r in REASONS},items=[dict(id='reviewed:1',name='已复核记录',excluded_reason='manual',matched_rule='manual',excluded_at='old',exclusion={'basis':'reviewed_id'})])
    (tmp_path/'goods-excluded.json').write_text(json.dumps(excluded))
    import goodsdex.exclusions
    def forbidden(*args,**kwargs): raise AssertionError('Schema migration reclassified exclusions')
    monkeypatch.setattr(goodsdex.exclusions,'build_excluded',forbidden)
    finalize_public(tmp_path,previous=[row],product_sources_only=True)
    after=json.loads((tmp_path/'goods-excluded.json').read_text())
    assert after['items'][0]['exclusion']==excluded['items'][0]['exclusion']
    assert after['items'][0]['excluded_reason']=='manual'
    assert json.loads((tmp_path/'meta.json').read_text())['total_all']==2


def test_new_capture_requires_standard_method_but_historical_method_is_retained():
    legacy=obs('mi_store',name='产品');legacy['evidence']['method']='legacy_capture'
    old=materialize({'id':'p'},observations=[legacy])
    assert old['display']['name']['method']=='legacy_capture'
    with pytest.raises(ValueError,match='page_fetch, api, manual or series_inherit'):
        upsert_source(old,legacy)
    legacy['evidence']['method']='api'
    legacy['captured_at']='2026-11-07T00:00:00Z'
    assert upsert_source(old,legacy)['display']['name']['method']=='api'
