from datetime import datetime, timezone
from source_registry import reconcile, metrics

def run(id, result):
    return dict(id=id,status='completed',conclusion=result,created_at='2026-11-06T00:00:00Z',updated_at='2026-11-06T00:01:00Z',html_url='https://github.com/test/run/'+str(id))

def test_two_failures_and_recovery():
    row=dict(period_minutes=1440,last_success='2026-11-05T00:00:00Z')
    failed=reconcile(row,[run(3,'failure'),run(2,'failure'),run(1,'success')],datetime.now(timezone.utc))
    assert failed['alert'] and failed['consecutive_failures']==2
    fixed=reconcile(failed,[run(4,'success'),run(3,'failure')],datetime.now(timezone.utc))
    assert not fixed['alert'] and fixed['consecutive_failures']==0
    assert fixed['last_success']=='2026-11-06T00:01:00Z'

def test_additions_are_unique_and_explain_missing_dates():
    old=[dict(id='a',name='old')]
    new=old+[dict(id='b',name='new',source='mihome')]*2
    result=metrics(old,new)
    assert result['items_new']==1 and result['new_date_ratio']==0
    assert result['additions'][0]['source']=='mihome' and result['additions'][0]['reason']
    assert metrics(new,new)['items_new']==0

def test_live_directory_intake_is_incremental_and_keeps_existing_immutable():
    import io
    from PIL import Image
    from directory_intake import intake
    image=io.BytesIO();Image.new('RGB',(860,580)).save(image,format='PNG')
    class Response:
        content=image.getvalue()
        def raise_for_status(self):pass
        def json(self):return {'data':{'model':'test.vacuum.v1','pdId':100}}
    old=[dict(id='old',name='Existing')]
    device=dict(model='miwear.headphone.test',name='Fixture Earbuds',icon_static=[dict(icon_url='https://cdn.cnbj1.fds.api.mi-img.com/test.png')])
    after,pending=intake(old,[device],'earbuds',fetch=lambda *a,**k:Response())
    assert not pending and len(after)==2 and after[0]==old[0]
    again,pending=intake(after,[device],'earbuds',fetch=lambda *a,**k:1/0)
    assert again==after and not pending
    device=dict(model='test.vacuum.v1',pdId=100,name='Fixture Vacuum',categoryName='吸尘器')
    after,pending=intake(old,[device],'gap',fetch=lambda *a,**k:Response())
    assert len(after)==2 and not pending and after[1]['price'] is None
    assert 'release' not in after[1]
    again,pending=intake(after,[device],'gap',fetch=lambda *a,**k:1/0)
    assert again==after and not pending

def test_image_refresh_skips_existing_and_rejects_ambiguous_identity():
    from refresh_missing_images import refresh
    rows=[dict(id='CN:mi_cn:product:1',name='Existing',image='https://example.org/a.png')]
    after,audit=refresh(rows,fetch=lambda *a,**k:1/0)
    assert after==rows and not audit
    class Response:
        def raise_for_status(self):pass
        def json(self):return dict(data=dict(product=dict(name='Another generation')))
    rows=[dict(id='CN:mi_cn:product:1',name='Exact model')]
    after,audit=refresh(rows,fetch=lambda *a,**k:Response())
    assert after==rows and audit[0]['status']=='pending'
