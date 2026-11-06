"""Read-only, deterministic inventory. Does not write catalog data."""
import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path
import random
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0,str(ROOT/'src'))
from goodsdex.mihome_intake import classify, norm

def save(p,v):
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--goods',type=Path,required=True);ap.add_argument('--out',type=Path,default=ROOT/'docs/mihome-gap-20261106');a=ap.parse_args()
    ds=json.loads((ROOT/'docs/mihome-catalog-20261106/devices.json').read_text());ms=json.loads((ROOT/'data/official/mihome-catalog.json').read_text())['items'];brands={b['id']:b['name'] for b in json.loads((ROOT/'docs/mihome-catalog-20261106/brands.json').read_text())}
    goods=json.loads(a.goods.read_text());byname=collections.defaultdict(list)
    for r in goods:
        if r.get('name'):byname[norm(r['name'])].append(r['id'])
    mapped={m['model'] for m in ms};out=[]
    for d in sorted(ds,key=lambda r:r['model']):
        if d['model'] in mapped:continue
        k,reason=classify(d)
        out.append(dict(model=d['model'],pd_id=d['pdId'],name=d['name'],category=d['categoryName'],brand=' / '.join(brands.get(b,str(b)) for b in d['brand_ids']),jumpUrl=d['jumpUrl'],classification=k,reason=reason,existing_same_name_ids=byname[norm(d['name'])],classifications=sorted({c['name'] for c in d['classifications']}),icon=d['icon']))
    a.out.mkdir(parents=True,exist_ok=True);save(a.out/'gaps.json',out)
    for k in 'ABC':
        rows=[r for r in out if r['classification']==k];save(a.out/f'{k}.json',rows)
        with (a.out/f'{k}.csv').open('w',encoding='utf-8-sig',newline='') as f:
            keys=['model','pd_id','name','category','brand','jumpUrl','classification','reason','existing_same_name_ids'];w=csv.DictWriter(f,keys,extrasaction='ignore');w.writeheader();w.writerows(rows)
    counts=collections.Counter((r['classification'],r['brand'],r['category']) for r in out)
    save(a.out/'brand-category-counts.json',[dict(classification=k,brand=b,category=c,count=n) for (k,b,c),n in sorted(counts.items())])
    sample=random.Random(20261106).sample([r for r in out if r['classification']=='A'],50);save(a.out/'sample-50-input.json',sample)
    summary=dict(directory=len(ds),mapping_rows=len(ms),mapped_unique_models=len(mapped),gap=len(out),counts=dict(collections.Counter(r['classification'] for r in out)),same_name=sum(bool(r['existing_same_name_ids']) for r in out),baseline_sha256=hashlib.sha256(a.goods.read_bytes()).hexdigest(),duplicate_mapping_models={k:v for k,v in collections.Counter(m['model'] for m in ms).items() if v>1})
    save(a.out/'inventory-summary.json',summary);print(json.dumps(summary,ensure_ascii=False))
if __name__=='__main__':main()
