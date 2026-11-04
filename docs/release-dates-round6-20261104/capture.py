"""Bounded public captures. No retries; blocked commerce hosts are forbidden."""
import gzip, hashlib, json, subprocess, time
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlsplit
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parent
class Text(HTMLParser):
 def __init__(self): super().__init__(); self.parts=[]; self.hidden=0
 def handle_starttag(self,t,a):
  if t in ('script','style'): self.hidden+=1
 def handle_endtag(self,t):
  if t in ('script','style'): self.hidden=max(0,self.hidden-1)
 def handle_data(self,s):
  if not self.hidden:self.parts.append(s)
def get(url, payload=None):
 assert not any(h in urlsplit(url).netloc for h in ['hpstore.cn','jd.com','tmall.com'])
 key=hashlib.sha256((url+('' if payload is None else json.dumps(payload,sort_keys=True))).encode()).hexdigest()[:20]; p=ROOT/'evidence'/f'{key}.json'
 if p.exists():return json.loads(p.read_text())
 raw=ROOT/'evidence'/f'{key}.html'; time.sleep(2.2)
 command=['curl','-L','--max-redirs','4','--max-time','30','-sS','-A','Mozilla/5.0','-o',str(raw),'-w','%{http_code}\n%{url_effective}',url]
 if payload is not None:command += ['-H','Content-Type: application/json','--data-binary',json.dumps(payload)]
 r=subprocess.run(command,capture_output=True,text=True)
 parts=r.stdout.splitlines();body=raw.read_bytes() if raw.exists() else b'';parser=Text();decoded=gzip.decompress(body) if body.startswith(b'\x1f\x8b') else body;parser.feed(decoded.decode('utf-8','replace'))
 o=dict(url=url,request=payload,http_status=int(parts[0]) if parts and parts[0].isdigit() else 0,final_url=parts[-1] if len(parts)>1 else url,error=r.stderr if r.returncode else None,sha256=hashlib.sha256(body).hexdigest(),captured_at=datetime.now(timezone.utc).isoformat(),text=' '.join(' '.join(parser.parts).split()),raw_file=str(raw),evidence_file=str(p))
 (raw.with_suffix('.html.gz')).write_bytes(gzip.compress(body,mtime=0));raw.unlink(missing_ok=True);o['raw_file']=str(raw.with_suffix('.html.gz').relative_to(Path.cwd()));p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n');print(o['http_status'],len(body),url,flush=True);return o
if __name__=='__main__':
 import sys
 for u in sys.argv[1:]: get(u)
