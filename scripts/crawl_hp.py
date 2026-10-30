#!/usr/bin/env python3
"""Collect public HP China computer SKU pages. Daily, GET only, fail-preserving.

--dry-run fetches and prints records/audit, and never writes files.
Requires Pillow for decoding/validating images (python3 -m pip install Pillow).
"""
from __future__ import annotations
import argparse
import hashlib
import html
import io
import json
import re
import sys
import time
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, urljoin, quote

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from goodsdex.public_fields import normalize_public_row

SEEDS = ['https://www.hpstore.cn/laptops-tablets.html',
         'https://www.hpstore.cn/desktops.html']
CORE = ['CPU型号', '运行内存', '存储容量', '显卡']

def clean(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]+>', ' ', s))).strip()

def json_after(text, marker):
    pos = text.find(marker)
    if pos < 0:
        raise ValueError('missing ' + marker)
    return json.JSONDecoder().raw_decode(text[pos + len(marker):].lstrip())[0]

class Client:
    def __init__(self, raw=None):
        self.last = {}
        self.raw = raw
        self.requests = []
    def get(self, url):
        host = urlparse(url).netloc
        time.sleep(max(0, 2.1 - (time.monotonic() - self.last.get(host, -100))))
        # Wait from completion, so even slow requests cannot overlap the next GET.
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'GoodsDex/1.0 (public computer catalogue; daily)'}), timeout=45) as r:
                data = r.read()
                info = dict(url=url, final_url=r.url, status=r.status,
                            content_type=r.headers.get('Content-Type',''), bytes=len(data),
                            sha256=hashlib.sha256(data).hexdigest(), fetched_at=datetime.now(timezone.utc).isoformat())
        finally:
            self.last[host] = time.monotonic()
        self.requests.append(info)
        if self.raw:
            self.raw.mkdir(parents=True, exist_ok=True)
            (self.raw / (info['sha256'] + '.bin')).write_bytes(data)
        return data, info

def listing(text, url):
    links = [html.unescape(u) for u in re.findall(r'<a\s+class="product-item-link"[^>]*href="([^"]+)"',text)]
    # Follow only the source's next-page link, never synthesize an unbounded range.
    next_link = re.search(r'<link\s+rel="next"\s+href="([^"]+)"', text)
    return list(dict.fromkeys(links)), urljoin(url,html.unescape(next_link[1])) if next_link else None

def capacity(value):
    m = re.search(r'(\d+(?:\.\d+)?)\s*(GB|TB|G)\b',value or '',re.I)
    return m[1]+('GB' if m[2].upper()=='G' else m[2].upper()) if m else None

def parse_product(text, url, fetched_at):
    source = json_after(text,'magentoStorefrontEvents.context.setProduct(')
    p = {clean(k): clean(v) for k,v in re.findall(r'<dd\s+data-th="([^"]+)">([\s\S]*?)</dd>',text)}
    sku = p.get('SKU')
    if not sku or sku != source.get('sku') or not re.fullmatch(r'[A-Z0-9]+(?:-[A-Z0-9]+)*(?:#[A-Z0-9]+)?',sku):
        raise ValueError('SKU missing or conflicts with product context')
    typ = p.get('产品类型','')
    form = p.get('外形','')
    source_type = ' '.join([typ,form,source['name']])
    if '服务器' in source_type: raise ValueError('out of scope: server')
    if '笔记本' in typ or typ == '移动工作站' or form == '移动工作站':
        category = '笔记本'
    elif any(k in source_type for k in ['台式','一体机','迷你电脑']):
        category = '台式机'
    else:
        raise ValueError('out of scope product type: '+typ)
    cpu = p.get('处理器')
    ram = p.get('内存（标配）') or p.get('内存')
    disk = p.get('硬盘说明') or p.get('内部存储')
    overview = {clean(k):clean(v) for k,v in re.findall(r'<p class="title[^"]*">([\s\S]*?)</p>\s*<p class="con">([\s\S]*?)</p>',text)}
    if not disk:
        parts=re.split('[;；]',overview.get('内存和存储',''))
        storage=[v.strip() for v in parts if re.search(r'固态硬盘|机械硬盘',v)]
        if len(storage)==1: disk=storage[0]
    gpu = p.get('显卡')
    # Two store CTO SKUs publish their fixed configuration only in the title.
    # Extract only the explicitly labelled tokens; never derive graphics from CPU.
    title_config=re.search(r'[：:]\s*(I[3579]-[0-9A-Za-z]+)/(\d+G)/(\d+G)/(集显)/',source['name'],re.I)
    if title_config:
        cpu=cpu or title_config[1]
        ram=ram or title_config[2]
        disk=disk or title_config[3]
        gpu=gpu or title_config[4]
    size = p.get('屏幕尺寸')
    if size in ('不适用', 'N/A', 'Not Applicable'): size = None
    # Display only the model before descriptive clocks/cache; keep full specs below.
    chip = re.split(r'[（(，,；;]',cpu or '')[0].strip()
    graphics = re.split(r'[（(，,；;]',gpu or '')[0].strip()
    spec = '+'.join(filter(None,[capacity(ram),capacity(disk)]))
    source_name = source['name']
    model = re.sub(r'[：:]\s*I[3579]-.*$', '', source_name)
    model = re.sub(r'^HP\s+', '惠普 ',model)
    model = re.sub(r'^惠普\s*\(HP\)\s*','惠普 ',model)
    model = re.sub(r'\s+-\s+[^-]+$','',model).strip()
    # HP's submodel suffix (e.g. ap1025AX) remains in source_name, not the family title.
    model = re.sub(r'\s+[A-Za-z]{1,3}\d{4}[A-Za-z]{1,3}\b','',model).strip()
    # This is an internal grouping key derived from a literal official model title,
    # never a fabricated HP SKU. The SKU identity below is the source's exact value.
    family = 'CN:hp_cn:model:' + quote(model, safe='')
    params = {'CPU型号':cpu, '运行内存':ram, '存储容量':disk, '显卡':gpu,
              '屏幕尺寸':size, '重量':p.get('重量'), '上市时间':p.get('上市时间'),
              '产品编号':sku, '产品类型':typ or form, '型号':model, 'source_specs':p, 'source_overview':overview}
    dims = {}
    for key,label in [('dimensionChip',chip),('dimensionCapacity',spec),('dimensionGpu',graphics)]:
        if label: dims[key] = dict(value=label,label=label)
    params['variant_attrs'] = dims
    # The visible finalPrice for this exact Magento product, not cross-sell prices.
    pid = source['productId']
    tag = re.search(r'<span\b(?=[^>]*\bid="product-price-'+str(pid)+r'")(?=[^>]*\bdata-price-type="finalPrice")(?=[^>]*\bdata-price-amount="([0-9.]+)")[^>]*>',text)
    price = float(tag[1]) if tag else None
    if price is not None and price <= 0: price = None
    row = dict(id='CN:hp_cn:sku:'+sku,product_id=family,part_number=sku,brand='惠普',
               source='hp_cn',market='CN',kind='machine',category=category,model=model,
               name=' '.join(filter(None,[model,chip,spec,graphics])), source_name=source_name,
               record_level='configuration',lookup_keys=[sku],source_url=url,price=price,
               price_kind='store_sale' if price is not None else None,currency='CNY',
               price_fetched_at=fetched_at if price is not None else None,
               market_price=None,image=None,fetched_at=fetched_at,params=params)
    # Search shorthand only: never relabel a new 星Book as an old 星14 Pro.
    star = re.search(r'星(?:Book)?(.*?)\s*(\d+(?:\.\d+)?)英寸',model,re.I)
    if star:
        row['lookup_keys'].append('星'+star[2]+star[1].strip())
    return normalize_public_row(row), source.get('mainImageUrl')

def image_check(client, url):
    if not url: return None,dict(url=None,ok=False,reason='not_collected: no main image URL')
    try:
        from PIL import Image
        data,info=client.get(url)
        im=Image.open(io.BytesIO(data)); im.load()
        info.update(width=im.width,height=im.height,format=im.format)
        ok=info['status']==200 and info['content_type'].lower().startswith('image/') and len(data)>30*1024 and im.width>=800
        info.update(ok=ok,reason=None if ok else 'image fails status/type/bytes/width policy')
        return url if ok else None, info
    except Exception as e:
        return None,dict(url=url,ok=False,reason=type(e).__name__+': '+str(e))

def merge_hp(previous, collected):
    if any(r.get('brand')!='惠普' or not r['id'].startswith('CN:hp_cn:sku:') for r in collected):
        raise ValueError('Non-HP input')
    by_id={r['id']:r for r in collected}
    # Same source configuration can have several sellable part numbers; expose SKU
    # only for those collisions so every physical label remains selectable.
    signatures=Counter((r['product_id'],json.dumps(r['params']['variant_attrs'],sort_keys=True)) for r in collected)
    for r in collected:
        if signatures[(r['product_id'],json.dumps(r['params']['variant_attrs'],sort_keys=True))]>1:
            r['params']['variant_attrs']['dimensionEdition']=dict(value=r['part_number'],label=r['part_number'])
    old_ids={r['id'] for r in previous}
    result=[by_id.pop(r['id'],r) for r in previous] + list(by_id.values())
    if not old_ids.issubset({r['id'] for r in result}): raise ValueError('Publication would drop previous IDs')
    if [r for r in previous if r.get('brand')!='惠普'] != [r for r in result if r.get('brand')!='惠普']:
        raise ValueError('Non-HP records changed')
    return result

def write_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(value,ensure_ascii=False,indent=1)+'\n');tmp.replace(path)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path,default=ROOT/'data/hp')
    ap.add_argument('--public',type=Path)
    ap.add_argument('--raw',type=Path,default=ROOT/'data/hp/raw')
    ap.add_argument('--reuse-images', action='store_true', help='Hourly refresh: reuse prior successful image checks; new/changed images are still verified')
    ap.add_argument('--dry-run',action='store_true')
    ap.add_argument('--limit',type=int)
    ap.add_argument('--replay',type=Path,help='Reparse saved audit/raw evidence; validate images missing from that audit')
    ap.add_argument('--seed',action='append',help='Additional public HP catalogue/search page')
    args=ap.parse_args()
    client=Client(None if args.dry_run else args.raw)
    replay=json.loads((args.replay/'audit.json').read_text()) if args.replay else None
    evidence={r['url']:r for r in replay['requests']} if replay else {}
    def page_get(url):
        if url in evidence:
            info=evidence[url]
            data=(args.replay/'raw'/(info['sha256']+'.bin')).read_bytes()
            if hashlib.sha256(data).hexdigest()!=info['sha256']: raise ValueError('Corrupt cached evidence')
            client.requests.append(info)
            return data,info
        return client.get(url)
    errors=[];urls=[];seen=set();pages=list(SEEDS)+(args.seed or [])
    while pages:
        url=pages.pop(0)
        if url in seen: continue
        if urlparse(url).hostname!='www.hpstore.cn': raise ValueError('Only public HP CN pages allowed')
        seen.add(url)
        try:
            data,_=page_get(url);links,nxt=listing(data.decode(),url)
            if not links: raise ValueError('No product links; catalogue parse failure')
            urls.extend(u for u in links if u not in urls)
            if nxt and not args.limit: pages.append(nxt)
        except Exception as e: errors.append(dict(url=url,error=str(e)))
    image_audit = replay
    if args.reuse_images and image_audit is None and (args.out/'audit.json').exists():
        image_audit = json.loads((args.out/'audit.json').read_text())
    rows=[];checks={i['url']:i for i in image_audit['images'] if i['ok']} if image_audit else {}
    images={u:u if i['ok'] else None for u,i in checks.items()}
    for url in urls[:args.limit] if args.limit else urls:
        try:
            if urlparse(url).hostname!='www.hpstore.cn': raise ValueError('Unexpected product host')
            data,info=page_get(url)
            row,img=parse_product(data.decode(),url,info['fetched_at'])
            if img not in checks: images[img],checks[img]=image_check(client,img)
            row['image']=images[img]
            if not row['image']:
                try:
                    gallery=json_after(data.decode(),'"mage/gallery/gallery":')['data']
                except (ValueError,KeyError): gallery=[]
                candidates=list(dict.fromkeys(g.get('full') for g in gallery if g.get('type')=='image' and g.get('full')))[:3]
                for candidate in candidates:
                    if candidate not in checks: images[candidate],checks[candidate]=image_check(client,candidate)
                    if images[candidate]: row['image']=images[candidate];break
            rows.append(row)
            print(row['id'],row['name'],flush=True)
        except Exception as e: errors.append(dict(url=url,error=str(e)))
    if not rows:
        print(json.dumps(dict(errors=errors),ensure_ascii=False));return 1
    if replay:
        client.requests=list({r['url']:r for r in [*replay['requests'],*client.requests]}.values())
    rows=list({r['id']:r for r in rows}.values())
    rows=merge_hp([],rows)
    audit=dict(fetched_at=datetime.now(timezone.utc).isoformat(),count=len(rows),
               categories=dict(Counter(r['category'] for r in rows)),
               configuration_complete=sum(all(r['params'].get(k) for k in CORE) for r in rows),
               fields={k:sum(bool(r['params'].get(k)) for r in rows) for k in [*CORE,'屏幕尺寸','重量','上市时间']},
               with_image=sum(bool(r['image']) for r in rows),with_price=sum(r['price'] is not None for r in rows),
               errors=errors,images=list(checks.values()),requests=client.requests)
    if args.dry_run:
        print(json.dumps(dict(rows=rows,audit=audit),ensure_ascii=False,indent=1));return bool(errors)
    # Archive successful SKU observations; missing/failed pages never delete old data.
    path=args.out/'goods.json'
    previous=json.loads(path.read_text()) if path.exists() else []
    write_json(path,merge_hp(previous,rows));write_json(args.out/'audit.json',audit)
    if args.public:
        from goodsdex.supplements import metadata
        previous=json.loads((args.public/'goods.json').read_text())
        result=merge_hp(previous,json.loads(path.read_text()))
        write_json(args.public/'goods.json',result)
        old_meta=json.loads((args.public/'meta.json').read_text())
        write_json(args.public/'meta.json',metadata(result,old_meta))
    print(json.dumps({k:v for k,v in audit.items() if k not in ['images','requests']},ensure_ascii=False))
    return bool(errors)

if __name__=='__main__': sys.exit(main())
