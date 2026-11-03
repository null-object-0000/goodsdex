"""Public archive capture: shared per-host 2.1s spacing, cached evidence, no login/retries."""
import gzip,hashlib,json,re,time,threading,urllib.request,urllib.error,fcntl
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlsplit,quote
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parent
_lock=threading.Lock();_last={};_cache={}
for folder in ['docs/release-dates-20261103/evidence','docs/release-dates-round2-20261103/evidence','docs/release-dates-round3-20261103/evidence',str(ROOT/'evidence')]:
 for p in Path(folder).glob('*.json'):
  try:
   o=json.loads(p.read_text())
   if isinstance(o,dict) and o.get('url') and o.get('text') and ((o.get('raw_file') and 'ascii' not in o.get('error','')) or (not o['url'].endswith('.xml') and len(o['text'])>2000)):
    if o['url'] not in _cache or o.get('captured_at','')>=_cache[o['url']][1].get('captured_at',''):_cache[o['url']]=(p,o)
  except (ValueError,OSError):pass
class Text(HTMLParser):
 def __init__(self):super().__init__();self.parts=[];self.hidden=0
 def handle_starttag(self,t,a):
  if t in ('script','style'):self.hidden+=1
 def handle_endtag(self,t):
  if t in ('script','style'):self.hidden=max(0,self.hidden-1)
 def handle_data(self,s):
  if not self.hidden:self.parts.append(s)
def get(url, payload=None):
 cache_key=url if payload is None else url+"#POST:"+json.dumps(payload,sort_keys=True)
 if cache_key in _cache:
  p,o=_cache[cache_key];return dict(o,evidence_file=str(p))
 host=urlsplit(url).netloc
 with _lock, open('/tmp/goodsdex-round4-rate-'+hashlib.sha256(host.encode()).hexdigest()[:16], 'a+') as rate:
  fcntl.flock(rate,fcntl.LOCK_EX);rate.seek(0);previous=rate.read()
  delay=2.15-(time.time()-float(previous or '0'))
  if delay>0:time.sleep(delay)
  rate.seek(0);rate.truncate();rate.write(str(time.time()));rate.flush()
 o=dict(url=url,request=payload,captured_at=datetime.now(timezone.utc).isoformat());raw=b''
 try:
  with urllib.request.urlopen(urllib.request.Request(quote(url,safe=':/?=&%'),data=json.dumps(payload).encode() if payload is not None else None,headers={'User-Agent':'Mozilla/5.0','Accept-Encoding':'identity','Content-Type':'application/json'}),timeout=25) as r:raw=r.read();o.update(http_status=r.status,final_url=r.url)
 except urllib.error.HTTPError as e:raw=e.read();o.update(http_status=e.code,final_url=e.url,error=str(e))
 except Exception as e:o.update(http_status=0,error=str(e))
 decoded=gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw
 h=decoded.decode('utf-8','replace');p=Text();p.feed(h)
 key=hashlib.sha256(cache_key.encode()).hexdigest()[:20]
 o.update(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),text=re.sub(r'\s+',' ',' '.join(p.parts)).strip(),raw_file=hashlib.sha256(raw).hexdigest()+'.response.gz')
 path=ROOT/'evidence'/(key+'-'+hashlib.sha256(raw).hexdigest()[:12]+'.json');(path.parent/o['raw_file']).write_bytes(gzip.compress(raw,mtime=0));path.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n');_cache[cache_key]=(path,o)
 print(o['http_status'],len(raw),url,flush=True)
 return dict(o,evidence_file=str(path))
def html(o):
 p=Path(o['evidence_file']);
 if not o.get('raw_file'):return o['text']
 raw=gzip.decompress((p.parent/o['raw_file']).read_bytes());raw=gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw;return raw.decode('utf-8','replace')
def save(name,obj):(ROOT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
