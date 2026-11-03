"""Capture full articles separately from search leads; never derive dates automatically."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib, html, json, re, requests
from pathlib import Path
ROOT=Path(__file__).parent

def plain(s):
 s=re.sub(r'<(script|style)\b[^>]*>.*?</\1>','',s,flags=re.S|re.I)
 return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',s))).strip()

def capture(url):
 key=hashlib.sha256(url.encode()).hexdigest()[:16];p=ROOT/'evidence'/f'{key}.html';p.parent.mkdir(exist_ok=True)
 meta=p.with_suffix('.json')
 if meta.exists() and not json.loads(meta.read_text()).get('error'):return json.loads(meta.read_text())
 s=requests.Session();s.trust_env=False
 try:
  r=s.get(url,timeout=25)
  if r.status_code in (403,429) and 'www.ithome.com' in url:
   number=''.join(re.findall(r'\d',url));r=s.get('https://m.ithome.com/html/'+str(int(number))+'.htm',timeout=25)
  r.raise_for_status();p.write_bytes(r.content)
  text=plain(r.content.decode('utf-8','replace'))
  title=html.unescape(re.search(r'<title>(.*?)</title>',r.text,re.S)[1])
  # Article prose only, excluding recommendations/footer and their unrelated dates.
  body=re.search(r'<div[^>]*id=["\']paragraph["\'][^>]*>(.*?)<div[^>]*class=["\'](?:share|editor|related)',r.text,re.S)
  if not body:body=re.search(r'<div[^>]*id=["\']paragraph["\'][^>]*>(.*)',r.text,re.S)
  t=plain(body[1]) if body else text
  if '投诉水文' in t:t=t.split('投诉水文')[0]
  d=dict(url=url,capture_url=r.url,title=title,sha256=hashlib.sha256(r.content).hexdigest(),captured_at=datetime.now(timezone.utc).isoformat(),capture_file=str(p.resolve().relative_to(Path.cwd())),text=t[:25000],header=text[:1800])
 except Exception as e:d=dict(url=url,error=str(e))
 meta.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');return d

if __name__=='__main__':
 import sys
 urls=sys.argv[1:]
 for d in ThreadPoolExecutor(6).map(capture,urls):print(json.dumps({k:v for k,v in d.items() if k not in ('text',)},ensure_ascii=False)[:2400])
