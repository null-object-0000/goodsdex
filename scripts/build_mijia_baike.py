"""Build reviewable, evidence-scoped metadata from anonymous collection caches."""
import argparse
from collections import Counter
import hashlib
import io
import csv
import json
import re
from pathlib import Path
import sys
import subprocess
from urllib.parse import quote, urlsplit
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from goodsdex.mijia_baike import apply_baike, hardware_models, norm
from collect_mijia_baike import fetch


def build(root, goods, destination):
    mapping = json.loads((root / 'mapping.json').read_text())
    catalog = {d['model']: d for d in json.loads((root / 'apk-catalog.json').read_text())}
    rows = json.loads(goods.read_text())
    enriched_path = root / 'enriched.json'
    transport = {x['model']:x for x in json.loads(enriched_path.read_text())} if enriched_path.exists() else {}
    byid = {r['id']: r for r in rows}
    entries, model_rows, rejected = [], [], []
    models = sorted({m for e in mapping['items'] for m in e['models']} | {'mibx5.washer.x15'})
    for model in models:
        product_file = root / 'raw' / (model + '.json')
        if not product_file.exists():
            rejected.append(dict(model=model, reason='product_not_collected')); continue
        capture = json.loads(product_file.read_text())
        response = capture.get('response', {})
        data = response.get('data') or {}
        if response.get('code') != 0 or data.get('model') != model or not data.get('name'):
            rejected.append(dict(model=model, reason=capture.get('error') or 'source_empty_or_error')); continue
        raw_product = json.dumps(response,ensure_ascii=False,separators=(',',':')).encode()
        assert hashlib.sha256(raw_product).hexdigest() == capture['sha256'], model
        def endpoint(name):
            p = root / 'raw' / f'{model}.{name}.json'
            if not p.exists(): return {}, None, 'not_collected'
            raw = p.read_bytes(); r = json.loads(raw)
            data = (r.get('data') or {}) if r.get('code') == 0 else {}
            return data, hashlib.sha256(raw).hexdigest(), ('success' if data else 'source_empty') if r.get('code')==0 else 'source_error'
        intro, intro_hash, intro_status = endpoint('introduction')
        attributes, attr_hash, attr_status = endpoint('attribute')
        parameters = list({json.dumps(a, sort_keys=True, ensure_ascii=False): a for a in
                           [*(data.get('attributeMap') or []), *(attributes.get('list') or [])]}.values())
        manual_url = (intro.get('introductionPdf') or {}).get('url')
        if intro.get('introductionType') == 'html':
            manual_url = 'https://home.mi.com/views/introduction.html?model=' + model + '&region=cn'
        pdf = root / 'manuals' / (model + '.pdf')
        page1 = root / 'manuals' / (model + '.page1.txt')
        valid_pdf = pdf.exists() and pdf.read_bytes().startswith(b'%PDF')
        if valid_pdf:
            valid_pdf = subprocess.run(['pdfinfo',str(pdf)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=15).returncode==0
        codes = hardware_models(page1.read_text()) if page1.exists() else []
        types = [a.get('attributeValue') for a in parameters if a.get('attributeName') in ('产品类型', '产品品类')]
        item = dict(model=model, productName=data['name'], product_url=capture['url'],
                    product_sha256=capture['sha256'], captured_at=capture['captured_at'],
                    manual_url=manual_url, manual_type=intro.get('introductionType'),
                    manual_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest() if valid_pdf else None,
                    introduction_sha256=intro_hash, attribute_sha256=attr_hash,
                    introduction_status=intro_status,
                    attribute_status=attr_status if parameters or attr_status!='success' else 'source_empty',
                    manual_status=('downloaded' if valid_pdf else 'html' if intro.get('introductionType')=='html' else
                                   'invalid_pdf' if pdf.exists() else 'download_failed' if manual_url else 'source_error' if intro_status=='source_error' else 'source_empty' if intro_hash else 'not_collected'),
                    manual_error=transport.get(model,{}).get('manual_error'),
                    hardware_models=codes, hardware_model_status='page1_model_codes' if codes else 'not_found_on_page1' if page1.exists() else 'not_extracted',
                    parameters=parameters, parameter_count=len(parameters),
                    category_clue=types or (catalog.get(model) or {}).get('cate_name'),
                    materialPictures=data.get('materialPictures') or [], image_missing=not bool(data.get('materialPictures')),
                    shop_url=(data.get('buyUrl') or {}).get('channelUrl'))
        model_rows.append(item)
    hardware_matches = []
    for item in model_rows:
        for code in item['hardware_models']:
            pattern = re.compile(r'(?<![A-Za-z0-9])' + re.escape(code) + r'(?![A-Za-z0-9])', re.I)
            for row in rows:
                if row['id'].startswith('CN:mi_cn:product:') and pattern.search(row.get('name', '')):
                    hardware_matches.append(dict(id=row['id'],name=row['name'],hardware_model=code,miio_model=item['model']))
    (root/'hardware-name-matches.json').write_text(json.dumps(hardware_matches,ensure_ascii=False,indent=2)+'\n')
    bymodel = {e['model']: e for e in model_rows}
    for bridge in mapping['items']:
        if len(bridge['models']) != 1: continue
        model = bridge['models'][0]
        if model not in bymodel or byid[bridge['id']].get('is_container'): continue
        entry = dict(bymodel[model], id=bridge['id'], expected_name=bridge['old_name'], mapping_method=bridge['method'])
        entry['mapping_evidence'] = ({'shop_url': entry['shop_url']} if bridge['method']=='baike_official_shop_link'
                                     else {**catalog[model], 'asset_sha256':mapping['catalog_asset_sha256']})
        row = byid[entry['id']]
        matches = [code for code in entry['hardware_models'] if any(norm(str((row.get('params') or {}).get(k,'')))==norm(code) for k in ('产品型号','设备型号','型号'))]
        if len(matches)==1: entry['name_repair_hardware_model']=matches[0]
        if not row.get('image'):
            for url in entry['materialPictures']:
                if not isinstance(url,str) or urlsplit(url).scheme!='https': continue
                try:
                    raw=fetch(quote(url,safe=':/?=&%+'))
                    from PIL import Image
                    picture=Image.open(io.BytesIO(raw)); picture.verify()
                    if min(picture.size)<400: continue
                    entry['verified_image']=dict(url=url,sha256=hashlib.sha256(raw).hexdigest(),size=list(picture.size))
                    break
                except Exception: continue
        entries.append(entry)
    manifest = {'schema':1,'policy':'no-release-no-category-structure-change', 'items':entries}
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    after = apply_baike(rows,manifest)
    new = {r['id']:r for r in after}
    changed_names = [dict(id=k,before=r['name'],after=new[k]['name']) for k,r in byid.items() if new[k]['name']!=r['name']]
    sample=json.loads((root/'sample-50.json').read_text())
    summary=dict(population=mapping['population'],sample_total=50,
                 sample_unique_candidates=sum(len(x['models'])==1 for x in sample),
                 sample_ambiguous=sum(len(x['models'])>1 for x in sample),
                 sample_confirmed_model=sum(bool(new[x['id']].get('miio_model')) for x in sample),
                 mapped_candidates=len(mapping['items']),unique_candidates=sum(len(x['models'])==1 for x in mapping['items']),
                 collected_models=len(model_rows),rejected_models=len(rejected),published_metadata=len(entries),
                 confirmed_models=sum('miio_model' in r for r in new.values()),
                 manual_urls=sum(bool(x['manual_url']) for x in model_rows),pdf_downloaded=sum(bool(x['manual_sha256']) for x in model_rows),
                 manual_failures=sum(x['manual_status']=='download_failed' for x in model_rows),
                 invalid_pdfs=sum(x['manual_status']=='invalid_pdf' for x in model_rows),
                 models_with_hardware_codes=sum(bool(x['hardware_models']) for x in model_rows),
                 models_with_parameters=sum(bool(x['parameter_count']) for x in model_rows),
                 total_parameters=sum(x['parameter_count'] for x in model_rows),
                 hardware_name_matches=len(hardware_matches),
                 names_corrected=len(changed_names),name_examples=changed_names,
                 categories_corrected=0,category_distribution={},
                 images_filled=sum(not byid[k].get('image') and bool(r.get('image')) for k,r in new.items()),
                 population_images_still_missing=sum(not r.get('image') for r in after if r['id'].startswith('CN:mi_cn:product:')),
                 mapped_images_still_missing=sum(not new[e['id']].get('image') for e in entries),
                 baike_material_missing=sum(x['image_missing'] for x in model_rows),
                 release_coverage_change=sum(bool(r.get('release')) for r in new.values())-sum(bool(r.get('release')) for r in byid.values()))
    for k,r in byid.items():
        for field in ('category','categories','release','release_date','release_upper_bound'):
            assert r.get(field)==new[k].get(field),(k,field)
    (root/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    (root/'collected-models.json').write_text(json.dumps(model_rows,ensure_ascii=False,indent=2)+'\n')
    with (root/'collected-models.tsv').open('w') as stream:
        fields=['model','productName','hardware_models','manual_url','manual_status','parameter_count','attribute_status','category_clue','image_missing']
        writer=csv.DictWriter(stream,fieldnames=fields,delimiter='\t',lineterminator='\n',extrasaction='ignore')
        writer.writeheader()
        for item in model_rows:
            writer.writerow({**item,'hardware_models':';'.join(item['hardware_models'])})
    (root/'rejected-models.json').write_text(json.dumps(rejected,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary,ensure_ascii=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--goods',type=Path,required=True)
    parser.add_argument('--manifest',type=Path,default=Path('data/official/mijia-baike.json'))
    args=parser.parse_args();build(args.output,args.goods,args.manifest)
