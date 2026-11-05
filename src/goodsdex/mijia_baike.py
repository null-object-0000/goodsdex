"""Scoped Mi Home metadata repairs. No directory/document timestamp is a release."""
from copy import deepcopy
import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import urlsplit, parse_qs

DEFAULT = Path(__file__).resolve().parents[2] / 'data/official/mijia-baike.json'


def norm(value):
    # Keep capacities, punctuation, generations and suffixes: never fuzzy-match.
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', value).casefold())


def hardware_models(text):
    """Only model-labelled text on page one; certification IDs are excluded."""
    out = set()
    lines = text.splitlines()
    token_pattern = r'[A-Z][A-Z0-9]*(?:[-_/][A-Z0-9]+)*'
    for i, line in enumerate(lines):
        # Covers manuals whose cover lists only the physical model numbers.
        standalone = re.fullmatch(r'\s*' + token_pattern + r'(?:[\s、，,]+' + token_pattern + r')*\s*', line)
        if standalone:
            for token in re.findall(token_pattern, line):
                if (4 <= len(token) <= 24 and re.search(r'[0-9]', token)
                        and len(re.findall('[A-Z]', token)) >= 2
                        and not token.startswith(('GB', 'IEC', 'ISO', 'CMIIT', 'IPX', 'USB', 'WIFI'))):
                    out.add(token)
        if not re.search(r'(?:产品)?型号\s*[:：]?', line) or any(k in line for k in ('核准', '认证', '无线电')):
            continue
        tail = re.split(r'型号\s*[:：]?', line, maxsplit=1)[-1]
        if not tail.strip() and i + 1 < len(lines):
            tail = lines[i + 1]
        for token in re.findall(r'(?<![A-Za-z0-9])[A-Z][A-Z0-9]*(?:[-_/][A-Z0-9]+)*(?![A-Za-z0-9])', tail):
            if len(token) >= 4 and re.search(r'[0-9]', token):
                out.add(token)
    return sorted(out)


def apply_baike(rows, manifest=None):
    if manifest is None:
        manifest = json.loads(DEFAULT.read_text()) if DEFAULT.exists() else {'schema': 1, 'items': []}
    if manifest.get('schema') != 1:
        raise ValueError('Unsupported baike evidence')
    entries = {}
    for entry in manifest['items']:
        key = entry['id']
        if (key in entries or not key.startswith('CN:mi_cn:product:')
                or not re.fullmatch(r'[a-z0-9_]+(?:\.[a-z0-9_]+){2}', entry['model'])
                or not entry['productName'] or len(entry['product_sha256']) != 64
                or entry['product_url'] != 'https://home.mi.com/cgi-op/api/v1/baike/v2/product?model=' + entry['model']
                or entry['mapping_method'] not in ('apk_exact_name', 'baike_official_shop_link')):
            raise ValueError('Invalid baike identity/evidence')
        proof = entry['mapping_evidence']
        if entry['mapping_method'] == 'apk_exact_name':
            if norm(proof['name']) != norm(entry['expected_name']) or proof['model'] != entry['model']:
                raise ValueError('Non-exact catalog mapping')
        else:
            url = urlsplit(proof['shop_url'])
            query = parse_qs(url.query)
            pid = (query.get('product_id') or query.get('commodityId') or [''])[0]
            if url.hostname not in ('m.mi.com', 'www.mi.com') or key != 'CN:mi_cn:product:' + pid:
                raise ValueError('Missing official product ID bridge')
        entries[key] = entry
    result = deepcopy(rows)
    for row in result:
        entry = entries.get(row['id'])
        if not entry or row.get('is_container'):
            continue
        # A changed SKU/name needs a fresh audit; replay is idempotent.
        if row.get('name') not in (entry['expected_name'], entry['productName']):
            continue
        row['mijia_baike'] = {k: entry[k] for k in (
            'model', 'productName', 'product_url', 'product_sha256', 'mapping_method',
            'manual_url', 'manual_type', 'manual_sha256', 'manual_status', 'attribute_status', 'hardware_models',
            'parameter_count', 'parameters', 'category_clue', 'materialPictures', 'image_missing')}
        if entry['mapping_method'] == 'apk_exact_name' or norm(entry['expected_name']) == norm(entry['productName']):
            row['miio_model'] = entry['model']
        # A shared shop link can cover several sizes/colours. Require an exact
        # physical model in the existing row before changing its display name.
        physical = entry.get('name_repair_hardware_model')
        params = row.get('params') or {}
        physical_match = physical and physical in entry['hardware_models'] and any(
            norm(str(params.get(k, ''))) == norm(physical) for k in ('产品型号', '设备型号', '型号'))
        if (physical_match and norm(entry['productName']).startswith(norm(row['name']))
                and len(norm(entry['productName'])) > len(norm(row['name']))):
            row.setdefault('name_before_baike_repair', row['name'])
            row['name'] = entry['productName']
            row['name_source'] = {'kind': 'official_mijia_baike', 'url': entry['product_url'],
                                  'sha256': entry['product_sha256']}
        if not row.get('image') and entry.get('verified_image'):
            image = entry['verified_image']
            if urlsplit(image['url']).scheme != 'https' or len(image['sha256']) != 64:
                raise ValueError('Invalid baike image')
            row.update(image=image['url'], image_missing=False, image_source='mijia_baike',
                       image_source_type='official', image_source_url=entry['product_url'])
    return result
