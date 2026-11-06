"""Download text-bearing official manuals linked by the captured baike response.

No OCR. Full PDFs stay in the ignored manuals cache; text and hashes are auditable.
"""
from concurrent.futures import ThreadPoolExecutor
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
from collect_homeappliance_params import request


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, default=Path('docs/homeappliance-params-20261106'))
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--models', nargs='*')
    ap.add_argument('--index', default='manuals.json')
    a = ap.parse_args(); p = a.output
    cs = json.loads((p / 'captures.json').read_text())
    targets = json.loads((p / 'targets.json').read_text())
    models = sorted({t['model'] for t in targets if t['model'] and not t['had_params']})
    if a.models: models = [m for m in models if m in a.models]
    (p / 'manuals').mkdir(exist_ok=True); (p / 'texts').mkdir(exist_ok=True)
    oldpath = p / a.index; old = json.loads(oldpath.read_text()) if oldpath.exists() else {}
    def collect(model):
        if model in old and not old[model].get('error'): return model, old[model]
        cap = cs.get(model + ':introduction', {})
        if not cap.get('sha256'): return model, {'error': 'introduction_not_available'}
        d = json.loads(gzip.decompress((p / 'raw' / (cap['sha256'] + '.json.gz')).read_bytes()))
        data = d.get('data') or {}; url = (data.get('introductionPdf') or {}).get('url')
        if not url: return model, {'status': 'html_or_empty', 'introduction_sha256': cap['sha256']}
        result = {'url': url, 'introduction_sha256': cap['sha256'], 'productName': data.get('productName')}
        try:
            path = p / 'manuals' / (model + '.pdf')
            raw = path.read_bytes() if path.exists() else request(url, max_bytes=64 * 1024 * 1024, max_seconds=90)
            if not raw.startswith(b'%PDF'): raise ValueError('Not a PDF')
            path.write_bytes(raw)
            text = subprocess.run(['pdftotext', '-layout', str(path), '-'], capture_output=True, check=True).stdout
            result.update(sha256=hashlib.sha256(raw).hexdigest(), text_sha256=hashlib.sha256(text).hexdigest(),
                          bytes=len(raw), status='text' if text.strip() else 'image_only')
            (p / 'texts' / (model + '.txt.gz')).write_bytes(gzip.compress(text, mtime=0))
        except Exception as e: result['error'] = str(e)
        return model, result
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        for i, (m, result) in enumerate(pool.map(collect, models), 1):
            old[m] = result
            oldpath.write_text(json.dumps(old, ensure_ascii=False, indent=2))
            if i % 10 == 0: print(i, '/', len(models), 'errors', sum('error' in x for x in old.values()), flush=True)
    print('done', len(models), flush=True)


if __name__ == '__main__': main()
