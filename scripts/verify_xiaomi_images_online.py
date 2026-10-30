"""Verify the released catalog, five real API samples and all OSS image bytes."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import urllib.parse
import requests

def main():
    p=argparse.ArgumentParser();p.add_argument('--public',type=Path,required=True);p.add_argument('--before',type=Path,required=True);p.add_argument('--artifacts',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=True)
    def fetch(url):
        with requests.Session() as s:
            s.trust_env=False
            r=s.get(url,headers={'Accept-Encoding':'gzip'},timeout=(15,90));r.raise_for_status()
            assert r.status_code==200
            return r
    base='https://spend.snewbie.site'
    rows=fetch(base+'/api/goods').json();expected=json.loads((a.public/'goods.json').read_text())
    assert rows==expected,'online full catalog differs from release'
    before=json.loads(a.before.read_text());assert len(before)==len(rows)
    transfers=json.loads((a.out/'oss-readback.json').read_text())
    changed=[]
    for old,new in zip(before,rows):
        if old!=new:changed.append(new['id'])
    assert sorted(changed)==sorted(r['id'] for r in transfers)
    assert all(old==new for old,new in zip(before,rows) if old.get('image'))
    def check(r):
        remote=fetch(r['oss_url']).content
        local=(a.artifacts/'image-transfer-cache'/Path(r['key']).name).read_bytes()
        assert remote==local and len(remote)==r['bytes']
        assert hashlib.sha256(remote).hexdigest()==r['sha256']
        return dict(pid=r['pid'],url=r['oss_url'],status=200,bytes=len(remote),byte_equal=True,sha256=r['sha256'])
    with ThreadPoolExecutor(max_workers=6) as pool:checks=list(pool.map(check,transfers))
    def stats(rs):
        mi=[r for r in rs if r['id'].startswith('CN:mi_cn:')]
        return dict(total=len(rs),total_missing=sum(not r.get('image') for r in rs),xiaomi_total=len(mi),xiaomi_with_image=sum(bool(r.get('image')) for r in mi),xiaomi_missing=sum(not r.get('image') for r in mi))
    audit=dict(before=stats(before),after=stats(rows),full_catalog_equal=True,changed_count=len(changed),existing_images_unchanged=True,upgraded_series_count=0,release_sha256=hashlib.sha256((a.public/'goods.json').read_bytes()).hexdigest())
    samples=[]
    for pid,kind in [('1945','new'),('7852','new'),('10000108','shared_series'),('19963','existing'),('10000118','skipped')]:
        key='CN:mi_cn:product:'+pid
        detail=fetch(base+'/api/goods/'+urllib.parse.quote(key,safe='')).json()
        assert detail==next(r for r in rows if r['id']==key)
        (a.out/f'online-detail-{pid}.json').write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n')
        if kind!='skipped':
            for grouped in ('0','1'):
                result=fetch(base+'/api/goods/search?'+urllib.parse.urlencode(dict(q=detail['name'],limit=50,group_products=grouped))).json()
                match=next(r for r in result['items'] if r.get('id',r.get('product_id'))==key)
                if kind!='existing':
                    for field in ['image','image_source','image_source_url','image_captured_at','image_scope','image_note']:
                        assert match[field]==detail[field],(pid,field)
                (a.out/f'online-search-{pid}-{grouped}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        fragment={k:detail[k] for k in ['id','name','image','image_source','image_source_type','image_source_url','image_captured_at','image_scope','image_note'] if k in detail}
        sample=dict(kind=kind,json=fragment)
        if kind=='skipped':
            skipped=json.loads((Path(__file__).resolve().parents[1]/'data/supplements/backfill-skipped-xiaomi-images-20261030.json').read_text())
            sample['skipped']=next(r for r in skipped if r['candidate']['pid']==pid)
        samples.append(sample)
    for name,obj in [('online-audit.json',audit),('online-oss-readback.json',checks),('online-samples.json',samples)]:
        (a.out/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(audit,ensure_ascii=False))
if __name__=='__main__':main()
