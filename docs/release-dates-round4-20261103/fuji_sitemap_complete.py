import json
from capture import *
out=[]
for u in json.load(open(ROOT/'fuji-sitemap-plan.json'))['extra']:
 o=get(u);out.append({k:o.get(k) for k in ['url','http_status','sha256','bytes','evidence_file','error']});save('fuji-sitemap-extra.json',out)
print('DONE',len(out),flush=True)
