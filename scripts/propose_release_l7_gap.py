"""Ground only new exact model mentions, in paced groups of fifty."""
import concurrent.futures,gzip,json,re,time
from pathlib import Path
import extract_release_l7_scale as base
from goodsdex.release_coverage import effective
from goodsdex.release_media import normalize
OUT=Path('docs/release-coverage/L7-gap');base.OUT=OUT

def main():
 rows=json.loads(gzip.decompress((OUT/'baseline.json.gz').read_bytes()))
 missing={r['id']:r for r in rows if not effective(r)}
 prior=set()
 for directory in ('L7','L7-scale'):
  for a in json.loads((OUT.parent/directory/'audit.json').read_text()):prior.add((normalize(a['name']),a['url']))
 items=[];seen=set()
 for directory in ('L7-scale','L7-gap'):
  p=OUT.parent/directory/'discovery.json'
  if not p.exists():continue
  for d in json.loads(p.read_text()):
   if not re.search('发布|推出|众筹|预售|首发|上市|新品|首销|开售|上新',d['title']):continue
   for m in d['models']:
    if m['id'] not in missing:continue
    row=missing[m['id']];name=row['name'];key=(normalize(name),d['url'])
    if key in seen or key in prior or name in ('Redmi','米家洗衣机Pro','米家波轮洗衣机','米家冰箱 对开门','米家冰箱Pro 双系统','米家冰箱 两门','米家吸顶灯C','Redmi Book 14') or '系列' in name:continue
    # Prioritize title matches; model-specific identity review still follows capture.
    seen.add(key);items.append(dict(id=row['id'],name=name,brand=row['brand'],url=d['url'],published=d['published'],title=d['title'],body=d['body'][:16000]))
 processed=set()
 for p in (OUT/'grounded').glob('*.input.json'):
  if not p.with_name(p.name.replace('.input.json','.json')).exists():continue
  for x in json.loads(p.read_text()):processed.add((x['id'],x['url']))
 items=[x for x in items if (x['id'],x['url']) not in processed]
 items.sort(key=lambda x:(x['id'],x['url']))
 (OUT/'grounding-inputs.json').write_text(json.dumps(items,ensure_ascii=False,indent=2))
 for i in range(0,len(items),50):
  batch=items[i:i+50]
  with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(base.work,[batch[j:j+5] for j in range(0,len(batch),5)]))
  print('batch',i//50+1,'mentions',len(batch),flush=True);time.sleep(5)
 print('total grounded inputs',len(items),flush=True)
if __name__=='__main__':main()
