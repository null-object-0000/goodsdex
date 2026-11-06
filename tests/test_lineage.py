from copy import deepcopy
import pytest
from goodsdex.lineage import resolve, materialize, coverage


def source(name='ithome', value='2025-05-22', precision='day', captured='2026-11-06T02:14:00+08:00', **fields):
    return dict(source=name,role='secondary',kind='release_date',captured_at=captured,source_url='https://www.ithome.com/0/123/456.htm',fields=dict(release_date=value,precision=precision,quote='新品正式发布',**fields),evidence=dict(method='page_fetch',verified=True,http_status=200,confidence='high'))


def test_precision_official_whitelist_and_real_time():
    month=source('apple_newsroom','2025-05','month')
    day=source()
    assert resolve([month,day])[0]['release_date']['source']=='ithome'
    official=source('apple_newsroom')
    assert resolve([day,official])[0]['release_date']['source']=='apple_newsroom'
    other=source('tencent_news')
    assert resolve([other,day])[0]['release_date']['source']=='ithome'
    # Lexicographic ISO strings have different offsets; compare actual instants.
    earlier=source(captured='2026-11-05T19:00:00+00:00')
    later=source(captured='2026-11-06T02:30:00+08:00')
    assert resolve([earlier,later])[0]['release_date']['captured_at']==later['captured_at']


def test_conflicts_boundary_and_month_intervals():
    a=source(value='2025-01-01');b=source('tencent_news',value='2025-02-15')
    assert resolve([a,b])[0]['release_date']
    b['fields']['release_date']='2025-02-16'
    display,conflicts=resolve([a,b]);assert display['release_date'] is None
    assert conflicts[0]['pairs'][0]['gap_days']==46
    assert len(conflicts[0]['alternatives'])==2
    assert resolve([source(value='2025-01',precision='month'),source(value='2025-03-01')])[0]['release_date']


def test_retain_every_candidate_and_no_history_noise():
    row={'id':'p','sources':[source(),source('tencent_news')]}
    first=materialize(row,migrate=False)
    assert len(first['display']['release_date']['alternatives'])==1
    assert len(first['field_history'])==1
    second=materialize(first,migrate=False)
    assert second==first
    second['sources'].append(source('sina_tech',captured='2026-11-07T00:00:00+08:00'))
    third=materialize(second,first,migrate=False)
    assert len(third['field_history'])==1
    third['sources'].append(source('apple_newsroom','2024-01-01'))
    fourth=materialize(third,third,migrate=False)
    assert fourth['display']['release_date'] is None
    assert len(fourth['field_history'])==2
    assert fourth['field_history'][-1]['to']['value'] is None


def test_requires_registered_source_time_url_and_verified_llm():
    for key,value in [('source','random'),('source_url',''),('captured_at','2026-11-06')]:
        s=source();s[key]=value
        with pytest.raises(ValueError): resolve([s])
    s=source('llm_verified');s['evidence']['verified']=False
    with pytest.raises(ValueError):resolve([s])
    s=source('series_inherit')
    with pytest.raises(ValueError):resolve([s])


def test_field_policy_and_generic_extensibility():
    a=source('mi_store');a['fields']={'name':'官方名','price':999,'price_kind':'current','promo':True,'params.CPU':'A'}
    b=source('youpin');b['fields']={'name':'渠道名','price':899,'price_kind':'channel'}
    d,_=resolve([b,a]);assert d['name']['value']=='官方名';assert d['price']['value']==999
    assert d['price']['promo'] is True;assert d['params.CPU']['source']=='mi_store'
    for kind,accepted in [('scene',False),('promotional',False),('product_main',True),('device_icon',False)]:
        s=source('mi_store');s['fields']={'image':'https://image.example/a.png','image_kind':kind}
        assert bool(resolve([s])[0]['image'])==accepted
    s['fields'].update(width=168,height=168,is_product_main=False)
    assert resolve([s])[0]['image']['is_product_main'] is False


def test_legacy_independent_and_coverage_arithmetic():
    row={'id':'p','release':{'date':'2025-05','granularity':'month','source':'third_party','evidence':{'url':'https://www.ithome.com/0/1/1.htm','captured_at':'2026-11-06T00:00:00Z','quote':'发布','sha256':'abc'}}}
    original=deepcopy(row);r=materialize(row)
    assert row==original
    independent={k:v for k,v in r.items() if k not in ('release','lineage_policy')}
    assert materialize(independent,migrate=False)['display']==r['display']
    assert r['release']==row['release']
    c=coverage([r,materialize({'id':'none'})]);assert sum(c['groups'].values())==c['covered']==1
    assert c['total']==c['covered']+c['missing']==2


def test_bad_legacy_not_promoted_or_discarded():
    r=materialize({'id':'p','release_llm':{'source':'llm','date':'2025-05','granularity':'month','evidence':{'quote':'模型估计'}}})
    assert r['display']['release_date'] is None
    assert r['lineage_issues'][0]['assertion']['date']=='2025-05'


def test_collector_refresh_retains_prior_sources_and_history():
    old=materialize({'id':'p','sources':[source()]},migrate=False)
    fresh={'id':'p','sources':[source('tencent_news',value='2025-05-23')]}
    merged=materialize(fresh,old,migrate=False)
    assert len(merged['sources'])==2
    assert merged['display']['release_date']['source']=='ithome'
    assert merged['field_history']==old['field_history']
    a=source('mi_store');a['fields']={'name':'旧名字'}
    old=materialize({'id':'p','sources':[a]},migrate=False)
    b=deepcopy(a);b['fields']['name']='新名字';b['captured_at']='2026-11-07T02:14:00+08:00'
    new=materialize({'id':'p','sources':[b]},old,migrate=False)
    assert new['display']['name']['value']=='新名字'
    assert new['display']['name']['alternatives'][0]['value']=='旧名字'
    assert len(new['field_history'])==2


def test_series_checks_cannot_be_promoted_to_product_and_disabled_stays_disabled():
    e={'url':'https://www.ithome.com/a','captured_at':'2026-11-06T00:00:00Z','quote':'系列发布','sha256':'abc'}
    release={'date':'2025-05','granularity':'month','source':'third_party','series':'系列A','checks':[{'source':'official','date':'2025-05','evidence':e}],'evidence':e,'inherited':True}
    r=materialize({'id':'p','release_series':release})
    assert {s['source'] for s in r['sources']}=={'series_inherit'}
    release['display_allowed']=False
    r=materialize({'id':'p','release_series':release})
    assert r['display']['release_date'] is None


def test_envelopes_add_date_without_identity_columns_and_preserve_history():
    from goodsdex.product_sources import materialize as product, upsert_source
    base=dict(source='mi_store',captured_at='2026-11-06T00:00:00Z',source_url='https://www.mi.com/p',fields={'name':'设备','params':{'CPU':'A'}},evidence={'method':'api'})
    first=product({'id':'new'},observations=[base,source()])
    assert first['primary_source']=='mi_store'
    assert first['display']['release_date']['source']=='ithome'
    assert first['display']['params.CPU']['method']=='api'
    assert first['release_effective']['date']=='2025-05-22'
    assert product(first)==first
    second=upsert_source(first,source('tencent_news',value='2025-08-01') | {'source_url':'https://news.qq.com/a'})
    assert second['display']['release_date'] is None
    assert second['release_effective'] is None
    assert second['conflicts'][0]['pairs'][0]['gap_days']>45
    assert second['field_history'][-1]['to']['value'] is None
    from goodsdex.release_coverage import matrix
    assert matrix([second])['total']['covered']==0


def test_generic_field_refresh_has_full_value_chain_and_no_refresh_noise():
    from goodsdex.product_sources import materialize as product, upsert_source
    base=dict(source='mi_store',captured_at='2026-11-06T00:00:00Z',source_url='https://www.mi.com/p',fields={'name':'设备','params':{'CPU':'A'}},evidence={'method':'api'})
    first=product({'id':'new'},observations=[base]);fresh=deepcopy(base)
    fresh['captured_at']='2026-11-07T00:00:00Z';fresh['fields']['params']['CPU']='B'
    second=upsert_source(first,fresh)
    assert second['display']['params.CPU']['value']=='B'
    assert second['display']['params.CPU']['alternatives'][0]['value']=='A'
    assert len([h for h in second['field_history'] if h['field']=='params.CPU'])==2
    assert product(second)==second


def test_missing_legacy_time_never_becomes_adopted_time_and_new_capture_required():
    from goodsdex.product_sources import migrate_row, upsert_source
    row={'id':'old','name':'历史名','source_url':'https://www.mi.com/old'}
    result=migrate_row(row)
    assert result['display']['name'] is None
    assert result['sources'][0]['observations'][0]['captured_at'] is None
    assert result['lineage_issues']
    assert result['name']=='历史名'  # legacy compatibility; display remains unadopted
    obs=result['sources'][0]['observations'][0]
    with pytest.raises(ValueError,match='actual field capture time'): upsert_source(result,obs)


def test_unadopted_legacy_name_does_not_create_observations_on_republication():
    from goodsdex.product_sources import migrate_row
    first=migrate_row({'id':'car','name':'历史名称','source_url':'https://www.byd.com/car'})
    assert first['display']['name'] is None
    assert migrate_row(first)==first


def test_rejected_legacy_effective_assertion_stays_in_issues_on_refresh():
    from goodsdex.product_sources import migrate_row
    row={'id':'legacy','name':'设备','source_url':'https://www.mi.com/p','fetched_at':'2026-11-06T00:00:00Z','release_effective':{'date':'2025-01','source':'llm','evidence':{'quote':'历史模型无链接估计'}}}
    first=migrate_row(row)
    assert first['lineage_issues']
    assert migrate_row(first)==first


@pytest.mark.parametrize('url', ['', 'https://', 'https:///missing-host', 'file:///proof'])
def test_verified_llm_requires_a_complete_evidence_url_at_both_boundaries(url):
    from goodsdex.product_sources import upsert_source
    observation=source('llm_verified')
    observation['source_url']=url
    with pytest.raises(ValueError,match='evidence URL'):
        resolve([observation])
    with pytest.raises(ValueError,match='evidence URL'):
        upsert_source({'id':'p'},observation)
