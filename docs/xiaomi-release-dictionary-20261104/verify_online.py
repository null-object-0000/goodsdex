"""Save real API responses and compare the published catalogue to reviewed output."""
import gzip,json,hashlib,subprocess
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import quote
import requests
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]

def main():
 expected=json.loads(gzip.decompress((OUT/'expected-finalizer.json.gz').read_bytes()))
 raw=subprocess.check_output(['git','show','origin/data:public/goods.json'],cwd=ROOT)
 published=json.loads(raw);meta=json.loads(subprocess.check_output(['git','show','origin/data:public/meta.json'],cwd=ROOT))
 project=lambda rows:[(r['id'],r.get('release'),r.get('release_series')) for r in rows]
 assert project(published)==project(expected)
 (OUT/'published-goods.json.gz').write_bytes(gzip.compress(raw,mtime=0))
 (OUT/'published-meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
 s=requests.Session();s.trust_env=False
 def get(path,name):
  r=s.get('https://spend.snewbie.site'+path,timeout=45,headers={'Cache-Control':'no-cache'});r.raise_for_status()
  (OUT/name).write_bytes(r.content);return r.json()
 live_meta=get('/api/meta','online-meta.json')
 rows=get('/api/goods','online-goods.json');assert project(rows)==project(expected)
 (OUT/'online-goods.json.gz').write_bytes(gzip.compress((OUT/'online-goods.json').read_bytes(),mtime=0));(OUT/'online-goods.json').unlink()
 assert live_meta==meta
 byid={r['id']:r for r in published};excerpts=[]
 for id in ['CN:mi_cn:product:20618','CN:mi_cn:product:21765','CN:mi_cn:product:25291']:
  row=get('/api/goods/'+quote(id,safe=''),'online-detail-'+id.split(':')[-1]+'.json')
  assert row['release_series']==byid[id]['release_series']
  excerpts.append(dict(id=id,name=row['name'],release_series={k:row['release_series'].get(k) for k in ('date','granularity','source','crosscheck_status','display_allowed','internal_only','usage','display')}))
 verification=dict(checked_at=datetime.now(timezone.utc).isoformat(),published_data_commit=subprocess.check_output(['git','rev-parse','origin/data'],cwd=ROOT,text=True).strip(),
  rows=len(rows),meta_equal=True,release_projection_equal=True,full_catalog_equal=rows==published,revision=live_meta['revision'],sha256=hashlib.sha256(raw).hexdigest(),details=excerpts)
 (OUT/'online-verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n')
 (OUT/'online-excerpts.md').write_text('# 发布后真实 API 摘录\n\n/api/meta：\n\n```json\n'+json.dumps({k:live_meta.get(k) for k in ('revision','total_published','release_series')},ensure_ascii=False,indent=2)+'\n```\n\n3个真实 /api/goods/<id>：\n\n```json\n'+json.dumps(excerpts,ensure_ascii=False,indent=2)+'\n```\n')
 print(json.dumps(verification,ensure_ascii=False))
if __name__=='__main__':main()
