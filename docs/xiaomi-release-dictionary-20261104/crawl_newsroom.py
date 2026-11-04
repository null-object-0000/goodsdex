"""Enumerate official newsroom pagination, not product-by-product searches."""
from crawl import capture,OUT,ROOT
import json
index=[]
for page in range(1,41):
 c=capture(f'https://go.buy.mi.com/global/page/discovery?from=pc&page_num={page}&show_type=newsroom')
 if c.get('error'):break
 d=json.loads((ROOT/c['capture_file']).read_bytes())
 entries=[a for p in (d.get('data',{}).get('page_data') or []) for a in p.get('assembly_info',[]) if a.get('go_to_url')]
 if not entries:break
 for a in entries:
  index.append(dict(title=a['title'],description=a['description'],url=a['go_to_url'],index_capture=c['capture_file'],metadata=json.loads(a.get('extended') or '{}')))
 (OUT/'newsroom-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n')
