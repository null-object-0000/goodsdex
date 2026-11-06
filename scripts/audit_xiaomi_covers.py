import json,sys,urllib.request,concurrent.futures,datetime,io,time
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "src"))
from pathlib import Path
from PIL import ImageFile
headers={'content-type':'application/x-www-form-urlencoded','X-User-Agent':'mi-shop','Mishop-Channel-Id':'1','X-Mishop-App-Source':'1','Mishop-Client-Id':'1'}
def image(url):
 if not url:return {'error':'no_image'}
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
  p=ImageFile.Parser()
  with urllib.request.urlopen(req,timeout=6) as f:
   for i in range(128):
    b=f.read(8192)
    if not b:break
    p.feed(b)
    if p.image:
     w,h=p.image.size;return dict(width=w,height=h,non_square=w!=h,jpg_ratio_gt_1_05=('.jpg' in url.lower() and max(w,h)/min(w,h)>1.05))
  return {'error':'no_dimensions'}
 except Exception as e:return {'error':str(e)}
def mtop(row):
 pid=row['id'].split(':')[-1]
 try:
  req=urllib.request.Request('https://m.mi.com/mtop/xiaomishop/product/info',data=json.dumps([{},dict(productId=int(pid))]).encode(),headers=headers)
  with urllib.request.urlopen(req,timeout=6) as f:d=json.load(f)
  gl=((d.get('data') or {}).get('goodsInfo') or {}).get('goodsList') or []
  url=(gl[0] or {}).get('imgUrl') if gl else None
  return row['id'],dict(image=url or None,code=d.get('code'),message=d.get('message'),captured_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
 except Exception as e:return row['id'],dict(image=None,error=str(e),captured_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
def main():
 import argparse,gzip,hashlib
 from goodsdex.xiaomi_covers import apply_covers
 parser=argparse.ArgumentParser(description='Audit all cover dimensions and exact-id Xiaomi mtop images, then optionally write an image-only local candidate. Never publishes.')
 parser.add_argument('--input',type=Path,required=True)
 parser.add_argument('--out',type=Path,required=True)
 parser.add_argument('--baseline-revision',help='Optional git revision of the audited input')
 parser.add_argument('--reuse',action='store_true',help='Reuse recorded dimensions and mtop observations; no requests')
 parser.add_argument('--output',type=Path,help='Optional local candidate goods.json')
 parser.add_argument('--write-evidence',type=Path,help='Optional frozen exact-id evidence for later publication')
 args=parser.parse_args();root=args.out;root.mkdir(parents=True,exist_ok=True)
 raw=args.input.read_bytes()
 if args.input.suffix=='.gz':raw=gzip.decompress(raw)
 rows=json.loads(raw)
 mi={r['id']:r for r in rows if r['id'].startswith('CN:mi_cn:product:') and r['id'].split(':')[-1].isdigit()}
 if args.reuse:
  dims=json.loads((root/'dimensions-before.json').read_text());obs=json.loads((root/'mtop-images.json').read_text())
 else:
  urls=sorted({r['image'] for r in rows if r.get('image')})
  with concurrent.futures.ThreadPoolExecutor(max_workers=32) as pool:dims=dict(zip(urls,pool.map(image,urls)))
  (root/'dimensions-before.json').write_text(json.dumps(dims,ensure_ascii=False,indent=1)+'\n')
  with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:obs=dict(pool.map(mtop,mi.values()))
  (root/'mtop-images.json').write_text(json.dumps(obs,ensure_ascii=False,indent=1)+'\n')
 before_dims=dict(dims)
 urls=sorted({o['image'] for o in obs.values() if o.get('image')}-dims.keys())
 if args.reuse:
  dims.update(json.loads((root/'dimensions-after.json').read_text()))
 else:
  with concurrent.futures.ThreadPoolExecutor(max_workers=24) as pool:dims.update(zip(urls,pool.map(image,urls)))
 for o in obs.values():
  d=dims.get(o.get('image'),{})
  if d.get('width'):o.update(width=d['width'],height=d['height'])
 after=apply_covers(rows,obs)
 assert [r for r in rows if r['id'] not in mi]==[r for r in after if r['id'] not in mi]
 for a,b in zip(rows,after):
  assert {k:v for k,v in a.items() if not k.startswith('image')}=={k:v for k,v in b.items() if not k.startswith('image')}
 def stats(rs,ds):
  from collections import Counter
  count=Counter(rows=0,non_square=0,square=0,no_image=0,dimensions_unverified=0,jpg_ratio_gt_1_05=0,mtop_different=0,marketing_heuristic_union=0)
  for r in rs:
   count['rows']+=1;url=r.get('image');d=ds.get(url,{})
   if not url:count['no_image']+=1
   elif not d or d.get('error'):count['dimensions_unverified']+=1
   else:
    count['non_square' if d['non_square'] else 'square']+=1
    count['jpg_ratio_gt_1_05']+=bool(d['jpg_ratio_gt_1_05'])
   o=obs.get(r['id']);different=bool(o and o.get('image') and o['image']!=url)
   count['mtop_different']+=different
   count['marketing_heuristic_union']+=bool(different or d.get('non_square'))
  return dict(count)
 report=dict(baseline_revision=args.baseline_revision,
             baseline_sha256=hashlib.sha256(raw).hexdigest(),before=stats(rows,before_dims),after=stats(after,dims),
             mi_before=stats([r for r in rows if r['id'] in mi],before_dims),mi_after=stats([r for r in after if r['id'] in mi],dims),
             mtop_unique_ids=len(obs),mtop_available=sum(bool(o.get('image')) for o in obs.values()),mtop_unavailable=sum(not o.get('image') for o in obs.values()),
             mtop_transport_unverified=sum(bool(o.get('error')) for o in obs.values()),image_changed_rows=sum(a.get('image')!=b.get('image') for a,b in zip(rows,after)),non_mi_unchanged=True,non_image_fields_unchanged=True)
 (root/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 changes=[dict(id=a['id'],before={k:v for k,v in a.items() if k=='id' or k.startswith('image')},after={k:v for k,v in b.items() if k=='id' or k.startswith('image')}) for a,b in zip(rows,after) if a!=b]
 (root/'cover-changes.json.gz').write_bytes(gzip.compress(json.dumps(changes,ensure_ascii=False).encode(),mtime=0))
 (root/'dimensions-after.json').write_text(json.dumps(dims,ensure_ascii=False,indent=1)+'\n')
 if args.write_evidence:args.write_evidence.write_text(json.dumps(obs,ensure_ascii=False,indent=1)+'\n')
 if args.output:
  args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(after,ensure_ascii=False,indent=1)+'\n')
 print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
