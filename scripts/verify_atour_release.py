"""Verify rendered official samples, all published SKU facts, OSS and online API."""
import argparse,hashlib,json,random,re,sys,urllib.request
from pathlib import Path
from urllib.parse import quote,urlencode
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from goodsdex.atour import build_rows,coverage


def fetch(url):
    with urllib.request.urlopen(url,timeout=120) as response:
        return response.read()


def verify(rows,capture,samples):
    expected=build_rows(capture); actual=[r for r in rows if r.get('source')=='atour' and r.get('status')!='retired']
    ids={r['id']:r for r in actual}
    assert len(actual)==len(ids)==len(expected)
    for r in expected:
        for field in ('name','official_name','sku_name','brand','category','price','promo_price','image','source_url','sku_no','spu_id','specs','bundle','bundle_contents','package_quantity','captured_at','official_sku_status','stock_num','price_status','sale_status'):
            assert ids[r['id']][field]==r[field],(r['id'],field)
    comparisons=[]
    for sample in samples:
        e=next(e for e in capture['entries'] if e['listing']['id']==sample['spu_id'])
        body=sample['body'];sku=body.split('已选\n',1)[1].split('\n图文详情',1)[0].strip()
        s=next(s for s in e['panel']['skuVOS'] if s['skuName']==sku)
        key=f"CN:atour:spu:{sample['spu_id']}:sku:{s['skuNo']}";r=ids[key]
        title=e['listing']['spuName'];assert title in body and r['official_name']==title and r['sku_name']==sku
        price_text=re.search(r'活动价\n￥([\d.]+)',body).group(1)
        assert float(price_text)==r['price'],(key,price_text,r['price'])
        comparisons.append(dict(id=key,url=sample['url'],page_name=title,database_official_name=r['official_name'],page_selected_sku=sku,database_sku_name=r['sku_name'],page_price=price_text,database_price=r['price'],equal=True))
    pillows=[r for r in actual if r['category']=='枕芯']
    chosen=random.Random(20261105).sample(pillows,5)
    return dict(counts=coverage(actual),page_comparisons=comparisons,pillow_samples=[{k:r[k] for k in ('id','name','price','promo_price','specs','image','source_url')} for r in chosen],api_examples=[{k:actual[i][k] for k in ('id','name','brand','category','price','promo_price','image','source_url','sku_no','spu_id','specs','specs_missing','bundle','package_quantity','bundle_contents','captured_at')} for i in (0,45,207)])


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--capture',type=Path,required=True);ap.add_argument('--h5-samples',type=Path,required=True);ap.add_argument('--public',type=Path);ap.add_argument('--online',action='store_true');ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    capture=json.loads(args.capture.read_text());samples=json.loads(args.h5_samples.read_text())
    if args.online:
        oss='https://spend-good.oss-cn-shanghai.aliyuncs.com/data/public/'
        meta=json.loads(fetch(oss+'meta.json'));raw=fetch(oss+'blobs/'+meta['files']['goods.json']['sha256']+'.json');rows=json.loads(raw)
        assert hashlib.sha256(raw).hexdigest()==meta['files']['goods.json']['sha256']
        api_meta=json.loads(fetch('https://spend.snewbie.site/api/meta'));assert api_meta['revision']==meta['revision'],('API synchronization pending',api_meta['revision'],meta['revision'])
        api=json.loads(fetch('https://spend.snewbie.site/api/goods?'+urlencode(dict(q='亚朵星球'))))
        args.out.parent.mkdir(parents=True,exist_ok=True);(args.out.parent/'api-atour.json').write_text(json.dumps(api,ensure_ascii=False,indent=1)+'\n')
        # API supports paginated response with items/total; full array is legacy.
        if isinstance(api,list):total=len(api);api_rows=api
        else:total=api['total'];api_rows=api.get('items',api.get('goods',api.get('data',[])))
        assert total==sum(r.get('source')=='atour' for r in rows),(total,meta.get('sources'))
        for r in api_rows:assert r['brand']=='亚朵星球' and r['id'].startswith('CN:atour:spu:')
        result=verify(rows,capture,samples);result.update(api_total=total,api_url='https://spend.snewbie.site/api/goods?'+urlencode(dict(q='亚朵星球')),revision=meta['revision'],meta_source=meta['sources']['atour'])
        assert meta['sources']['atour']['sku_count']==267 and meta['sources']['atour']['spu_count']==38
        assert meta['brands']['亚朵星球']==267
        (args.out.parent/'online-meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=1)+'\n')
        # Detail API must retain full SKU facts and source provenance.
        for sample in result['api_examples']:
            detail=json.loads(fetch('https://spend.snewbie.site/api/goods/'+quote(sample['id'],safe='')))
            expected=next(r for r in rows if r['id']==sample['id']);assert detail==expected
    else:
        rows=json.loads((args.public/'goods.json').read_text());result=verify(rows,capture,samples)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=1)+'\n');print(json.dumps({k:v for k,v in result.items() if k in ('counts','api_total','revision')},ensure_ascii=False))
