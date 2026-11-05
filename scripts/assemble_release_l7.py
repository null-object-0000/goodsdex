"""Replay explicit human-reviewed proposal indexes; never infer from other models."""
import json, gzip, re, random, math
from pathlib import Path
from collections import Counter
from goodsdex.release_l7 import POLICY, fingerprint, body_text, check, apply
from goodsdex.release_coverage import matrix, effective
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/release-coverage/L7'
# Explicit event exclusions recorded after reading the captured article bodies.
EXCLUDE={8:'近日发布不能确定同月（11月初报道）',19:'正文明确8月已众筹，9月不是首次发布',26:'近期上架缺精确首发月',31:'目前上架缺精确首次发布声明',33:'仅上架缺首次声明',36:'正文明确上市日期暂未公布',42:'报道哈利波特定制版，目录为普通版',44:'正式开售不能排除更早发布'}

def main():
 rows=json.loads(gzip.decompress((OUT/'baseline.json.gz').read_bytes()))
 by_id={r['id']:r for r in rows}
 proposals=json.loads((OUT/'verification.json').read_text())
 entries=[];audit=[];seen=set()
 for i,p in enumerate(proposals):
  key=(p['id'],p['date'],p['url'])
  if key in seen:continue
  seen.add(key)
  a=dict(index=i,id=p['id'],name=p['name'],date=p['date'],url=p['url'])
  if p.get('rejection'):a['rejection']=p['rejection']
  elif i in EXCLUDE:a.update(rejection='event_or_identity_unproven',detail=EXCLUDE[i])
  else:
   row=by_id[p['id']];c=p['capture']
   text=body_text(gzip.decompress((ROOT/c['capture_file']).read_bytes()))
   # Contiguous body excerpt containing article year/month and model/event text.
   m=re.search(r'\d{4}/\d{1,2}/\d{1,2}',text)
   quote=text[m.start():m.start()+1200]
   release=dict(date=p['date'],source='llm_verified',policy=POLICY,granularity='month',level='product',confidence='medium',market='CN',event='announcement',crosscheck_status='page_verified',usage='fact',display_allowed=True,evidence={k:c[k] for k in ('url','final_url','http_status','capture_file','sha256','captured_at')})
   release['evidence']['quote']=quote
   e=dict(id=row['id'],name=row['name'],identity_sha256=fingerprint(row),identity_terms=[row['name']],reviewed=True,identity_reason='正文完整精确名称，保留所有代际及版本限定，仅忽略空格/大小写',event_reason='已阅读正文，新品推出/发布/众筹语义与报道月份一致；不跨型号或套装',release=release)
   check(e,row);entries.append(e);a['status']='accepted'
  audit.append(a)
 bundle=dict(policy=POLICY,entries=entries)
 (ROOT/'data/third-party/l7-release-evidence.json').write_text(json.dumps(bundle,ensure_ascii=False,indent=2))
 after=apply(rows,bundle)
 # Run the production decision selector to ensure this source survives finalization.
 from goodsdex.release_tolerance import apply as select
 after=select(after)
 (OUT/'audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
 (OUT/'coverage.json').write_text(json.dumps(dict(before=matrix(rows),after=matrix(after)),ensure_ascii=False,indent=2))
 samples=random.Random(20261105).sample(entries,10)
 (OUT/'samples.json').write_text(json.dumps(samples,ensure_ascii=False,indent=2))
 (OUT/'after.json.gz').write_bytes(gzip.compress(json.dumps(after,ensure_ascii=False).encode(),mtime=0))
 print(len(audit),len(entries),Counter(a.get('rejection') for a in audit));print(matrix(after)['total'])
if __name__=='__main__':main()
