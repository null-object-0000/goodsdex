"""Build reviewed directory mappings and a deterministic 100-product sample."""
import argparse
from collections import Counter, defaultdict
import gzip, hashlib, io, json, random, re, time
from pathlib import Path
from urllib.parse import urlencode
import requests
from PIL import Image
from goodsdex.mihome_catalog import apply_catalog, norm
from goodsdex.release_coverage import effective


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1)+'\n')


def build(root, destination):
    devices=json.loads((root/'devices.json').read_text())
    rows=json.loads(gzip.decompress((root/'goods-before.json.gz').read_bytes()))
    products={r['id']:r for r in rows if r['id'].startswith('CN:mi_cn:product:')}
    names=defaultdict(list)
    for d in devices:names[norm(d['name'])].append(d)
    evidence={}
    urls={x['file']:x['url'] for x in json.loads((root/'requests.json').read_text())}
    for f in sorted((root/'raw').glob('list-*.json')):
        _,bid,cid,page=f.stem.split('-')
        for d in json.loads(f.read_bytes())['data']['productList']:
            evidence.setdefault(d['model'],dict(source_url=urls[str(f.relative_to(root))],source_file=str(f.relative_to(root)),source_sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
    items=[]; rejected=[]
    for key,row in sorted(products.items()):
        if row.get('is_container'):continue
        matches=names[norm(row['name'])];method='exact_name';capacity=None
        if not matches:
            capacity=norm(str((row.get('params') or {}).get('洗涤容量','')))
            if re.fullmatch(r'\d+(?:\.\d+)?kg',capacity):
                matches=names[norm(row['name'])+capacity];method='core_capacity'
        if len(matches)!=1:
            rejected.append(dict(id=key,name=row['name'],status='ambiguous' if matches else 'unmatched',candidates=[x['model'] for x in matches]));continue
        d=matches[0]
        e=dict(id=key,expected_name=row['name'],name=d['name'],model=d['model'],pd_id=d['pdId'],
               category=d['categoryName'],classifications=d['classifications'],method=method,**evidence[d['model']])
        if capacity and method=='core_capacity':e['capacity']=capacity
        if not row.get('image'):
            try:
                f=root/'raw'/('icon-'+d['model']+'.bin')
                if not f.exists():
                    r=requests.get(d['icon'],timeout=30);r.raise_for_status();f.write_bytes(r.content);time.sleep(.15)
                data=f.read_bytes();im=Image.open(io.BytesIO(data));im.verify()
                e['verified_icon']=dict(url=d['icon'],width=im.width,height=im.height,sha256=hashlib.sha256(data).hexdigest())
            except Exception as ex:e['icon_error']=str(ex)
        items.append(e)
    # Frozen pre-migration values must survive future directory refreshes.
    previous = json.loads(destination.read_text()) if destination.exists() else {'items': []}
    originals = {e['id']: e['legacy_original_fields'] for e in previous['items'] if 'legacy_original_fields' in e}
    previous_icons = {e['id']: e.get('verified_icon', {}) for e in previous['items']}
    for e in items:
        icon, prior = e.get('verified_icon', {}), previous_icons.get(e['id'], {})
        if (prior.get('public_url') and icon.get('url') == prior.get('url')
                and icon.get('sha256') == prior.get('sha256')):
            icon['public_url'] = prior['public_url']
        if e['id'] in originals:
            e['legacy_original_fields'] = originals[e['id']]
    manifest=dict(schema=1,items=items);save(destination,manifest)
    after=apply_catalog(rows,manifest);a={r['id']:r for r in after}
    # This task owns zero date fields, including evidence and missing reasons.
    date_fields={k for row in rows for k in row if k.startswith(('release','page_first_archived'))}
    assert all({k:r.get(k) for k in date_fields}=={k:s.get(k) for k in date_fields} for r,s in zip(rows,after))
    changes=[]
    for row,new in zip(rows,after):
        fields=[k for k in ('name_mihome','image_mihome','category_mihome') if row.get(k)!=new.get(k)]
        if fields:changes.append(dict(id=row['id'],fields=fields,before={k:row.get(k) for k in ('name','image','category','name_mihome','image_mihome','category_mihome')},after={k:new.get(k) for k in ('name','image','category','name_mihome','image_mihome','category_mihome')},model=new['mihome_model'],pd_id=new['mihome_pd_id'],image_dimensions=[(new.get('image_mihome') or {}).get('width'),(new.get('image_mihome') or {}).get('height')]))
    byid={x['id']:x for x in items};sample=[]
    for key in random.Random(20261106).sample(sorted(products),100):
        e=byid.get(key);sample.append(dict(id=key,name=products[key]['name'],matched=bool(e),model=e['model'] if e else None,method=e['method'] if e else None))
    stats=dict(device_count=len(devices),unique_pd_ids=len({d['pdId'] for d in devices}),product_population=len(products),matched=len(items),methods=dict(Counter(x['method'] for x in items)),sample_matched=sum(x['matched'] for x in sample),sample_total=100,
               name_repairs=0,name_sources_added=sum('name_mihome' in x['fields'] for x in changes),truncated_name_repairs=sum(x['method']=='core_capacity' for x in items),images_added=0,image_sources_added=sum('image_mihome' in x['fields'] for x in changes),categories_repaired=0,category_sources_added=sum('category_mihome' in x['fields'] for x in changes),
               image_dimensions=dict(Counter(f"{x['verified_icon']['width']}x{x['verified_icon']['height']}" for x in items if x.get('verified_icon'))),
               classifications=dict(Counter(c for d in devices for c in {c['name'] for c in d['classifications']})),
               leaf_categories=dict(Counter(d['categoryName'] for d in devices)),
               dated_before=sum(bool(effective(r)) for r in rows),dated_after=sum(bool(effective(r)) for r in after),row_count=len(rows),date_fields_unchanged=True)
    save(root/'summary.json',stats);save(root/'sample-100.json',sample);save(root/'changes.json',changes);save(root/'unmatched.json',rejected)
    print(json.dumps(stats,ensure_ascii=False,indent=1))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--manifest',type=Path,default=Path('data/official/mihome-catalog.json'));a=p.parse_args();build(a.output,a.manifest)
