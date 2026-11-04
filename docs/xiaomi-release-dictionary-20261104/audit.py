"""Reproduce field/source/coverage audits and independently re-fetch 30 official entries."""
from pathlib import Path
import json,gzip,random,collections,hashlib,re,html,subprocess,time
from datetime import datetime,timezone
from urllib.parse import urlparse
import requests
import sys
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1];sys.path.insert(0,str(ROOT/'src'))
from goodsdex.series_release import apply_series_releases,is_accessory,reconcile_series
from goodsdex.release_dates import apply_release_dates

def read(p):return json.loads(Path(p).read_text())
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def norm(s):return re.sub(r'\s+','',html.unescape(s))
def category(e):
 u=urlparse(e['evidence']['url'])
 if e['evidence']['source_type']!='official':return '其它：非官方'
 if u.hostname=='m.mi.com':return '商城新品/产品参数'
 if 'community' in u.hostname:return '社区公告'
 if u.hostname=='ir.mi.com' or '/discover/' in u.path:return '小米官网新闻/业绩公告'
 return '其它：官方发展历程'

def count(rows):
 def c(rs):
  def assertion(r):return any((r.get(k) or {}).get('date') for k in ('release','release_series'))
  def visible(r):return not is_accessory(r) and r.get('kind')!='service' and any((r.get(k) or {}).get('date') and (r.get(k) or {}).get('usage')!='disabled' and (r.get(k) or {}).get('display_allowed',True) and not (r.get(k) or {}).get('internal_only',False) for k in ('release','release_series'))
  return dict(total=len(rs),assertion=sum(bool(assertion(r)) for r in rs),display=sum(bool(visible(r)) for r in rs))
 return dict(all=c(rows),xiaomi=c([r for r in rows if r.get('brand')=='小米']))

def main():
 D=read(ROOT/'data/official/xiaomi-release-dictionary.json')['entries'];B=read(ROOT/'data/official/series-releases.json')
 before=json.loads(gzip.decompress((OUT/'baseline.json.gz').read_bytes()));after=apply_series_releases(before)
 assert len(D)==256 and len({e['id'] for e in D})==256
 assert all(e.get('product_name') and e.get('date') and e.get('evidence',{}).get('quote') and urlparse(e['evidence']['url']).scheme in ('http','https') for e in D)
 result=dict(dictionary_entries=len(D),required_fields_valid=256,sources=dict(collections.Counter(category(e) for e in D)),nonofficial=[dict(id=e['id'],name=e['product_name'],url=e['evidence']['url']) for e in D if e['evidence']['source_type']!='official'],coverage=dict(before=count(before),after=count(after)))
 full=apply_series_releases(apply_release_dates(before))
 result['coverage_isolated']=result['coverage']
 result['coverage_published']=dict(before=count(before),after=count(full))
 result['previous_commit_replayed_dates']=[dict(id=b['id'],name=b['name'],old_release=a.get('release'),release=b.get('release')) for a,b in zip(after,full) if a!=b]
 (OUT/'expected-finalizer.json.gz').write_bytes(gzip.compress(json.dumps(full,ensure_ascii=False).encode(),mtime=0))
 write(OUT/'audit-summary.json',result)
 rng=random.Random(20261104)
 # Fixed stratification, all 30 from the 229 official entries. Third-party seeds listed separately.
 samples=[]
 for origin,n in [('archive',10),('official_newsroom',12),('existing_product_official',8)]:samples+=rng.sample([e for e in D if e['origin']==origin],n)
 # Explicitly include the corrected history entry as a defect regression sample.
 replacement=next(e for e in D if e['product_name']=='小米12系列')
 if replacement not in samples:samples[0]=replacement
 write(OUT/'dictionary-sample-30.json',samples)
 capdir=OUT/'recheck';capdir.mkdir(exist_ok=True);s=requests.Session();s.trust_env=False
 checks=[]
 for e in samples:
  ev=e['evidence'];url=ev.get('capture_url',ev['url']);req=ev.get('request',{});key=hashlib.sha256((url+json.dumps(req,sort_keys=True)).encode()).hexdigest()[:16];mp=capdir/(key+'.json');bp=capdir/(key+'.bin')
  if mp.exists():c=read(mp)
  else:
   c=dict(url=url,request=req,captured_at=datetime.now(timezone.utc).isoformat())
   try:
    if req.get('method')=='POST':r=s.post(url,json=[{},{'productId':req['productId']}],headers={'User-Agent':'Mozilla/5.0','Referer':ev['url']},timeout=35)
    else:r=s.get(url,timeout=35)
    c.update(status=r.status_code,final_url=r.url,sha256=hashlib.sha256(r.content).hexdigest());bp.write_bytes(r.content)
   except Exception as ex:c['error']=str(ex)
   write(mp,c);time.sleep(2.1)
  found=False;parts=ev.get('quote_parts',[ev['quote']]);text=''
  if c.get('status')==200:
   raw=bp.read_bytes()
   if raw.startswith(b'%PDF'):
    subprocess.run(['pdftotext','-layout',str(bp),str(bp.with_suffix('.txt'))],check=True);text=bp.with_suffix('.txt').read_text()
   else:
    text=raw.decode('utf-8','replace')
    try:
     obj=json.loads(text)
     def flatten(o):
      if isinstance(o,dict):
       if 'name' in o and 'value' in o:yield str(o['name'])+'：'+str(o['value'])
       for v in o.values():yield from flatten(v)
      elif isinstance(o,list):
       for v in o:yield from flatten(v)
      elif isinstance(o,str):yield o
     text+='\n'+'\n'.join(flatten(obj))
    except ValueError:pass
    text=html.unescape(re.sub('<[^>]+>',' ',text))
   found=all(norm(q) in norm(text) for q in parts)
  checks.append(dict(id=e['id'],product_name=e['product_name'],date=e['date'],url=ev['url'],capture=c,quote=ev['quote'],quote_found_live=found))
  print(e['product_name'],c.get('status'),found,flush=True)
 write(OUT/'dictionary-live-recheck.json',checks)
 print(json.dumps(result['coverage'],ensure_ascii=False));print('live',sum(x['quote_found_live'] for x in checks),'/30')
if __name__=='__main__':main()
