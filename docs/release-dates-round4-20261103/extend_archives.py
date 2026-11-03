import json,re,concurrent.futures
from urllib.parse import urljoin
from capture import *
def mi():
 out=[]
 for u in ['https://www.mi.com/about/news/','https://www.mi.com/about/news','https://ir.mi.com/zh-hans/news-events/news-releases?page=0','https://ir.mi.com/zh-hans/news-events/news-releases?page=1']:
  o=get(u);out.append(o);save('mi-index.json',out)
  if o.get('http_status')==200:
   links=list(dict.fromkeys(urljoin(u,x.replace('&amp;','&')) for x in re.findall(r'href=["\x27]([^"\x27]+)',html(o)) if re.search('news-details|news-detail|news/\d|xinwen|news-releases/news',x)))
   for v in links[:60]:out.append(get(v));save('mi-index.json',out)
def apple():
 o=get('https://www.apple.com.cn/newsroom/sitemap.xml')
 urls=list(dict.fromkeys(re.findall(r'https://www\.apple\.com\.cn/newsroom/\d{4}/\d{2}/[^\s<]+/',html(o))))
 selected=[u for u in urls if re.search(r'apple-(introduces|unveils|announces|updates)|introducing|new-|all-new-',u) and not re.search('music|arcade|podcast|store|fitness|developer|security|software|ios-|ipados|macos|watchos|tv-plus|services|education|results|earnings',u)]
 save('apple-plan.json',dict(indexed=len(urls),selected=selected,cap=240))
 out=[]
 for u in sorted(selected,reverse=True)[:240]:out.append(get(u));save('apple-articles.json',out)
def fuji():
 old=json.load(open('docs/release-dates-round3-20261103/fuji-archive-discovery.json'))
 selected=[(u,t) for u,t in old.items() if re.search('推出|发布|上市',t)]
 out=[]
 for u,t in selected:out.append(dict(title=t,capture=get('https://www.fujifilm.com.cn'+u)));save('fuji-articles.json',out)
 # Sitemap is an additional historical-discovery entrance, not guess-number enumeration.
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(lambda f:f(),[mi,apple,fuji]))
