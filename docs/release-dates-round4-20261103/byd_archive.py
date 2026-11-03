import json,re
from capture import *
out=[];entries=[]
for i in range(1,16):
 o=get('https://cms-api.byd.com/es/search',dict(brandName='byd',siteName='cn',page=i,size=12,type='news',sortField='date'));out.append(o)
 if o['http_status']!=200:break
 d=json.loads(o['text']);entries+=d.get('data',{}).get('records',[]);save('byd-archive.json',dict(pages=out,entries=entries))
selected=[a for a in entries if re.search('汉|海豚|夏|宋Pro|元PLUS|秦PLUS|智驾|飞驰',a['title'])]
save('byd-selected.json',selected)
articles=[]
for a in selected:
 o=get('https://www.byd.com'+a['url']);articles.append(dict(entry=a,capture=o));save('byd-articles.json',articles)
