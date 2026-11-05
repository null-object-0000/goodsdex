"""Anonymous official directory collection; no numeric brand range scan."""
import argparse, hashlib, json, time
from pathlib import Path
import requests

BASE = 'https://home.mi.com/cgi-op/api/v1/'

def save(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=1)+'\n')

def collect(out, seeds):
    session = requests.Session()
    captures=json.loads((out/'requests.json').read_text()) if (out/'requests.json').exists() else []
    def fetch(path, params, label):
        target=out/'raw'/f'{label}.json'
        if target.exists(): return json.loads(target.read_text())
        r=session.get(BASE+path, params=params, timeout=45);r.raise_for_status()
        data=r.json()
        if data.get('code') != 0: raise ValueError((r.url,data))
        target.write_bytes(r.content)
        captures.append(dict(file=str(target.relative_to(out)),url=r.url,sha256=hashlib.sha256(r.content).hexdigest()))
        save(out/'requests.json',captures)
        time.sleep(.15)
        return data
    detail=fetch('brand/h5/detail',{'id':1520},'brand-1520')
    baseline=fetch('brand/h5/list',dict(brandId=1520,classifyId=0,limit=100),'probe-baseline')['data']['productList']
    probes=[]
    for p in [dict(pageIndex=2),dict(offset=100),dict(pageSize=5,pageIndex=2),dict(cursor=100),dict(page=2),dict(start=100),dict(changeTime=baseline[-1]['changeTime'],lastPdId=baseline[-1]['pdId'])]:
        data=fetch('brand/h5/list',dict(brandId=1520,classifyId=0,limit=100,**p),'probe-'+str(len(probes)))['data']['productList']
        probes.append(dict(params=p,count=len(data),same_as_baseline=[x['pdId'] for x in data]==[x['pdId'] for x in baseline],first_ids=[x['pdId'] for x in data[:3]]))
    save(out/'pagination-probes.json',probes)
    brands={1520}
    # Seeds are explicit brand IDs observed in existing anonymous product responses.
    brands.update(map(int, seeds))
    details=[]; all_devices={}; canonical=set(); last_detail=time.monotonic()
    for bid in [1520, *sorted(brands - {1520})]:
        time.sleep(max(0,2.15-(time.monotonic()-last_detail)))
        d=fetch('brand/h5/detail',{'id':bid},f'brand-{bid}').get('data') or {}
        last_detail=time.monotonic();details.append(dict(d,requested_id=bid));save(out/'brands.json',details)
        if d.get('id') in canonical: continue
        canonical.add(d.get('id'))
        if not d.get('classifyList'): continue
        for category in d['classifyList']:
            cursor={};seen=set();count=0
            for page in range(200):
                batch=fetch('brand/h5/list',dict(brandId=bid,classifyId=category['id'],limit=100,**cursor),f'list-{bid}-{category["id"]}-{page}')['data']['productList']
                if not batch:break
                fresh={x['pdId'] for x in batch}-seen
                if not fresh:raise ValueError(('cursor stalled',bid,category,page))
                seen.update(fresh);count+=len(batch)
                for x in batch:
                    key=x['model'];entry=all_devices.setdefault(key,dict(x,brand_ids=[],classifications=[]))
                    if bid not in entry['brand_ids']:entry['brand_ids'].append(bid)
                    c=dict(brand_id=bid,id=category['id'],name=category['name'])
                    if category['id'] and c not in entry['classifications']:entry['classifications'].append(c)
                cursor=dict(changeTime=batch[-1]['changeTime'],lastPdId=batch[-1]['pdId'])
            print(bid,d.get('name'),category['name'],len(seen),flush=True)
            save(out/'devices.json',list(all_devices.values()))
        save(out/'brands.json',details)
    return all_devices

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--seed-brands',type=Path,required=True);a=p.parse_args()
    collect(a.output,json.loads(a.seed_brands.read_text()))
