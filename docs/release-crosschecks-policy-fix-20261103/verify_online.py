"""Compare all 39 live release objects and the five real conflict detail endpoints."""
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--expected', type=Path, required=True)
    args = ap.parse_args()
    out = Path(__file__).parent
    stamp = datetime.now(timezone.utc).isoformat()
    base = 'https://spend.snewbie.site'
    def fetch(path):
        url = base+path+'?evidence_policy='+quote(stamp, safe='')
        with urlopen(Request(url, headers={'Accept-Encoding':'gzip'}), timeout=60) as res:
            raw = res.read()
            if res.headers.get('Content-Encoding') == 'gzip':
                raw = gzip.decompress(raw)
        return url, json.loads(raw)
    expected = {r['id']: r for r in json.loads(args.expected.read_text())}
    _, actual = fetch('/api/goods')
    by_id = {r['id']:r for r in actual}
    comparison = json.loads((out/'comparison-39.json').read_text())
    for r in comparison:
        key = r['id']
        assert by_id[key]['release'] == expected[key]['release'], key
        assert by_id[key]['release']['evidence'] == r['original_evidence'], key
    details = []
    for r in json.loads((out/'conflicts-5.json').read_text()):
        key = r['id']
        url, actual = fetch('/api/goods/'+quote(key,safe=''))
        assert actual['id'] == key and actual['release'] == expected[key]['release'], key
        details.append(dict(id=key, name=actual['name'], url=url, release=actual['release'], release_equal=True))
    _, health = fetch('/health.json')
    result = dict(checked_at=stamp, expected_catalog_sha256=hashlib.sha256(args.expected.read_bytes()).hexdigest(),
        all_39_release_objects_equal=True, original_third_party_evidence_unchanged=True,
        all_5_detail_endpoints_equal=True, samples=details,
        health=dict(now=health.get('now'),gitCommit=health.get('gitCommit'), data=health.get('data')))
    (out/'final-releases-online.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(dict(all_39_release_objects_equal=True, all_5_detail_endpoints_equal=True,checked_at=stamp)))


if __name__ == '__main__':
    main()
