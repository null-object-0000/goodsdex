"""Exact-product HP PartSurfer supplements; no marketing-name inference."""
import hashlib
import json
import re
from copy import deepcopy
from pathlib import Path

DEFAULT = Path(__file__).resolve().parents[2] / 'data/official/hp-configurations.json'


def parse_parts(capture, row):
    sku = row['part_number']
    expected = ('https://partsurfer.hpcloud.hp.com/bff/proxy/get?input='
                f'/Product/GetProduct/{sku}/country/US/usertype/EXT')
    if capture['url'] != expected or capture['status'] != 200:
        raise ValueError('Not an exact official HP parts response')
    if hashlib.sha256(capture['body'].encode()).hexdigest() != capture['sha256']:
        raise ValueError('HP parts response hash mismatch')
    data = json.loads(capture['body'])
    parts = data.get('Body')
    if data.get('Status', {}).get('Code') != 'S-0001' or not parts:
        raise ValueError('HP parts response has no verified product')
    if any(p.get('ProductNumber') != sku for p in parts):
        raise ValueError('HP parts product-number mismatch')
    specs = {}
    support_name = row.get('params', {}).get('source_specs', {}).get('productName', '')
    memory = re.search(r'\b(\d+)GB/', support_name)
    if memory and row.get('support_evidence', {}).get('product_number') == sku:
        specs['运行内存'] = memory[1] + 'GB'
    # Read only actual display panels. FHD webcam bezels and QHD covers are
    # not panel specifications. Multiple panel options stay explicitly unknown.
    panels = [p for p in parts if re.search(r'\b(?:RAW PANEL|LCD PANEL)\b', p['EnhancedDescription'])]
    resolutions = {m[1] for p in panels if (m := re.search(r'(?<![A-Z])(FHD|QHD|HD|WUXGA|WQXGA)(?![A-Z])', p['EnhancedDescription']))}
    if len(resolutions) == 1:
        specs['屏幕规格'] = next(iter(resolutions))
    drives = [p for p in parts if re.search(r'\bSSD\b', p['EnhancedDescription'])]
    capacities = {m[1] + m[2] for p in drives if (m := re.search(r'\b(\d+)\s*(TB|GB)\b', p['EnhancedDescription']))}
    if len(capacities) == 1:
        specs['存储容量'] = next(iter(capacities))
    evidence = dict(url=capture['url'], source_url=f'https://partsurfer.hp.com/?searchtext={sku}&searchby=product',
                    response_sha256=capture['sha256'], observed_at=capture['observed_at'],
                    product_number=sku, scope='exact_product_service_parts_not_serial_number_as_built',
                    panels=[{k: p[k] for k in ('PartNumber', 'EnhancedDescription')} for p in panels],
                    drives=[{k: p[k] for k in ('PartNumber', 'EnhancedDescription')} for p in drives])
    return dict(part_number=sku, params=specs, configuration_evidence=evidence,
                configuration_missing={
                    **({} if len(resolutions) == 1 else {'display': 'official_parts_have_no_single_panel_resolution'}),
                    **({} if len(capacities) == 1 else {'storage': 'official_parts_have_no_single_ssd_capacity'}),
                    'refresh_rate': 'official_product_label_and_parts_do_not_state_refresh_rate',
                    'marketing_identity': 'official_sku_sources_do_not_explicitly_map_to_zhan66_generation6'})


def apply_configurations(rows, path=DEFAULT):
    if not Path(path).exists():
        return rows
    bundle = json.loads(Path(path).read_text())
    if bundle.get('schema') != 1:
        raise ValueError('Unknown HP configurations schema')
    supplements = {s['part_number']: s for s in bundle['rows']}
    if len(supplements) != len(bundle['rows']):
        raise ValueError('Duplicate HP configuration part number')
    result = []
    for original in rows:
        row = deepcopy(original)
        supplement = supplements.get(row.get('part_number')) if row.get('source') == 'hp_cn' else None
        if supplement:
            sku = row['part_number']
            evidence = supplement['configuration_evidence']
            if row['id'] != 'CN:hp_cn:sku:' + sku or evidence['product_number'] != sku:
                raise ValueError('HP configuration identity mismatch')
            if evidence['url'] != ('https://partsurfer.hpcloud.hp.com/bff/proxy/get?input='
                                   f'/Product/GetProduct/{sku}/country/US/usertype/EXT'):
                raise ValueError('HP configuration requires exact official provenance')
            params = row.setdefault('params', {})
            for key, value in supplement['params'].items():
                # Existing store facts remain authoritative; conflicts are kept
                # visible in the evidence rather than overwritten by a parts list.
                if not params.get(key) or (key == '运行内存' and re.fullmatch(r'\d+GBGB', str(params[key]))):
                    params[key] = value
            row['configuration_evidence'] = deepcopy(evidence)
            row['configuration_missing'] = deepcopy(supplement['configuration_missing'])
        result.append(row)
    return result
