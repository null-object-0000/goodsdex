"""Build a frozen model manifest from the existing DSH CN evidence."""
import csv
import json
from pathlib import Path
import unicodedata
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
DOC=ROOT/'docs/earbuds-intake-20261106'

def main():
    capture=json.loads((DOC/'evidence/directory-capture.json').read_text())
    probes={e['model']:e for e in json.loads((DOC/'channel-searches.json').read_text())}
    catalog=list(csv.DictReader((DOC/'evidence/catalog/product-list.tsv').open(),delimiter='\t'))
    rows=[]
    manifest_path=ROOT/'data/official/earbuds-intake.json'
    existing=json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    intake_at=next((r['intake_at'] for r in existing.get('items',[]) if r.get('intake_at')), datetime.now(timezone.utc).isoformat())
    for e in catalog:
        if e['in_lib']!='N':continue
        name=' '.join(unicodedata.normalize('NFKC',e['name']).split())
        image=e['icon_clean'];key=e['model']
        fields=dict(name=name,model=key,image=image,image_kind='white_background',width=860,height=580,category='耳机')
        evidence=dict(method='anonymous_api',cookie_kind='app_static',http_status=200,verified=True,sha256=capture['sha256'],captured_at_precision='day',captured_at_basis=capture['captured_at_basis'])
        sources=[dict(source='earbuds_directory',role='primary',kind='device_directory',source_url=capture['source_url'],captured_at=capture['captured_at'],fields=fields,evidence=evidence)]
        links=[]
        for m in probes[key]['matches']:
            # A channel list amount is evidence for a linked product/SKU, not an
            # offer owned by this directory reference. It never becomes row.price.
            sf=dict(name=m['official_name'],channel_price=m['price'],price_kind='list',channel=m['channel'],gid=m['gid'])
            if m.get('product_id'):sf['product_id']=m['product_id']
            sources.append(dict(source=m['channel'],role='secondary',kind='channel_listing',captured_at=m['captured_at'],source_url=m['source_url'],fields=sf,evidence=dict(method='api',http_status=200,verified=True,mapping=m.get('mapping','unique_exact_name'),detail_url=m['detail_url'],file=m['evidence_file'])))
            links.append({k:m[k] for k in ('channel','product_id','gid','price','price_kind','source_url') if k in m})
        r=dict(id=key,model=key,region='CN',name=name,brand='小米',category='耳机',kind='machine',record_level='model_reference',catalog_identity='earbuds_directory_cn_v1',source='earbuds_directory',source_url=capture['source_url'],source_channels=['earbuds_directory'],primary_source='earbuds_directory',discovered_by='earbuds_directory',captured_at=capture['captured_at'],image=image,image_missing=False,image_scope='product_image',image_source='earbuds_directory',price=None,price_kind='unknown',price_missing='no_channel_price',price_comparable=False,sale_status='unverified',params={},sources=sources,channel_links=links)
        r['intake_at']=intake_at
        rows.append(r)
    assert len(rows)==23 and len({r['id'] for r in rows})==23
    manifest_path.write_text(json.dumps(dict(schema=1,items=rows),ensure_ascii=False,indent=1)+'\n')
    supplements_path=ROOT/'data/supplements/goods-supplements.json'
    supplements=json.loads(supplements_path.read_text())
    ids={r['id'] for r in rows}
    supplements=[r for r in supplements if r['id'] not in ids]+rows
    supplements_path.write_text(json.dumps(supplements,ensure_ascii=False,indent=1)+'\n')
if __name__=='__main__':main()
