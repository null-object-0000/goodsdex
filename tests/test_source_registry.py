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
