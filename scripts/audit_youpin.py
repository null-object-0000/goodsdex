#!/usr/bin/env python3
"""Bounded anonymous Youpin evidence audit; never mutates published goods."""
import argparse
import hashlib
import gzip
import json
import random
import time
import unicodedata
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('docs/youpin-20261105')
SEMANTIC_ALIASES = {'Xiaomi Sound': 'Xiaomi Sound 音箱',
    'Xiaomi Pad 7 Ultra': 'Xiaomi Pad 7 Ultra 平板电脑',
    'Xiaomi Pad 7S Pro 12.5': 'Xiaomi Pad 7S Pro 12.5 平板电脑',
    'Xiaomi Watch 5': 'Xiaomi Watch 5 手表',
    'Xiaomi Pad 8系列': 'Xiaomi Pad 8 平板电脑'}

HEADERS = {'Content-Type': 'application/json', 'X-Yp-App-Source': 'front-PC',
           'X-User-Agent': 'channel/youpin platform/youpin.pc'}
BASE = 'https://www.xiaomiyoupin.com'


def norm(name):
    return ''.join(unicodedata.normalize('NFKC', name).casefold().split())


def fetch(kind, key, body):
    path = ROOT / 'raw' / f'{kind}-{hashlib.sha256(str(key).encode()).hexdigest()[:16]}.json.gz'
    if path.exists():
        return json.loads(gzip.decompress(path.read_bytes()))['response']
    url = BASE + ('/api/gateway/detail' if kind == 'detail' else '/mtop/market/search/v2/doSearch')
    data = json.dumps(body, ensure_ascii=False).encode()
    req = urllib.request.Request(url, data=data, headers=HEADERS)
    start = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read()
            response = json.loads(raw)
            evidence = {'url': url, 'method': 'POST', 'headers': HEADERS, 'body': body,
                        'captured_at': datetime.now(timezone.utc).isoformat(), 'status': r.status,
                        'seconds': time.monotonic()-start, 'sha256': hashlib.sha256(raw).hexdigest(),
                        'response': response, 'response_raw': raw.decode('utf-8')}
        path.write_bytes(gzip.compress(json.dumps(evidence, ensure_ascii=False).encode(), mtime=0))
        if response.get('code') != 0:
            raise RuntimeError(f'API failure {response.get("code")} {response.get("message")}')
        return response
    finally:
        time.sleep(0.7)


def search(name):
    response = fetch('search', name, [{}, {'query': [{'queryName': name, 'queryType': 0, 'rule': []}],
        'sortBy': 0, 'pageIdx': 0, 'strategyInfo': None, 'filter': None,
        'baseParam': {'imei': '', 'clientVersion': '', 'ypClient': 3}, 'source': 'searchPage',
        'recentAddress': None, 'requestExtraInfo': {}, 'pageSize': 20}])
    return [r['data']['goodsInfo'] for r in response.get('data', {}).get('data', {}).get('goods', [])]


def detail(gid):
    return fetch('detail', gid, {'groupName': 'details', 'groupParams': [[str(gid)]], 'pid': '',
        'methods': [], 'version': '1.0.0', 'debug': False, 'channel': '', 'vipMode': False, 'system': '3'})['data']['goods']


def exact(name):
    candidates = search(name)
    hits = {r['gid']: r for r in candidates if norm(r['name']) == norm(name)}
    return candidates, list(hits.values())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['mapping', 'semantics'])
    parser.add_argument('--goods', default='/tmp/youpin-baseline-goods.json')
    args = parser.parse_args()
    ROOT.mkdir(exist_ok=True, parents=True)
    if args.mode == 'mapping':
        goods = [r for r in json.loads(Path(args.goods).read_text()) if r['id'].startswith('CN:mi_cn:product:')]
        # Simple random sample from all published Xiaomi product rows, fixed seed.
        sample = random.Random(156975).sample(sorted(goods, key=lambda r:r['id']), 50)
        rows = []
        for r in sample:
            row = {'id': r['id'], 'name': r['name'], 'category': r.get('category'),
                   'release_missing': not bool(r.get('release')), 'matches': []}
            try:
                candidates, hits = exact(r['name'])
                row['candidates'] = [{'gid':c['gid'], 'name':c['name']} for c in candidates]
                if len(hits) == 1:
                    g = detail(hits[0]['gid'])
                    b = g.get('brand', {})
                    row['brand'] = b.get('brandName')
                    if b.get('brandName') in ('小米自营产品', '小米', '米家'):
                        row['matches'] = [{'gid':hits[0]['gid'], 'name':g['goodsInfo']['name']}]
                    else:
                        row['rejection'] = 'brand_relationship_not_verified'
                elif len(hits) > 1:
                    row['rejection'] = 'ambiguous_gid'
                else:
                    row['rejection'] = 'no_exact_name_in_first_20_results'
            except Exception as e:
                row['error'] = str(e)
            rows.append(row)
            (ROOT/'mapping-50.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2))
            print(len(rows),row['name'],row['matches'],row.get('error',''),flush=True)
    else:
        entries = json.loads(Path('data/official/xiaomi-release-dictionary.json').read_text())['entries']
        entries = [r for r in entries if r.get('granularity') == 'day' and r.get('event') == 'announcement'
                   and r.get('evidence', {}).get('source_type') == 'official']
        rows = []
        for r in entries:
            try:
                candidates, hits = exact(SEMANTIC_ALIASES.get(r['product_name'], r['product_name']))
                if len(hits) != 1:
                    continue
                g = detail(hits[0]['gid'])
                rows.append({'gid':hits[0]['gid'], 'name':g['goodsInfo']['name'],
                    'goodsInfo':g['goodsInfo'], 'official_date':r['date'], 'official_evidence':r['evidence'],
                    'brand':g.get('brand',{}).get('brandName'),
                    'official_model_name':r['product_name'],
                    'identity_note':'Exact model or curated category suffix; Pad 8 is an explicitly named member of its official launch series'})
                (ROOT/'semantics.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2))
                print(len(rows),r['product_name'],r['date'],flush=True)
                if len(rows) >= 20:
                    break
            except Exception as e:
                print('ERROR',r['product_name'],str(e),flush=True)

if __name__ == '__main__':
    main()
