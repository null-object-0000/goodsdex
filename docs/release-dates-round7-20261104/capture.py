"""Explicit media URLs only; no retailer or official crawling."""
import subprocess,hashlib,json,re,gzip
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import urlparse
from html.parser import HTMLParser
class TextParser(HTMLParser):
 def __init__(self):super().__init__();self.parts=[];self.skip=0
 def handle_starttag(self,t,a):
  if t in ('script','style'):self.skip+=1
 def handle_endtag(self,t):
  if t in ('script','style'):self.skip=max(0,self.skip-1)
 def handle_data(self,d):
  if not self.skip:self.parts.append(d)

ROOT=Path(__file__).resolve().parent
DOMAINS=('ithome.com','mydrivers.com','zol.com.cn','pconline.com.cn')
def capture(url):
 h=urlparse(url).hostname
 if not any(h==d or h.endswith('.'+d) for d in DOMAINS):raise ValueError(url)
 key=hashlib.sha256(url.encode()).hexdigest()[:16];p=ROOT/'evidence'/f'{key}.json';p.parent.mkdir(exist_ok=True)
 if p.exists():return json.loads(p.read_text())
 now=datetime.now(timezone.utc).isoformat()
 result=subprocess.run(['curl','-fsS','--max-time','30',url],capture_output=True,check=True)
 raw=result.stdout
 if raw.startswith(b'\x1f\x8b'):raw=gzip.decompress(raw)
 charset=re.search(br'charset=[\"\']?([A-Za-z0-9_-]+)',raw[:10000])
 encoding=charset[1].decode() if charset else 'utf-8'
 soup=TextParser();soup.feed(raw.decode(encoding,errors='replace'))
 text=re.sub(r'\s+',' ',' '.join(soup.parts)).strip()
 (p.with_suffix('.html.gz')).write_bytes(gzip.compress(raw,mtime=0))
 v=dict(url=url,status=200,captured_at=now,sha256=hashlib.sha256(raw).hexdigest(),text=text)
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2));return v
if __name__=='__main__':
 import sys
 for u in sys.argv[1:]:
  try:
   v=capture(u);print(v['url'],len(v['text']))
  except Exception as e:print(u,type(e).__name__,str(e))
