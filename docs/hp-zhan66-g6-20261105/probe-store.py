import urllib.request,urllib.parse,concurrent.futures,json,hashlib
from pathlib import Path
p=Path('docs/hp-zhan66-g6-20261105')
base='https://www.hpstore.cn/'
q='{products(filter:{sku:{eq:"7P2D5PC"}}){items{sku name description{html} short_description{html}}}}'
urls=[base+'hp-probook-450-15-6-inch-g10-notebook-pc-7p2d5pc.html',base+'rest/V1/products/7P2D5PC',base+'graphql?'+urllib.parse.urlencode({'query':q}),base+'catalogsearch/result/?q=7P2D5PC']
def get(t):
 i,u=t
 try:
  r=urllib.request.build_opener(urllib.request.ProxyHandler({})).open(u,timeout=20);b=r.read();f=p/f'store-probe-{i}.txt';f.write_bytes(b);return dict(url=u,status=r.status,final_url=r.url,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),file=str(f))
 except Exception as e:return dict(url=u,error=str(e))
x=list(concurrent.futures.ThreadPoolExecutor(4).map(get,enumerate(urls)));(p/'store-probes.json').write_text(json.dumps(x,indent=1));print(json.dumps(x,indent=1))
