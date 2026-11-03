"""Exact-name candidate discovery from dated official report sentences, never family-year inference.

Produces a review queue only. It does not mutate the publication input.
"""
from pathlib import Path
import re,json,hashlib
ROOT=Path(__file__).resolve().parent

def norm(s):
 s=re.sub(r'\s+','',s).lower()
 s=s.translate(str.maketrans({'環':'环','電':'电','視':'视','機':'机','淨':'净','風':'风','雙':'双','區':'区','紀':'纪','週':'周','無':'无','線':'线','閃':'闪','煮':'煮','儲':'储','鮮':'鲜','錶':'表','鏡':'镜','體':'体','開':'开','門':'门','龍':'龙','熱':'热','凍':'冻','嵌':'嵌','曬':'晒','烘':'烘','曠':'旷'}))
 return s.replace('xiaomi','小米').replace('redmi','红米')

def main():
 rows=json.load(open('/tmp/goodsdex-release-dates/public/goods.json'));rows=list({r['id']:r for r in rows if r['id'].startswith('CN:mi_cn:') and not r.get('release')}.values());found=[]
 for p in sorted((ROOT/'evidence').glob('mi-*.txt')):
  if 'normalized' in p.name or 'annual' in p.name:continue
  meta=p.with_suffix('.json')
  if not meta.exists():continue
  d=json.loads(meta.read_text())
  if d.get('http_status')!=200:continue
  for page,t in enumerate(p.read_text().split('\f')[:14]):
   for sentence in re.split('[。；]',re.sub(r'\s+','',t)):
    dates=re.findall(r'(20\d{2})年(\d{1,2})月',sentence)
    if len(set(dates))!=1 or not re.search('推出|發佈|發布|上市',sentence):continue
    if not re.search('我們.{0,25}(推出|發佈|發布)|(?:推出|發佈|發布).{0,15}我們|正式上市',sentence):continue
    for r in rows:
     name=norm(r['name']);n=norm(sentence)
     if len(name)<4:continue
     if re.search(re.escape(name)+r'(?![a-z0-9]|系列|pro|ultra|青春|至尊|限定|限量|纪念|陶瓷|nfc)',n):
      yy,mm=dates[0]
      found.append(dict(id=r['id'],name=r['name'],category=r.get('category'),date=f'{yy}-{int(mm):02}',file=str(p.relative_to(ROOT)),page=page+1,quote=sentence,url=d['url'],sha256=d['sha256']))
 (ROOT/'ir-review-queue.json').write_text(json.dumps(found,ensure_ascii=False,indent=2)+'\n')
 for o in found:print(o['id'].split(':')[-1],o['name'],o['date'],o['file'],o['page'],o['quote'][:250])
 print('candidate IDs',len(set(o['id'] for o in found)))
if __name__=='__main__':main()
