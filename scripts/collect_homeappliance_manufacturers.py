"""Exact-model manufacturer manuals (currently Roborock's public product center)."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import re
import unicodedata
from urllib.parse import urlencode
from collect_homeappliance_params import request


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,default=Path('docs/homeappliance-params-20261106'));a=ap.parse_args();p=a.output
    def capture(url,label):
        raw=request(url);sha=hashlib.sha256(raw).hexdigest();(p/(label+'.gz')).write_bytes(gzip.compress(raw,mtime=0));return raw,sha
    url='https://productcn.roborock.com/api/category/products';raw,sha=capture(url,'roborock-products')
    products=json.loads(raw)['data']; targets=json.loads((p/'targets.json').read_text()); models={t['model'] for t in targets if not t['had_params'] and t['category']=='扫地机器人'}
    candidates=[{**x,'query_model':m} for x in products for m in (x.get('model') or '').split(',') if m in models];out={}
    def collect(x):
        model=x['query_model'];u='https://productcn.roborock.com/api/product/info?'+urlencode({'spuId':x['id']})
        r=dict(model=model,catalog_url=url,catalog_sha256=sha,info_url=u,captured_at=datetime.now(timezone.utc).isoformat())
        try:
            raw,info_sha=capture(u,'roborock-info-'+str(x['id']));d=json.loads(raw)['data']
            if model not in d['model'].split(','):raise ValueError('Model identity mismatch')
            manuals=d.get('manualList') or []
            # Ambiguous multiple manuals/water-supply variants require a manual review.
            if len(manuals)!=1:
                norm=lambda s: re.sub(r'\s+', '', unicodedata.normalize('NFKC',s).casefold())
                names={norm(t['expected_name']) for t in targets if t['model']==model}
                manuals=[m for m in manuals if norm(m['manualName']) in names]
                if len(manuals)!=1:raise ValueError('Multiple or missing manuals')
            u=manuals[0]['manualAddress'];path=p/'manuals'/('manufacturer-'+model+'.pdf')
            raw=path.read_bytes() if path.exists() else request(u);path.write_bytes(raw)
            text=subprocess.run(['pdftotext','-layout',str(path),'-'],capture_output=True,check=True).stdout
            (p/'texts'/('manufacturer-'+model+'.txt.gz')).write_bytes(gzip.compress(text,mtime=0))
            r.update(info_sha256=info_sha,url=u,sha256=hashlib.sha256(raw).hexdigest(),text_sha256=hashlib.sha256(text).hexdigest(),name=d['name'])
        except Exception as e:r['error']=str(e)
        return model,r
    with ThreadPoolExecutor(max_workers=3) as pool:
        for m,r in pool.map(collect,candidates):out[m]=r;print(m,r.get('error','ok'),flush=True)
    legacy=p/'manufacturer-legacy-review.json'
    for review in json.loads(legacy.read_text()) if legacy.exists() else []:
        model=review['model']
        if not review.get('reviewed') or not any(t['model']==model and t['id']==review['id'] and t['expected_name']==review['expected_name'] for t in targets):
            raise ValueError('Unreviewed legacy manual identity')
        path=p/'manuals'/('manufacturer-'+model+'.pdf')
        raw=path.read_bytes() if path.exists() else request(review['url'])
        if hashlib.sha256(raw).hexdigest()!=review['sha256']:raise ValueError('Legacy manual capture changed')
        path.write_bytes(raw)
        text=subprocess.run(['pdftotext','-layout',str(path),'-'],capture_output=True,check=True).stdout
        if review['title'] not in text.decode().split('\f')[0]:raise ValueError('Legacy manual title mismatch')
        (p/'texts'/('manufacturer-'+model+'.txt.gz')).write_bytes(gzip.compress(text,mtime=0))
        out[model]={**review,'text_sha256':hashlib.sha256(text).hexdigest(),'captured_at':datetime.now(timezone.utc).isoformat()}
    (p/'manufacturer-manuals.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
