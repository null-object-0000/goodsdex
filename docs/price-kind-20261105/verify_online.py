"""Verify one coherent OSS manifest/blob and the public API against the same release."""
import hashlib,json,subprocess,sys,time
from pathlib import Path
from urllib.parse import quote
ROOT=Path(__file__).resolve().parent
OSS='https://spend-good.oss-cn-shanghai.aliyuncs.com/data/public/'
API='https://spend.snewbie.site'
TARGET='CN:atour:spu:1984:sku:0899000039-C2C-b'
def fetch(url):
    return subprocess.check_output(['curl','--fail','-LsS','--max-time','55','-H','Cache-Control: no-cache',url])
meta_raw=fetch(OSS+'meta.json?price_audit='+str(time.time_ns()));meta=json.loads(meta_raw)
assert 'price_kind' in meta,'New price semantics not yet mirrored'
blob=fetch(OSS+'blobs/'+meta['files']['goods.json']['sha256']+'.json')
assert hashlib.sha256(blob).hexdigest()==meta['files']['goods.json']['sha256']
rows=json.loads(blob);atour=[r for r in rows if r.get('source')=='atour'];target=next(r for r in atour if r['id']==TARGET)
assert len(atour)==267 and len({r['spu_id'] for r in atour})==38
assert target['price'] is None and target['price_kind']=='unknown' and target['price_missing'] and not target['price_comparable'] and target['source_price']==10
assert all(r['price_kind']=='full' or r['price'] is None for r in rows)
from collections import Counter
assert dict(Counter(r['price_kind'] for r in rows))==meta['price_kind']
api_meta_raw=fetch(API+'/api/meta');api_meta=json.loads(api_meta_raw)
assert api_meta['revision']==meta['revision'],'API has not imported the new manifest yet'
api_target=json.loads(fetch(API+'/api/goods/'+quote(TARGET,safe='')))
assert api_target==target,'API detail differs from exact OSS release'
health=json.loads(fetch(API+'/health.json'))
assert health['db']['revision']==meta['revision'] and health['db']['revisionMatches'], 'Admin DB has not imported the new publication'
(ROOT/'evidence/admin-db-health.json').write_text(json.dumps(health['db'],ensure_ascii=False,indent=1)+'\n')
result=json.loads(fetch(API+'/api/goods?q='+quote('亚朵星球')+'&limit=300'))
assert result['total']==267
matched=next(r for r in result['items'] if r['id']==TARGET)
assert matched['price'] is None
(ROOT/'evidence/meta-after.json').write_bytes(meta_raw)
(ROOT/'evidence/api-meta-after.json').write_bytes(api_meta_raw)
(ROOT/'evidence/target-after.json').write_text(json.dumps(target,ensure_ascii=False,indent=1)+'\n')
summary=dict(checked_at=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),revision=meta['revision'],count=len(rows),
    price_kind=meta['price_kind'],atour_count=len(atour),target={k:target[k] for k in ['id','price','price_kind','price_missing','price_comparable','source_price']},
    api_matches_oss=True,goods_sha256=meta['files']['goods.json']['sha256'])
(ROOT/'online-verification.json').write_text(json.dumps(summary,ensure_ascii=False,indent=1)+'\n')
print(json.dumps(summary,ensure_ascii=False))
