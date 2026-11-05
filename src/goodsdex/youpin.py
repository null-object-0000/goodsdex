"""Reviewed Youpin crosswalk. Listing times never silently become announcements."""
from copy import deepcopy
import json
from pathlib import Path
import unicodedata

DEFAULT = Path(__file__).resolve().parents[2] / 'data/official/youpin-crosswalk.json'


def normalize_name(value):
    return ''.join(unicodedata.normalize('NFKC', value).casefold().split())


def apply_youpin(rows, manifest=None):
    manifest = json.loads(DEFAULT.read_text()) if manifest is None else manifest
    if manifest.get('schema') != 1:
        raise ValueError('Unsupported Youpin crosswalk')
    approved = {}
    for item in manifest['items']:
        key = item['id']
        if key in approved or not key.startswith('CN:mi_cn:product:'):
            raise ValueError('Invalid or duplicate Xiaomi product identity')
        if (item['mapping_method'] != 'unique_exact_name'
                or normalize_name(item['mi_name']) != normalize_name(item['youpin_name'])
                or item['brand_name'] not in ('小米自营产品', '小米', '米家')):
            raise ValueError('Unverified Youpin identity or brand relationship')
        if item['evidence']['url'] != f'https://www.xiaomiyoupin.com/detail?gid={item["gid"]}':
            raise ValueError('Youpin evidence does not identify the mapped gid')
        approved[key] = item
    result = deepcopy(rows)
    for row in result:
        entry = approved.get(row['id'])
        if not entry:
            continue
        # A later source rename/version change requires renewed identity review.
        if normalize_name(row['name']) != normalize_name(entry['mi_name']):
            continue
        row['youpin_gid'] = entry['gid']  # row.gid is a DIFFERENT Xiaomi Mall namespace.
        row['youpin_evidence'] = entry['evidence']
        row['youpin_category'] = entry['category']
        if row.get('category') == '旧款机型' and all(entry['category']):
            row['category_before_youpin'] = row['category']
            row['category'] = entry['category'][2]
            row['categories'] = entry['category']
            row['category_source'] = 'youpin'
        if not row.get('image') and not row.get('image_url') and entry.get('image'):
            row['image'] = row['image_url'] = entry['image']
            row['image_source'] = 'youpin'
            row['image_source_url'] = entry['evidence']['url']
        row['youpin_offers'] = entry['offers']
        row['youpin_listed'] = entry['listed']
        # Conservative bound: this exact product was listed by this date. This
        # does not determine the announcement day or assert it was for sale.
        bound = {'date': entry['listed']['date'], 'precision': 'day',
                 'source': 'youpin_listed', 'event': 'channel_listing',
                 'evidence': entry['evidence']}
        if not row.get('release_upper_bound') or row['release_upper_bound']['date'] > bound['date']:
            row['release_upper_bound'] = bound
    return result
