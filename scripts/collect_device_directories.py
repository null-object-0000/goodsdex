"""Fresh directory observations; unknown identities enter a review queue, never guessed prices/dates."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import requests
from collect_mihome_catalog import collect

def save(p,data):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,indent=1)+'\n')

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',choices=['mihome','earbuds','gap'],required=True);p.add_argument('--root',type=Path,default=Path('_data'));a=p.parse_args()
    rows=json.loads((a.root/'public/goods.json').read_text())
    target=a.root/'data/categories'; known={str(r.get('miio_model') or r.get('mihome_model') or r.get('model')) for r in rows}
    if a.source=='earbuds':
        key=os.environ.get('EARBUDS_AUTH_KEY')
        if not key:raise RuntimeError('Missing EARBUDS_AUTH_KEY repository secret')
        r=requests.get('https://cn.tws.wear.xiaomiwear.com/twswear/product/get_product_list',params={'data':json.dumps(dict(app_version='9.0.278',app_platform=0,last_modify_time=0))},headers={'Cookie':'auth_key='+key},timeout=45);r.raise_for_status()
        devices=r.json()['result']['tw_product_list']
    else:
        # Fresh run-specific directory, so yesterday's cache cannot suppress network requests.
        out=Path(os.environ.get('RUNNER_TEMP','/tmp'))/('mihome-'+os.environ.get('GITHUB_RUN_ID',str(os.getpid())))
        (out/'raw').mkdir(parents=True,exist_ok=True)
        seeds=json.loads(Path('data/official/mihome-seed-brands.json').read_text())
        devices=list(collect(out,seeds).values())
    if not devices:raise ValueError('Empty directory; refusing successful empty observation')
    save(target/(a.source+'-directory.json'),dict(schema=1,items=devices))
    missing=[d for d in devices if d.get('model') not in known]
    save(target/(a.source+'-discovery.json'),dict(schema=1,items=missing,reason='待核验商品身份；目录无价格、无发布日期'))
    # Existing IDs are retained. Only exact, unique model matches may enrich their directory fields.
    models={}
    for d in devices:models.setdefault(d.get('model'),[]).append(d)
    if a.source!='gap':
        for row in rows:
            matches=models.get(row.get('miio_model') or row.get('mihome_model') or row.get('model'),[])
            if len(matches)==1:
                d=matches[0];row['name_'+a.source]=d['name']
        save(a.root/'public/goods.json',rows)
    save(Path(os.environ.get('RUNNER_TEMP','/tmp'))/'directory-metrics.json',dict(items_found=len(devices),discovery_pending=len(missing)))
if __name__=='__main__':main()
