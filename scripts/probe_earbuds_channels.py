"""Capture anonymous channel searches for the 23 reviewed CN directory models."""
import json
from pathlib import Path
import time
import unicodedata
import probe_mihome_channels as channels
ROOT=Path(__file__).resolve().parents[1]/'docs/earbuds-intake-20261106'
channels.ROOT=ROOT
fetch_original=channels.fetch

def cached_fetch(url,body=None,headers=None):
    import hashlib
    d=fetch_original(url,body,headers)
    key=hashlib.sha256((url+json.dumps(body,ensure_ascii=False,sort_keys=True)).encode()).hexdigest()
    d['file']='raw/'+key+'.json.gz'
    return d

channels.fetch=cached_fetch

def norm(s):
    return ''.join(unicodedata.normalize('NFKC',s or '').casefold().split())

def main():
    import csv
    entries=[r for r in csv.DictReader((ROOT/'evidence/catalog/product-list.tsv').open(),delimiter='\t') if r['in_lib']=='N']
    output=[]
    for e in entries:
        name=' '.join(unicodedata.normalize('NFKC',e['name']).split())
        mi=channels.mi_search(name);time.sleep(.7)
        yp=channels.yp_search(name);time.sleep(.7)
        matches=[]
        for c in mi['candidates']:
            if norm(c.get('name')).startswith(norm(name)):
                matches.append(dict(channel='mi_store',product_id=str(c['product_id']),name=c['name'],search_price=c.get('price')))
        for c in yp['candidates']:
            if norm(c.get('name')).startswith(norm(name)):
                matches.append(dict(channel='youpin',gid=str(c['gid']),name=c['name'],search_price_fen=c.get('priceMin')))
        # Reviewed existing SKU relation from DSH; require an actual matching Wi-Fi SKU.
        if e['model']=='miwear.headphone.o71c':
            matches.append(dict(channel='mi_store',product_id='20978',name=name,mapping='reviewed_wifi_sku'))
        matches=list({(m['channel'], m.get('product_id') or m.get('gid')):m for m in matches}.values())
        confirmed=[]
        for m in matches:
            if m['channel']=='mi_store':
                u='https://api2.order.mi.com/product/view?product_id='+m['product_id']+'&version=2'
                d=channels.fetch(u);data=d.get('response',{}).get('data') or {};p=data.get('product_info') or data.get('product') or {};gs=[g['goods_info'] for g in data.get('goods_list',[]) if g.get('goods_info')] or (data.get('goodsInfo') or {}).get('goodsList') or []
                exact=[g for g in gs if norm(g.get('name'))==norm(name)]
                if m.get('mapping')=='reviewed_wifi_sku':
                    exact=[g for g in gs if 'wifi' in norm(g.get('name')).replace('-','') and 'buds5pro' in norm(g.get('name'))]
                    if not exact: continue
                elif norm(p.get('name'))!=norm(name) and not exact:continue
                g=(exact or gs or [{}])[0]
                if not g.get('price'):continue
                m.update(official_name=g.get('name') if exact else p['name'],price=float(g['price']),gid=str(g.get('goods_id') or g.get('gid') or g.get('commodity_id') or ''),source_url='https://www.mi.com/shop/buy/detail?product_id='+m['product_id'],detail_url=u,captured_at=d['captured_at'],evidence_file=d['file'],price_kind='list')
            else:
                body={'groupName':'details','groupParams':[[m['gid']]],'pid':'','methods':[],'version':'1.0.0','debug':False,'channel':'','vipMode':False,'system':'3'}
                d=channels.fetch('https://www.xiaomiyoupin.com/api/gateway/detail',body,{'Content-Type':'application/json','X-Yp-App-Source':'front-PC','X-User-Agent':'channel/youpin platform/youpin.pc'})
                g=(d.get('response',{}).get('data') or {}).get('goods') or {};info=g.get('goodsInfo') or {};p=g.get('priceInfo') or {}
                if norm(info.get('name'))!=norm(name):continue
                brand=g.get('brand') or {}
                if (info.get('brandName') or brand.get('brandName')) not in ('小米自营产品','小米','米家'):continue
                price=info.get('priceMin')
                if not price:continue
                m.update(official_name=info['name'],price=float(price)/100,source_url='https://www.xiaomiyoupin.com/detail?gid='+m['gid'],detail_url=d['url'],captured_at=d['captured_at'],evidence_file=d['file'],price_kind='list')
            confirmed.append(m)
        output.append(dict(model=e['model'],name=name,mi=mi,youpin=yp,matches=confirmed))
        (ROOT/'channel-searches.json').write_text(json.dumps(output,ensure_ascii=False,indent=1)+'\n')
        print(len(output),name,'hits',len(confirmed),'errors',bool(mi['error']),bool(yp['error']),flush=True)
if __name__=='__main__':main()
