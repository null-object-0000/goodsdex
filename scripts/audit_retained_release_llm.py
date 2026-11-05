import json,sys,hashlib,re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import argparse
p=argparse.ArgumentParser();p.add_argument('--goods',type=Path,required=True);a=p.parse_args()
from collect_release_tolerance import capture,save
from goodsdex.release_structured import Page,norm
rows=[r for r in json.loads(a.goods.read_text()) if (r.get('release')or{}).get('source')=='llm']
directory=ROOT/'docs/release-coverage/tolerance-llm-retained';directory.mkdir(exist_ok=True)
urls=sorted({r['release']['evidence']['url'] for r in rows})
with ThreadPoolExecutor(max_workers=6) as pool:cs=list(pool.map(lambda u:capture(u,directory),urls))
by_url={c['url']:c for c in cs};audits=[]
for row in rows:
 r=row['release'];e=r['evidence'];c=by_url[e['url']];quote=e['quote'].split(' | ',1)[-1]
 text=Page(Path(c['capture_file']).read_bytes().decode('utf-8')).text if c['status']=='captured' else ''
 supported=bool(text and norm(quote) in norm(text))
 audits.append(dict(id=row['id'],name=row['name'],date=r['date'],event=r['event'],quote_found=supported,capture=c,quote=quote))
save(directory/'audit.json',audits)
print('captured',sum(c['status']=='captured' for c in cs),'quoted',sum(a['quote_found'] for a in audits))
for a in audits:
 print(a['id'],a['name'],a['date'],a['quote_found'])
