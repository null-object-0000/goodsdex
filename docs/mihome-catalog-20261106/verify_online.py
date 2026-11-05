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
if not baseline.exists(): baseline=root/'goods-before.json.gz'
before=json.loads(gzip.decompress(baseline.read_bytes()))
expected=apply_catalog(before);actual=blob('goods.json')
# Exact equality also verifies every date field and every unrelated field.
assert actual==expected,'Online catalog differs from reviewed patch over the captured baseline'
current={r['id']:r for r in actual};samples=[]
changes=json.loads((root/'changes.json').read_text());picked=[]
for field,n in [('name',2),('image',1),('category',2)]:
    picked.extend(c for c in [c for c in changes if field in c['fields'] and c['id'] not in {x['id'] for x in picked}][:n])
for c in picked:
    key=c['id'];detail=blob(f'detail/{shard_for(key):02x}.json')[key]
    assert detail==current[key]
    samples.append(dict(id=key,model=detail['mihome_model'],pd_id=detail['mihome_pd_id'],name=detail['name'],image_source=detail.get('image_source'),category=detail['category']))
# Verify model/pdId and icon dimensions also survive the paginated list projection.
index_names=[k for k in meta['files'] if 'index/mi_cn' in k]
indexed=[]
for name in index_names:
    d=blob(name)
    indexed.extend(d.get('items',[]) if isinstance(d,dict) else d)
if index_names:
    ix={r['id']:r for r in indexed}
    for r in actual:
        if 'mihome_model' in r:
            assert ix[r['id']]['mihome_model']==r['mihome_model']
            assert ix[r['id']]['mihome_pd_id']==r['mihome_pd_id']
        if r.get('image_source')=='mihome_icon':
            assert ix[r['id']]['image_width']==ix[r['id']]['image_height']==168
result=dict(baseline_file=baseline.name,revision=meta['revision'],count=len(actual),entire_catalog_equals_reviewed_patch=True,
            mappings=sum('mihome_model'in r for r in actual),icons=sum(r.get('image_source')=='mihome_icon' for r in actual),
            changes={field:sum(a.get(field)!=b.get(field) for a,b in zip(before,actual)) for field in ('name','image','category')},
            date_fields_unchanged=True,dated_before=sum(bool(effective(r)) for r in before),dated_after=sum(bool(effective(r)) for r in actual),
            detail_samples=samples,index_files_verified=index_names)
(root/'online-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=1)+'\n')
print(json.dumps(result,ensure_ascii=False))
