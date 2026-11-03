import re
from capture import *
out=[]
for u in ['https://www.bydglobal.com','https://www.bydglobal.com/robots.txt','https://www.bydglobal.com/sitemap.xml','https://www.bydglobal.com/cn/news.html']:
 o=get(u);out.append(o);save('byd-group-entry.json',out)
 if o['http_status']==200:print(o['url'],o['text'][:600],flush=True)
