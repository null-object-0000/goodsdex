"""Anonymous baike evidence collection. Catalog timestamps are never release dates."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.request
import urllib.parse
import time

BASE = 'https://home.mi.com/cgi-op/api/v1/baike/v2/'


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as response:
        chunks = []
        started = time.monotonic()
        size = 0
        while True:
            chunk = response.read(65536)
            if not chunk: break
            chunks.append(chunk); size += len(chunk)
            if time.monotonic() - started > 45 or size > 50 * 1024 * 1024:
                raise TimeoutError('anonymous fetch exceeded 45 seconds / 50 MiB')
        raw = b''.join(chunks)
    return raw


def collect(model, root):
    path = root / (model + '.json')
    if path.exists():
        return json.loads(path.read_text())
    url = BASE + 'product?' + urllib.parse.urlencode({'model': model})
    item = dict(model=model, url=url, captured_at=datetime.now(timezone.utc).isoformat())
    try:
        raw = fetch(url)
        item.update(sha256=hashlib.sha256(raw).hexdigest(), response=json.loads(raw))
    except Exception as exc:
        item['error'] = str(exc)
    path.write_text(json.dumps(item, ensure_ascii=False))
    return item


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=Path('docs/mijia-baike-20261106'))
    args = parser.parse_args()
    root = args.output / 'raw'
    root.mkdir(parents=True, exist_ok=True)
    catalog = root / 'miot-instances.json'
    if not catalog.exists():
        catalog.write_bytes(fetch('https://miot-spec.org/miot-spec-v2/instances?status=all'))
    models = sorted({x['model'] for x in json.loads(catalog.read_text())['instances']
                     if x['model'].startswith(('xiaomi.', 'mijia.', 'mibx', 'zhimi.', 'roborock.',
                                              'dreame.', 'deerma.', 'chunmi.', 'yeelink.', 'dmaker.', 'chuangmi.'))})
    with ThreadPoolExecutor(max_workers=8) as pool:
        for i, result in enumerate(pool.map(lambda m: collect(m, root), models), 1):
            if i % 200 == 0:
                print(i, '/', len(models), flush=True)
    print('done', len(models), flush=True)


if __name__ == '__main__':
    main()
