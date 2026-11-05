"""Re-fetch exact reviewed official originals/CDN crops at >=2.1s, verify digests.

Creates contact sheets for visual review. Does not approve images or change facts.
"""
import argparse,hashlib,io,json,time,urllib.request
from pathlib import Path
from PIL import Image,ImageDraw

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--manifest',type=Path,default=Path('data/official/atour-images.json'));ap.add_argument('--out',type=Path,required=True);ap.add_argument('--interval',type=float,default=2.1);args=ap.parse_args()
    if args.interval<2.1:ap.error('Minimum interval is 2.1 seconds')
    args.out.mkdir(parents=True,exist_ok=True);last=0;results=[]
    for key,r in json.loads(args.manifest.read_text())['skus'].items():
        item=dict(id=key)
        for field,digest_field in [('official_origin','origin_sha256'),('url','crop_sha256')]:
            url=r[field];name=hashlib.sha256(url.encode()).hexdigest()[:16]+'.webp';p=args.out/name
            if not p.exists():
                time.sleep(max(0,last+args.interval-time.monotonic()));last=time.monotonic()
                with urllib.request.urlopen(url,timeout=30) as response:raw=response.read()
                p.write_bytes(raw)
            raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==r[digest_field],(key,field)
            item[field]=str(p)
        with Image.open(item['url']) as im:assert im.size==(r['crop']['width'],r['crop']['height'])
        results.append(item)
    for offset in range(0,len(results),50):
        chunk=results[offset:offset+50];sheet=Image.new('RGB',(1200,150*((len(chunk)+4)//5)),'#ddd');draw=ImageDraw.Draw(sheet)
        for n,r in enumerate(chunk):
            im=Image.open(r['url']).convert('RGB');im.thumbnail((230,120));x=n%5*240;y=n//5*150;sheet.paste(im,(x+(240-im.width)//2,y));draw.text((x+3,y+123),f"{offset+n} SPU {r['id'].split(':')[3]}",fill='black')
        sheet.save(args.out/f'sheet-{offset//50}.jpg')
    (args.out/'verified.json').write_text(json.dumps(results,ensure_ascii=False,indent=1)+'\n')
    print('Verified',len(results),'official SKU images')
