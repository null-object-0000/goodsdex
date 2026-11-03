"""Read-only exact-ID mobile scan. No LLM calls; checkpoint one file per request."""
import sys,json,hashlib,concurrent.futures
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from goodsdex.sources.mi_cn import _mtop_call,MTOP_URL
ROOT=Path(__file__).resolve().parent

def walk(x,p='$'):
 if isinstance(x,dict):
  if x.get('name') in ('发布时间','发布日期','上市时间','上市日期'):yield dict(locator=p,**x)
  for k,v in x.items():yield from walk(v,p+'.'+k)
 elif isinstance(x,list):
  for i,v in enumerate(x):yield from walk(v,p+f'[{i}]')

def collect(r):
 pid=r['id'].split(':')[-1];p=ROOT/'evidence'/f'mi-{pid}.json'
 if p.exists():return json.loads(p.read_text())
 d,raw,status,error=_mtop_call(pid)
 o=dict(id=r['id'],name=r['name'],category=r.get('category'),url=MTOP_URL,request={'method':'POST','productId':pid},captured_at=datetime.now(timezone.utc).isoformat(),http_status=status,error=error,code=d.get('code'),message=d.get('message'),product=d.get('data',{}).get('product'),nodes=list(walk(d)),sha256=hashlib.sha256(raw.encode()).hexdigest())
 p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n');return o
if __name__=='__main__':
 rows=json.load(open('/tmp/goodsdex-release-dates/public/goods.json'))
 rows=[r for r in rows if r['id'].startswith('CN:mi_cn:')]
 with concurrent.futures.ThreadPoolExecutor(6) as pool:
  for i,o in enumerate(pool.map(collect,rows)):
   if i%100==0 or o['nodes']:print(i,o['id'],o['name'],o['http_status'],o['code'],[(n['name'],n.get('value'),n.get('isPageShow')) for n in o['nodes']],flush=True)
