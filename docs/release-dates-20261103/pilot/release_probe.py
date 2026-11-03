import urllib.request,re,concurrent.futures,json,hashlib
from html.parser import HTMLParser
from pathlib import Path
class Text(HTMLParser):
 def __init__(self):super().__init__();self.parts=[];self.hidden=0
 def handle_starttag(self,t,a):
  if t in ('script','style'):self.hidden+=1
 def handle_endtag(self,t):
  if t in ('script','style'):self.hidden=max(0,self.hidden-1)
 def handle_data(self,d):
  if not self.hidden:self.parts.append(d)
def get(url):
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=35) as r:raw=r.read();final=r.url
  s=Text();s.feed(raw.decode('utf-8','replace'));t=re.sub(r'\s+',' ',' '.join(s.parts)).strip()
  return {'url':url,'final_url':final,'text':t,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
 except Exception as e:return {'url':url,'error':str(e)}
if __name__=='__main__':
 urls=['https://www.fujifilm.com.cn/cn/zh-hans/news/detail/3786','https://www.apple.com.cn/newsroom/2025/03/apple-introduces-ipad-air-with-powerful-m3-chip-and-new-magic-keyboard/','https://www.fujifilm-x.com/zh-cn/products/cameras/x-s20/specifications/','https://www.apple.com.cn/newsroom/sitemap.xml','https://www.apple.com/newsroom/sitemap.xml','https://www.mi.com/xiaomi-14/specs','https://www.bydauto.com.cn/cn/parameter-comparison?goodsId=165','https://item.jd.com/100053477906.html']
 for o in concurrent.futures.ThreadPoolExecutor(6).map(get,urls):
  p=Path('docs/release-dates-20261103/evidence')/(hashlib.sha256(o['url'].encode()).hexdigest()[:16]+'.json');p.write_text(json.dumps(o,ensure_ascii=False,indent=1));t=o.get('text','');print(o['url'],o.get('error',o.get('bytes')),t[:100]);print([t[max(0,m.start()-65):m.end()+95] for m in re.finditer(r'发售|开售|上市|2023年|2025 年|Available|available',t)][:8])
