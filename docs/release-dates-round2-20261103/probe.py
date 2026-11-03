"""Capture HTTP status, complete response hash and visible text without script dates."""
import urllib.request,urllib.error,json,re,hashlib,sys,concurrent.futures,gzip
from pathlib import Path
from datetime import datetime,timezone
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parent
class Text(HTMLParser):
 def __init__(self):super().__init__();self.parts=[];self.hidden=0
 def handle_starttag(self,t,a):
  if t in ('script','style'):self.hidden+=1
 def handle_endtag(self,t):
  if t in ('script','style'):self.hidden=max(0,self.hidden-1)
 def handle_data(self,d):
  if not self.hidden:self.parts.append(d)
def get(url):
 key=hashlib.sha256(url.encode()).hexdigest()[:16];p=ROOT/'evidence'/f'web-{key}.json'
 if p.exists() and not (ROOT/'evidence'/f'web-{key}.html').read_bytes().startswith(b'\x1f\x8b'):return json.loads(p.read_text())
 o=dict(url=url,captured_at=datetime.now(timezone.utc).isoformat());raw=b''
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=40) as r:raw=r.read();o.update(http_status=r.status,final_url=r.url)
 except urllib.error.HTTPError as e:raw=e.read();o.update(http_status=e.code,error=str(e),final_url=e.url)
 except Exception as e:o.update(http_status=0,error=str(e))
 decoded=gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw
 rawtext=decoded.decode('utf-8','replace');t=Text();t.feed(rawtext);o.update(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),text=re.sub(r'\s+',' ',' '.join(t.parts)).strip())
 (ROOT/'evidence'/f'web-{key}.html').write_bytes(raw)
 p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n');return o
if __name__=='__main__':
 urls=json.load(open(sys.argv[1]))
 for o in concurrent.futures.ThreadPoolExecutor(5).map(get,urls):
  print(o['url'],o['http_status'],o['bytes'],[(o['text'][max(0,m.start()-45):m.end()+95]) for m in re.finditer('上市|发售|开售|即日起|今日发布|发布时间|发布日期|验证|登录',o['text'])][:12],flush=True)
