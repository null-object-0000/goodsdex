"""Replay explicit per-candidate review decisions and preserve prior approved input."""
import gzip,json,math,random,re
from collections import Counter,defaultdict
from pathlib import Path
from goodsdex.release_l7 import POLICY,fingerprint,body_text,check,apply
from goodsdex.release_coverage import effective,matrix
from goodsdex.release_tolerance import apply as select
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/release-coverage/L7-scale'
def main():
 rows=json.loads(gzip.decompress((OUT/'baseline.json.gz').read_bytes()));by={r['id']:r for r in rows}
 prior=json.loads((OUT/'prior-evidence.json').read_text())
 decisions={(x['id'],x['date'],x['url']):x for x in json.loads((OUT/'review-decisions.json').read_text())}
 audit=[];entries=[];approved_ids=set()
 for i,p in enumerate(json.loads((OUT/'verification.json').read_text())):
  a={k:p[k] for k in ('id','name','date','url')};a.update(index=i,batch=i//50+1)
  decision=decisions.get((p['id'],p['date'],p['url']))
  if p.get('rejection'):a['rejection']=p['rejection']
  elif not decision:a.update(rejection='not_reviewed',detail='尚未逐条复核，不入库')
  elif not decision['approved']:a.update(rejection='event_or_identity_unproven',detail=decision['reason'])
  else:
   row=by[p['id']]
   if decision.get('identity_sha256') != fingerprint(row):
    raise ValueError('Missing or changed manually reviewed identity fingerprint')
   c=p['capture'];text=body_text(gzip.decompress((ROOT/c['capture_file']).read_bytes()))
   m=re.search(r'\d{4}/\d{1,2}/\d{1,2}',text)
   if not m:raise ValueError('Explicit body date not found')
   # Reviewed article lead, never model-generated text or related-story date.
   name_pattern=r'\s*'.join(re.escape(c) for c in re.sub(r'\s+', '', row['name']))
   title_model=re.search(name_pattern, text[:m.start()], re.I)
   start=title_model.start() if title_model else m.start()
   quote=text[start:].split('广告声明：')[0].split('投诉水文')[0].strip()
   release=dict(date=p['date'],source='llm_verified',policy=POLICY,granularity='month',level='product',confidence='medium',market='CN',event='announcement',crosscheck_status='page_verified',usage='fact',display_allowed=True,evidence={k:c[k] for k in ('url','final_url','http_status','capture_file','sha256','captured_at')})
   release['evidence']['quote']=quote
   e=dict(id=row['id'],name=row['name'],identity_sha256=fingerprint(row),identity_terms=[row['name']],reviewed=True,identity_reason='逐条精确型号及版本复核；名称仅规范空白和大小写',event_reason=decision['reason'],release=release)
   check(e,row);a['status']='accepted';entries.append(e);approved_ids.add(row['id'])
  audit.append(a)
 dates=defaultdict(set)
 for e in entries: dates[e['id']].add(e['release']['date'])
 if any(len(v)>1 for v in dates.values()):
  raise ValueError('Conflicting approved months: '+str({k:sorted(v) for k,v in dates.items() if len(v)>1}))
 # Several sources may corroborate one row; candidate counts and newly covered rows differ.
 bundle=dict(policy=POLICY,entries=prior['entries']+entries)
 after=select(apply(rows,bundle))
 before_matrix=matrix(rows);after_matrix=matrix(after)
 (ROOT/'data/third-party/l7-release-evidence.json').write_text(json.dumps(bundle,ensure_ascii=False,indent=2)+'\n')
 batches=[];current=rows
 for batch in sorted({a['batch'] for a in audit}):
  subset=[a for a in audit if a['batch']==batch];keys={(a['id'],a['date'],a['url']) for a in subset if a.get('status')=='accepted'}
  es=[e for e in entries if (e['id'],e['release']['date'],e['release']['evidence']['url']) in keys]
  start=matrix(current)['total'];current=select(apply(current,dict(policy=POLICY,entries=es)));end=matrix(current)['total']
  batches.append(dict(batch=batch,candidates=len(subset),accepted=len(es),rejections=dict(Counter(a['rejection'] for a in subset if a.get('rejection'))),before=start,after=end))
 missing=Counter((r['brand'],r.get('category','其他')) for r in after if not effective(r))
 gap=max(0,math.ceil(len(rows)*.45)-after_matrix['total']['covered']);rate=len(entries)/len(audit) if audit else 0
 summary=dict(candidates=len(audit),accepted=len(entries),rejected=sum('rejection' in a for a in audit),new_rows=after_matrix['total']['covered']-before_matrix['total']['covered'],reasons=dict(Counter(a['rejection'] for a in audit if a.get('rejection'))),before=before_matrix,after=after_matrix,gap_to_45=gap,candidates_at_prior_72_percent=math.ceil(gap/.72),candidates_at_observed_rate=math.ceil(gap/rate) if rate else None,batches=batches,missing_categories=[dict(brand=b,category=c,count=n) for (b,c),n in missing.most_common()])
 for name,value in [('audit.json',audit),('summary.json',summary),('new-entries.json',entries),('samples.json',random.Random(20261105).sample(list({e['id']:e for e in entries}.values()),min(12,len(approved_ids))))]: (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
 (OUT/'after.json.gz').write_bytes(gzip.compress(json.dumps(after,ensure_ascii=False).encode(),mtime=0))
 print(json.dumps({k:summary[k] for k in ('candidates','accepted','rejected','new_rows','reasons','gap_to_45')},ensure_ascii=False));print(after_matrix['total'])
if __name__=='__main__':main()
