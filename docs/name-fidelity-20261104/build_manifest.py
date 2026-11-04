"""Build repair solely from successful live title evidence, preserving raw responses."""
import json, gzip, hashlib, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from goodsdex.mi_names import page_name
from goodsdex.series_release import identity
from goodsdex.release_dates import digest
here=Path(__file__).resolve().parent
records=[json.loads(l) for l in (here/'titles.jsonl').read_text().splitlines()]
items=[]
for r in records:
    if not r['official_name']:continue
    raw=gzip.decompress((ROOT/r['evidence']).read_bytes())
    assert hashlib.sha256(raw).hexdigest()==r['sha256']
    assert page_name(raw.decode('utf8','replace'))==r['official_name']
    items.append(dict(id=r['id'],name=r['official_name'],**{k:r[k] for k in ('title','status','url','final_url','requested_at','sha256','evidence')}))
manifest=dict(schema=1,rule='official title minus exact 立即购买-小米商城 suffix; preserve all model/bundle/accessory words',items=items)
(ROOT/'data/official/mi-page-names.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
# A literal name repair legitimately changes a reviewed membership fingerprint.
# Add only exact same-ID, same-model, same-params alternatives backed by live titles.
source=ROOT/'data/official/series-releases.json';series=json.loads(source.read_text())
members={m['id']:m for b in series['batches'] for m in b['members']}
by_id={i['id']:i for i in items};updates=json.loads((here/'series-membership-title-repairs.json').read_text()) if (here/'series-membership-title-repairs.json').exists() else []
paths=[here/'baseline-goods.json.gz', ROOT/'docs/independent-dates-20261103/baseline-goods.json.gz',ROOT/'docs/series-release-rollout-20261103/baseline-goods.json.gz']
for path in paths:
    raw=path.read_bytes();rows=json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)
    for row in rows:
        entry=by_id.get(row['id']);member=members.get(row['id'])
        if not entry or not member or row['name']==entry['name']:continue
        old=digest(identity(row));allowed=[member['identity_sha256'],*member.get('identity_sha256_alternates',[])]
        if old not in allowed:continue
        updated=digest(identity(dict(row,name=entry['name'])))
        if updated not in allowed:
            member.setdefault('identity_sha256_alternates',[]).append(updated)
            updates.append(dict(id=row['id'],before=row['name'],after=entry['name'],original_sha256=old,alternate_sha256=updated,evidence=entry['evidence']))
source.write_text(json.dumps(series,ensure_ascii=False,indent=2)+'\n')
(here/'series-membership-title-repairs.json').write_text(json.dumps(updates,ensure_ascii=False,indent=2)+'\n')
print('verified names',len(items),'series alternatives added',len(updates))
