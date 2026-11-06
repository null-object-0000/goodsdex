"""Collect Mi Home introduction PDFs independently of image refresh; no OCR.

Requires Poppler pdftotext. Successful HTTP evidence is cached; failures retry.
--seed optionally reuses byte-exact captures from the preceding appliance run.
"""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import gzip
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import urlencode
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from goodsdex.manual_params import parse_manual
from goodsdex.homeappliance_params import apply_params
from collect_homeappliance_params import request, read_rows, BASE


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--goods', type=Path, required=True)
    ap.add_argument('--cache', type=Path, default=Path('data/manual-pdf'))
    ap.add_argument('--output', type=Path, default=Path('docs/manual-params-20261106'))
    ap.add_argument('--manifest', type=Path, default=Path('data/enrichment/manual-params.json'))
    ap.add_argument('--seed', type=Path)
    ap.add_argument('--workers', type=int, default=6)
    ap.add_argument('--reparse-only', action='store_true', help='Reparse frozen text evidence without network or PDF conversion')
    ap.add_argument('--appliances-only', action='store_true', help='Limit run to the five acceptance appliance categories')
    a = ap.parse_args(); a.cache.mkdir(parents=True, exist_ok=True); a.output.mkdir(parents=True, exist_ok=True)
    if a.reparse_only:
        index = json.loads((a.output/'collection.json').read_text())
        targets = json.loads((a.output/'targets.json').read_text())
        for model, result in index.items():
            if 'text_sha256' not in result: continue
            raw = gzip.decompress((a.output/'texts'/(model+'.txt.gz')).read_bytes())
            if hashlib.sha256(raw).hexdigest() != result['text_sha256']: raise ValueError('Text hash mismatch')
            parsed = parse_manual(raw.decode(),model,result['pdf_url'])
            if not raw.strip(): parsed['status'] = 'no_text'
            for v in parsed['params'].values(): v.update(pdf_sha256=result['pdf_sha256'],text_sha256=result['text_sha256'])
            result.update(parsed)
        write_results(a,index,targets)
        return
    rows = apply_params(read_rows(a.goods))
    audited = {e['id']:e for e in json.loads(Path('data/enrichment/homeappliance-params.json').read_text())['items']}
    targets = []
    for r in rows:
        e = audited.get(r['id'], {})
        if a.appliances_only and not (e or r.get('category') in ('空调','扫地机器人','冰箱','微波炉','波轮洗衣机','滚筒洗衣机','洗衣机')): continue
        model = r.get('miio_model') or r.get('mihome_model')
        if not model and e.get('expected_name') == r['name']: model = e.get('model')
        if model and re.fullmatch(r'[\w.-]+', model) and (r.get('brand') in ('小米','米家','小米公司') or e):
            targets.append(dict(id=r['id'],expected_name=r['name'],model=model,category=r.get('category'),had_params=bool(r.get('params'))))
    seed_index = json.loads((a.seed/'captures.json').read_text()) if a.seed else {}
    def collect(model):
        intro_url = BASE+'introduction?'+urlencode(dict(model=model,region='cn'))
        result = dict(model=model,introduction_url=intro_url)
        phase = 'introduction_error'
        try:
            path = a.cache/(model+'.introduction.json')
            if not path.exists():
                cap = seed_index.get(model+':introduction', {})
                raw = gzip.decompress((a.seed/'raw'/(cap['sha256']+'.json.gz')).read_bytes()) if cap.get('sha256') and (a.seed/'raw'/(cap['sha256']+'.json.gz')).exists() else request(intro_url)
                d = json.loads(raw)
                if d.get('code',0) != 0: raise ValueError('API error: '+str(d.get('code')))
                path.write_bytes(raw)
            raw = path.read_bytes(); d = json.loads(raw).get('data') or {}
            (a.output/'introductions').mkdir(exist_ok=True)
            (a.output/'introductions'/(model+'.json.gz')).write_bytes(gzip.compress(raw,mtime=0))
            result.update(introduction_sha256=hashlib.sha256(raw).hexdigest(),productName=d.get('productName'),title=d.get('title'))
            url = (d.get('introductionPdf') or {}).get('url')
            if not url: return {**result,'status':'no_pdf','introduction_type':d.get('introductionType')}
            result['pdf_url'] = url; phase = 'download_error'
            path = a.cache/(model+'.pdf')
            if not path.exists():
                seed = a.seed/'manuals'/(model+'.pdf') if a.seed else None
                if seed and seed.exists(): shutil.copyfile(seed,path)
                else: path.write_bytes(request(url,max_bytes=64*1024*1024,max_seconds=90))
            raw = path.read_bytes()
            if not raw.startswith(b'%PDF'): path.unlink(); raise ValueError('Not a PDF')
            result['pdf_sha256'] = hashlib.sha256(raw).hexdigest(); phase = 'text_error'
            text = subprocess.run(['pdftotext','-layout',str(path),'-'],capture_output=True,check=True,timeout=60).stdout
            result['text_sha256'] = hashlib.sha256(text).hexdigest()
            (a.cache/(model+'.txt')).write_bytes(text)
            (a.output/'texts').mkdir(exist_ok=True)
            (a.output/'texts'/(model+'.txt.gz')).write_bytes(gzip.compress(text,mtime=0))
            if not text.strip(): return {**result,'status':'no_text'}
            phase = 'parse_error'; parsed = parse_manual(text.decode(),model,url)
            for v in parsed['params'].values(): v.update(pdf_sha256=result['pdf_sha256'],text_sha256=result['text_sha256'])
            return {**result,**parsed}
        except Exception as exc: return {**result,'status':phase,'error':str(exc)}
    models = sorted({t['model'] for t in targets}); index = {}
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        for i,v in enumerate(pool.map(collect,models),1):
            index[v['model']] = v
            (a.output/'collection.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n')
            if i%20==0: print(i,'/',len(models),dict(Counter(x['status'] for x in index.values())),flush=True)
    write_results(a,index,targets)


def write_results(a,index,targets):
    (a.output/'collection.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n')
    items = [{**{k:t[k] for k in ('id','expected_name','model','category')},'params':index[t['model']]['params']} for t in targets if index[t['model']].get('params')]
    a.manifest.write_text(json.dumps(dict(schema=1,items=items),ensure_ascii=False,indent=2)+'\n')
    (a.output/'targets.json').write_text(json.dumps(targets,ensure_ascii=False,indent=2)+'\n')
    print('done',len(index),dict(Counter(x['status'] for x in index.values())),flush=True)


if __name__=='__main__': main()
