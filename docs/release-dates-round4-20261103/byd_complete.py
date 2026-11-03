import json
from capture import *
out=[]
for a in json.load(open(ROOT/'byd-archive.json'))['entries']:
 o=get('https://www.byd.com'+a['url']);out.append(dict(entry=a,capture={k:o.get(k) for k in ['url','http_status','sha256','bytes','evidence_file','error']}));save('byd-complete.json',out)
print('DONE',len(out),flush=True)
