from copy import deepcopy
import json
from goodsdex.xiaomi_covers import apply_covers, record_cover, SOURCE
from goodsdex.publish import to_public
from goodsdex.sources import mi_cn

PID = 'CN:mi_cn:product:20833'
URL = 'https://cdn.cnbj1.fds.api.mi-img.com/main.png'

def test_only_exact_xiaomi_id_changes_and_all_other_fields_survive():
    rows = [dict(id=PID, image='poster', price=199, release='2024-12-01', params={'a':1}),
            dict(id='CN:mi_cn:product:21630', image='other'),
            dict(id='CN:apple_cn:commodity:A', image='apple')]
    before = deepcopy(rows)
    obs = {PID:dict(image=URL,captured_at='2026-11-06T13:00:00Z',width=800,height=800),
           'CN:apple_cn:commodity:A':dict(image=URL)}
    after = apply_covers(rows, obs)
    assert rows == before and after[1:] == before[1:]
    assert after[0]['image'] == URL and after[0]['price'] == 199
    assert after[0]['release'] == before[0]['release'] and after[0]['params'] == before[0]['params']
    assert apply_covers(after,obs) == after


def test_unavailable_retains_exact_existing_image_never_borrows_other_model():
    rows=[dict(id=PID,image='original'),dict(id='CN:mi_cn:product:21630',image=None)]
    after=apply_covers(rows,{PID:dict(image=None),rows[1]['id']:dict(image=None)})
    assert after[0]['image']=='original' and after[1]['image'] is None
    assert all(r['image_status']=='official_unavailable' for r in after)


def test_collector_assertion_wins_over_resolved_poster_and_frozen_evidence():
    rec=dict(product=dict(product_id=PID,name='商品'),view=dict(values=dict(img_url='poster',price=199)),
             fetched_at='2026-11-06T14:00:00Z',assertions=[dict(source=SOURCE,attribute='official_main_image',subject_id='20833',raw_value=URL,capture_id='cap')])
    row=to_public(rec)
    assert row['image']==URL and row['price']==199
    assert 'official_main_image' not in row['params']
    assert apply_covers([row],{PID:dict(image='https://example.org/old.png',captured_at='2026-11-06T13:00:00Z')})==[row]
    rec['assertions'][0]['raw_value']=None
    row=to_public(rec)
    assert row['image']=='poster' and row['image_status']=='official_unavailable'
    assert apply_covers([row],{PID:dict(image=URL,captured_at='2026-11-06T13:00:00Z')})==[row]


def test_cover_request_uses_verified_channel_and_preserves_request_evidence(monkeypatch):
    class Response:
        status=200
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def read(self):return json.dumps(dict(code=0,data=dict(goodsInfo=dict(goodsList=[dict(imgUrl=URL)])))).encode()
    def open_request(req,timeout):
        assert json.loads(req.data)==[{},dict(productId=20833)]
        assert req.get_header('Content-type')=='application/x-www-form-urlencoded'
        assert req.get_header('X-user-agent')=='mi-shop'
        return Response()
    monkeypatch.setattr(mi_cn.urllib.request,'urlopen',open_request)
    caps, assertions=mi_cn.fetch_cover('20833')
    assert assertions[0].raw_value==URL and caps[0].response_raw
    assert json.loads(caps[0].request_body)[1]['productId']==20833
    def fail(*args,**kwargs):raise TimeoutError('offline')
    monkeypatch.setattr(mi_cn.urllib.request,'urlopen',fail)
    caps, assertions=mi_cn.fetch_cover('20833')
    assert assertions[0].raw_value is None and caps[0].status.value=='transport_error'


def test_unavailable_fallback_survives_history_replay():
    from goodsdex.legacy_catalog import apply_legacy_catalog
    row=dict(id='CN:mi_cn:product:10000023',name='红米4',image='https://example.org/exact-model.jpg',record_level='model_reference')
    obs={row['id']:dict(image=None,captured_at='2026-11-06T13:00:00Z')}
    first=apply_covers([row],obs)
    history=apply_legacy_catalog(first)
    assert history[0]['image']==row['image']
    assert history[0]['image_status']=='official_unavailable'
    assert apply_covers(history,obs)[0]['image']==first[0]['image']


def test_realicon_priority_over_newer_mtop_and_exact_model_only():
    from goodsdex.xiaomi_covers import BAIKE_SOURCE, BAIKE_URL
    model = 'xiaomi.pet_waterer.70m2'
    row = dict(id=PID, miio_model=model, image=URL, image_source=SOURCE,
               image_checked_at='2026-11-07T00:00:00Z', image_width=800, image_height=800,
               price=199, release={'date':'2024-12-24'}, params={'型号':'ABC'})
    baike = {model:dict(model=model, image='https://example.org/realIcon.png',
                        width=480, height=480, captured_at='2026-11-06T00:00:00Z')}
    before = deepcopy(row)
    result = apply_covers([row], {PID:dict(image=URL)}, baike)[0]
    assert row == before
    assert result['image'] == baike[model]['image']
    assert result['image_source'] == BAIKE_SOURCE
    assert result['image_source_url'] == BAIKE_URL + model
    assert (result['image_width'], result['image_height']) == (480,480)
    assert {k:v for k,v in row.items() if not k.startswith('image')} == {k:v for k,v in result.items() if not k.startswith('image')}
    assert apply_covers([result], {PID:dict(image=URL)}, baike) == [result]
    mismatch = {model:dict(baike[model], model='other.model.v1')}
    assert apply_covers([dict(id=PID,miio_model=model)], {PID:dict(image=URL)}, mismatch)[0]['image'] == URL


def test_realicon_failure_or_missing_model_falls_back_to_mtop_then_existing():
    model = 'xiaomi.pet_waterer.70m2'
    for unavailable in ({}, {model:dict(model=model,image=None,error='offline')},
                        {model:dict(model=model,image='http://invalid')}):
        row = dict(id=PID, miio_model=model, image='original')
        selected = apply_covers([row], {PID:dict(image=URL)}, unavailable)[0]
        assert selected['image'] == URL and selected['image_source'] == SOURCE
        selected = apply_covers([row], {PID:dict(image=None)}, unavailable)[0]
        assert selected['image'] == 'original' and selected['image_status'] == 'official_unavailable'
    available = {model:dict(model=model,image='https://example.org/realIcon.png')}
    assert apply_covers([dict(id=PID,image='original')], {PID:dict(image=URL)}, available)[0]['image'] == URL


def test_realicon_never_changes_other_sources_even_with_same_miio_model():
    model = 'xiaomi.pet_waterer.70m2'
    rows = [dict(id='CN:'+source+':product:20833',miio_model=model,image=source)
            for source in ('apple_cn','hp','dji','fujifilm','mihome')]
    assert apply_covers(rows, {r['id']:dict(image=URL) for r in rows},
                        {model:dict(model=model,image=URL)}) == rows
