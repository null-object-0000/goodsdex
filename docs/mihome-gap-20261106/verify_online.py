"""Verify immutable OSS release bytes against the real publication parent."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import urllib.request
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from goodsdex.mihome_intake import apply_intake
from goodsdex.shards import shard_for
from goodsdex.release_coverage import effective
ROOT=Path(__file__).resolve().parent
BASE='https://spend-good.oss-cn-shanghai.aliyuncs.com/data/public/'

def git(ref,name):
    return subprocess.check_output(['git','show',ref+':public/'+name])

def get(url):
    with urllib.request.urlopen(url,timeout=45) as r:return r.read()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data-commit',required=True);ap.add_argument('--run-id',type=int,required=True);a=ap.parse_args()
    before_raw=git(a.data_commit+'^','goods.json');before=json.loads(before_raw);meta=json.loads(git(a.data_commit,'meta.json'));expected=apply_intake(before);cache={}
    def blob(name):
        if name not in cache:
            desc=meta['files'][name];raw=get(BASE+'blobs/'+desc['sha256']+'.json');assert hashlib.sha256(raw).hexdigest()==desc['sha256'];cache[name]=json.loads(raw)
        return cache[name]
    after=blob('goods.json');assert after==expected;assert after[:len(before)]==before
    new=after[len(before):];current={r['id']:r for r in after};samples=json.loads((ROOT/'sample-10-new.json').read_text())
    for r in samples:assert blob(f"detail/{shard_for(r['id']):02x}.json")[r['id']]==current[r['id']]
    ix={}
    for name in ('index/mi_cn.json','index/other.json'):
        ix.update({r['id']:r for r in blob(name)['items']})
    for r in new:
        for field in ('name','image','category','image_mihome','name_mihome','category_mihome','miio_model','mihome_pd_id','source_channels','price','price_missing','price_comparable'):
            assert ix[r['id']].get(field)==r.get(field),(r['id'],field)
        if r['price'] is None:assert not r['price_comparable'] and r['price_missing']=='no_channel_price'
        if r['source']=='mihome':assert r['image'] is None
    pointer=json.loads(get(BASE+'meta.json'));assert pointer['revision']==meta['revision'],'A later release changed the active pointer; recheck latest separately'
    (ROOT/'publication-before.json.gz').write_bytes(gzip.compress(before_raw,mtime=0))
    before_dated=sum(bool(effective(r)) for r in before);after_dated=sum(bool(effective(r)) for r in after)
    result=dict(publication_run_id=a.run_id,data_commit=a.data_commit,revision=meta['revision'],active_pointer_matches=True,before_rows=len(before),after_rows=len(after),added=len(new),with_price=sum(r['price'] is not None for r in new),without_price=sum(r['price'] is None for r in new),comparable=sum(r['price_comparable'] for r in new),all_existing_fields_unchanged=True,entire_catalog_equals_reviewed_append=True,before_dated=before_dated,after_dated=after_dated,coverage_before=before_dated/len(before),coverage_after=after_dated/len(after),coverage_if_20pct_new_dated=(before_dated+len(new)*.2)/len(after),detail_samples_verified=len(samples),new_index_rows_verified=len(new),verified_files=list(cache))
    (ROOT/'online-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
