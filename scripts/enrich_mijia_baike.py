import sys,json,hashlib,subprocess,re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,str(Path(__file__).resolve().parent))
from collect_mijia_baike import collect,fetch,BASE
import argparse
parser=argparse.ArgumentParser()
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
root=args.output; mapping=json.loads((root/'mapping.json').read_text())
models=sorted({m for x in mapping['items'] for m in x['models']}|{'mibx5.washer.x15'})

def run(m):
 x=collect(m,root/'raw');d=x.get('response',{}).get('data') or {};out={'model':m,'productName':d.get('name'),'product_url':x['url'],'product_sha256':x.get('sha256'),'materialPictures':d.get('materialPictures') or [],'image_missing':not bool(d.get('materialPictures')),'attributeMap':d.get('attributeMap') or []}
 for endpoint,suffix in [('introduction','&region=cn'),('attribute','')]:
  p=root/'raw'/f'{m}.{endpoint}.json'
  url=BASE+endpoint+'?model='+m+suffix
  try:
   raw=p.read_bytes() if p.exists() else fetch(url)
   p.write_bytes(raw); v=json.loads(raw)
   out[endpoint]={'url':url,'sha256':hashlib.sha256(raw).hexdigest(),'response':v}
  except Exception as e:out[endpoint]={'error':str(e)}
 intro=(out['introduction'].get('response',{}).get('data') or {});pdf=(intro.get('introductionPdf') or {}).get('url');out['manual_url']=pdf or intro.get('introductionHtml');out['manual_type']=intro.get('introductionType');out['hardware_models']=[]
 if pdf:
  try:
   p=root/'manuals'/f'{m}.pdf';p.parent.mkdir(exist_ok=True)
   if not p.exists():p.write_bytes(fetch(pdf))
   if not p.read_bytes().startswith(b'%PDF'):raise ValueError('not PDF')
   out['manual_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
   target=p.with_suffix('.page1.txt');subprocess.run(['pdftotext','-f','1','-l','1','-layout',str(p),str(target)],check=True,stderr=subprocess.DEVNULL)
   txt=target.read_text();from goodsdex.mijia_baike import hardware_models
   out['hardware_models']=hardware_models(txt)
   # Candidate tokens stay evidence only: specifications and model labels need review.
   out['hardware_model_status']='page1_model_labels'
  except Exception as e:out['manual_error']=str(e)
 out['parameter_count']=len(out['attributeMap'])+len((out['attribute'].get('response',{}).get('data') or {}).get('list') or [])
 return out
with ThreadPoolExecutor(max_workers=8) as pool:
 results=[]
 for i,x in enumerate(pool.map(run,models),1):
  results.append(x)
  if i%40==0:print(i,'/',len(models),flush=True)
(root/'enriched.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print('done',len(results),flush=True)
