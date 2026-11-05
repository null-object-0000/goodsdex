"""Continue captured IT Home discovery over missing exact catalogue identities."""
import gzip,json,time,re
from pathlib import Path
from urllib.parse import urlencode
import verify_release_l7 as verifier
from goodsdex.release_l7 import body_text
from goodsdex.release_media import normalize
from goodsdex.release_coverage import effective
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/release-coverage/L7-gap'
verifier.OUT=OUT
rows=json.loads(gzip.decompress((OUT/'baseline.json.gz').read_bytes()))
missing=list({r['id']:r for r in rows if r.get('brand') in ('小米','亚朵星球','比亚迪') and not effective(r)}.values())
found={}
p=OUT/'discovery.json'
if p.exists():found={d['url']:d for d in json.loads(p.read_text())}
# Earlier scale run covered 小米 pages 1..100 and 米家 pages 1..180.
for tag,start,end in [('小米',101,350),('红米',1,50),('亚朵星球',1,5),('亚朵',1,5)]:
 for page in range(start,end+1):
  u='https://m.ithome.com/api/news/newstaglistpageget?'+urlencode(dict(NewsTag=tag,PageNo=page))
  c=verifier.fetch(u)
  if c.get('http_status')!=200:break
  try:news=json.loads(gzip.decompress((ROOT/c['capture_file']).read_bytes())).get('Result')
  except (ValueError,KeyError):break
  if not isinstance(news,list) or not news:break
  for n in news:
   text=body_text(n.get('c','').encode());norm=normalize(text)
   matches=[{k:r.get(k) for k in ('id','name','brand')} for r in missing if len(normalize(r['name']))>=4 and normalize(r['name']) in norm]
   if not matches:continue
   sid=str(n['newsid']).zfill(6);url='https://www.ithome.com/'+str(int(sid[:-6]) if len(sid)>6 else 0)+'/'+sid[-6:-3]+'/'+sid[-3:]+'.htm'
   found[url]=dict(url=url,title=n['title'],published=n.get('postdate'),body=text,models=matches,discovery_capture=c)
  p.write_text(json.dumps(list(found.values()),ensure_ascii=False,indent=2))
  print(tag,page,'articles',len(found),'mentions',sum(len(x['models']) for x in found.values()),flush=True)
  if (page-start+1)%50==0:time.sleep(5)
