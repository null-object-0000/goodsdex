from copy import deepcopy
from datetime import date, timedelta
import gzip
import hashlib
import json
from pathlib import Path
import re

import pytest
from goodsdex.series_release import apply_series_releases, reconcile_series, validate_batch, identity
from goodsdex.release_dates import digest

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / 'docs/xiaomi-series-expansion-20261104'

@pytest.fixture
def batch():
    return json.loads((DOC/'reviewed-new-batches.json').read_text())[0]

@pytest.mark.parametrize('delta,status,allowed,erased', [
    (0,'corroborated',True,False),(14,'corroborated',True,False),
    (15,'disagreement',False,False),(45,'disagreement',False,False),
    (46,'conflict',False,True)])
def test_series_same_thresholds_and_manual_queue(batch,delta,status,allowed,erased):
    r=batch['series_release']
    r['crosschecks'][0]['date']=(date.fromisoformat(r['date'])+timedelta(days=delta)).isoformat()
    out=reconcile_series(r,batch['id'])
    assert out['crosscheck_status']==status
    assert out['display_allowed'] is allowed
    assert (out['date'] is None) is erased
    assert out['manual_review_required'] is erased
    if not allowed:
        assert out['display'] is None and out['usage']=='disabled'
    if erased:
        assert out['original_date']==r['date']

@pytest.mark.parametrize('change', ['publisher','url','market','event','batch','verified','capture','independence','llm'])
def test_reposts_other_generations_and_unproven_checks_never_unlock(batch,change):
    r=batch['series_release'];c=r['crosschecks'][0]
    if change=='publisher':c['evidence']['publisher']=r['evidence']['publisher']
    elif change=='url':c['evidence']['url']=r['evidence']['url']
    elif change=='market':c['market']='GLOBAL'
    elif change=='event':c['event']='availability'
    elif change=='batch':c['batch_id']='other-generation'
    elif change=='verified':c['evidence']['verified']=False
    elif change=='capture':c['evidence'].pop('sha256')
    elif change=='independence':c.pop('independence_reason')
    elif change=='llm':c['source']='llm'
    out=reconcile_series(r,batch['id'])
    assert out['crosscheck_status']=='unverified' and out['display'] is None

def test_agreement_cannot_mask_captured_conflict(batch):
    r=batch['series_release'];c=deepcopy(r['crosschecks'][0]);c['date']='2020-01-01'
    r['crosschecks'].append(c)
    out=reconcile_series(r,batch['id'])
    assert out['date'] is None and out['manual_review_required']

@pytest.mark.parametrize('when,precision,display',[
    ('2025','year','该系列 2025 年发布'),
    ('2025-05','month','该系列 2025 年 5 月发布'),
    ('2025-05-22','day','该系列 2025 年 5 月 22 日发布')])
def test_official_precision_does_not_invent_lower_units(tmp_path,when,precision,display):
    bundle=json.loads((ROOT/'data/official/series-releases.json').read_text())
    b=deepcopy(next(b for b in bundle['batches'] if b['series_release']['source']=='official'))
    b['series_release'].update(date=when,granularity=precision)
    bundle['batches']=[b]
    path=tmp_path/'series.json';path.write_text(json.dumps(bundle))
    rows=json.loads(gzip.decompress((DOC/'baseline.json.gz').read_bytes()))
    row=next(r for r in rows if r['id']==b['members'][0]['id'])
    out=apply_series_releases([row],path)[0]['release_series']
    assert out['date']==when and out['display']==display
    bad=deepcopy(b);bad['series_release'].update(date='2025-02-30',granularity='day')
    with pytest.raises(ValueError):validate_batch(bad)

def test_exact_census_identity_capture_and_all_thirty_quotes():
    rows=json.loads(gzip.decompress((DOC/'baseline.json.gz').read_bytes()))
    result=apply_series_releases(rows)
    assert [{k:v for k,v in r.items() if k!='release_series'} for r in result]==[
        {k:v for k,v in r.items() if k!='release_series'} for r in rows]
    assert apply_series_releases(result)==result
    fs=json.loads((DOC/'families.json').read_text())
    assert sum(f['row_count'] for f in fs)==1472
    membership=[m['id'] for f in fs for m in f['members']]
    missing=[r['id'] for r in rows if r.get('brand')=='小米' and not (r.get('release')or{}).get('date') and not (r.get('release_series')or{}).get('date')]
    from collections import Counter
    assert Counter(membership)==Counter(missing)
    batches=json.loads((DOC/'reviewed-new-batches.json').read_text())
    for b in batches:
        validate_batch(b)
        for m in b['members']:
            hashes={m['identity_sha256'],*m.get('identity_sha256_alternates',[])}
            assert {digest(identity(r)) for r in rows if r['id']==m['id']}==hashes
        for e in [b['series_release']['evidence']]+[c['evidence'] for c in b['series_release'].get('crosschecks',[])]:
            raw=(ROOT/e['capture_file']).read_bytes()
            assert hashlib.sha256(raw).hexdigest()==e['sha256']
            if e['capture_file'].endswith('.html'):
                capture=json.loads((ROOT/e['capture_file']).with_suffix('.json').read_text())
                assert not capture.get('error') and not capture.get('body_unavailable')
                assert re.sub(r'\s+','',e['quote']) in re.sub(r'\s+','',capture['text'])
    samples=json.loads((DOC/'sample-30.json').read_text())
    assert len(samples)==len({s['id'] for s in samples})==30
    byid={r['id']:r for r in result}
    assert all(byid[s['id']]['release_series']['date']==s['date'] for s in samples)

def test_frozen_duplicate_projection_is_not_fuzzy_identity_permission():
    rows=json.loads(gzip.decompress((DOC/'baseline.json.gz').read_bytes()))
    dup=[r for r in rows if r['id']=='CN:mi_cn:product:22172']
    assert len(dup)==3
    assert all(r['release_series']['display_allowed'] for r in apply_series_releases(dup))
    dup[0]['params']['cpu']='未来一代处理器'
    with pytest.raises(ValueError,match='drift'):apply_series_releases(dup)

def test_unreviewed_later_capacity_services_and_supplies_stay_empty():
    rows=json.loads(gzip.decompress((DOC/'baseline.json.gz').read_bytes()))
    byid={r['id']:r for r in apply_series_releases(rows)}
    # Same name/capacity is insufficient for new batches or combination packs.
    for tail in ['8154','22575','23957','23579','10000110','4814','13847']:
        assert 'release_series' not in byid['CN:mi_cn:product:'+tail]
