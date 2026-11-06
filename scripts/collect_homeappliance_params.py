"""Collect anonymous, exact-model appliance evidence; never OCR or publish.

Raw responses are content-addressed gzip files. The index records errors separately
from valid empty pages. Re-running retries errors while reusing successful captures.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import gzip
import hashlib
import ipaddress
import json
from pathlib import Path
import socket
import sys
import time
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from goodsdex.sources.mi_cn import MTOP_HEADERS, MTOP_URL, UA_PC

CATEGORIES = ('微波炉', '空调', '扫地机器人', '冰箱')
MICROWAVE_IDS = frozenset({'CN:mi_cn:product:10330', 'CN:mi_cn:product:12548',
                           'CN:mi_cn:product:20545', 'CN:mi_cn:product:21480', 'mihome:66347'})
BASE = 'https://home.mi.com/cgi-op/api/v1/baike/v2/'


def read_rows(path):
    return json.loads(gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_bytes())


def request(url, body=None, headers=None, *, max_bytes=30 * 1024 * 1024, max_seconds=60):
    # Public Xiaomi requests can use HTTPS_PROXY; never proxy an internal host.
    parsed = urllib.parse.urlsplit(url)
    url = urllib.parse.urlunsplit(parsed._replace(path=urllib.parse.quote(parsed.path, safe='/%:@')))
    host = parsed.hostname
    addresses = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    internal = any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({})) if internal else urllib.request.build_opener()
    req = urllib.request.Request(url, data=body, headers=headers or {'User-Agent': UA_PC, 'Referer': 'https://www.mi.com/'})
    with opener.open(req, timeout=25) as response:
        chunks = []; size = 0; started = time.monotonic()
        while True:
            chunk = response.read(65536)
            if not chunk: break
            chunks.append(chunk); size += len(chunk)
            if size > max_bytes:raise ValueError(f'response exceeds {max_bytes} bytes')
            if time.monotonic() - started > max_seconds:raise TimeoutError('response exceeded wall time limit')
        return b''.join(chunks)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--goods', type=Path, required=True)
    ap.add_argument('--output', type=Path, default=ROOT / 'docs/homeappliance-params-20261106')
    ap.add_argument('--workers', type=int, default=4)
    a = ap.parse_args()
    a.output.mkdir(parents=True, exist_ok=True)
    rawdir = a.output / 'raw'; rawdir.mkdir(exist_ok=True)
    rows = [r for r in read_rows(a.goods) if r.get('category') in CATEGORIES or r['id'] in MICROWAVE_IDS]
    baike = {r['id']: r for r in json.loads((ROOT / 'data/official/mijia-baike.json').read_text())['items']}
    targets = []
    for row in rows:
        bridge = baike.get(row['id'], {})
        # Use only previously audited device identity or the audited shop-ID bridge.
        model = row.get('miio_model') or row.get('mihome_model')
        if not model and bridge.get('expected_name') == row['name']:
            model = bridge['model']
        targets.append({'id': row['id'], 'expected_name': row['name'], 'category': '微波炉' if row['id'] in MICROWAVE_IDS else row['category'],
                        'model': model, 'mapping': 'existing_model' if row.get('miio_model') or row.get('mihome_model') else 'audited_baike_bridge',
                        'had_params': bool(row.get('params'))})
    (a.output / 'targets.json').write_text(json.dumps(targets, ensure_ascii=False, indent=2))
    jobs = {}
    def add(key, url, body=None, headers=None): jobs[key] = (url, body, headers)
    for t in targets:
        if t['model']:
            for ep in ('product', 'attribute', 'introduction'):
                add(t['model'] + ':' + ep, BASE + ep + '?model=' + t['model'] + ('&region=cn' if ep == 'introduction' else ''))
        if t['id'].startswith('CN:mi_cn:product:'):
            pid = t['id'].split(':')[-1]
            add(pid + ':pc', 'https://api2.order.mi.com/product/view?product_id=' + pid + '&version=2')
            add(pid + ':mobile', MTOP_URL, json.dumps([{}, {'productId': pid}]).encode(), MTOP_HEADERS)
    # 21312 is explicitly requested for investigation; not an alias of 21480.
    add('21312:pc', 'https://api2.order.mi.com/product/view?product_id=21312&version=2')
    add('21312:mobile', MTOP_URL, b'[{}, {"productId": "21312"}]', MTOP_HEADERS)
    oldpath = a.output / 'captures.json'
    captures = json.loads(oldpath.read_text()) if oldpath.exists() else {}
    def fetch(item):
        key, (url, body, headers) = item
        if key in captures and 'error' not in captures[key]: return key, captures[key]
        result = {'url': url, 'method': 'POST' if body else 'GET', 'body': body.decode() if body else None,
                  'captured_at': datetime.now(timezone.utc).isoformat()}
        try:
            raw = request(url, body, headers)
            json.loads(raw)
            digest = hashlib.sha256(raw).hexdigest()
            (rawdir / (digest + '.json.gz')).write_bytes(gzip.compress(raw, mtime=0))
            result.update(sha256=digest, http_status=200)
        except Exception as exc: result['error'] = f'{type(exc).__name__}: {exc}'
        time.sleep(.15)
        return key, result
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        for i, (key, result) in enumerate(pool.map(fetch, jobs.items()), 1):
            captures[key] = result
            if i % 40 == 0:
                oldpath.write_text(json.dumps(captures, ensure_ascii=False, indent=2))
                print(i, '/', len(jobs), 'errors', sum('error' in x for x in captures.values()), flush=True)
    oldpath.write_text(json.dumps(captures, ensure_ascii=False, indent=2))
    print('done', len(targets), 'rows', len(jobs), 'captures', flush=True)


if __name__ == '__main__': main()
