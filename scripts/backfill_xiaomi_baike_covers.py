"""Image-only exact-model baike backfill from the frozen published pdId models.

Four workers maximum; every GET has a 12-second total timeout and one retry.
Validate every returned image with Pillow before accepting any model's rows.
"""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
from urllib.parse import urlencode

from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from goodsdex.xiaomi_covers import realicon_cover

ROOT = Path('docs/baike-covers-20261106')
EVIDENCE = Path('data/official/xiaomi-realicon-images.json')
API = 'https://home.mi.com/cgi-op/api/v1/baike/v2/product?'


def write(path, value):
    raw = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()
    path.write_bytes(gzip.compress(raw, mtime=0) if path.suffix == '.gz' else raw)


def get(url):
    attempts = []
    for _ in range(2):
        with tempfile.TemporaryDirectory(prefix='baike-cover-') as tmp:
            path = Path(tmp) / 'body'
            p = subprocess.run(['curl', '-L', '-sS', '--max-time', '12',
                                '-A', 'Mozilla/5.0', '-o', str(path),
                                '-w', '%{http_code}\n%{content_type}', url],
                               capture_output=True, text=True, timeout=15)
            parts = p.stdout.splitlines()
            status = int(parts[0]) if parts and parts[0].isdigit() else None
            attempts.append(dict(http_status=status, error=p.stderr.strip() or None))
            if p.returncode == 0 and status == 200:
                return path.read_bytes(), dict(http_status=status,
                    content_type=parts[1] if len(parts) > 1 else None, attempts=attempts)
    return None, dict(http_status=status, attempts=attempts)


def collect(model):
    url = API + urlencode({'model': model})
    out = dict(model=model, source_url=url, captured_at=datetime.now(timezone.utc).isoformat())
    raw, check = get(url)
    out['product_request'] = check
    if raw is None:
        return dict(out, failure='http_error')
    out['response_sha256'] = hashlib.sha256(raw).hexdigest()
    try:
        response = json.loads(raw)
        out['response'] = response
        image = (response.get('data') or {}).get('realIcon')
    except (ValueError, AttributeError) as exc:
        return dict(out, failure='http_error', error='invalid API response: ' + str(exc))
    if not isinstance(image, str) or not image.startswith('https://'):
        return dict(out, failure='no_realIcon')
    out['image'] = image
    raw, check = get(image)
    out['image_request'] = check
    if raw is None:
        return dict(out, failure='http_error')
    out.update(bytes=len(raw), image_sha256=hashlib.sha256(raw).hexdigest())
    try:
        with Image.open(io.BytesIO(raw)) as im:
            im.load()
            out.update(width=im.width, height=im.height)
    except Exception as exc:
        return dict(out, failure='http_error', error='image decode: ' + str(exc))
    if out['width'] < 400 or out['height'] < 400:
        out['failure'] = 'undersized'
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--reuse', action='store_true')
    args = ap.parse_args()
    ROOT.mkdir(parents=True, exist_ok=True)
    raw = args.input.read_bytes()
    if args.input.suffix == '.gz':
        raw = gzip.decompress(raw)
    rows = json.loads(raw)
    mapping = json.loads(Path('data/official/xiaomi-pdid-map.json').read_text())
    old = json.loads(EVIDENCE.read_text())
    def has480(row):
        e = old.get(row.get('miio_model'), {})
        w, h = row.get('image_width'), row.get('image_height')
        if row.get('image') and row.get('image') == e.get('image'):
            w, h = e.get('width', w), e.get('height', h)
        return (w or 0) >= 480 and (h or 0) >= 480 and bool(row.get('image'))
    candidates = [r for r in rows if r.get('miio_model') in mapping and not has480(r)]
    models = sorted({r['miio_model'] for r in candidates})
    path = ROOT / 'observations.json.gz'
    results = json.loads(gzip.decompress(path.read_bytes())) if args.reuse else []
    if args.reuse:
        assert sorted(r['model'] for r in results) == models
    else:
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = {pool.submit(collect, model): model for model in models}
            for i, future in enumerate(as_completed(futures), 1):
                results.append(future.result())
                if i % 50 == 0 or i == len(models):
                    write(path, sorted(results, key=lambda r:r['model']))
                    print(f'{i}/{len(models)}; failures={dict(Counter(r["failure"] for r in results if r.get("failure")))}', flush=True)
    accepted = {r['model']: {k:v for k,v in r.items() if k not in ('response', 'product_request', 'image_request')}
                for r in results if not r.get('failure')}
    eligible = {r['id'] for r in candidates}
    after = [realicon_cover(r, accepted) or r if r['id'] in eligible else r for r in rows]
    changes = []
    for b, a in zip(rows, after):
        assert {k:v for k,v in b.items() if k != 'image' and not k.startswith('image_')} == {k:v for k,v in a.items() if k != 'image' and not k.startswith('image_')}
        if a != b:
            changes.append(dict(id=b['id'], model=b['miio_model'],
                before={k:v for k,v in b.items() if k == 'image' or k.startswith('image_')},
                after={k:v for k,v in a.items() if k == 'image' or k.startswith('image_')}))
    changed_models = sorted({c['model'] for c in changes})
    sample = [accepted[m] for m in random.Random(20261106).sample(changed_models, 40)]
    assert len({r['image'] for r in sample}) == 40
    assert all(r['width'] >= 400 and r['height'] >= 400 for r in sample)
    assert [realicon_cover(r, accepted) or r if r['id'] in eligible else r for r in after] == after
    # Freeze only accepted exact-model observations; failed models keep their old evidence.
    old.update(accepted)
    write(EVIDENCE, old)
    write(ROOT / 'cover-changes.json.gz', changes)
    write(ROOT / 'sample-40.json', sample)
    failures = [r for r in results if r.get('failure')]
    write(ROOT / 'failures.json', [{k:v for k,v in r.items() if k != 'response'} for r in failures])
    report = dict(baseline_sha256=hashlib.sha256(raw).hexdigest(), rows=len(rows), map_models=len(mapping),
        candidate_models=len(models), candidate_rows=len(candidates), accepted_models=len(accepted),
        changed_rows=len(changes), changed_sources=dict(Counter(c['after']['image_source'] for c in changes)),
        failure_models={k:sum(r['failure']==k for r in failures) for k in ('no_realIcon', 'undersized', 'http_error')},
        failure_rows={k:sum(c['miio_model'] in {r['model'] for r in failures if r['failure']==k} for c in candidates)
                      for k in ('no_realIcon', 'undersized', 'http_error')},
        non_image_fields_unchanged=True, idempotent=True,
        target={k:v for k,v in next(r for r in after if r['id']=='mihome:13363').items() if k in ('id','miio_model','image','image_source')})
    write(ROOT / 'report.json', report)
    encoded = (json.dumps(after, ensure_ascii=False, separators=(',', ':'))+'\n').encode()
    args.output.write_bytes(gzip.compress(encoded, mtime=0) if args.output.suffix == '.gz' else encoded)
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
