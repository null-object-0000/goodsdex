"""Verify actual API, committed publication, locked parent and 3 real details."""
import argparse,datetime,gzip,hashlib,json,pathlib,subprocess
from urllib.parse import quote
from goodsdex.release_dates import apply_release_dates
from goodsdex.series_release import apply_series_releases
from goodsdex.release_scope import scope_coverage,displayable
ROOT=pathlib.Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--data-revision',required=True);args=ap.parse_args()
def gitfile(rev,path):return subprocess.check_output(['git','show',rev+':public/'+path])
def fetch(path):
 result=subprocess.run(['curl','-fLsS','--compressed','--max-time','90','https://spend.snewbie.site'+path],capture_output=True,check=True)
 return result.stdout,json.loads(result.stdout)
stamp=datetime.datetime.now(datetime.timezone.utc).isoformat();query='?round10='+quote(stamp,safe='')
published=json.loads(gitfile(args.data_revision,'goods.json'));pubmeta=json.loads(gitfile(args.data_revision,'meta.json'));parent=json.loads(gitfile(args.data_revision+'^','goods.json'))
(ROOT/'locked-parent-goods.json.gz').write_bytes(gzip.compress(json.dumps(parent,ensure_ascii=False).encode()))
raw,actual=fetch('/api/goods'+query);(ROOT/'online-goods.json.gz').write_bytes(gzip.compress(raw))
raw,meta=fetch('/api/meta'+query);(ROOT/'meta-after.json').write_bytes(raw)
assert actual==published,'Real online goods differ from the data commit'
assert meta==pubmeta,'Real online meta differs from the data commit'
assert scope_coverage(actual)==meta['release_scope']
expected=apply_series_releases(apply_release_dates(parent));assert expected==published,'Locked parent replay differs'
assert len(parent)==len(published)
for a,b in zip(parent,published,strict=True):
 assert {k:v for k,v in a.items() if k not in ('release','release_series')}=={k:v for k,v in b.items() if k not in ('release','release_series')},a['id']
baseline=json.loads(gzip.decompress((ROOT/'baseline.json.gz').read_bytes()));idx={r['id']:r for r in actual}
locked=[r for r in baseline if r.get('brand')=='Apple' and displayable(r.get('release'))]
assert len(locked)==417
for r in locked:assert r['release']==idx[r['id']]['release'],r['id']
cs=json.load(open(ROOT/'new-candidates.json'))+json.load(open(ROOT/'apple-new-candidates.json'))
for c in cs:
 r=idx[c['ids'][0]]['release'];assert displayable(r)
 for key in ('date','event','market','source','evidence'):assert r[key]==c['release'][key],(c['name'],key)
ids=['CN:fuji:model:x-s20','CN:fuji:kit:x-e5-xf23mmf28-r-wr','GLOBAL:apple_support:model:111940'];samples=[]
for i,key in enumerate(ids,1):
 path='/api/goods/'+quote(key,safe='');raw,value=fetch(path+query);(ROOT/f'online-detail-{i}.json').write_bytes(raw);assert value==idx[key],key
 r=value['release'];sample={k:value.get(k) for k in ('id','gid','name')};sample['url']='https://spend.snewbie.site'+path;sample['release']={k:r[k] for k in ('date','event','market','source','label','crosscheck_status') if k in r};sample['release']['evidence']={k:r['evidence'][k] for k in ('url','quote')};samples.append(sample)
result=dict(checked_at=stamp,data_revision=args.data_revision,online_meta_equals_committed=True,online_goods_equals_committed=True,locked_parent_replay_equals_committed=True,non_date_fields_unchanged=True,apple_locked_unchanged=len(locked),new_assertions_verified=len(cs),rows=len(actual),unique_ids=len(idx),release_changes=sum(a.get('release')!=b.get('release') for a,b in zip(parent,published)),series_changes=sum(a.get('release_series')!=b.get('release_series') for a,b in zip(parent,published)),meta={k:meta.get(k) for k in ('revision','total_all','total_published','total_excluded','release_scope')},samples=samples)
(ROOT/'online-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
(ROOT/'online-excerpts.md').write_text('# 真实线上 /api/meta 与三个详情摘录\n\n核验时间：'+stamp+'。下面均为实际HTTP返回，不是本地重建。三个canonical ID的gid均按实际响应保留；不虚构数值gid。\n\n```json\n'+json.dumps(dict(meta=result['meta'],samples=samples),ensure_ascii=False,indent=2)+'\n```\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('meta','samples')},ensure_ascii=False));print(json.dumps(meta['release_scope']['brands'],ensure_ascii=False))
