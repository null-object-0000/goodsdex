import re,json,concurrent.futures
from urllib.parse import urljoin
from capture import *
def hp():
 out=[]
 for u in ['https://www.hp.com/us-en/newsroom.html','https://www.hp.com/us-en/newsroom/press-releases.html','https://www.hpstore.cn/sitemap-1-1.xml','https://www.hpstore.cn/sitemap-1-2.xml','https://www.hpstore.cn/sitemap-1-3.xml']:
  o=get(u);out.append(o);save('hp-index.json',out)
  if o['http_status']==200:
   links=list(dict.fromkeys(urljoin(u,x) for x in re.findall(r'(?:href=["\x27]|<loc>)([^"\x27<]+)',html(o)) if re.search('/press-releases/|/news/|/newsroom/press|/announcement|/blog',x)))
   for v in links[:80]:out.append(get(v));save('hp-index.json',out)
def byd():
 out=[]
 for u in ['https://www.byd.com/component/byd-cn/news/news-list/news-newsList_1c801f5d14021000.js','https://www.byd.com/sitemap.xml']:
  out.append(get(u));save('byd-index.json',out)
def fuji():
 out=[]
 for u in ['https://www.fujifilm.com.cn/cn/zh-hans/news?page=1','https://www.fujifilm.com.cn/cn/zh-hans/news?page=7','https://www.fujifilm.com.cn/cn/zh-hans/news?page=8']:
  out.append(get(u));save('fuji-index.json',out)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(lambda f:f(),[hp,byd,fuji]))
