"""Discover exact-name mentions from public publisher tag pages, never infer dates."""
import gzip,json,time
from pathlib import Path
from urllib.parse import urlencode
import verify_release_l7 as verifier
from goodsdex.release_l7 import body_text
from goodsdex.release_media import normalize
from goodsdex.release_coverage import effective
OUT=Path('docs/release-coverage/L7-scale').resolve()
verifier.OUT=OUT
rows=json.loads(gzip.decompress((OUT/'baseline.json.gz').read_bytes()))
missing=list({r['id']:r for r in rows if r.get('brand') in ('小米','亚朵星球','比亚迪') and not effective(r)}.values())
found={}
old=OUT/'discovery.json'
if old.exists():found={x['url']:x for x in json.loads(old.read_text())}
for tag,limit in [('米家',180),('小米',100),('Redmi',60),('亚朵',5),('比亚迪',20),('米兔',30),('90分',20),('小米路由器',25),('小米笔记本',25),('8H',20),('小爱音箱',20),('红米4',10),('红米6A',10),('小米移动电源',20)]:
 for page in range(1,limit+1):
  u='https://m.ithome.com/api/news/newstaglistpageget?'+urlencode(dict(NewsTag=tag,PageNo=page))
  c=verifier.fetch(u)
  if c.get('http_status')!=200:break
  try:v=json.loads(gzip.decompress((Path(c['capture_file'])).read_bytes()))
  except (ValueError,KeyError):break
  news=v.get('Result')
  if not isinstance(news,list) or not news:break
  for n in news:
   text=body_text(n.get('c','').encode());norm=normalize(text)
   matches=[{k:r.get(k) for k in ('id','name','brand')} for r in missing if len(normalize(r['name']))>=4 and normalize(r['name']) in norm]
   if not matches:continue
   sid=str(n['newsid']).zfill(6);url='https://www.ithome.com/'+str(int(sid[:-6]) if len(sid)>6 else 0)+'/'+sid[-6:-3]+'/'+sid[-3:]+'.htm'
   found[url]=dict(url=url,title=n['title'],published=n.get('postdate'),body=text,models=matches,discovery_capture=c)
  old.write_text(json.dumps(list(found.values()),ensure_ascii=False,indent=2))
  print(tag,page,'articles',len(found),'model_mentions',sum(len(x['models']) for x in found.values()),flush=True)
  if page%50==0:time.sleep(5)
