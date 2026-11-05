#!/usr/bin/env python3
"""Build HP history only from captured exact-SKU official support responses.

The sitemap comparison describes withdrawal from the current China store
catalogue. It is not a manufacturer discontinuation date or end-of-support claim.
"""
import argparse
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from goodsdex.hp_history import validate, literal_generation


def parse_capture(capture, catalogue):
    if capture.get('status') != 200:
        raise ValueError('Non-200 support response')
    body = capture['body']
    if hashlib.sha256(body.encode()).hexdigest() != capture['sha256']:
        raise ValueError('Support response hash mismatch')
    data = json.loads(body)
    specs = data['data']['devices'][0]['productSpecs']
    product = specs['data']
    sku = product['productNumber']
    requested = capture['payload']['devices'][0]['productNumber']
    if data['code'] != 200 or specs['code'] != 200 or sku != requested:
        raise ValueError('Support SKU does not match the requested part number')
    if capture['url'] != 'https://support.hp.com/wcc-services/profile/devices/warranty/specs?cache=true':
        raise ValueError('Unrecognized official support endpoint')
    if product['prodCategory'] not in ('laptop', 'desktop', 'pc', 'workstation'):
        raise ValueError('Not a supported computer category')
    series_name = product['productSeriesName']
    name = product['productName']
    family = re.search(r'ProBook|EliteBook|EliteDesk|EliteOne|ProDesk|ProOne|ZBook|Dragonfly|Chromebox|Pavilion|ENVY|Spectre|OMEN|Victus|ZHAN|Elite|Pro', series_name, re.I)
    generation = literal_generation(series_name, product['redirectUrl'])
    image = product.get('imageUri')
    if not image or 'fallback_product' in image:
        image = None
    else:
        image = urljoin('https://support.hp.com', image)
    category = '笔记本' if product['prodCategory'] == 'laptop' else '台式机'
    if 'ZBook' in series_name or 'Workstation' in series_name or '工作站' in series_name:
        category = '工作站'
    cpu = re.search(r'\b(?:i[3579]-[0-9A-Za-z]+|R[3579]-[0-9A-Za-z]+)\b', name, re.I)
    ram = re.search(r'\b(\d+)GB/', name)
    # An unlabelled '/512' is left verbatim; do not guess its unit or drive type.
    config = re.search(r'\b\d+GB/[0-9A-Za-z+]+', name)
    params = {'产品编号': sku, '型号': series_name,
              '官方配置标识': config[0] if config else name,
              'source_specs': {'productName': name, 'productSeriesName': series_name,
                               'productPlatform': product.get('productPlatform'),
                               'productType': product.get('productType')}}
    if cpu:
        params['CPU型号'] = cpu[0]
    if ram:
        params['运行内存'] = ram[1] + 'GB'
    size = re.search(r'(\d+(?:\.\d+)?)\s*(?:英寸|inch)', series_name, re.I)
    if size:
        params['屏幕尺寸'] = size[1] + '英寸'
    source_url = 'https://support.hp.com/cn-zh' + product['redirectUrl']
    row = dict(id='CN:hp_cn:sku:' + sku, product_id='CN:hp_cn:support-series:' + str(product['productSeriesOid']),
               name=name, source_name=name, model=series_name, part_number=sku,
               series=family[0] if family else series_name,
               generation=generation,
               category=category, categories=[category], brand='惠普', source='hp_cn', market='CN', kind='machine',
               record_level='configuration', lookup_keys=[sku, series_name, name],
               image=image, image_scope='official_support_product_reference' if image else None,
               source_url=source_url, price=None, market_price=None, price_kind=None, currency='CNY',
               fetched_at=capture['observed_at'], params=params,
               support_evidence=dict(url=capture['url'], method='POST', product_number=sku,
                   response_sha256=capture['sha256'], observed_at=capture['observed_at'],
                   model_oid=product['productNameOid'], series_oid=product['productSeriesOid'],
                   support_first_published=product.get('webFirstPublishingDate')),
               specs_scope='exact_sku_official_configuration_label',
               specs_missing='unlabelled_storage_units_and_unpublished_gpu_are_not_inferred')
    if not generation:
        row['generation_missing'] = 'official_series_name_has_no_generation_token'
    if not image:
        row['image_missing'] = 'official_support_only_supplied_generic_fallback_or_no_image'
    row['params']['variant_attrs'] = {'dimensionEdition': dict(value=sku, label=sku)}
    if sku in catalogue['part_numbers']:
        row['status'] = 'available'
    else:
        row.update(status='retired', retired_at=catalogue['observed_at'],
                   retirement_evidence=dict(reason='absent_from_completed_official_store_catalogue',
                       scope='hpstore.cn current sellable catalogue; not hardware end-of-life',
                       source_url='https://www.hpstore.cn/',
                       catalogue_capture_id=catalogue['capture_id'],
                       sitemap_urls=catalogue['urls'], observed_at=catalogue['observed_at']))
    validate(row)
    return row


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--captures', type=Path, action='append', required=True)
    ap.add_argument('--catalogue', type=Path, required=True)
    ap.add_argument('--families', type=Path)
    ap.add_argument('--out', type=Path, default=ROOT / 'data/official/hp-history.json')
    args = ap.parse_args()
    catalogue = json.loads(args.catalogue.read_text())
    if len(catalogue.get('urls', [])) != 3 or len(catalogue.get('part_numbers', [])) < 200:
        raise ValueError('Missing complete three-file official store sitemap evidence')
    captures = []
    for path in args.captures:
        if path.is_dir():
            captures.extend(json.loads(p.read_text()) for p in sorted(path.glob('*.json')) if p.name != 'audit.json')
        else:
            captures.extend(json.loads(gzip.decompress(path.read_bytes())))
    rows = {}
    not_imported = []
    for capture in captures:
        if capture.get('status') == 200 and capture.get('body'):
            requested = capture['payload']['devices'][0]['productNumber']
            if requested.endswith('PA') and requested not in catalogue['part_numbers']:
                # A translated CN support context does not establish the sales
                # market of a regional PA SKU found in a global accessory list.
                not_imported.append(dict(part_number=requested,
                    reason='regional_PA_SKU_has_no_verified_China_store_market_evidence'))
                continue
            # Re-validate raw evidence; an earlier narrower category allowlist
            # may have rejected HP's literal 'pc' desktop category.
            row = parse_capture(capture, catalogue)
            rows[row['id']] = row
    if args.families:
        for row in json.loads(args.families.read_text()):
            validate(row)
            rows[row['id']] = row
    result = dict(schema=1, scope='China SKU history from official HP support; explicitly separated marketing families',
                  catalogue=catalogue, not_imported=not_imported, rows=list(rows.values()))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n')
    print(json.dumps(dict(count=len(rows), with_part_number=sum(bool(r.get('part_number')) for r in rows.values())), ensure_ascii=False))


if __name__ == '__main__':
    main()
