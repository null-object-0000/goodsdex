"""Release extraction must fail closed when generation or date is unsupported."""
import importlib.util
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location('release_lane_xiaomi', Path(__file__).resolve().parents[1]/'scripts/release_lane_xiaomi.py')
lane = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lane)


def test_priority_scope_includes_old_computers_but_not_stickers():
    def row(name, category='旧款机型'):
        return dict(id='CN:mi_cn:product:1', name=name, category=category)
    assert lane.in_scope(row('15.6"游戏本 8代i7 16G 1060'))
    assert lane.in_scope(row('米家宠物空气净化器','空气净化器'))
    assert not lane.in_scope(row('米家智能宠物饮水机滤芯套装','宠物饮水机'))
    assert not lane.in_scope(row('小米笔记本定制贴纸','笔记本'))


def test_official_2021_release_cannot_date_2025_generation(tmp_path, monkeypatch):
    payload = tmp_path/'article.json'
    payload.write_text(json.dumps(dict(data=dict(content='RedmiBook Pro 11th Gen Intel Core H35. Official sales start from March 4th, 2021 via all Xiaomi official channels in Mainland China.'))))
    def fake_fetch(url, directory, refresh):
        return dict(url=url,status=200,reason='retrieved_requires_exact_model_event_review',
                    capture_file=str(payload),sha256='a'*64,captured_at='2026-11-05T00:00:00Z')
    monkeypatch.setattr(lane,'fetch',fake_fetch)
    rows=[dict(id='CN:mi_cn:product:20992',name='REDMI Book Pro 14 2025',category='笔记本',
               source_url='https://www.mi.com/shop/buy/detail?product_id=20992')]
    result=lane.run(rows,tmp_path/'out',live=False)
    assert result['candidates']==[]
    assert result['discoveries'][0]['date']=='2021-03-04'
    assert result['records'][0]['official_absence_confirmed'] is False
    assert result['observations'][0]['reason']=='no_verified_month_level_statement_for_exact_model'


def test_model_year_and_page_metadata_cannot_supply_month(tmp_path, monkeypatch):
    payload=tmp_path/'article.json'
    payload.write_text(json.dumps(dict(data=dict(add_time='1618827484',content='RedmiBook Pro announced in 2021.'))))
    monkeypatch.setattr(lane,'fetch',lambda url,directory,refresh:dict(url=url,status=200,
        reason='retrieved_requires_exact_model_event_review',capture_file=str(payload),sha256='b'*64,captured_at='2026-11-05T00:00:00Z'))
    rows=[dict(id='CN:mi_cn:product:1',name='REDMI Book Pro 2021',category='笔记本')]
    result=lane.run(rows,tmp_path/'out',live=False)
    assert not result['candidates']
    assert not result['discoveries']
    assert result['summary']==dict(total=1,hits=0,missing=1)


def test_full_catalogue_includes_nonpriority_and_rejects_third_party(tmp_path, monkeypatch):
    import hashlib
    raw = tmp_path/'launch.txt'
    raw.write_text('September 25, 2025 Xiaomi 17 launched in mainland China.')
    # run_all uses repository-relative evidence, including explicit absolute test paths.
    evidence = dict(url='https://www.mi.com/news/launch', source_type='official',
                    quote=raw.read_text(), sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),
                    captured_at='2026-11-05', capture_file=str(raw), locator='launch paragraph')
    entries = [dict(id='launch', product_name='Xiaomi 17', aliases=[], date='2025-09-25',
                    granularity='day', market='CN', event='announcement',
                    origin='official_newsroom', evidence=evidence)]
    import copy
    bad=copy.deepcopy(entries[0]);bad.update(id='bad', product_name='Xiaomi 18')
    bad['evidence'].update(url='https://www.ithome.com/news', source_type='third_party')
    entries.append(bad)
    rows=[dict(id='CN:mi_cn:product:1', name='Xiaomi 17', category='手机'),
          dict(id='CN:mi_cn:product:2', name='Xiaomi 18', category='手机'),
          dict(id='CN:mi_cn:product:3', name='Xiaomi 17 Pro', category='手机')]
    monkeypatch.setattr(lane,'capture_serial',lambda url,directory,live:dict(url=url,status=200))
    result=lane.run_all(rows,tmp_path/'out',live=False,entries=entries,enumerate_newsroom=False)
    assert result['summary']['processed']==3
    assert result['summary']['hits']==1
    assert result['candidates'][0]['release']['granularity']=='day'
    assert all(not r['official_absence_confirmed'] for r in result['records'])
    raw.write_text('Changed evidence')
    result=lane.run_all(rows,tmp_path/'out',live=False,entries=entries,enumerate_newsroom=False)
    assert result['summary']['hits']==0
    assert result['summary']['rejected_entries']=={'archived_hash_mismatch':1}


def test_serial_fetch_resumes_without_network_and_no_live_never_fetches(tmp_path,monkeypatch):
    monkeypatch.setattr(lane.requests,'get',lambda *a,**k: (_ for _ in ()).throw(AssertionError('network')))
    url='https://www.mi.com/news'
    assert lane.capture_serial(url,tmp_path,False)['reason']=='not_captured'
    key=lane.hashlib.sha256(url.encode()).hexdigest()[:20]
    (tmp_path/(key+'.json')).write_text(json.dumps(dict(url=url,status=200)))
    assert lane.capture_serial(url,tmp_path,True)['status']==200


def test_serial_requests_are_spaced_and_foreign_redirect_rejected(tmp_path, monkeypatch):
    now=[100.0]; starts=[]
    import time
    monkeypatch.setattr(time,'time',lambda:now[0])
    monkeypatch.setattr(time,'sleep',lambda delay:now.__setitem__(0,now[0]+delay))
    class Response:
        is_redirect=False
        status_code=200
        content=b'official body'
        url='https://www.mi.com/news'
    def get(*args,**kwargs):
        starts.append(now[0]);return Response()
    monkeypatch.setattr(lane.requests,'get',get)
    # Keep capture files within ROOT because production stores relative paths.
    monkeypatch.setattr(lane,'ROOT',tmp_path)
    lane.capture_serial('https://www.mi.com/a',tmp_path/'captures',True)
    lane.capture_serial('https://www.mi.com/b',tmp_path/'captures',True)
    assert starts[1]-starts[0]>=2.1-1e-9
    class Redirect:
        is_redirect=True
        headers={'Location':'https://www.ithome.com/date'}
    monkeypatch.setattr(lane.requests,'get',lambda *a,**k:Redirect())
    r=lane.capture_serial('https://www.mi.com/c',tmp_path/'captures',True)
    assert r['reason']=='transport_error' and 'outside official' in r['error']
