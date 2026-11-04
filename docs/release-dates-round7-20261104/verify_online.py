"""Verify actual published data, meta and three detail endpoints after normal sync."""
import gzip,json,hashlib,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import quote
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'src'))
from goodsdex.release_dates import apply_release_dates
from goodsdex.series_release import apply_series_releases

def main():
 baseline=json.loads(gzip.decompress((OUT/'baseline.json.gz').read_bytes()))
 frozen_expected=apply_series_releases(apply_release_dates(baseline))
 locked_raw=subprocess.check_output(['git','show','origin/data^:public/goods.json'],cwd=ROOT)
 locked=json.loads(locked_raw)
 (OUT/'locked-parent-goods.json.gz').write_bytes(gzip.compress(locked_raw,mtime=0))
 expected=apply_series_releases(apply_release_dates(locked))
 raw=subprocess.check_output(['git','show','origin/data:public/goods.json'],cwd=ROOT)
 published=json.loads(raw);meta=json.loads(subprocess.check_output(['git','show','origin/data:public/meta.json'],cwd=ROOT))
 project=lambda rows:[(r['id'],r.get('release'),r.get('release_series')) for r in rows]
 assert project(published)==project(frozen_expected), 'Latest publication date projection changed'
 assert published==expected,'Unexpected non-date publication changes'
 from collections import Counter
 delta=Counter(k for x,y in zip(baseline,locked,strict=True) for k in set(x)|set(y) if x.get(k)!=y.get(k))
 publication_delta=Counter(k for x,y in zip(locked,published,strict=True) for k in set(x)|set(y) if x.get(k)!=y.get(k))
 assert publication_delta=={'release':55}
 (OUT/'publication-invariants.json').write_text(json.dumps(dict(locked_parent=subprocess.check_output(['git','rev-parse','origin/data^'],cwd=ROOT,text=True).strip(),frozen_to_locked_changed_fields=dict(delta),locked_to_published_changed_fields=dict(publication_delta),date_projection_matches_frozen_review=True,exact_replay_over_locked_parent=True),ensure_ascii=False,indent=2)+'\n')
 (OUT/'published-goods.json.gz').write_bytes(gzip.compress(raw,mtime=0))
 (OUT/'published-meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
 def get(path,name):
  body=subprocess.check_output(['curl','-fsS','--compressed','--max-time','45','-H','Cache-Control: no-cache','https://spend.snewbie.site'+path])
  (OUT/name).write_bytes(gzip.compress(body,mtime=0) if name.endswith('.gz') else body)
  return json.loads(body)
 live_meta=get('/api/meta','online-meta.json')
 rows=get('/api/goods','online-goods.json.gz')
 assert rows==published
 assert live_meta==meta
 assert live_meta['release_scope']['tiers']=={'machine':2554,'accessory':256,'third_party_selection':92}
 byid={r['id']:r for r in published};excerpts=[]
 for id in ['CN:dji:sku:192291','CN:mi_cn:product:8152','CN:byd:car:han:2023:dmi']:
  row=get('/api/goods/'+quote(id,safe=''),'online-detail-'+id.split(':')[-1]+'.json')
  assert row['release']==byid[id]['release']
  r=row['release'];assert r['source']=='third_party' and r['display_allowed'] and len(r['assertions'])==2
  excerpts.append(dict(id=id,name=row['name'],release={k:r.get(k) for k in ('date','source','event','display_allowed','crosscheck_status','crosscheck_delta_days')},sources=[dict(date=a['date'],event=a['event'],url=a['evidence']['url'],quote=a['evidence']['quote']) for a in r['assertions']]))
 verification=dict(checked_at=datetime.now(timezone.utc).isoformat(),published_data_commit=subprocess.check_output(['git','rev-parse','origin/data'],cwd=ROOT,text=True).strip(),rows=len(rows),meta_equal=True,full_catalog_equal=True,reviewed_output_equal=True,revision=live_meta['revision'],sha256=hashlib.sha256(raw).hexdigest(),details=excerpts)
 (OUT/'online-verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n')
 (OUT/'online-excerpts.md').write_text('# 发布后真实 API 摘录\n\n/api/meta：\n\n```json\n'+json.dumps({k:live_meta.get(k) for k in ('revision','total_published','release_scope')},ensure_ascii=False,indent=2)+'\n```\n\n3个真实 /api/goods/<id>：\n\n```json\n'+json.dumps(excerpts,ensure_ascii=False,indent=2)+'\n```\n')
 print(json.dumps({k:v for k,v in verification.items() if k!='details'},ensure_ascii=False))
if __name__=='__main__':main()
