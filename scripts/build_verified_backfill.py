"""Offline conversion of reviewed candidates; no collection and no public writes."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
D = ROOT / 'data'
def read(p): return json.loads((D / p).read_text())
def write(p, data): (D / 'supplements' / p).write_text(json.dumps(data, ensure_ascii=False, indent=1)+'\n')
def valid(c): return all(c.get(k) for k in ('source','source_url','captured_at'))
def main():
    extras = read('supplements/goods-supplements.json')
    patches, skipped, pending, added = [], [], [], []
    for c in read('research/xiaomi-names-20261030/candidates.json'):
        if c['confidence'] != 'high': pending.append(c); continue
        if not valid(c): skipped.append(dict(candidate=c,reason='missing_provenance')); continue
        key = 'CN:mi_cn:product:'+c['pid']
        fields = dict(name=c['name'], name_source=c['source'], source_url=c['source_url'], captured_at=c['captured_at'])
        patches.append(dict(id=key,field='name',fields=fields,**{k:c[k] for k in ('source','source_url','captured_at')}))
        added.append(dict(id=key, **fields, source='xiaomi_archive_history', catalog_identity='verified_backfill_20261030', brand='小米', kind='unknown', category='旧款机型', categories=['旧款机型'], record_level='model_reference', discontinued=True, price=None, image=None, params={}))
    for c in read('research/apple-backfill-20261030/images.json'):
        if not valid(c): skipped.append(dict(candidate=c,reason='missing_provenance',missing=[k for k in ('source','source_url','captured_at') if not c.get(k)])); continue
        fields=dict(image=c['image_url'],image_source='apple_support' if 'support' in c['source'] else 'apple_store',image_source_url=c['source_url'],image_scope=c['image_scope'],image_captured_at=c['captured_at'])
        patches.append(dict(id=c['id'],field='image',fields=fields,**{k:c[k] for k in ('source','source_url','captured_at')}))
    for c in read('research/apple-backfill-20261030/prices.json'):
        if not valid(c): skipped.append(dict(candidate=c,reason='missing_provenance')); continue
        fields=dict(historical_price=c['price_cny'],price_kind=c['price_kind'],price_source=c['source'],price_source_url=c['source_url'],captured_at=c['captured_at'],price_basis=c['price_basis'])
        patches.append(dict(id=c['id'],field='historical_price',fields=fields,**{k:c[k] for k in ('source','source_url','captured_at')}))
    for group in read('research/car-years-20261030/byd.json'):
        trims=[]
        for c in group['trims']:
            if not valid(c): raise ValueError('Car missing provenance')
            tid='CN:byd:car:pcauto:'+c['spec_url'].split('/m')[1].split('/')[0]
            t=dict(id=tid,name=c['config_name'],price=None,historical_price=c['price_cny'],price_kind='msrp_historical',image=None,image_scope=None,image_status='missing',params={},source_record=dict(c, id=tid, brand='比亚迪', category='汽车', categories=['汽车'], product_type='car', series='汉', model_year=group['model_year'], price=None, historical_price=c['price_cny']))
            trims.append(t)
        year,power=group['model_year'],group['powertrain']
        key=f'CN:byd:car:han:{year}:{power.lower().replace("-", "")}'
        added.append(dict(id=key,product_id=key,schema='car-product-v2',record_level='car_product',name=f'比亚迪 汉 {year}款 {power}',display_name=f'比亚迪 汉 {year}款 {power}',official_name='汉',brand='比亚迪',kind='machine',category='汽车',categories=['汽车'],product_type='car',series='汉',model_year=year,model_year_source='pcauto',model_year_confidence='third_party',model_year_source_url=trims[0]['source_record']['source_url'],powertrain=power,source='pcauto',source_url=trims[0]['source_record']['source_url'],captured_at=trims[0]['source_record']['captured_at'],catalog_identity='verified_backfill_20261030',trims=trims,legacy_ids=[t['id'] for t in trims],price=None,price_kind='msrp_historical',image=None,image_scope=None,image_status='missing',sale_status='discontinued',params={}))
    for group in read('research/car-years-20261030/xiaomi.json'):
        if group['model_year'] is not None or not all(valid(c) for c in group['trims']):
            raise ValueError('Invalid Xiaomi year evidence')
    existing={r['id']:r for r in extras}
    for r in added:
        if r['id'] in existing:
            if existing[r['id']] != r: raise ValueError('Supplement conflict '+r['id'])
        else: extras.append(r)
    write('goods-supplements.json', extras)
    write('verified-backfill-20261030.json',patches)
    write('backfill-skipped-20261030.json',skipped)
    write('backfill-pending-20261030.json',pending)
    print(dict(new_rows=len(added),patches=len(patches),skipped=len(skipped),pending=len(pending)))
if __name__=='__main__': main()
