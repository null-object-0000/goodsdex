"""Verify immutable OSS blobs against one manifest and the frozen pre-release audit."""
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from goodsdex.exclusions import validate_excluded
BASE = 'https://spend-good.oss-cn-shanghai.aliyuncs.com/data/public/'


def fetch(path):
    return subprocess.check_output(['curl', '-fsS', '--retry', '2', '--max-time', '45', BASE + path])


def main():
    raw_meta = fetch('meta.json')
    meta = json.loads(raw_meta)
    assert meta['excluded_by_rule'].get('apparel') == 77
    files = {}
    for name in ('goods.json', 'goods-excluded.json'):
        d = meta['files'][name]
        raw = fetch('blobs/' + d['sha256'] + '.json')
        assert len(raw) == d['bytes']
        assert hashlib.sha256(raw).hexdigest() == d['sha256']
        files[name] = json.loads(raw)
    goods, excluded = files['goods.json'], files['goods-excluded.json']
    validate_excluded(meta, excluded, goods)
    before = json.loads(gzip.decompress((HERE / 'published-before.json.gz').read_bytes()))
    expected = json.loads((HERE / 'audit.json').read_text())
    removed = {r['id'] for r in before} - {r['id'] for r in goods}
    assert removed == set(expected['removed_ids'])
    assert not ({r['id'] for r in goods} - {r['id'] for r in before})
    assert len(goods) == meta['total_published'] == 3605
    assert meta['total_all'] == 4822 and meta['total_excluded'] == 1217
    hits = [r for r in excluded['items'] if r['excluded_reason'] == 'apparel']
    assert {r['id'] for r in hits} == removed
    by_id = {r['id']: r for r in before}
    assert all(all(r.get(k) == v for k,v in by_id[r['id']].items()) for r in hits)
    assert all(r['matched_rule'] in ('category','name') and r['matched_text'] for r in hits)
    evidence = json.loads((HERE / 'counterexamples.json').read_text())
    keep_ids = {evidence['washer_observed']['id'], *[r['id'] for r in evidence['observed_category_conflicts_kept']]}
    assert keep_ids <= {r['id'] for r in goods}
    candidates = json.loads((HERE / 'non-durables.json').read_text())
    candidate_ids = {r['id'] for r in candidates['items'] if r['status']=='published'}
    assert candidate_ids <= {r['id'] for r in goods}
    assert json.loads(fetch('meta.json'))['revision'] == meta['revision']
    (HERE / 'online-meta.json').write_bytes(raw_meta)
    (HERE / 'online-apparel.json').write_text(json.dumps(hits, ensure_ascii=False, indent=2) + '\n')
    result = dict(revision=meta['revision'], generated_at=meta['generated_at'],
                  before_published=len(before), after_published=len(goods),
                  total_all=meta['total_all'], total_excluded=meta['total_excluded'],
                  excluded_by_rule=meta['excluded_by_rule'],
                  sha256={n:meta['files'][n]['sha256'] for n in files},
                  removed_ids=sorted(removed), counterexample_kept_ids=sorted(keep_ids),
                  non_durable_candidate_kept_ids=sorted(candidate_ids))
    (HERE / 'online-verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k:v for k,v in result.items() if not k.endswith('_ids')},ensure_ascii=False))

if __name__ == '__main__':
    main()
