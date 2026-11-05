"""Evidence-scoped repairs for archived Xiaomi notebooks, replayed on every release."""
from copy import deepcopy
import json
from pathlib import Path
from urllib.parse import urlsplit

DEFAULT = Path(__file__).resolve().parents[2] / 'data/official/mi-legacy-names.json'


def apply_legacy_names(rows, manifest=None):
    manifest = json.loads(DEFAULT.read_text()) if manifest is None else manifest
    if manifest.get('schema') != 1:
        raise ValueError('Unsupported legacy name evidence')
    approved = {}
    for item in manifest['items']:
        key = item['id']
        if key in approved or not key.startswith('CN:mi_cn:product:'):
            raise ValueError('Invalid legacy identity')
        for evidence in [*item['name_evidence'], item['historical_price_evidence'], item['retirement_evidence']]:
            host = urlsplit(evidence['source_url']).hostname or ''
            if (not (host == 'mi.com' or host.endswith('.mi.com'))
                    or not evidence['quote'] or len(evidence['sha256']) != 64):
                raise ValueError('Invalid official legacy evidence')
        # A matching product ID in the official campaign is required. A family
        # parameter page on its own must never rename an arbitrary similar SKU.
        pid = key.rsplit(':', 1)[-1]
        if not any(e.get('selector') == f'.item [data-stat-productid="{pid}"]'
                   for e in item['name_evidence']):
            raise ValueError('Missing product-scoped official name evidence')
        if item['retirement_evidence'].get('business_code') != 400480502:
            raise ValueError('Missing official retirement evidence')
        approved[key] = item
    result = deepcopy(rows)
    for row in result:
        entry = approved.get(row['id'])
        if not entry:
            continue
        if row.get('brand') not in (None, '小米') or row.get('record_level') != 'model_reference':
            raise ValueError('Legacy repair identity scope changed: ' + row['id'])
        # Never turn a new observed offer back into a retired reference record.
        if row.get('status') == 'available' or row.get('discontinued') is False or row.get('price') is not None:
            continue
        row.setdefault('name_before_legacy_repair', row.get('name'))
        row.update(name=entry['name'], brand='小米', source_url=entry['source_url'],
                   name_source=dict(kind='official_legacy_composite', evidence=entry['name_evidence']),
                   is_historical=True, status='retired', price=None, price_missing=True,
                   historical_price=entry['historical_price'], price_kind='historical_campaign',
                   historical_price_evidence=entry['historical_price_evidence'],
                   historical_price_note='官方旧活动页历史标价，非现价；未核实活动生效日期',
                   retirement_evidence=entry['retirement_evidence'],
                   name_resolution=entry['resolution'],
                   unrestored_fields=entry['unrestored_fields'])
        if not row.get('release'):
            row['release_missing_reason'] = entry['release_missing_reason']
    return result
