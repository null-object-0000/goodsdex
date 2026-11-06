"""Verify immutable online bytes, all product fields, and five displayed examples."""
import gzip,hashlib,json,sys,urllib.request
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from goodsdex.mihome_catalog import apply_catalog
from goodsdex.shards import shard_for
from goodsdex.release_coverage import effective
BASE='https://spend-good.oss-cn-shanghai.aliyuncs.com/data/public/'
root=Path(__file__).resolve().parent

def get(url):
    with urllib.request.urlopen(url,timeout=60) as r:return r.read()

meta=json.loads(get(BASE+'meta.json'))
cache={}
def blob(name):
    if name not in cache:
        desc=meta['files'][name];raw=get(BASE+'blobs/'+desc['sha256']+'.json')
        assert hashlib.sha256(raw).hexdigest()==desc['sha256']
        cache[name]=json.loads(raw)
    return cache[name]

baseline=root/'publication-before.json.gz'
if not baseline.exists(): raise FileNotFoundError('Capture real publication parent as publication-before.json.gz first')
before=json.loads(gzip.decompress(baseline.read_bytes()))
expected=apply_catalog(before);actual=blob('goods.json')
# Exact equality also verifies every date field and every unrelated field.
assert actual==expected,'Online catalog differs from reviewed patch over the captured baseline'
current={r['id']:r for r in actual}
source_samples=json.loads((root/'sample-10-sources.json').read_text())
samples=[]
for source in source_samples:
    key=source['id'];detail=blob(f'detail/{shard_for(key):02x}.json')[key]
    assert detail == current[key]
    assert detail['name']==source['official_page_name']
    assert detail['name_mihome']==source['mihome_page_name']
    samples.append(dict(id=key,name=detail['name'],name_mihome=detail['name_mihome'],name_source=detail['name_source']))
icons=[]
for r in [r for r in actual if r.get('image_mihome') and not r.get('image')][:5]:
    detail=blob(f"detail/{shard_for(r['id']):02x}.json")[r['id']]
    assert detail == r
    view=r['catalog_display']
    assert view['image']==r['image_mihome']['url'] and view['image_scope']=='device_icon'
    assert view['image_width']==view['image_height']==168
    icons.append(dict(id=r['id'],image=r.get('image'),image_mihome=r['image_mihome'],display=view))
assert len(icons)==5
index_names=[k for k in meta['files'] if 'index/mi_cn' in k]
indexed=[]
for name in index_names:
    d=blob(name);indexed.extend(d.get('items',[]) if isinstance(d,dict) else d)
ix={r['id']:r for r in indexed}
for r in actual:
    if r.get('name_mihome'):
        for field in ('name','name_mihome','category','category_mihome','catalog_display','image_mihome','miio_model','mihome_pd_id'):
            assert ix[r['id']].get(field)==r.get(field), (r['id'],field)
result=dict(baseline_file=baseline.name,revision=meta['revision'],count=len(actual),entire_catalog_equals_reviewed_patch=True,
            mappings=sum('mihome_model'in r for r in actual),icons=sum(bool(r.get('image_mihome')) for r in actual),independent_names=sum(bool(r.get('name_mihome')) for r in actual),
            changes={field:sum(a.get(field)!=b.get(field) for a,b in zip(before,actual)) for field in ('name','image','category')},
            date_fields_unchanged=True,dated_before=sum(bool(effective(r)) for r in before),dated_after=sum(bool(effective(r)) for r in actual),
            detail_samples=samples,icon_samples=icons,index_files_verified=index_names)
(root/'online-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=1)+'\n')
print(json.dumps(result,ensure_ascii=False))
