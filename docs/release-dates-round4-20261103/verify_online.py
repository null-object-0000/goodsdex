"""Wait for the ordinary public API refresh, then verify every newly added detail."""
import gzip,json,sys,time
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parent
expected=json.load(open('/tmp/goodsdex-release-round4/public/goods.json'));by={r['id']:r for r in expected};new=json.load(open(ROOT/'new-candidates.json'));first=new[0]['ids'][0];base='https://spend.snewbie.site';attempts=[]
def fetch(path):
 with urlopen(Request(base+path,headers={'Accept-Encoding':'gzip'}),timeout=90) as r:
  raw=r.read()
  if r.headers.get('Content-Encoding')=='gzip':raw=gzip.decompress(raw)
  return json.loads(raw)
def save(name,obj):(ROOT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
for i in range(32):
 stamp=datetime.now(timezone.utc).isoformat();url='/api/goods/'+quote(first,safe='')+'?round4='+quote(stamp,safe='');o=fetch(url);match=o.get('release')==by[first].get('release');attempts.append(dict(at=stamp,id=first,equal=match,actual_release=o.get('release')));save('online-sync-attempts.json',attempts)
 print('sync',i,stamp,match,flush=True)
 if match:break
 time.sleep(45)
else:raise RuntimeError('API has not refreshed within 24 minutes; no success claim')
time.sleep(2.15)
actual=fetch('/api/goods?round4='+quote(stamp,safe=''));assert len(actual)==len(expected)
assert [r['id'] for r in actual]==[r['id'] for r in expected]
assert [r.get('release') for r in actual]==[r.get('release') for r in expected], 'Published release corpus differs'
full_equal=actual==expected
extra=['CN:mi_cn:product:18520','CN:mi_cn:product:20543','GLOBAL:apple_support:model:111843','CN:hp_cn:sku:7Y0Y4PC','CN:dji:sku:158331']
keys=list(dict.fromkeys([c['ids'][0] for c in new]+extra));samples=[]
for key in keys:
 time.sleep(2.15);url='/api/goods/'+quote(key,safe='')+'?round4='+quote(stamp,safe='');detail=fetch(url);assert detail['id']==key and detail.get('release')==by[key].get('release'),key
 samples.append(dict(id=key,name=detail['name'],url=base+url,release=detail.get('release'),release_equal=True));save('online-verification.json',dict(checked_at=stamp,complete=len(samples)==len(keys),full_catalog_equal=full_equal,full_release_corpus_equal=True,rows=len(actual),new_ids_verified=sum(s['id'] in {c['ids'][0] for c in new} for s in samples),samples=samples))
 print('detail',len(samples),len(keys),key,flush=True)
print('COMPLETE',len(samples),'new',len(new),'catalog_equal',full_equal,flush=True)
