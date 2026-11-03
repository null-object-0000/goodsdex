import json
from capture import *
entries=json.load(open('docs/release-dates-round3-20261103/fuji-archive-discovery.json'));out=[]
for u,title in entries.items():
 o=get('https://www.fujifilm.com.cn'+u);out.append(dict(title=title,capture={k:o.get(k) for k in ['url','http_status','sha256','bytes','evidence_file','error']}));save('fuji-complete.json',out)
print('DONE',len(out),flush=True)
