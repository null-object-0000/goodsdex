import json
from capture import *
entries=[];pages=[];out=[]
for i in range(1,4):
 o=get('https://cms-prod.byd.com/es/search',dict(brandName='bydglobal',siteName='cn',type='news',page=i,size=12,sortField='date',asc=False,tags=[]));pages.append(o)
 if o['http_status']!=200:break
 entries+=json.loads(o['text'])['data']['records'];save('byd-group-archive.json',dict(pages=pages,entries=entries))
for a in entries:
 o=get('https://www.bydglobal.com'+a['url']);out.append(dict(entry=a,capture={k:o.get(k) for k in ['url','http_status','sha256','bytes','evidence_file','error']}));save('byd-group-complete.json',out)
print('DONE',len(out))
