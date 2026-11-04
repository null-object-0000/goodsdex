"""Independently check persisted observations, data/OSS parity and live APIs."""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import urllib.parse
import urllib.request

OUT = Path(__file__).resolve().parent
OSS = 'https://spend-good.oss-cn-shanghai.aliyuncs.com/data/public/'


def download(url):
    with urllib.request.urlopen(url, timeout=90) as response:
        return response.read()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main(public, online):
    raw_index = (public / 'price-history/index.json').read_bytes()
    index = json.loads(raw_index)
    before = {}
    tip = index['git_backfill']['tip']
    old = json.loads(subprocess.check_output(['git', 'show', f'{tip}:public/price-history/index.json']))
    for d in old['files'] + old['archived_files']:
        raw = subprocess.check_output(['git', 'show', f'{tip}:public/{d["path"]}'])
        for line in gzip.decompress(raw).splitlines():
            e = json.loads(line)
            before[e['gid'], e['at']] = e
    counts, sources, seen = Counter(), Counter(), set()
    suspicious, existing_changed, suspicious_count = [], [], 0
    for descriptor in index['files'] + index['archived_files']:
        path = public / descriptor['path']
        raw = path.read_bytes()
        assert sha(raw) == descriptor['sha256'] and len(raw) == descriptor['bytes']
        if online:
            assert download(OSS + descriptor['path']) == raw
        n = 0
        with gzip.open(path, 'rt') as fp:
            for line in fp:
                e = json.loads(line)
                key = e['gid'], e['at']
                assert key not in seen
                seen.add(key)
                n += 1
                counts[e['gid']] += 1
                sources[e['time_source']] += 1
                assert e['time_source'] in ('fetched_at', 'commit')
                assert e['price'] is None or 0 < e['price'] < 200000
                if e.get('suspicious'):
                    suspicious_count += 1
                    assert e['price'] is None and 'raw_price' in e
                    if len(suspicious) < 10:
                        suspicious.append(e)
                if key in before:
                    changed = {k: (v, e.get(k)) for k, v in before[key].items() if e.get(k) != v}
                    if changed:
                        existing_changed.append(dict(gid=e['gid'], at=e['at'], changes=changed))
        assert n == descriptor['count']
    assert set(before) <= seen
    assert not existing_changed, existing_changed[:10]
    assert len(seen) == index['observation_count']
    expected = json.loads((OUT / 'statistics.json').read_bytes())
    assert suspicious_count == expected['suspicious_count']
    assert len(counts) == expected['gid_count']
    goods = (public / 'goods.json').read_bytes()
    assert goods == subprocess.check_output(['git', 'show', f'{tip}:public/goods.json'])
    result = dict(index_sha256=sha(raw_index), observation_count=len(seen), gid_count=len(counts),
                  distribution=dict(sorted(Counter(counts.values()).items())), time_sources=dict(sources),
                  existing_preserved=len(before), goods_unchanged=True,
                  suspicious_count=suspicious_count, suspicious_samples=suspicious)
    if online:
        remote = download(OSS + 'price-history/index.json')
        assert remote == raw_index
        result.update(oss_index_sha256=sha(remote), data_commit=subprocess.check_output(['git', '-C', str(public.parent), 'rev-parse', 'HEAD'], text=True).strip())
        samples = json.loads((OUT / 'statistics.json').read_bytes())['sample_gids'][:3]
        api = []
        for gid in samples:
            response = json.loads(download('https://spend.snewbie.site/api/price-history?' + urllib.parse.urlencode(dict(gid=gid))))
            assert response['ok'] and response['observationCount'] == counts[gid], (gid, response['observationCount'], counts[gid])
            api.append(response)
        (OUT / 'api-responses.json').write_text(json.dumps(api, ensure_ascii=False, indent=2) + '\n')
        result['api_summary'] = [{k: e[k] for k in ('gid', 'observationCount', 'intervalMin', 'intervalMax', 'observationStart', 'observationEnd')} for e in api]
    (OUT / ('acceptance.json' if online else 'local-validation.json')).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--public', type=Path, required=True)
    parser.add_argument('--online', action='store_true')
    args = parser.parse_args()
    main(args.public, args.online)
