"""Dated event coverage, exact full product names; review-only queue."""
import sys,json,re,hashlib,gzip
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from probe import get,Text,ROOT
from ir_candidates import norm
EVENTS={'https://www.ithome.com/1/006/476.htm':'2026-09','https://www.ithome.com/0/999/486.htm':'2026-09','https://www.ithome.com/0/953/645.htm':'2026-05','https://www.ithome.com/0/855/282.htm':'2025-05','https://www.ithome.com/0/930/804.htm':'2026-03','https://www.ithome.com/0/908/038.htm':'2025-12','https://www.ithome.com/0/863/991.htm':'2025-06'}
def modelnorm(s):
 return norm(s).replace('小米pad','小米平板').replace('小米watch','小米手表').replace('小米book','小米笔记本')
def plain(s):
 p=Text();p.feed(s);return re.sub(r'\s+',' ',' '.join(p.parts)).strip()
def main():
 rows=json.load(open('/tmp/goodsdex-release-dates/public/goods.json'));rows=list({r['id']:r for r in rows if r['id'].startswith('CN:mi_cn:') and not r.get('release')}.values());out=[]
 for u,date in EVENTS.items():
  d=get(u);p=ROOT/'evidence'/('web-'+hashlib.sha256(u.encode()).hexdigest()[:16]+'.html');b=p.read_bytes();s=(gzip.decompress(b) if b.startswith(b'\x1f\x8b') else b).decode('utf8','ignore')
  h=list(re.finditer(r'<h[23][^>]*>(.*?)</h[23]>',s,re.S))
  for i,m in enumerate(h):
   title=plain(m[1]);section=plain(s[m.end():h[i+1].start() if i+1<len(h) else len(s)]);n=modelnorm(title+' '+section)
   if not re.match(r'^(?:[一二三四五六七八九十]+、|0\d\.)',title) or '总结' in title:continue
   for r in rows:
    rn=modelnorm(r['name'])
    if len(rn)<4 or r.get('is_container'):continue
    hit=re.search(re.escape(rn)+r'(?![a-z0-9]|pro|ultra|青春|至尊|限定|限量|纪念|陶瓷|nfc)',n)
    if not hit:continue
    out.append(dict(id=r['id'],name=r['name'],category=r.get('category'),date=date,url=u,locator='article #paragraph / '+title,section_title=title,section=section,quote=title+'；'+section[:400],sha256=d['sha256'],captured_at=d['captured_at']))
 (ROOT/'event-review-queue.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 for o in out:print(o['id'].split(':')[-1],o['name'],o['date'],o['section_title'])
if __name__=='__main__':main()
