"""Inspect every missing published DJI SKU; do not infer dates from page metadata."""
import concurrent.futures,json,re
from capture import get,ROOT
rows=[r for r in json.load(open('/tmp/goodsdex-round6-before.json')) if r.get('brand')=='大疆' and not (r.get('release') or {}).get('date')]
def inspect(r):
 o=get(r['source_url']);t=o['text'];snips=[]
 for m in re.finditer(r'上市|发布|发售|20\d{2}\s*年|20\d{2}-\d{2}-\d{2}',t):
  s=t[max(0,m.start()-65):m.end()+100]
  if s not in snips:snips.append(s)
 return dict(id=r['id'],name=r['name'],kind=r.get('kind'),source_url=r['source_url'],capture_file=o['evidence_file'],http_status=o['http_status'],snippets=snips)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 out=list(pool.map(inspect,rows))
(ROOT/'dji-product-probes.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
