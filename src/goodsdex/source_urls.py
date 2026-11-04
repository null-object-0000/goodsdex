"""Replay reviewed official-page URL evidence without changing existing provenance."""
from copy import deepcopy
import json
from pathlib import Path
import re

DEFAULT = Path(__file__).resolve().parents[2] / 'data/official/source-url-backfill.json'
MI = 'https://www.mi.com/shop/buy/detail?product_id='


def mi_url(key):
    match = re.fullmatch(r'CN:mi_cn:product:([0-9]+)', key)
    return MI + match[1] if match else None


def apply_source_urls(rows, manifest=None):
    if manifest is None:
        manifest = json.loads(DEFAULT.read_text())
    if manifest['schema'] != 1:
        raise ValueError('Unsupported source URL evidence')
    samples = manifest['samples']
    if len(samples) != 20 or len({s['id'] for s in samples}) != 20:
        raise ValueError('Source URL gate requires 20 distinct sampled products')
    def valid(s):
        return (s['passed'] and s['status'] == 200 and s['url'] == mi_url(s['id'])
                and s['final_url'] == s['url'] and (s['score'] >= .6 or s.get('model_hit')))
    passed = {s['id'] for s in samples if valid(s)}
    eligible = len(passed) / len(samples) >= .8
    rejected = {s['id'] for s in samples if s['id'] not in passed}
    approved = {}
    for entry in manifest['approved']:
        key = entry['id']
        if key in rejected or (not eligible and key not in passed):
            raise ValueError('Unverified URL below sample gate or failed sample: ' + key)
        if entry['url'] != mi_url(key):
            raise ValueError('Only the reviewed official Xiaomi rule is allowed')
        if key in approved:
            raise ValueError('Duplicate source URL approval')
        approved[key] = entry
    result = deepcopy(rows)
    for row in result:
        evidence = approved.get(row['id'])
        # Scope is frozen to reviewed identities/names; future records cannot inherit this audit.
        if not row.get('source_url') and evidence and row.get('name') == evidence['name']:
            row['source_url'] = evidence['url']
    return result


def coverage(rows):
    brands = {}
    for row in rows:
        brand = row.get('brand') or ('小米' if row['id'].startswith('CN:mi_cn:') else '未知')
        count = brands.setdefault(brand, dict(total=0, with_source_url=0, missing=0))
        count['total'] += 1
        count['with_source_url'] += bool(row.get('source_url'))
        count['missing'] += not bool(row.get('source_url'))
    for count in brands.values():
        count['ratio'] = count['with_source_url'] / count['total']
    return dict(total=len(rows), with_source_url=sum(bool(r.get('source_url')) for r in rows), by_brand=brands)
