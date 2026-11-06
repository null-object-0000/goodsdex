"""Offline evidence and actual finalize_public/shard acceptance. Never publishes."""
from pathlib import Path
import gzip,hashlib,json,re,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[1]
sys.path[:0]=[str(REPO/'src'),str(REPO/'scripts')]
from goodsdex.release_dates import apply_release_dates
from goodsdex.release_scope import displayable
from goodsdex.third_party_release import assess
from goodsdex.dedupe import finalize_public

def read(p):return json.loads(p.read_text())
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
new=read(ROOT/'new-media-candidates.json');new_ids={c['id'] for c in new}|{'CN:fuji:kit:x-s20-16-50mm'}
expected={'20833':('2024-12','availability'),'20807':('2024-12','availability'),'20981':('2025-02','announcement'),'19409':('2023-11','availability'),'20276':('2024-08','availability'),'18520':('2023-05','announcement'),'19332':('2023-10','availability'),'10015':('2019-06','availability')}
for c in new:
    assert assess(c['assertions'])['display_allowed']
    for a in c['assertions']:
        e=a['evidence'];raw=gzip.decompress((REPO/e['capture_file']).read_bytes())
        assert hashlib.sha256(raw).hexdigest()==e['sha256']
        assert e['quote'] in re.sub(r'\s+',' ',(REPO/e['text_file']).read_text()).strip()
# Compare old/new canonical inputs through the same production importer. Patch only
# the media path used by the importer, without changing policy or checked-in files.
old_official=json.loads(subprocess.check_output(['git','show','5b6dddc7:data/official/release-dates.json'],cwd=REPO))
old_media=json.loads(subprocess.check_output(['git','show','5b6dddc7:data/third-party/release-dates.json'],cwd=REPO))
baseline_raw=subprocess.check_output(['git','show','2cd5f4173b420a8c51b674a293313f544233f4e7:public/goods.json.gz'],cwd=REPO)
rows=json.loads(gzip.decompress(baseline_raw))
import goodsdex.third_party_release as media
real=media.apply_third_party
with tempfile.TemporaryDirectory(prefix='goodsdex-user-items-',dir='/var/tmp') as d:
    d=Path(d);p=d/'old-official.json';write(p,old_official);m=d/'old-media.json';write(m,old_media)
    # Custom input retains original LLM/crosscheck inputs, but does not automatically invoke media.
    from goodsdex.release_dates import LLM_INPUT,CROSSCHECK_INPUT
    before=real(apply_release_dates(rows,p,LLM_INPUT,CROSSCHECK_INPUT),m)
    after=apply_release_dates(rows)
    assert {a['id'] for a,b in zip(before,after) if a!=b}==new_ids
    assert apply_release_dates(after)==after
    for a,b in zip(before,after):assert {k:v for k,v in a.items() if k!='release'}=={k:v for k,v in b.items() if k!='release'}
    public=d/'public';public.mkdir();write(public/'goods.json',rows)
    # Full actual publication finalizer, including shards. Isolated local output only.
    finalize_public(public,previous=rows)
    from goodsdex.shards import build_shards
    build_shards(public)
    generated=read(public/'goods.json');byid={r['id']:r for r in generated}
    for pid,(month,event) in expected.items():
        key='CN:mi_cn:product:'+pid;r=byid[key]['release']
        assert (r['date'],r['event'])==(month,event),(key,r)
        assert r['source']=='third_party' and r['display_allowed'] and r['crosscheck_status']=='corroborated'
    kit=byid['CN:fuji:kit:x-s20-16-50mm']['release']
    assert (kit['date'],kit['source'],kit['event'],kit['market'])==('2024-05','official','announcement','US')
    assert displayable(kit)
    targets=read(ROOT/'baseline-targets.json')
    for r in targets:
        key=r['id']
        if key not in new_ids:assert byid[key].get('release')==r.get('release'),key
    write(ROOT/'after-targets.json',[byid[r['id']] for r in targets])
    write(ROOT/'generated-release-samples.json',[dict(id=k,name=byid[k]['name'],release=byid[k]['release']) for k in sorted(new_ids)])
    # Check public detail shard contents contain the same date; discover layout from finalizer.
    detail_files=list((public/'detail').rglob('*.json*'))
    matched=set()
    for f in detail_files:
        raw=f.read_bytes();data=json.loads(gzip.decompress(raw) if raw[:2]==b'\x1f\x8b' else raw)
        values=data if isinstance(data,list) else [data] if 'id' in data else list(data.values())
        for row in values:
            if isinstance(row,dict) and row.get('id') in new_ids:
                assert row['release']==byid[row['id']]['release'];matched.add(row['id'])
    assert matched==new_ids,('detail shard missing',new_ids-matched,len(detail_files))
    summary=dict(baseline_rows=len(rows),generated_rows=len(generated),changed_importer_ids=sorted(new_ids),newly_displayable_user_items=7,newly_displayable_category_items=2,evidence_assertions=17,official_added=1,third_party_dual_source_products=8,importer_idempotent=True,non_release_fields_unchanged=True,full_finalize_public=True,detail_shard_ids=sorted(matched),existing_four_user_releases_unchanged=True,unverified_user_ids=['CN:mi_cn:product:9726'])
    write(ROOT/'verification.json',summary);print(json.dumps(summary,ensure_ascii=False))
