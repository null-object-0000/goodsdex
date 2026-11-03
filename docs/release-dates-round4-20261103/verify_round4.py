"""Data/evidence acceptance check; no network and no publication mutation."""
import collections,gzip,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,'src')
from goodsdex.release_dates import coverage,validate
from capture import ROOT,html,save
before=json.load(open('/tmp/goodsdex-round4-before.json'));after=json.load(open('/tmp/goodsdex-release-round4/public/goods.json'));new=json.load(open(ROOT/'new-candidates.json'))
assert len(before)==len(after)==3968
assert [r['id'] for r in before]==[r['id'] for r in after]
assert [{k:v for k,v in r.items() if k!='release'} for r in before]==[{k:v for k,v in r.items() if k!='release'} for r in after]
by={r['id']:r for r in after};added={c['ids'][0] for c in new};assert len(added)==len(new)
for a,b in zip(before,after):
 if a['id'] not in added:assert a.get('release')==b.get('release'),a['id']
for c in new:
 validate(c);e=c['release']['evidence'];p=Path(c['capture_file']);o=json.load(open(p));raw=gzip.decompress((p.parent/o['raw_file']).read_bytes());assert hashlib.sha256(raw).hexdigest()==e['sha256'],c['ids'][0]
 assert e['quote'] in (html(dict(o,evidence_file=str(p))) if c['ids'][0]=='CN:mi_cn:product:8382' else o['text']),c['ids'][0]
 assert by[c['ids'][0]]['release']['date']==c['release']['date']
 assert by[c['ids'][0]]['release']['source']=='official'
 assert 'capture_file' not in by[c['ids'][0]]['release']['evidence']
assert sum(bool(r.get('release')) for r in after)-sum(bool(r.get('release')) for r in before)==len(new)
assert not by['CN:dji:sku:158331'].get('release')
result=dict(rows_before=len(before),rows_after=len(after),unique_ids=len(by),non_release_fields_equal=True,old_release_fields_equal=True,verified_new_evidence_count=len(new),new_events=dict(collections.Counter(c['release']['event'] for c in new)),before=coverage(before),after=coverage(after))
save('identity-invariants.json',result);print(json.dumps(result,ensure_ascii=False))
