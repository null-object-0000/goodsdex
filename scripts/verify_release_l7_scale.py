"""Deduplicate and fetch batches of 50 grounded proposals; never auto-approve."""
import gzip,json,re,time
from pathlib import Path
import verify_release_l7 as base
from goodsdex.release_l7 import publisher,body_text,has_month
from goodsdex.release_media import normalize
OUT=Path('docs/release-coverage/L7-scale').resolve();base.OUT=OUT
ROOT=Path(__file__).resolve().parents[1]
INELIGIBLE_NAMES={'Redmi','米家洗衣机Pro','米家冰箱 对开门','米家波轮洗衣机','米家吸顶灯C','米家冰箱Pro 双系统','Redmi Book 14','米家冰箱 两门','米家筒射灯2 蓝牙Mesh版'}
def read_proposals():
 output=[]
 for directory in ('proposals','grounded'):
  for path in sorted((OUT/directory).glob('*.json')):
   if any(s in path.name for s in ('.input.','.prompt.','.error.')):continue
   try:
    response=json.loads(path.read_text());v=json.loads(re.sub(r'^```(?:json)?\s*|\s*```$','',response['choices'][0]['message']['content'].strip()))
    if isinstance(v,list):output.extend(dict(x,proposal_file=str(path.relative_to(ROOT))) for x in v if isinstance(x,dict))
   except (KeyError,ValueError,TypeError):continue
 return output
def main():
 targets={(x['id'],x['name']) for x in json.loads((OUT/'targets.json').read_text())}
 seen=set();results=[];abstentions=[];duplicates=[];ineligible={}
 excluded_file=OUT/'ineligible.json'
 if excluded_file.exists():
  ineligible={(normalize(p['name']),p.get('date'),p.get('url')):p for p in json.loads(excluded_file.read_text())}
 previous=json.loads((ROOT/'docs/release-coverage/L7/audit.json').read_text())
 prior={(normalize(x['name']),x['date'],x['url']) for x in previous}
 proposals=read_proposals()
 ledger=OUT/'verification.json'
 existing=json.loads(ledger.read_text()) if ledger.exists() else []
 # Append-only order preserves the 50-candidate batches already reported.
 old_keys={(normalize(p['name']),p['date'],p['url']) for p in existing}
 proposals=existing+[p for p in proposals if not p.get('date') or not p.get('url') or (normalize(p.get('name','')),p['date'],p['url']) not in old_keys]
 for p in proposals:
  if (p.get('id'),p.get('name')) not in targets:continue
  if p['name'] in INELIGIBLE_NAMES:
   ineligible[(normalize(p['name']),p.get('date'),p.get('url'))]=dict(p,preflight_exclusion='brand_or_series_not_exact_model')
   continue
  if not p.get('date') or not p.get('url'):abstentions.append(p);continue
  key=(normalize(p['name']),p['date'],p['url'])
  if key in seen or key in prior:duplicates.append(p);continue
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
  results.append(r)
  (OUT/'verification.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
  if len(results)%50==0:print('submitted batch',len(results)//50,flush=True);time.sleep(5)
 for filename,v in [('abstentions.json',abstentions),('duplicates.json',duplicates),('ineligible.json',list(ineligible.values()))]: (OUT/filename).write_text(json.dumps(v,ensure_ascii=False,indent=2))
 print('unique candidates',len(results),'abstentions',len(abstentions),'duplicate/prior',len(duplicates),flush=True)
if __name__=='__main__':main()
