"""Check immutable release bytes, public API, excluded accessories, and real bundles."""
import argparse, gzip, hashlib, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from goodsdex.mi_names import apply_page_names
from goodsdex.exclusions import validate_excluded
from goodsdex.accessories import classify
here=Path(__file__).resolve().parent
BASE='https://spend-good.oss-cn-shanghai.aliyuncs.com/data/public/'
API='https://spend.snewbie.site'
def fetch(url):
    return subprocess.check_output(['curl','--noproxy','*','--compressed','-fsSL','--retry','2','--connect-timeout','10','--max-time','90',url])
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--public',type=Path);a=ap.parse_args()
    meta=json.loads(fetch(BASE+'meta.json'));files={}
    for name in ('goods.json','goods-excluded.json'):
        desc=meta['files'][name];raw=fetch(BASE+'blobs/'+desc['sha256']+'.json')
        assert len(raw)==desc['bytes'] and hashlib.sha256(raw).hexdigest()==desc['sha256']
        files[name]=json.loads(raw)
    goods=files['goods.json'];excluded=files['goods-excluded.json'];validate_excluded(meta,excluded,goods)
    api_meta=json.loads(fetch(API+'/api/meta'))
    assert api_meta['revision']==meta['revision'] and api_meta['count']==meta['count']
    api_raw=fetch(API+'/api/goods');actual=json.loads(api_raw);assert actual==goods,'API differs from manifest goods'
    if a.public:assert json.loads((a.public/'goods.json').read_bytes())==goods,'data artifact differs from manifest'
    g={r['id']:r for r in goods};e={r['id']:r for r in excluded['items']}
    manifest=json.loads((ROOT/'data/official/mi-page-names.json').read_text())
    for item in manifest['items']:
        row=g.get(item['id']) or e.get(item['id']);assert row
        assert row['name']==item['name']
        assert row['is_accessory'] is classify(row)['accessory']
        assert row['source_url']==item['url']
    expected={'22104':('Xiaomi Sound 2 Max',False),'22105':('Xiaomi Sound 2 Max 金属面板',True),
        '22547':('Xiaomi Sound 2 Max+2 Pro+无线连接器套装',False),'23722':('Xiaomi Sound 2 Max双支装',False),
        '22107':('Xiaomi Sound 金属落地支架',True),'22544':('Xiaomi Sound 2 Pro 金属面板',True)}
    details=[]
    for pid,(name,accessory) in expected.items():
        key='CN:mi_cn:product:'+pid;row=(e if accessory else g)[key]
        assert row['name']==name and row['is_accessory'] is accessory
        if accessory:
            assert key not in g and row['excluded_reason'].startswith('accessory:')
            code=subprocess.check_output(['curl','--noproxy','*','-sSL','--max-time','30','-o','/dev/null','-w','%{http_code}',API+'/api/goods/'+quote(key,safe='')],text=True)
            assert code=='404'
        else:
            response=json.loads(fetch(API+'/api/goods/'+quote(key,safe='')));assert response==row
        details.append(dict(id=key,name=name,price=row['price'],is_accessory=accessory,published=key in g))
    keywords=json.loads((here/'accessory-22-decisions.json').read_text())
    for row in keywords:assert (row['id'] in g)==row['published']
    for pid in ('22547','23722','25473','20585','20845','22559','22574'):
        assert 'CN:mi_cn:product:'+pid in g
    assert json.loads(fetch(BASE+'meta.json'))['revision']==meta['revision']
    result=dict(checked_at=datetime.now(timezone.utc).isoformat(),revision=meta['revision'],count=len(goods),excluded_count=excluded['total'],verified_names=len(manifest['items']),api_goods_equal_manifest=True,artifact_equal_manifest=bool(a.public),keyword_22_decisions_correct=True,bundles_preserved=True,goods_sha256=meta['files']['goods.json']['sha256'],details=details)
    (here/'online-meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
    (here/'online-goods.json.gz').write_bytes(gzip.compress(api_raw,mtime=0))
    (here/'online-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
