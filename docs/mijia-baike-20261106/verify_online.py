"""Read and verify the published immutable OSS export and five detail shards."""
import gzip
import hashlib
import json
from pathlib import Path
import sys
import urllib.request
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from goodsdex.shards import shard_for
from goodsdex.mijia_baike import apply_baike
BASE='https://spend-good.oss-cn-shanghai.aliyuncs.com/data/public/'
root=Path(__file__).resolve().parent

def get(url):
    with urllib.request.urlopen(url,timeout=60) as response:return response.read()

meta=json.loads(get(BASE+'meta.json'))
def blob(name):
    descriptor=meta['files'][name]
    raw=get(BASE+'blobs/'+descriptor['sha256']+'.json')
    assert hashlib.sha256(raw).hexdigest()==descriptor['sha256']
    return json.loads(raw)

rows=blob('goods.json'); current={r['id']:r for r in rows}
before={r['id']:r for r in json.loads(gzip.decompress((root/'goods-before.json.gz').read_bytes()))}
expected={r['id']:r for r in apply_baike(list(before.values()))}
expected_ids={k for k,r in expected.items() if r.get('mijia_baike')}
actual_ids={k for k,r in current.items() if r.get('mijia_baike')}
missing=sorted(expected_ids-actual_ids)
changes={field:[k for k in before.keys() & current.keys() if before[k].get(field)!=current[k].get(field)]
         for field in ('name','category','categories','release','release_date','release_upper_bound')}
for key in expected_ids & actual_ids:
    assert current[key]['mijia_baike']==expected[key]['mijia_baike'],key
samples=[]
for key in sorted(expected_ids & actual_ids)[:5]:
    detail=blob(f'detail/{shard_for(key):02x}.json')
    assert detail[key]['mijia_baike']==current[key]['mijia_baike']
    samples.append(dict(id=key,model=detail[key]['mijia_baike']['model'],manual_url=detail[key]['mijia_baike']['manual_url']))
result=dict(revision=meta['revision'],count=meta['count'],expected_metadata=len(expected_ids),
            actual_metadata=len(actual_ids),confirmed_models=sum('miio_model' in r for r in current.values()),
            missing_metadata=missing,changed_fields=changes,detail_samples=samples)
(root/'online-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False))
assert not missing
assert not any(changes.values())
