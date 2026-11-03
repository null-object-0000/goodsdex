import json,re,concurrent.futures
from urllib.parse import urljoin
from capture import *
def dji():
 archive=json.load(open('docs/release-dates-round3-20261103/dji-archive-discovery.json'))
 # Full existing 40-page index, newest first; broaden beyond title-filtered recent pilot.
 entries=archive['entries'];selected=[a for a in entries if a['published_at']<'2023' and ('产品发布' in a['tags'] or re.search('发布|推出|上市|发售',a['title']))]
 selected=sorted(selected,key=lambda a:a['published_at'],reverse=True)[:220]
 save('dji-plan.json',dict(index_reused='round3:40 pages',indexed=len(entries),selected=selected))
 out=[]
 for a in selected:out.append(dict(entry=a,capture=get('https://www.dji.com/cn/media-center/announcements/'+a['slug'])));save('dji-articles.json',out)
def other():
 urls=['https://www.mi.com/robots.txt','https://www.mi.com/sitemap.xml','https://www.mi.com/about/','https://ir.mi.com/zh-hans/news-events/news-releases','https://www.mi.com/global/discover/','https://www.hp.com/cn-zh/hp-information.html','https://www.hp.com/cn-zh/newsroom.html','https://www.hp.com/cn-zh/newsroom/press-releases.html','https://www.hpstore.cn/robots.txt','https://www.hpstore.cn/sitemap.xml','https://www.byd.com/cn/news','https://www.byd.com/robots.txt','https://www.fujifilm.com.cn/robots.txt','https://www.fujifilm.com.cn/sitemap.xml','https://www.apple.com.cn/newsroom/sitemap.xml']
 out=[]
 for u in urls:out.append(get(u));save('entry-captures.json',out)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(lambda f:f(),[dji,other]))
