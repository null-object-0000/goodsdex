"""Twenty preselected missing exact products; no first-result matching."""
import json,re
from urllib.parse import quote
from capture import ROOT,many
rows=json.load(open('/tmp/goodsdex-round3-before.json'));by={r['id']:r for r in rows}
ids=['CN:hp_cn:sku:'+p for p in ['7Y0Y4PC','7Z5S1PC','915D1PC','9X2Y9PC','BL9C1PC']]
ids+=['CN:mi_cn:product:'+p for p in ['19963','20435','23630','4348','20618']]
ids+=['CN:dji:sku:'+p for p in ['101241','107481','144651','169791','173511']]
ids+=['CN:fuji:'+p for p in ['model:x-m5','model:x-t50','model:x-h2s','kit:x-s20-xc35mm','lens:xc15-45mmf35-56-ois-pz']]
probes=[dict(id=k,brand=by[k].get('brand') or '小米',model=by[k]['name'],query=by[k].get('part_number') or by[k]['name']) for k in ids]
urls=['https://search.jd.com/Search?keyword='+quote(p['query'])+'&enc=utf-8' for p in probes]
urls+=['https://so.m.jd.com/ware/search.action?keyword='+quote(p['query']) for p in probes]
res=many(urls)
for i,p in enumerate(probes):
 p['searches']=[res[i],res[i+20]]
 p.update(matched_sku=None,has_launch_field=None,original_quote=None,correct=None,accepted=False,
          reason='Exact SKU not verified; search blocked, login shell, or no unique exact identity; no first-result selection')
(ROOT/'jd-probes.json').write_text(json.dumps(probes,ensure_ascii=False,indent=2)+'\n')
for p in probes:print(p['brand'],p['query'],[(x['http_status'],x['final_url'] if 'final_url' in x else x.get('error'),x['text'][:110]) for x in p['searches']],flush=True)
