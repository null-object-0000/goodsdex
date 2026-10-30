"""Read-only live verification of the reviewed three-batch supplemental release."""
import json,urllib.request,urllib.parse,collections,gzip,argparse,hashlib
from pathlib import Path
parser=argparse.ArgumentParser(description='Verify the 20261030 supplemental release against the live API')
parser.add_argument('--public',type=Path,required=True)
parser.add_argument('--out',type=Path,required=True)
args=parser.parse_args()
out=args.out;out.mkdir(parents=True,exist_ok=True)
local=args.public
def fetch(path):
 with urllib.request.urlopen(urllib.request.Request('https://spend.snewbie.site'+path,headers={'Accept-Encoding':'gzip'}),timeout=90) as r:
  assert r.status==200
  data=r.read()
  return json.loads(gzip.decompress(data) if r.headers.get('Content-Encoding')=='gzip' else data)
rows=fetch('/api/goods');expected=json.load(open(local/'goods.json'))
assert rows==expected,'Online catalog differs from release'
(out/'online-catalog-check.json').write_text(json.dumps(dict(full_catalog_equal=True,count=len(rows),release_sha256=hashlib.sha256((local/'goods.json').read_bytes()).hexdigest()),indent=2)+'\n')
a=[r for r in rows if r.get('brand')=='Apple'];mi=[r for r in rows if r['id'].startswith('CN:mi_cn:')];h=[r for r in rows if r.get('series')=='汉'];x=[r for r in rows if r.get('brand')=='小米汽车']
assert len(x)==3 and all(r['model_year'] is None for r in x)
stats=dict(total=len(rows),unique_ids=len({r['id'] for r in rows}),xiaomi_named_rows=sum(bool(r.get('name')) for r in mi),xiaomi_named_unique_ids=len({r['id'] for r in mi if r.get('name')}),apple_total=len(a),apple_with_image=sum(bool(r.get('image')) for r in a),apple_with_current_price=sum(r.get('price') is not None for r in a),apple_with_historical_price=sum(r.get('historical_price') is not None for r in a),apple_with_either_price=sum(r.get('price') is not None or r.get('historical_price') is not None for r in a),han_products=len(h),han_trims=sum(len(r['trims']) for r in h),xiaomi_car_years=[r['model_year'] for r in x])
(out/'online-stats.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n')
ids=['CN:mi_cn:product:722','CN:mi_cn:product:2392','GLOBAL:apple_support:model:111340','GLOBAL:apple_support:model:111343','CN:byd:car:han:2023:dmi','CN:byd:car:han:2024:ev']
samples=[]
for i,key in enumerate(ids,1):
 actual=fetch('/api/goods/'+urllib.parse.quote(key,safe=''));source=next(r for r in rows if r['id']==key)
 assert actual==source,(key,'detail field mismatch')
 (out/f'online-detail-{i}.json').write_text(json.dumps(actual,ensure_ascii=False,indent=1)+'\n')
 if i<3: fields='id name name_source source_url captured_at record_level price'
 elif i<5: fields='id name price historical_price price_kind price_source price_source_url captured_at price_basis'
 else: fields='id name model_year model_year_source model_year_confidence model_year_source_url source source_url captured_at price price_kind image image_scope'
 fragment={k:actual[k] for k in fields.split()}
 if i>=5:
  fragment['trim_count']=len(actual['trims']);fragment['trims']=[{k:actual['trims'][0][k] for k in ('id','name','price','historical_price','price_kind')}]
 samples.append(dict(id=key,url='https://spend.snewbie.site/api/goods/'+urllib.parse.quote(key,safe=''),all_fields_equal=True,json=fragment))
 # Search projections must retain source and historical semantics, too.
 q=fetch('/api/goods/search?'+urllib.parse.urlencode({'q':actual['name'],'limit':50}))
 match=next(r for r in q['items'] if r['id']==key)
 assert match['price'] is None
 if i<3:assert match['name_source']==actual['name_source']
 elif i<5:assert match['historical_price']==actual['historical_price'] and match['price_kind']=='msrp_historical'
 else: assert match['model_year_source']=='pcauto'
 (out/f'online-search-{i}.json').write_text(json.dumps(q,ensure_ascii=False,indent=1)+'\n')
(out/'online-samples.json').write_text(json.dumps(samples,ensure_ascii=False,indent=2)+'\n')
print(stats)
