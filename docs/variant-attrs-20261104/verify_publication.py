"""Verify data/OSS manifest and actual API responses against the published release."""
import argparse
import gzip
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))
from goodsdex.variant_attributes import apply_variant_attributes

ROOT = Path(__file__).resolve().parent
BASE = 'https://spend.snewbie.site'
CONFLICT = 'CN:mi_cn:product:20425'
SAMPLES = ['CN:mi_cn:product:10050230', 'CN:mi_cn:product:24248', 'CN:apple_cn:commodity:MD3Y4CH/A']

def fetch(path):
    return subprocess.check_output(['curl', '--noproxy', '*', '--compressed', '-fsSL',
        '--connect-timeout', '10', '--max-time', '120', BASE + path])

def write(name, value):
    (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--public', required=True, type=Path)
    parser.add_argument('--run-id', required=True)
    args = parser.parse_args()
    expected_raw = (args.public / 'goods.json').read_bytes()
    expected = json.loads(expected_raw)
    published_meta = json.loads((args.public / 'meta.json').read_bytes())
    meta = json.loads(fetch('/api/meta'))
    actual_raw = fetch('/api/goods')
    actual = json.loads(actual_raw)
    assert meta['revision'] == published_meta['revision'], 'API has not loaded this release'
    assert meta['files'] == published_meta['files']
    assert hashlib.sha256(expected_raw).hexdigest() == meta['files']['goods.json']['sha256']
    assert actual == expected, 'API inventory differs from data/OSS release'
    replayed, stats = apply_variant_attributes(actual)
    assert replayed == actual
    assert meta['variant_attrs'] == published_meta['variant_attrs'] == stats
    assert stats['groups'] == 98 and stats['members_tagged'] == 665
    tagged = [r for r in actual if r.get('attrs')]
    assert len(tagged) == 665
    assert all(r.get('attrs_source') and r.get('attrs_confidence') for r in tagged)
    conflicts = [r for r in actual if r['id'] == CONFLICT]
    assert conflicts and all(not any(k in r for k in ('attrs', 'attrs_source', 'attrs_confidence')) for r in conflicts)
    details = []
    for key in SAMPLES:
        detail = json.loads(fetch('/api/goods/' + quote(key, safe='')))
        assert detail == next(r for r in actual if r['id'] == key)
        details.append({k: detail[k] for k in ('id', 'name', 'attrs', 'attrs_source', 'attrs_confidence')})
    (ROOT / 'online-goods.json.gz').write_bytes(gzip.compress(actual_raw, mtime=0))
    write('online-meta.json', meta)
    write('api-samples.json', details)
    result = dict(run_id=args.run_id, revision=meta['revision'], variant_attrs=stats,
        actual_rows_with_attrs=len(tagged), conflict_id=CONFLICT, conflict_rows_without_attrs=len(conflicts),
        all_goods_equal=True, manifest_equal=True, goods_sha256=meta['files']['goods.json']['sha256'],
        annotated_by_brand=dict(Counter(r['brand'] for r in tagged)), samples=details)
    write('online-verification.json', result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
