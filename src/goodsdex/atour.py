"""Official Atour H5 business objects -> SKU facts; completed snapshots only."""
from collections import Counter
from datetime import datetime
from copy import deepcopy
from pathlib import Path
import json
import re

BRAND = '亚朵星球'
SOURCE = 'atour'
CATALOG_URL = 'https://h5mall.yaduo.com/pages/category/category'
IMAGE_MANIFEST = Path(__file__).resolve().parents[2] / 'data/official/atour-images.json'
CATEGORY_MANIFEST = Path(__file__).resolve().parents[2] / 'data/official/atour-categories.json'


def validate_capture(capture):
    if capture.get('complete') is not True:
        raise ValueError('Incomplete Atour capture; no inventory update')
    pages = capture['pages']
    info = pages[0]['pageInfo']
    if len(pages) != info['totalPage'] or [p['pageInfo']['pageNo'] for p in pages] != list(range(1,len(pages)+1)):
        raise ValueError('Missing catalogue pages')
    listings = [p for page in pages for p in page['data']]
    if len(listings) != info['totalCount'] or len({p['id'] for p in listings}) != len(listings):
        raise ValueError('Catalogue total/unique mismatch')
    brand = {p['id']:p for p in listings if p['spuName'].startswith(BRAND + ' ')}
    entries = capture['entries']
    if not brand or len(entries) != len(brand) or {e['listing']['id'] for e in entries} != brand.keys():
        raise ValueError('Brand panel coverage incomplete')
    ids=set()
    for e in entries:
        p=e['listing']; detail=e['detail']
        if p != brand[p['id']] or detail['id'] != p['id'] or detail['spuName'] != p['spuName']:
            raise ValueError('SPU identity mismatch')
        if not e['panel']['skuVOS']:
            raise ValueError('Empty SKU panel')
        for s in e['panel']['skuVOS']:
            key=(p['id'],s['skuNo'])
            if not s['skuNo'] or not s['skuName'] or s['spuId'] != p['id'] or key in ids:
                raise ValueError('Missing/duplicate/mismatched SKU')
            ids.add(key)
            if not isinstance(s['salesPrice'],(int,float)) or isinstance(s['salesPrice'],bool) or s['salesPrice'] < 0:
                raise ValueError('Invalid SKU sales price')
    # Log contains URL/method/time only. Page session/authentication is never saved.
    stamps=[datetime.fromisoformat(x['started_at']) for x in capture.get('requests',[])]
    if any((b-a).total_seconds() < 2.1 for a,b in zip(stamps,stamps[1:])):
        raise ValueError('Atour request interval below 2.1 seconds')
    return brand


def package(s, p):
    """Extract only explicit counts/components; unknown composition remains null."""
    text=s['skuName']
    sid=p.get('id')
    if sid==2099:
        core=2 if '两只装' in text else 1
        parts=[dict(name='深睡枕 Pro4.0 枕芯',quantity=core),dict(name='岩溪蓝 外枕套',quantity=core)]
        if '+深睡枕套' in text:
            parts.append(dict(name='深睡枕套'+text.split('+深睡枕套',1)[1].removesuffix('*1'),quantity=1))
        return sum(x['quantity'] for x in parts),parts
    if sid in (2108,2101):
        season='冬季' if sid==2108 else '四季'
        return 3,[dict(name='深睡枕 Pro4.0 枕芯',quantity=1),dict(name='深睡枕套 Pro4.0 岩溪蓝',quantity=1),dict(name='深睡控温被·'+season+' Pro3.0',quantity=1)]
    if '四件套' in p['spuName']:
        return 4,[dict(name='被套',quantity=1),dict(name='床笠' if '床笠款' in text else '床单',quantity=1),dict(name='枕套',quantity=2)]
    if sid==2110:
        qty=2 if '枕芯*2' in text else 1
        return qty*2+2,[dict(name='深睡枕Pro4.0 枕芯',quantity=qty),dict(name='深睡枕Pro4.0 外枕套',quantity=qty),dict(name='深睡儿童枕 枕芯',quantity=1),dict(name='深睡儿童枕 外枕套',quantity=1)]
    # Count literal named components, never dimensional multiplication.
    if '枕套*2' in text:
        return 2,[dict(name='枕套',quantity=2)]
    q=2 if re.search(r'两只装|双只装|两条装|2只装',text) else 1 if '单只装' in text else None
    if q:
        return q,[dict(name=p['spuName'],quantity=q)]
    # Names in official combinations are retained; no inferred filling/accessories.
    if '组合装' in p['spuName']:
        names=p['spuName'].removeprefix(BRAND+' ').split(' 组合装')[0].split(' + ')
        if len(names)>1: return len(names),[dict(name=n,quantity=1) for n in names]
    if '+' in text and not re.search(r'\d\+',text):
        names=text.split('+')
        return len(names),[dict(name=n,quantity=1) for n in names]
    return None,None


def build_rows(capture, images=None, categories=None):
    validate_capture(capture)
    images=images if images is not None else json.loads(IMAGE_MANIFEST.read_text())['skus']
    categories=categories if categories is not None else json.loads(CATEGORY_MANIFEST.read_text())['spus']
    result=[]
    for e in capture['entries']:
        p=e['listing']; sid=p['id']; config=json.loads(e['panel'].get('skuConfigJson') or '[]')
        for s in e['panel']['skuVOS']:
            key=f"CN:atour:spu:{sid}:sku:{s['skuNo']}"
            review=images.get(key)
            candidates={x.get('resourceUrl') for x in e['detail'].get('imageResourceList') or []} | {s.get('skuImgUrl')}
            if not review or (review.get('official_origin') or review['url']) not in candidates or review.get('classification') != 'A' or review.get('identity_verified') is not True:
                raise ValueError('No reviewed official white-background photo for '+key)
            if review.get('crop'):
                crop=review['crop']
                expected=(review['official_origin'].split('?')[0]+f"?imageMogr2/crop/!{crop['width']}x{crop['height']}a{crop['x']}a{crop['y']}/format/webp")
                if review['url'] != expected or not review.get('origin_sha256') or not review.get('crop_sha256'):
                    raise ValueError('Unverified CDN crop for '+key)
            if not review['url'].startswith('https://xbu-qiniu.yaduo.com/'):
                raise ValueError('Non-official photo')
            cat=categories[str(sid)]
            quantity,contents=package(s,p)
            specs=dict(official_text=s['skuName'], dimensions=None,height=None,filling=None)
            # Literal values only; unknown material/height stays null.
            match=re.search(r'\d+(?:\.\d+)?(?:\s*[*×xX]\s*\d+(?:\.\d+)?){1,2}\s*(?:cm|CM|m|M)',s['skuName'])
            if match:specs['dimensions']=match.group()
            if match and match.group().count('*')+match.group().count('×')==2:
                specs['height']=re.split(r'[*×xX]',match.group())[-1]
            is_bundle='组合装' in p['spuName'] or '四件套' in p['spuName'] or bool(quantity and quantity>1) or '+' in s['skuName']
            row=dict(id=key,name=p['spuName']+' / '+s['skuName'],official_name=p['spuName'],sku_name=s['skuName'],
                brand=BRAND,source=SOURCE,market='CN',currency='CNY',category=cat['category'],categories=cat['categories'],
                category_source=cat['evidence'],price=s['salesPrice'],promo_price=s.get('activityPrice'),
                price_kind='sku_sales_price',price_status='unavailable_option' if s.get('spuStatus') != 1 else 'observed',
                sale_status='unavailable_option' if s.get('spuStatus') != 1 else 'listed',price_basis='官方SKU面板 salesPrice；promo_price仅为activityPrice，不含优惠券、国补或会员结算优惠',
                image=review['url'],image_missing=False,image_policy='official-cdn-product-crop-v1',image_source=review.get('source','main'),image_scope=review.get('scope','sku'),image_review=review,
                source_url=f'https://h5mall.yaduo.com/subpacks/mall/goodsDetail/goodsDetail?id={sid}',
                sku_no=s['skuNo'],spu_id=sid,sku_id=s['id'],specs=specs,specs_missing=[k for k,v in specs.items() if v is None],
                params={'规格':s['skuName'],'官方规格选项':config},bundle=is_bundle,bundle_contents=contents if is_bundle else None,
                package_quantity=quantity,bundle_contents_missing=is_bundle and contents is None,
                bundle_quantity_basis='商品组件数；赠礼袋等赠品不计入' if is_bundle else None,
                captured_at=e['captured_at'],fetched_at=e['captured_at'],price_fetched_at=e['captured_at'],
                record_level='sku',kind='whole',status='available',official_sku_status=s.get('spuStatus'),
                stock_num=s.get('stockNum'),catalog_scope='official_h5_brand_current_sku_options')
            result.append(row)
    return result


def merge_snapshot(previous, capture, **kwargs):
    from goodsdex.retirement import completed_snapshot, reconcile
    rows=build_rows(capture,**kwargs)
    stamp=capture['captured_at']
    merged=completed_snapshot(previous,[deepcopy(r) for r in previous if r.get('source') != SOURCE]+rows,
        brands=[BRAND],observed_at=stamp,snapshot_url=CATALOG_URL)
    return reconcile(previous,merged,[dict(id=r['id'],state='available',observed_at=stamp,source_url=r['source_url']) for r in rows])


def coverage(rows):
    selected=[r for r in rows if r.get('source')==SOURCE]
    current=[r for r in selected if r.get('status')!='retired']
    return dict(source=SOURCE,source_url=CATALOG_URL,spu_count=len({r['spu_id'] for r in current}),sku_count=len(current),
        total_with_retired=len(selected),retired_sku_count=len(selected)-len(current),
        bundle_spu_count=len({r['spu_id'] for r in current if '组合装' in r['official_name']}),
        bundle_sku_count=sum(r['bundle'] for r in current),
        official_sku_status_counts={str(k):v for k,v in Counter(r.get('official_sku_status') for r in current).items()},price_field='salesPrice',promo_price_field='activityPrice',
        scope='匿名官方H5全部亚朵星球SKU选项；含官方不可选/缺货选项，不代表全部有货')
