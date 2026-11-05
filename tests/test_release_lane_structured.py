"""L6 negative identity, capture integrity, precedence and real interval boundaries."""
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import pytest
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import goodsdex.release_structured as l6
from goodsdex.release_coverage import usable
from release_lane_structured import sample_rows,Fetcher


def fixture(tmp_path,monkeypatch,site='zol',name='小米15S Pro',field='国内发布时间：2025年05月22日'):
    monkeypatch.setattr(l6,'ROOT',tmp_path)
    row=dict(id='CN:mi_cn:product:1',name=name,brand='小米')
    html=f'<html><title>{name}参数</title><h1>{name}</h1><table><tr><th>{field.split("：")[0]}</th><td>{field.split("：")[1]}</td></tr></table></html>'
    raw=html.encode();p=tmp_path/'capture.html.gz';p.write_bytes(gzip.compress(raw))
    page=l6.Page(html);f=l6.parse_field(page,site)
    entry=dict(id=row['id'],name=name,site=site,identity_sha256=l6.fingerprint(row),match_evidence=l6.identity_proof(row,page),field=f,evidence=dict(url='https://'+l6.SITES[site]+'/item/123.html',quote=f['quote'],sha256=hashlib.sha256(raw).hexdigest(),capture_file=p.name,encoding='utf-8',captured_at='2026-11-05T00:00:00Z',source_type='third_party'))
    return row,entry,dict(policy=l6.POLICY,entries=[entry])


def test_field_precision_and_baike_default_downgrade():
    for site in l6.SITES:
        f=l6.parse_field(l6.Page('<dl><dt>上市时间</dt><dd>2025年5月22日</dd></dl>'),site)
        assert f['date']==('2025-05' if site=='baike' else '2025-05-22')
        assert f['baike_downgraded']==(site=='baike')
    assert l6.parse_field(l6.Page('上市日期 2025年5月'), 'zol')['granularity']=='month'
    for text in ['上市日期 2025年','上市日期 发布时间 2025年5月22日', '上市日期 2025年2月30日']:
        f=l6.parse_field(l6.Page(text),'zol')
        if '发布时间' not in text:assert f is None


def test_exact_title_rejects_series_siblings_and_configurations():
    row=dict(id='CN:mi_cn:product:1',name='红米6')
    for title in ['红米6 Pro','红米6A','红米6系列','红米6X','红米6（4GB/64GB）']:
        assert l6.identity_proof(row,l6.Page('<title>'+title+'参数</title>红米6')) is None
    assert l6.identity_proof(row,l6.Page('<title>红米6参数</title><h1>红米6</h1>'))
    assert l6.identity(dict(id='CN:apple_cn:commodity:x',name='iPad')) is None


def test_replay_hash_and_identity_revalidated(tmp_path,monkeypatch):
    row,e,b=fixture(tmp_path,monkeypatch)
    r=l6.apply([row],b)[0];assert r['release']['date']=='2025-05-22' and usable(r['release'])
    assert l6.apply([r],b)==[r]
    bad=deepcopy(e);bad['evidence']['sha256']='0'*64
    with pytest.raises(ValueError,match='hash'):l6.check(bad,row)
    changed=dict(r,name='小米15S Pro Max');out=l6.apply([changed],b)[0]
    assert not out.get('release',{}).get('date')


@pytest.mark.parametrize('source',['official','official_hidden'])
def test_official_hidden_preserved(tmp_path,monkeypatch,source):
    row,e,b=fixture(tmp_path,monkeypatch);row['release']=dict(source=source,date='2000-01',display_allowed=False)
    out=l6.apply([row],b)[0];assert out['release']==row['release']
    assert out['release_structured_crosschecks']


def test_l5_conflict_clears_date_and_inheritance(tmp_path,monkeypatch):
    row,e,b=fixture(tmp_path,monkeypatch);row['release']=dict(source='third_party',policy='l5-first-report-v1',date='2024-01',granularity='month')
    row['release_inherited']=dict(date='2024-01');row['release_quote']='old'
    out=l6.apply([row],b)[0]
    assert out['release']['date'] is None and out['release_structured_review']
    assert 'release_inherited' not in out and 'release_quote' not in out
    assert l6.apply([out],b)==[out]
    assert not l6.conflict('2025-01-01','2025-02-15')
    assert l6.conflict('2025-01-01','2025-02-16')
    assert l6.conflict('2025-01','2025-03')


def test_precedence_alternates_and_baike_month(tmp_path,monkeypatch):
    row,e,b=fixture(tmp_path,monkeypatch)
    baike=deepcopy(e);baike['site']='baike';baike['evidence']['url']='https://baike.baidu.com/item/123';baike['field']=l6.parse_field(l6.Page(gzip.decompress((tmp_path/'capture.html.gz').read_bytes()).decode()),'baike')
    b['entries']=[baike,e];out=l6.apply([row],b)[0]
    assert out['release']['granularity']=='day' and out['release']['alternates'][0]['site']=='baike'
    assert out['release_cross_check']==baike['evidence']['url']
    b['entries']=[baike];out=l6.apply([row],b)[0]
    assert out['release']['date']=='2025-05' and out['release_precision']=='month'


def test_sample_is_deterministic_unique_and_stratified():
    rows=[dict(id=str(i),name='小米'+str(i),brand='小米' if i%2 else 'Apple') for i in range(400)]
    s=sample_rows(rows);assert len(s)==300 and len({r['id'] for r in s})==300
    assert s==sample_rows(list(reversed(rows)))
    assert {r['brand'] for r in s}=={'小米','Apple'}


def test_throttle_503_persists_ten_second_backoff_and_replay_uses_cache(tmp_path,monkeypatch):
    import release_lane_structured as collector
    from email.message import Message
    from urllib.error import HTTPError
    import io
    monkeypatch.setattr(collector,'ROOT',tmp_path)
    clock=[100.0];sleeps=[];calls=[]
    monkeypatch.setattr(collector.time,'time',lambda:clock[0])
    def sleep(seconds):sleeps.append(seconds);clock[0]+=seconds
    monkeypatch.setattr(collector.time,'sleep',sleep)
    class Opener:
        def open(self,request,timeout):
            calls.append(clock[0])
            return HTTPError(request.full_url,503,'unavailable',Message(),io.BytesIO(b'busy'))
    monkeypatch.setattr(collector.urllib.request,'build_opener',lambda *a:Opener())
    f=collector.Fetcher(tmp_path/'output')
    a=f.fetch('https://product.pconline.com.cn/mobile/123.html')
    assert a['reason']=='rate_limited'
    b=f.fetch('https://product.pconline.com.cn/mobile/456.html')
    assert calls[1]-calls[0]>=10
    assert f.fetch(a['url'])==a and len(calls)==2
    state=json.loads((tmp_path/'output/throttle/pconline.com.cn.json').read_text())
    assert state['interval']>=10


def test_stored_per_gid_checkpoint_resumes_without_requests(tmp_path,monkeypatch):
    import release_lane_structured as collector
    row=dict(id='CN:apple_cn:commodity:a',name='iPad',brand='Apple')
    monkeypatch.setattr(collector.Fetcher,'fetch',lambda *a:pytest.fail('checkpoint should not fetch'))
    first=collector.collect_site('zol',[row],tmp_path,False)
    second=collector.collect_site('zol',[row],tmp_path,False)
    assert first==second and first[0]['reason']=='ambiguous_model_or_configuration'


def test_regular_finalizer_priority_replay_keeps_l6_policy(tmp_path,monkeypatch):
    from goodsdex.release_coverage import apply_priority_dates
    row,e,b=fixture(tmp_path,monkeypatch)
    path=tmp_path/'bundle.json';path.write_text(json.dumps(b));monkeypatch.setattr(l6,'INPUT',path)
    first=apply_priority_dates([row]);second=apply_priority_dates(first)
    assert first==second
    assert first[0]['release']['policy']==l6.POLICY
    assert usable(first[0]['release'])


def test_title_only_cannot_prove_model_in_body():
    row=dict(id='CN:mi_cn:product:1',name='红米6')
    assert l6.identity_proof(row,l6.Page('<title>红米6参数</title><body>暂无资料</body>')) is None


def test_date_cannot_consume_next_numeric_field_or_narrative_mention():
    p=l6.Page('<dl>上市时间 2025年5月 22万元起售</dl>')
    f=l6.parse_field(p,'zol');assert f['date']=='2025-05' and f['granularity']=='month'
    assert l6.parse_field(l6.Page('这款产品上市时间2025年5月22日'),'zol') is None
    f=l6.parse_field(l6.Page('发布时间：2025-05-22'),'pconline');assert f['date']=='2025-05-22'
