"""L5 adversarial policy and replay, distinct from legacy two-source policy."""
from copy import deepcopy
from datetime import date,timedelta
import hashlib,json
from pathlib import Path
import pytest
from goodsdex.release_media import check,decide,apply,POLICY,protected,publisher,INPUT
from goodsdex.release_coverage import usable,matrix

ROOT=Path(__file__).resolve().parents[1]

def fixture():
    e=deepcopy(json.loads((ROOT/'data/third-party/l5-reviewed.json').read_text())['entries'][0])
    rows=json.loads((ROOT/'tests/fixtures/release/l5-identities.json').read_text())
    row=next(r for r in rows if r['id']==e['id'])
    row={k:v for k,v in row.items() if not k.startswith('release')}
    return e,row


def test_single_first_report_is_month_with_explicit_media_provenance():
    e,row=fixture();check(e,row)
    out=apply([row],dict(lane='L5',policy=POLICY,entries=[e]))
    r=out[0]['release']
    assert r['source']=='third_party' and r['granularity']=='month' and len(r['date'])==7
    assert r['confidence']=='medium' and usable(r)
    assert out[0]['release_evidence']==e['assertion']['evidence']['url']
    assert apply(out,dict(lane='L5',policy=POLICY,entries=[e]))==out
    m=matrix(out)['total']; assert m['third_party']==1 and m['official']==0


@pytest.mark.parametrize('source',['official','official_hidden'])
@pytest.mark.parametrize('display',[True,False])
def test_official_even_hidden_or_internal_is_never_overwritten(source,display):
    e,row=fixture();old=dict(source=source,date='2001-01',display_allowed=display)
    row['release']=deepcopy(old)
    out=apply([row],dict(lane='L5',policy=POLICY,entries=[e]))[0]
    assert out['release']==old and out['release_media_crosschecks']==[e]


@pytest.mark.parametrize('domain',['https://item.jd.com/1.html','https://mp.weixin.qq.com/s/x','https://baijiahao.baidu.com/x','https://forum.ithome.com/x','https://ithome.com.evil.test/x'])
def test_rejects_retail_and_selfmedia_domains(domain):
    if 'forum.ithome' in domain:
        # Subdomains must be restricted below; publisher is not a broad suffix allowlist.
        assert not publisher(domain)
    else: assert not publisher(domain)


def test_crosscheck_sites_never_supply_a_primary():
    e,_=fixture();e['assertion']['evidence']['url']='https://detail.zol.com.cn/x'
    assert decide([e])['status']=='crosscheck_only'


@pytest.mark.parametrize('days,status',[(45,'accepted'),(46,'conflict'),(90,'conflict')])
def test_real_calendar_day_conflict_threshold_and_order(days,status):
    e,_=fixture();a=e['assertion'];a.update(date='2024-01-31',granularity='day',reported_at='2024-01-31')
    b=deepcopy(e);b['assertion'].update(date=(date(2024,1,31)+timedelta(days=days)).isoformat(),reported_at='2024-05-01')
    b['assertion']['evidence']['url']='https://finance.sina.com.cn/tech/x.shtml'
    result=decide([b,e]);assert result['status']==status
    if status=='accepted':assert result['release']['date']=='2024-01-31'


def test_month_bounds_do_not_invent_a_first_day():
    e,_=fixture();a=e['assertion'];a.update(date='2024-01',granularity='month',reported_at='2024-01-31')
    b=deepcopy(e);b['assertion'].update(date='2024-03',reported_at='2024-03-01')
    result=decide([b,e]);assert result['status']=='uncertain_interval'
    assert result['delta_days_min']==30 and result['delta_days_max']==90


def test_quote_identity_hash_day_and_series_fail_closed():
    e,row=fixture()
    for mutate in [lambda v:v.update(identity_kind='series'),
                   lambda v:v.update(identity_terms=['型号不存在']),
                   lambda v:v['assertion']['evidence'].update(quote='虚构原文'),
                   lambda v:v['assertion']['evidence'].update(sha256='0'*64),
                   lambda v:v['assertion'].update(date=v['assertion']['date']+'-01',granularity='day')]:
        c=deepcopy(e);mutate(c)
        with pytest.raises(ValueError):check(c,row)
    changed=dict(row,name=row['name']+' Max')
    with pytest.raises(ValueError):check(e,changed)


def test_frozen_entries_are_exact_captured_and_every_brand_is_accounted():
    from release_lane_media import run
    rows=json.loads((ROOT/'tests/fixtures/release/l5-identities.json').read_text())
    entries=json.loads((ROOT/'data/third-party/l5-reviewed.json').read_text())['entries']
    for e in entries:
        for r in rows:
            if r['id']==e['id']:check(e,r)
    for host in ['zol.com.cn','pconline.com.cn','cnmo.com']:
        assert not publisher('https://'+host+'/1')
        assert publisher('https://'+host+'/1',primary=False)


def test_explicit_product_event_day_is_accepted_but_publication_day_alone_is_not(tmp_path,monkeypatch):
    import goodsdex.release_media as media
    e,row=fixture()
    sentence=row['name']+'于10月29日发布'
    body='2024/10/29 记者报道：'+sentence+'。'
    raw=('<html><body>'+body+'</body></html>').encode()
    (tmp_path/'article.html').write_bytes(raw);monkeypatch.setattr(media,'ROOT',tmp_path)
    a=e['assertion'];a.update(date='2024-10-29',granularity='day',reported_at='2024-10-29')
    a['evidence'].update(capture_file='article.html',sha256=hashlib.sha256(raw).hexdigest(),quote=body,identity_quote=body,explicit_event_quote=sentence,encoding='utf-8')
    check(e,row);r=apply([row],dict(lane='L5',policy=POLICY,entries=[e]))[0]['release']
    assert r['date']=='2024-10-29' and r['granularity']=='day' and r['confidence']=='high'
    a['evidence'].pop('explicit_event_quote')
    with pytest.raises(ValueError,match='explicit month/day'):check(e,row)


def test_stale_identity_does_not_leak_an_old_l5_date():
    e,row=fixture();out=apply([row],dict(lane='L5',policy=POLICY,entries=[e]))[0]
    out['name']+=' 另一代'
    out=apply([out],dict(lane='L5',policy=POLICY,entries=[e]))[0]
    assert 'release' not in out and 'release_source' not in out
    assert out['release_media_skipped']['reason']=='Exact catalogue identity changed'
