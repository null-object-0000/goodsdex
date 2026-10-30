"""Validated field supplements. Never replace a populated catalog value."""
from copy import deepcopy
from pathlib import Path
import json
import re
from datetime import datetime
from urllib.parse import urlsplit

DEFAULT = Path(__file__).resolve().parents[2] / 'data/supplements/verified-backfill-20261030.json'


def apply(rows, patches):
    rows = deepcopy(rows)
    audit = {'applied': [], 'skipped': [], 'unchanged': []}
    for patch in patches:
        for key in ('source', 'source_url', 'captured_at'):
            if not patch.get(key):
                raise ValueError('Backfill missing provenance: ' + key)
        fields = patch['fields']
        if 'historical_price' in fields:
            if fields.get('price_kind') != 'msrp_historical' or 'price' in fields:
                raise ValueError('Historical price cannot populate current price')
        if 'image' in fields and fields.get('image_scope') not in ('series', 'model'):
            raise ValueError('Image must retain reference scope')
        if 'image' in fields:
            if not re.fullmatch(r'https://spend-good\.oss-cn-shanghai\.aliyuncs\.com/goods/[a-f0-9]{40}\.(jpg|png)', fields['image']):
                raise ValueError('Image backfill requires owned OSS object')
            if (fields.get('image_source_url') != patch['source_url']
                    or fields.get('image_captured_at') != patch['captured_at']
                    or not fields.get('image_source') or not fields.get('image_note')):
                raise ValueError('Image backfill requires matching image provenance')
            if urlsplit(patch['source_url']).scheme not in ('http', 'https'):
                raise ValueError('Image source must be a page URL')
            datetime.fromisoformat(patch['captured_at'].replace('Z', '+00:00'))
        matches = [r for r in rows if r['id'] == patch['id']]
        if not matches:
            audit['skipped'].append(dict(id=patch['id'],reason='target_absent',field=patch['field']))
        for row in matches:
            primary = patch['field']
            if all(row.get(k) == v for k, v in fields.items()):
                audit['unchanged'].append(dict(id=row['id'],field=primary))
                continue
            if row.get(primary) not in (None, ''):
                audit['skipped'].append(dict(id=row['id'], reason='existing_value', field=primary))
                continue
            if primary == 'historical_price' and row.get('price') is not None:
                audit['skipped'].append(dict(id=row['id'], reason='existing_current_price', field=primary))
                continue
            # Metadata is equally protected: do not partially overwrite provenance.
            conflicts = [k for k, v in fields.items() if row.get(k) not in (None, '', v)
                         and not (k == 'price_kind' and primary == 'historical_price'
                                  and row.get('price') is None and row.get(k) in ('none', 'not_applicable'))]
            if conflicts:
                audit['skipped'].append(dict(id=row['id'], reason='field_conflict', field=primary))
                continue
            row.update(deepcopy(fields))
            audit['applied'].append(dict(id=row['id'], field=primary))
    return rows, audit


def apply_default(rows):
    audits = {'applied': [], 'skipped': [], 'unchanged': []}
    for path in sorted(DEFAULT.parent.glob('verified-backfill-*.json')):
        rows, audit = apply(rows, json.loads(path.read_text()))
        for key in audits:
            audits[key].extend(audit[key])
    return rows, audits


def validate_row(row):
    if row.get('catalog_identity') != 'verified_backfill_20261030':
        return
    for evidence in [row] + [t['source_record'] for t in row.get('trims', [])]:
        if not all(evidence.get(k) for k in ('source', 'source_url', 'captured_at')):
            raise ValueError('Verified supplement missing provenance: ' + row['id'])
    if row.get('schema') == 'car-product-v2':
        if row.get('model_year_source') != 'pcauto' or row.get('model_year_confidence') != 'third_party':
            raise ValueError('Missing historical model year provenance')
        if row.get('price') is not None or any(t.get('price') is not None for t in row['trims']):
            raise ValueError('Historical MSRP must not populate current price')
    elif not row.get('name_source'):
        raise ValueError('Missing name provenance')
