"""Acceptance readback: frozen append, no lost/changed rows, sources and prices."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from goodsdex.earbuds_intake import apply_intake
from goodsdex.price_semantics import comparable, validate
from goodsdex.release_coverage import matrix
from goodsdex.shards import shard_for

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--before',type=Path,required=True);ap.add_argument('--public',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    before=json.loads(a.before.read_text());after=json.loads((a.public/'goods.json').read_text());meta=json.loads((a.public/'meta.json').read_text())
    assert after==apply_intake(before), 'Unexpected change outside reviewed Earbuds append'
    assert after[:len(before)]==before
    assert len(after)-len(before) in (0,23)
    new=after[len(before):];validate(new)
    for r in new:
        assert r['primary_source']==r['discovered_by']=='earbuds_directory'
        assert sum(s['role']=='primary' for s in r['sources'])==1
        assert r['price'] is None and r['price_missing']=='no_channel_price' and not comparable(r)
        assert r['display']['price']['missing']=='no_channel_price'
        assert not r.get('release_effective')
        detail=json.loads((a.public/'detail'/f'{shard_for(r["id"]):02x}.json').read_text())
        assert detail[r['id']]==r
    for path,info in meta['files'].items():
        assert hashlib.sha256((a.public/path).read_bytes()).hexdigest()==info['sha256']
    b=matrix(before)['total'];e=matrix(after)['total']
    assert b['covered']==e['covered']
    assert meta['release_precision']['total']==e
    result=dict(ok=True,revision=meta['revision'],before=len(before),after=len(after),added=len(new),existing_rows_unchanged=True,duplicate_rows_retained=True,new_comparable_offers=sum(comparable(r) for r in new),sources_and_shards_verified=len(new),before_coverage=b,after_coverage=e,manifest_hashes_verified=len(meta['files']))
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=1)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('before_coverage','after_coverage')},ensure_ascii=False))
if __name__=='__main__':main()
