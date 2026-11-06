"""Build a reviewable frozen intake manifest, never change existing goods."""
import argparse
from collections import Counter
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from goodsdex.mihome_intake import apply_intake
from goodsdex.price_semantics import normalize
from discover_mihome_gaps import norm,save
from probe_mihome_channels import fetch,ROOT

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--goods',type=Path,required=True);a=ap.parse_args()
    old=json.loads(a.goods.read_text());byname={norm(r.get('name')):r['id'] for r in old if r.get('name')};ids={r['id'] for r in old};known_models={r.get('miio_model') or r.get('mihome_model') for r in old}
    ds=json.loads((ROOT/'A.json').read_text());probes={r['model']:r for r in json.loads((ROOT/'channels-all.json').read_text())};items=[];decisions=[];now=datetime.now(timezone.utc).isoformat();sha=hashlib.sha256((ROOT.parent/'mihome-catalog-20261106/devices.json').read_bytes()).hexdigest()
    for d in ds:
        p=probes.get(d['model']);decision=dict(model=d['model'],name=d['name'],pd_id=d['pd_id'])
        if not p:raise ValueError('Incomplete probe '+d['model'])
        if norm(d['name']) in byname or d['model'] in known_models:
            decisions.append(dict(decision,status='existing_identity_or_same_name_review',existing_id=byname.get(norm(d['name']))));continue
        matches=list({(m['channel'],m['product_id']):m for m in p['matches']}.values());mi=[m for m in matches if m['channel']=='mi_cn'];yp=[m for m in matches if m['channel']=='youpin'];chosen=mi if len(mi)==1 else yp if len(yp)==1 else []
        if not p['baike']['valid']:
            decisions.append(dict(decision,status='baike_identity_unverified'));continue
        r=dict(id=f"mihome:{d['pd_id']}",name=d['name'],name_mihome=d['name'],category=d['category'],category_mihome=d['category'],brand='小米' if d['brand']=='小米公司' else d['brand'],miio_model=d['model'],mihome_model=d['model'],mihome_pd_id=d['pd_id'],image=None,image_missing=True,image_mihome=dict(url=d['icon'],scope='device_icon',source='mihome_directory',note='米家设备图标，非商品主图'),price=None,price_missing='no_channel_price',price_kind='unknown',source='mihome',source_url=d['jumpUrl'],source_channels=['mihome'],kind='machine',record_level='device_reference',catalog_identity='mihome_durable_device_v1',captured_at=now,params={},channel_search_status=p['status'])
        selected=None
        if chosen:
            selected=chosen[0];s=selected['channel'];pid=selected['product_id'];key=f'CN:mi_cn:product:{pid}' if s=='mi_cn' else f'youpin:{pid}'
            if key in ids:
                decisions.append(dict(decision,status='existing_channel_id',existing_id=key));continue
            cat=selected.get('channel_category') or {};cat=cat.get('newCname3') or cat.get('cname3') if isinstance(cat,dict) else None
            price=selected.get('price') if s=='mi_cn' else selected.get('price_fen');price=float(price)/(100 if s=='youpin' else 1) if price else None
            r.update(id=key,source=s,name=selected['name'],category=cat or d['category'],image=selected.get('image'),image_missing=not bool(selected.get('image')),image_source=s,image_scope='product_image',image_source_url=selected['source_url'],source_url=selected['source_url'],source_channels=['mihome',s],record_level='product',product_id=pid,price=price,price_kind='full' if price else 'unknown',price_missing=False if price else 'no_channel_price',price_source_url=selected['source_url'],price_basis='channel_display_starting_price',price_fetched_at=now)
            if s=='youpin':
                body={'groupName':'details','groupParams':[[pid]],'pid':'','methods':[],'version':'1.0.0','debug':False,'channel':'','vipMode':False,'system':'3'}
                e=fetch('https://www.xiaomiyoupin.com/api/gateway/detail',body);g=e['response']['data']['goods'];info=g['goodsInfo'];pr=g.get('priceInfo') or {}
                r.update(youpin_gid=pid,price_status='current' if pr.get('onSale',info.get('onSale')) else 'stale',sale_status='available' if pr.get('onSale',info.get('onSale')) else 'unavailable')
                r['image']=info.get('img800s') or info.get('img800') or info.get('imgSquare') or r['image']
        r=normalize(r)
        if r['price'] is None:r['price_missing']='no_channel_price'
        # Same names across several device models are an identity review queue.
        if norm(r['name']) in byname or r['id'] in ids:
            decisions.append(dict(decision,status='duplicate_name_or_channel_review',existing_id=byname.get(norm(r['name']))));continue
        items.append(dict(classification='A',directory_sha256=sha,channel_verified=bool(selected),row=r));ids.add(r['id']);byname[norm(r['name'])]=r['id'];known_models.add(d['model']);decisions.append(dict(decision,status='added',id=r['id'],has_price=r['price'] is not None))
    manifest=dict(schema=1,items=items);save(Path('data/official/mihome-intake.json'),manifest);save(ROOT/'intake-decisions.json',decisions)
    after=apply_intake(old,manifest);assert after[:len(old)]==old
    save(ROOT/'intake-summary.json',dict(added=len(after)-len(old),with_price=sum(e['row']['price'] is not None for e in items),without_price=sum(e['row']['price'] is None for e in items),by_source=dict(Counter(e['row']['source'] for e in items)),decisions=dict(Counter(r['status'] for r in decisions))))
    priced=[e['row'] for e in items if e['row']['price'] is not None];unpriced=[e['row'] for e in items if e['row']['price'] is None];save(ROOT/'sample-10-new.json',(priced[:7]+unpriced[:3])[:10]);print((ROOT/'intake-summary.json').read_text())
if __name__=='__main__':main()
