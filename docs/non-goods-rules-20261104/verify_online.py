"""Verify one OSS manifest and its immutable goods/exclusion blobs."""
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
from collections import Counter

HERE = Path(__file__).resolve().parent
BASE = 'https://spend-good.oss-cn-shanghai.aliyuncs.com/data/public/'

def fetch(path):
    return subprocess.check_output(['curl', '-fsS', '--retry', '3', '--max-time', '90', BASE + path])


def main():
    raw_meta = fetch('meta.json')
    meta = json.loads(raw_meta)
    assert meta['excluded_by_rule']['preorder_deposit'] == 1
    files = {}
    hashes = {}
    for name in ('goods.json', 'goods-excluded.json'):
        descriptor = meta['files'][name]
        raw = fetch(f"blobs/{descriptor['sha256']}.json")
        assert hashlib.sha256(raw).hexdigest() == descriptor['sha256']
        assert len(raw) == descriptor['bytes']
        files[name] = json.loads(raw)
        hashes[name] = descriptor['sha256']
    goods, excluded = files['goods.json'], files['goods-excluded.json']
    before = json.loads(gzip.decompress((HERE / 'published-before.json.gz').read_bytes()))
    target = 'CN:mi_cn:product:19045'
    assert {r['id'] for r in before} - {r['id'] for r in goods} == {target}
    assert not ({r['id'] for r in goods} - {r['id'] for r in before})
    assert excluded['revision'] == meta['revision']
    assert excluded['generatedAt'] == meta['generated_at']
    assert meta['count'] == meta['total_published'] == len(goods) == 2855
    assert meta['total_excluded'] == excluded['total'] == len(excluded['items']) == 1127
    assert meta['total_all'] == len(goods) + excluded['total'] == 3982
    counts = Counter(r['matched_rule'] for r in excluded['items'])
    assert meta['excluded_by_rule'] == {k: counts[k] for k in meta['excluded_by_rule']}
    hit = next(r for r in excluded['items'] if r['id'] == target)
    assert hit['matched_rule'] == hit['exclusion']['matched_rule'] == 'preorder_deposit'
    assert hit['matched_text'] == hit['exclusion']['matched_text'] == '权益'
    assert hit['price'] == 1
    assert json.loads(fetch('meta.json'))['revision'] == meta['revision'], 'Manifest changed during verification'
    (HERE / 'online-meta.json').write_bytes(raw_meta)
    summary = dict(revision=meta['revision'], total_all=meta['total_all'],
                   before_published=len(before), after_published=len(goods),
                   total_excluded=excluded['total'], excluded_by_rule=meta['excluded_by_rule'],
                   sha256=hashes, removed_ids=[target], excluded_item=hit)
    (HERE / 'online-verification.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k:v for k,v in summary.items() if k != 'excluded_item'}, ensure_ascii=False))

if __name__ == '__main__':
    main()
