"""Independent denominator boundaries and actual captured media contract."""
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import pytest
from goodsdex.release_scope import release_scope, scope_coverage
from goodsdex.third_party_release import assess, apply_third_party
ROOT=Path(__file__).resolve().parents[1]

@pytest.mark.parametrize('name,category,kind,tier',[
 ('米家扫地机器人主刷','旧款机型','unknown','accessory'),
 ('小米手环 10（含NFC版、陶瓷版等）','穿戴配件','unknown','machine'),
 ('【生活优选】焕醒手动剃须刀套装','剃须刀','machine','third_party_selection'),
 ('米家热泵烘干机10kg','家电','unknown','machine'),
 ('空调清洁保养服务','中央空调Pro','service','accessory'),
 ('米家便携电热杯2','水杯','unknown','machine'),
 ('米家台式净饮机3','家电','unknown','machine'),
 ('米家桌面打印相纸 6英寸','打印机','unknown','accessory'),
])
def test_scope_boundaries(name,category,kind,tier):
 assert release_scope(dict(name=name,category=category,kind=kind,brand='小米'))['tier']==tier

def assertions():
 cs=json.loads((ROOT/'data/third-party/release-dates.json').read_text())['candidates']
 return deepcopy(cs[0]['assertions'])

@pytest.mark.parametrize('days,status',[(14,'corroborated'),(15,'disagreement'),(45,'disagreement'),(46,'conflict')])
def test_real_day_threshold_across_months(days,status):
 from datetime import date,timedelta
 a=assertions();a[0]['date']='2025-01-25';a[1]['date']=(date(2025,1,25)+timedelta(days=days)).isoformat()
 assert assess(a)['status']==status

def test_no_single_reprint_llm_or_event_mixing():
 a=assertions();assert not assess(a[:1])['display_allowed']
 a[1]['source']='llm';assert not assess(a)['display_allowed']
 a=assertions();a[1]['event']='availability';assert not assess(a)['display_allowed']
 a=assertions();a[1]['evidence']['upstream_origin']='ithome.com';assert not assess(a)['display_allowed']
 a=assertions();a[1]['evidence']['url']='https://m.ithome.com/html/123.htm';assert not assess(a)['display_allowed']
 a=assertions();a[1]['evidence']['sha256']=a[0]['evidence']['sha256'];assert not assess(a)['display_allowed']

def test_frozen_media_review_and_replay(tmp_path):
 cs=json.loads((ROOT/'data/third-party/release-dates.json').read_text())['candidates']
 # Concrete expected release population, independent of the importer.
 assert {c['brand']:sum(x['brand']==c['brand'] for x in cs) for c in cs}=={'大疆':10,'小米':4,'比亚迪':2}
 evidence=ROOT/'docs/release-dates-round7-20261104/evidence'
 for c in cs:
  assert len(c['assertions'])==2
  for a in c['assertions']:
   e=a['evidence'];key=hashlib.sha256(e['url'].encode()).hexdigest()[:16]
   capture=json.loads((evidence/(key+'.json')).read_text())
   raw=gzip.decompress((evidence/(key+'.html.gz')).read_bytes())
   assert hashlib.sha256(raw).hexdigest()==e['sha256']
   assert e['quote'] in capture['text'] and e['identity_quote'] in capture['text']
  assert assess(c['assertions'])=={'status':'corroborated','delta_days':0,'display_allowed':True}
 rows=[dict(id=c['id'],name=c['name'],brand=c['brand'],kind='machine',category='相机') for c in cs]
 result=apply_third_party(rows)
 assert apply_third_party(result)==result
 for before,after in zip(rows,result):
  assert {k:v for k,v in after.items() if k!='release'}==before
  assert after['release']['source']=='third_party' and after['release']['display_allowed']
 assert sum(scope_coverage(result)['tiers'].values())==len(rows)
 # Duplicate-name records never get dates even if the media names a model.
 with pytest.raises(ValueError,match='identity'):
  apply_third_party(rows+[dict(rows[0],id='duplicate')])

@pytest.mark.parametrize('day,expected,status',[('2025-08-21','2025-08','disagreement'),('2025-09-21',None,'conflict')])
def test_importer_degrades_and_clears_real_conflicts(tmp_path,day,expected,status):
 c=deepcopy(json.loads((ROOT/'data/third-party/release-dates.json').read_text())['candidates'][0])
 c['assertions'][1]['date']=day
 path=tmp_path/'review.json';path.write_text(json.dumps(dict(schema=1,candidates=[c])))
 row=dict(id=c['id'],name=c['name'],brand='大疆',kind='machine')
 r=apply_third_party([row],path)[0]['release']
 assert r['date']==expected and r['crosscheck_status']==status
 assert r['display'] is None and not r['display_allowed'] and r['internal_only']
 assert r['manual_review_required'] is (status=='conflict')
 assert apply_third_party([dict(row,release=r)],path)[0]['release']==r
