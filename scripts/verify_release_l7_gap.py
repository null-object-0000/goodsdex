"""Append-only globally deduplicated, paced capture ledger. Never auto-approve."""
import gzip,json,re,time
from pathlib import Path
import verify_release_l7 as base
from goodsdex.release_l7 import publisher,body_text,has_month
from goodsdex.release_media import normalize
from goodsdex.release_coverage import effective
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/release-coverage/L7-gap';base.OUT=OUT

def main():
 rows=json.loads(gzip.decompress((OUT/'baseline.json.gz').read_bytes()))
 targets={(r['id'],r['name']):r for r in rows if not effective(r)}
 prior=set()
 for d in ('L7','L7-scale'):
  for a in json.loads((OUT.parent/d/'audit.json').read_text()):prior.add((normalize(a['name']),a['date'],a['url']))
 search=OUT/'search-proposals.json'
 proposals=json.loads(search.read_text()) if search.exists() else []
 for folder in (OUT/'grounded',OUT/'identity/proposals'):
  for path in sorted(folder.glob('*.json')):
   if any(x in path.name for x in ('.input.','.prompt.','.error.')):continue
   try:
    d=json.loads(path.read_text());v=json.loads(re.sub(r'^```(?:json)?\s*|\s*```$','',d['choices'][0]['message']['content'].strip()))
    if isinstance(v,list):proposals.extend(dict(x,proposal_file=str(path.relative_to(ROOT))) for x in v if isinstance(x,dict))
   except (ValueError,KeyError,TypeError):continue
 ledger=OUT/'verification.json';results=json.loads(ledger.read_text()) if ledger.exists() else []
 seen=prior|{(normalize(p['name']),p['date'],p['url']) for p in results}
 abstentions=[];duplicates=[]
 for p in proposals:
  if (p.get('id'),p.get('name')) not in targets:continue
  if not p.get('url') or not p.get('date'):abstentions.append(p);continue
  key=(normalize(p['name']),p['date'],p['url'])
  if key in seen:duplicates.append(p);continue
  seen.add(key);r=dict(p)
  if not publisher(p['url']):r['rejection']='source_not_allowed'
  else:
   c=base.fetch(p['url']);r['capture']=c
   if c.get('http_status')!=200 or c.get('reason')!='retrieved':r['rejection']='link_unavailable'
   else:
    text=body_text(gzip.decompress((ROOT/c['capture_file']).read_bytes()))
    if normalize(p['name']) not in normalize(text):r['rejection']='page_no_model'
    else:
     try:ok=has_month(text,p['date'])
     except (ValueError,TypeError):ok=False
     if not ok:r['rejection']='page_no_month'
     else:r['status']='requires_event_review'
  results.append(r);ledger.write_text(json.dumps(results,ensure_ascii=False,indent=2))
  if len(results)%50==0:print('captured batch',len(results)//50,flush=True);time.sleep(5)
 for f,v in [('abstentions.json',abstentions),('duplicates.json',duplicates)]: (OUT/f).write_text(json.dumps(v,ensure_ascii=False,indent=2))
 print('unique',len(results),'abstentions',len(abstentions),'duplicate/prior',len(duplicates),flush=True)
if __name__=='__main__':main()
