import requests,json,gzip,hashlib,re,time,tarfile
from pathlib import Path
from datetime import datetime,timezone
from goodsdex.mi_names import page_name
root=Path('docs/mihome-independent-20261106');(root/'source-pages').mkdir(exist_ok=True)
rows={r['id']:r for r in json.loads(Path('.task-tmp/goods-after.json').read_text())}
entries={e['id']:e for e in json.loads(Path('data/official/mihome-catalog.json').read_text())['items']}
keys=json.loads((root/'sample-candidates.json').read_text())[:10];results=[]
with tarfile.open('docs/mihome-catalog-20261106/evidence.tar.gz') as archive:
 for key in keys:
  r,e=rows[key],entries[key];pid=key.rsplit(':',1)[1];url=f'https://www.mi.com/shop/buy/detail?product_id={pid}'
  obs=dict(id=key,name=r['name'],name_mihome=r['name_mihome'],name_source=r['name_source'],url=url,requested_at=datetime.now(timezone.utc).isoformat())
  try:
   response=requests.get(url,timeout=35);raw=response.content
   (root/'source-pages'/f'{pid}.html.gz').write_bytes(gzip.compress(raw,mtime=0))
   obs.update(status=response.status_code,sha256=hashlib.sha256(raw).hexdigest(),title=re.search(r'<title[^>]*>(.*?)</title>',response.text,re.S).group(1))
   obs['official_page_name']=page_name(response.text);obs['exact_official_match']=obs['official_page_name']==r['name']
  except Exception as ex:obs['error']=str(ex)
  raw=archive.extractfile(e['source_file']).read();assert hashlib.sha256(raw).hexdigest()==e['source_sha256']
  d=next(d for d in json.loads(raw)['data']['productList'] if d['model']==e['model'] and d['pdId']==e['pd_id'])
  obs.update(mihome_page_name=d['name'],exact_mihome_match=d['name']==r['name_mihome'],mihome_source_url=e['source_url'],mihome_source_sha256=e['source_sha256'])
  obs['display_name_correct']=r['catalog_display']['name']==r['name']
  results.append(obs);print(key,obs.get('exact_official_match'),obs.get('error'),flush=True);time.sleep(2.2)
(root/'sample-10-sources.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
