"""Read back a fixed data release and OSS; retain reproducible acceptance evidence."""
from pathlib import Path
import collections
import gzip
import hashlib
import json
import subprocess
import urllib.request

OUT = Path(__file__).resolve().parent
ROOT = Path.home() / '.cache/goodsdex-price-published'
OSS = 'https://spend-good.oss-cn-shanghai.aliyuncs.com/data/public/'


def download(name):
    with urllib.request.urlopen(OSS + name, timeout=60) as response:
        return response.read(), response.status


def main():
    revision = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip()
    local = (ROOT / 'public/price-history/index.json').read_bytes()
    remote, status = download('price-history/index.json')
    index = json.loads(remote)
    data_sha = hashlib.sha256(local).hexdigest()
    oss_sha = hashlib.sha256(remote).hexdigest()
    assert local == remote
    meta = json.loads(download('meta.json')[0])
    assert index['revision'] == meta['revision']
    events = []
    for descriptor in index['files'] + index['archived_files']:
        raw, _ = download(descriptor['path'])
        assert hashlib.sha256(raw).hexdigest() == descriptor['sha256']
        rows = [json.loads(line) for line in gzip.decompress(raw).splitlines()]
        assert len(rows) == descriptor['count']
        events.extend(rows)
    assert len({(e['gid'], e['at']) for e in events}) == len(events)
    assert not any(e['price'] == 0 for e in events)
    missing = [e for e in events if e['missing_status'] != 'ok']
    assert all(e['price'] is None for e in missing)
    fresh = [e for e in events if not e.get('backfilled')]
    grouped = collections.defaultdict(list)
    for e in events:
        grouped[e['gid']].append(e)
    eligible = {gid: sorted(rows, key=lambda e:e['at']) for gid, rows in grouped.items()
                if len(rows) >= 3 and any(e.get('backfilled') for e in rows) and all(e['price'] is not None for e in rows)}
    gid = 'CN:mi_cn:product:10015'
    trend = eligible[gid]
    result = dict(data_commit=revision, revision=index['revision'], http_status=status,
                  data_sha256=data_sha, oss_sha256=oss_sha, index=index,
                  today_added_count=sum(e['at'].startswith('2026-11-04') for e in fresh),
                  collection_rounds=dict(collections.Counter(e['at'] for e in fresh)),
                  fresh_samples=fresh[:3], missing_count=len(missing),
                  missing_samples=[next(e for e in missing if e['missing_status']==status) for status in ('no_price','unavailable')],
                  backfilled_count=sum(bool(e.get('backfilled')) for e in events),
                  backfilled_priced_count=sum(bool(e.get('backfilled')) and e['price'] is not None for e in events),
                  gid=gid, trend=trend)
    (OUT / 'acceptance.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    (OUT / 'published-index.json').write_bytes(remote)
    print(json.dumps({k:v for k,v in result.items() if k not in ('index','trend','fresh_samples','missing_samples','collection_rounds')}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
