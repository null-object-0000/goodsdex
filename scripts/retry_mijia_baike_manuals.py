from pathlib import Path
import json,subprocess,concurrent.futures
import argparse
parser=argparse.ArgumentParser()
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
root=args.output;rows=json.loads((root/'collected-models.json').read_text());enriched=json.loads((root/'enriched.json').read_text());by={x['model']:x for x in enriched}
models={x['model'] for x in rows if x['manual_status']=='download_failed'}|{x['model'] for x in enriched if x.get('manual_error')}
def retry(x):
 if x['model'] not in models:return
 p=root/'manuals'/(x['model']+'.pdf');new=p.with_suffix('.retry.pdf')
 url=x['manual_url']
 proc=subprocess.run(['curl','--fail','--location','--silent','--show-error','--max-time','90',url,'-o',str(new)],capture_output=True)
 if proc.returncode==0 and new.read_bytes().startswith(b'%PDF'):
  valid=subprocess.run(['pdfinfo',str(new)],capture_output=True)
  if valid.returncode==0:
   new.replace(p); target=p.with_suffix('.page1.txt');out=subprocess.run(['pdftotext','-f','1','-l','1','-layout',str(p),str(target)],capture_output=True)
   if out.returncode==0:by[x['model']].pop('manual_error',None)
   print(x['model'],'retried',p.stat().st_size,flush=True);return
 if new.exists():new.unlink()
 print(x['model'],'retry_failed',proc.returncode,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(retry,rows))
(root/'enriched.json').write_text(json.dumps(enriched,ensure_ascii=False,indent=2))
