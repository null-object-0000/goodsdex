"""Read manifest, verify exact public files, then apply inventory audit."""
from urllib.request import urlopen
from pathlib import Path
import hashlib
import json
import subprocess
import sys
from collections import Counter

base = 'https://spend-good.oss-cn-shanghai.aliyuncs.com/data/public/'
def fetch(name):
    with urlopen(base + name, timeout=45) as response:
        return response.read()
meta = json.loads(fetch('meta.json'))
root = Path(sys.argv[1]); root.mkdir(parents=True, exist_ok=True)
for name in ['goods.json', 'goods-excluded.json']:
    raw = fetch(name)
    assert hashlib.sha256(raw).hexdigest() == meta['files'][name]['sha256']
    (root / name).write_bytes(raw)
(root / 'meta.json').write_text(json.dumps(meta))
e = json.loads((root / 'goods-excluded.json').read_bytes())
assert e['revision'] == meta['revision'] and e['generatedAt'] == meta['generated_at']
counts = Counter(r['excluded_reason'] for r in e['items'])
assert all(e['reasons'][k] == counts[k] for k in e['reasons'])
assert counts['service:installation'] == 17 and counts['service:other'] == 29
assert meta['total_all'] == 3982 == meta['total_published'] + meta['total_excluded']
assert meta['total_published'] == 2856 and meta['total_excluded'] == 1126
result = dict(url=base+'goods-excluded.json', revision=meta['revision'], generatedAt=meta['generated_at'], reasons=e['reasons'], total_all=meta['total_all'], total_published=meta['total_published'], total_excluded=meta['total_excluded'], hashes_verified=True, run='https://github.com/null-object-0000/goodsdex/actions/runs/41798580189')
Path('docs/services-20261104/online.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
print(json.dumps(result, ensure_ascii=False))
