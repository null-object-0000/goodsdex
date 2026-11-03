"""Verify the actual data commit, OSS mirror and public HTTP responses."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
from urllib.parse import quote

import requests

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
BASE = 'https://spend.snewbie.site'
OSS = 'https://spend-good.oss-cn-shanghai.aliyuncs.com/data/public'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--before', type=Path, required=True)
    ap.add_argument('--published', type=Path, required=True)
    ap.add_argument('--data-commit', required=True)
    args = ap.parse_args()
    raw = args.published.read_bytes()
    before = json.loads(args.before.read_bytes())
    after = json.loads(raw)
    expected = {key: b for b in json.loads((ROOT / 'docs/series-release-rollout-20261103/batches.json').read_text()) for key in b['ids']}
    by_id = {r['id']: r for r in after}
    assert {r['id'] for r in after if r.get('release_series')} == expected.keys()
    assert len(expected) == 149
    assert len(before) == len(after) == 2909
    assert sum(bool(r.get('release')) for r in before) == sum(bool(r.get('release')) for r in after) == 671
    assert {r['id']: r.get('release') for r in before} == {r['id']: r.get('release') for r in after}
    strip = lambda rows: [{k: v for k, v in r.items() if k not in ('series_release', 'release_series')} for r in rows]
    assert strip(before) == strip(after)
    assert all('series_release' not in r for r in after)
    for key, batch in expected.items():
        series = by_id[key]['release_series']
        assert (series['date'], series['batch_id'], series['evidence']['url']) == (batch['date'], batch['batch_id'], batch['url'])
        assert series['level'] == 'series' and series['granularity'] == 'month'
        assert series['inherited'] is (not bool((by_id[key].get('release') or {}).get('date')))
    session = requests.Session()
    session.trust_env = False

    def get(url):
        response = session.get(url, headers={'Cache-Control': 'no-cache'}, timeout=60)
        response.raise_for_status()
        return response

    oss = get(OSS + '/goods.json')
    assert oss.content == raw
    oss_meta = get(OSS + '/meta.json').json()
    sha = hashlib.sha256(raw).hexdigest()
    assert oss_meta['files']['goods.json']['sha256'] == sha
    live = get(BASE + '/api/goods')
    assert live.json() == after
    assert get(BASE + '/api/meta').json()['files']['goods.json']['sha256'] == sha
    samples = []
    for tail in ['23270', '22339', '21825', '23577', '10050236']:
        key = 'CN:mi_cn:product:' + tail
        url = BASE + '/api/goods/' + quote(key, safe='')
        row = get(url).json()
        assert row['release_series'] == by_id[key]['release_series']
        assert row.get('release') == by_id[key].get('release')
        samples.append(dict(id=key, name=row['name'], release=row.get('release'), release_series=row['release_series'], api=url))
    assert samples[-1]['release']['date'] == '2026-08'
    assert samples[-1]['release_series']['date'] == '2026-09'
    assert samples[-1]['release_series']['inherited'] is False
    listing = get(BASE + '/api/goods/search?q=' + quote('巨省电') + '&limit=20').json()
    assert listing['items'] and all('release_series' not in r for r in listing['items'])
    from datetime import datetime, timezone
    result = dict(checked_at=datetime.now(timezone.utc).isoformat(), data_commit=args.data_commit,
                  count=len(after), release_before=671, release_after=671, release_series_before=sum(bool(r.get('release_series')) for r in before),
                  release_series_after=149, batches=len({r['release_series']['batch_id'] for r in after if r.get('release_series')}),
                  product_objects_unchanged=True, all_other_fields_unchanged=True, goods_sha256=sha,
                  oss_bytes_equal=True, api_catalog_equal=True, search_omits_series_evidence=True, samples=samples,
                  members=[dict(id=key, batch_id=b['batch_id']) for key, b in expected.items()])
    (P / 'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    (P / 'baseline-goods.json.gz').write_bytes(gzip.compress(args.before.read_bytes(), mtime=0))
    (P / 'published-goods.json.gz').write_bytes(gzip.compress(raw, mtime=0))
    (P / 'oss-meta.json').write_text(json.dumps(oss_meta, ensure_ascii=False, indent=2) + '\n')
    lines = ['# 线上五条抽查', '', '|ID|名称|单品日期|系列日期|批次|证据|', '|---|---|---|---|---|---|']
    for row in samples:
        series = row['release_series']
        lines.append(f"|{row['id']}|{row['name']}|{(row['release'] or {}).get('date', 'null')}|{series['date']}|{series['batch_id']}|[原文]({series['evidence']['url']})|")
    lines += ['', '巨省电真实详情摘录（完整字段见 verification.json）：', '', '```json', json.dumps(samples[0], ensure_ascii=False, indent=2), '```', '', '最后一条为并存反例：单品日期 2026-08 原样保留，系列日期为 2026-09，inherited=false。']
    (P / 'samples.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('samples', 'members')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
