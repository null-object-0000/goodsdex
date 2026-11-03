"""Read-only verification of the published date corpus and real detail endpoints."""
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import sys
from urllib.parse import quote
from urllib.request import Request, urlopen

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from goodsdex.release_dates import coverage


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--public',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--base',default='https://spend.snewbie.site')
    ap.add_argument('--sample-id',action='append',default=[],
                    help='Additional exact IDs to verify through real detail endpoints')
    args = ap.parse_args()
    rows = json.loads((args.public/'goods.json').read_text())
    stamp = datetime.now(timezone.utc).isoformat()
    def fetch(path):
        with urlopen(Request(args.base+path,headers={'Accept-Encoding':'gzip'}),timeout=90) as response:
            raw = response.read()
            if response.headers.get('Content-Encoding') == 'gzip':
                raw = gzip.decompress(raw)
            return json.loads(raw)
    actual = fetch('/api/goods?release_check='+quote(stamp,safe=''))
    assert actual == rows, 'Online catalogue does not match this data release yet'
    examples = ['CN:mi_cn:product:18520', 'CN:mi_cn:product:20543',
                'GLOBAL:apple_support:model:111843', 'CN:hp_cn:sku:7Y0Y4PC', 'CN:mi_cn:product:23261']
    examples += [next(r['id'] for r in rows if (r.get('release') or {}).get('event') == 'planned_availability')]
    examples += [next(r['id'] for r in rows if r.get('source') == 'apple_cn' and
                     (r.get('release') or {}).get('event') == 'availability')]
    examples = list(dict.fromkeys(examples + args.sample_id))
    samples = []
    for key in examples:
        path = '/api/goods/'+quote(key,safe='')+'?release_check='+quote(stamp,safe='')
        detail = fetch(path)
        expected = next(r for r in rows if r['id'] == key)
        assert detail['id'] == key
        assert detail.get('release') == expected.get('release'), (key, 'release field mismatch')
        samples.append(dict(id=key,name=detail['name'],url=args.base+path,
                            release=detail.get('release'),release_equal=True))
    result = dict(checked_at=stamp,full_catalog_equal=True,coverage=coverage(actual),
                  release_sha256=hashlib.sha256((args.public/'goods.json').read_bytes()).hexdigest(),
                  samples=samples)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(full_catalog_equal=True,details=len(samples),coverage=result['coverage']),ensure_ascii=False))


if __name__ == '__main__':
    main()
