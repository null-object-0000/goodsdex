import re,json
from urllib.parse import urljoin
from capture import *
entries=[];pages=[]
for i in range(1,4):
 o=get(f'https://www.hpstore.cn/sitemap-1-{i}.xml');pages.append(o);entries+=re.findall(r'<loc>(.*?)</loc>',html(o))
selected=[u for u in entries if '/blog/' in u or re.search('news|notice|announcement',u)]
save('hp-china-plan.json',dict(sitemaps=pages,indexed=len(entries),selected=selected,cap=100))
out=[]
for u in selected[:100]:out.append(get(u));save('hp-china-articles.json',out)
