"""Reviewed CN Earbuds model intake. No channel prices or dates are invented."""
from copy import deepcopy
import json
from pathlib import Path
from .product_sources import materialize, validate_source
from .price_semantics import comparable

DEFAULT = Path(__file__).resolve().parents[2] / 'data/official/earbuds-intake.json'


def apply_intake(rows, manifest=None):
    if manifest is None:
        manifest = json.loads(DEFAULT.read_text()) if DEFAULT.exists() else {'schema': 1, 'items': []}
    if manifest.get('schema') != 1:
        raise ValueError('Unsupported Earbuds intake')
    result = list(rows)
    known = {r['id'] for r in rows}
    seen = set()
    for original in manifest['items']:
        r = deepcopy(original)
        key = r['id']
        if key in seen or key != r.get('model') or not key.startswith('miwear.headphone.'):
            raise ValueError('Invalid or duplicate Earbuds model identity')
        seen.add(key)
        if r.get('region') != 'CN' or r.get('source') != 'earbuds_directory' or r.get('discovered_by') != 'earbuds_directory':
            raise ValueError('CN directory identity required')
        directory = [s for s in r['sources'] if s['source'] == 'earbuds_directory']
        if len(directory) != 1 or directory[0]['fields'].get('model') != key:
            raise ValueError('Missing exact directory model evidence')
        for s in r['sources']:
            validate_source(s)
        if r.get('price') is not None or r.get('price_missing') != 'no_channel_price' or comparable(r):
            raise ValueError('Model reference cannot supply a comparable channel offer')
        if any(r.get(k) for k in ('release', 'release_date', 'release_series', 'release_llm')):
            raise ValueError('Directory supplies no launch date')
        if key in known:
            continue
        r = materialize(r, at=r['intake_at'])
        if not r.get('name') or not r.get('image') or r['primary_source'] != 'earbuds_directory':
            raise ValueError('Incomplete directory display')
        result.append(r)
        known.add(key)
    return result
