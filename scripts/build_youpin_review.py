#!/usr/bin/env python3
"""Build the conservative reviewed manifest from the bounded audit evidence."""
import hashlib
import gzip
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from audit_youpin import ROOT, detail, exact


def main():
    mapping = json.loads((ROOT/'mapping-50.json').read_text())
    # User-provided control is separate from the fixed 50-row random sample.
    control = {'id':'CN:mi_cn:product:16725', 'name':'米家负离子吹风机 H301',
               'matches':[{'gid':156975}], 'control':True}
    items=[]
    for row in [*mapping, control]:
        if not row['matches']:
            continue
        gid=row['matches'][0]['gid'];g=detail(gid);info=g['goodsInfo']
        path=ROOT/'raw'/f'detail-{hashlib.sha256(str(gid).encode()).hexdigest()[:16]}.json.gz'
        ev=json.loads(gzip.decompress(path.read_bytes()));offers=[]
        for pid,sku in g['productInfo'].items():
            price_info=g.get('priceInfo',{}).get('productsPriceInfo',{}).get(pid,{})
            single=price_info.get('singlePrice') or {}
            promotion=single.get('promotionPrice')
            price=single.get('price',sku.get('price'))
            offers.append({'pid':int(pid),'sku_id':sku.get('skuId'),'name':sku['name'],
                'attribute_values':sku.get('attributeValues',[]),'image':sku.get('img'),
                'price':price/100 if price is not None else None,'currency':'CNY',
                'price_kind':'promotion' if promotion else 'channel_sku',
                'promotion_type':promotion.get('promotionType') if promotion else None,
                'listed_base_price':sku['price']/100 if sku.get('price') is not None else None,
                'market_price':sku['marketPrice']/100 if sku.get('marketPrice') is not None else None,
                'on_sale':sku.get('onSale'),'inventory':sku.get('inventory'),
                'price_status':'provided' if sku.get('onSale') else 'not_on_sale',
                'observed_at':ev['captured_at']})
        items.append({'id':row['id'],'mi_name':row['name'],'gid':gid,
            'youpin_name':info['name'],'mapping_method':'unique_exact_name',
            'brand_name':g['brand']['brandName'],'category':[g['category'].get(f'newCname{i}') for i in (1,2,3)],
            'image':info.get('img800') or info.get('picUrl'), 'offers':offers,
            'listed':{'timestamp':info['firstTime'],'date':datetime.fromtimestamp(info['firstTime'],ZoneInfo('Asia/Shanghai')).date().isoformat(),
                      'precision':'day','source':'youpin_listed','event':'channel_listing'},
            'evidence':{'url':f'https://www.xiaomiyoupin.com/detail?gid={gid}',
                'capture_url':ev['url'],'captured_at':ev['captured_at'],'sha256':ev['sha256'],
                'capture_file':str(path),'response_json_sha256':hashlib.sha256(json.dumps(ev['response'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'locator':'$.data.goods',
                'name_locator':'$.data.goods.goodsInfo.name','time_locator':'$.data.goods.goodsInfo.firstTime'},
            'control':row.get('control',False)})
    out={'schema':1,'policy':'Channel listing is an upper bound, never an unverified announcement date. Exact name + unique gid + verified Xiaomi self-operated brand only. Ecosystem brands require separate official relationship evidence.',
         'sample_seed':156975,'sample_size':50,'sample_hits':sum(bool(r['matches']) for r in mapping),'items':items}
    Path('data/official/youpin-crosswalk.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print('Reviewed mappings:',len(items))

if __name__=='__main__':main()
