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
