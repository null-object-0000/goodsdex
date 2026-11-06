"""Audit the supplied baike endpoint; reuse the existing mtop audit. Local only."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys
import urllib.request
from urllib.parse import quote
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from goodsdex.xiaomi_covers import BAIKE_URL, apply_covers, is_xiaomi_product


def fetch(model):
    at = datetime.now(timezone.utc).isoformat()
    observation = dict(model=model, captured_at=at, image=None, source_url=BAIKE_URL + model)
    raw = b''
    try:
        with urllib.request.urlopen(BAIKE_URL + model, timeout=20) as response:
            raw = response.read()
        d = json.loads(raw)
        data = d.get('data') or {}
        observation.update(code=d.get('code'), response_sha256=hashlib.sha256(raw).hexdigest())
        if d.get('code') == 0 and data.get('model') == model:
            url = data.get('realIcon')
            if isinstance(url, str) and url.startswith('https://'):
                # Decode before treating the URL as usable; no assumed dimensions.
                with urllib.request.urlopen(quote(url, safe=":/?&=%+;,@!$'()*~-._"), timeout=20) as response:
                    image_bytes = response.read()
                with Image.open(io.BytesIO(image_bytes)) as image:
                    image.load()
                    observation.update(image=url, width=image.width, height=image.height,
                                       image_sha256=hashlib.sha256(image_bytes).hexdigest())
            else:
                observation['error'] = 'realIcon_unavailable'
        else:
            observation['error'] = 'baike_unavailable_or_model_mismatch'
    except Exception as exc:
        observation['error'] = str(exc)
    return model, observation, raw.decode('utf-8', errors='replace')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--mtop', type=Path, default=Path('data/official/xiaomi-cover-images.json'))
    parser.add_argument('--write-evidence', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--reuse', action='store_true')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    raw = args.input.read_bytes()
    if args.input.suffix == '.gz': raw = gzip.decompress(raw)
    rows = json.loads(raw)
    mi = [r for r in rows if is_xiaomi_product(r['id'])]
    models = sorted({r['miio_model'] for r in mi if r.get('miio_model')})
    if args.reuse:
        observations = json.loads(args.write_evidence.read_text())
    else:
        with ThreadPoolExecutor(max_workers=12) as pool:
            results = list(pool.map(fetch, models))
        observations = {model: observation for model, observation, _ in results}
        responses = {model: response for model, _, response in results}
        (args.out / 'baike-responses.json.gz').write_bytes(gzip.compress(json.dumps(responses, ensure_ascii=False).encode(), mtime=0))
        args.write_evidence.write_text(json.dumps(observations, ensure_ascii=False, indent=1) + '\n')
    mtop = json.loads(args.mtop.read_text())
    after = apply_covers(rows, mtop, observations)
    assert apply_covers(after, mtop, observations) == after
    assert [r for r in rows if not is_xiaomi_product(r['id'])] == [r for r in after if not is_xiaomi_product(r['id'])]
    for a, b in zip(rows, after):
        assert {k:v for k,v in a.items() if not k.startswith('image')} == {k:v for k,v in b.items() if not k.startswith('image')}
    changes = [dict(id=a['id'], miio_model=a.get('miio_model'),
                    before={k:v for k,v in a.items() if k.startswith('image')},
                    after={k:v for k,v in b.items() if k.startswith('image')})
               for a,b in zip(rows, after) if a != b]
    (args.out / 'cover-changes.json.gz').write_bytes(gzip.compress(json.dumps(changes, ensure_ascii=False).encode(), mtime=0))
    from collections import Counter
    report = dict(baseline_sha256=hashlib.sha256(raw).hexdigest(), rows=len(rows),
                  mi_rows=len(mi), mi_with_model=sum(bool(r.get('miio_model')) for r in mi),
                  unique_models=len(models), realicon_available=sum(bool(o.get('image')) for o in observations.values()),
                  realicon_unavailable=sum(not o.get('image') for o in observations.values()),
                  selected_sources=dict(Counter(r.get('image_source', 'existing') for r in after if is_xiaomi_product(r['id']))),
                  image_changed_rows=sum(a.get('image') != b.get('image') for a,b in zip(rows, after)),
                  non_mi_unchanged=True, non_image_fields_unchanged=True, idempotent=True,
                  targets=[{k:r.get(k) for k in ('id','name','miio_model','image','image_source','image_source_url','image_width','image_height')}
                           for r in after if r['id'] in ('CN:mi_cn:product:20833','CN:mi_cn:product:21630')])
    (args.out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    args.output.write_text(json.dumps(after, ensure_ascii=False, indent=1)+'\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == '__main__': main()
