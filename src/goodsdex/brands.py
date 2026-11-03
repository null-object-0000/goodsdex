"""Reproducible brand attribution. Namespaces outrank source and product names.

Aliases are exact (case-insensitive); a marketplace/source URL is not a brand.
Unknowns stay empty, with no invented attribution source, and enter review.
"""
from collections import Counter
from copy import deepcopy
import re

BRAND_ALIASES = {
    '小米': ('小米', '米家', '红米', 'xiaomi', 'mijia', 'redmi', 'mi_cn',
             'xiaomi_archive_history', 'goods_supplements:xiaomi_mobile_official'),
    '小米汽车': ('小米汽车', 'xiaomi ev', 'xiaomi_ev', 'mi_ev'),
    'Apple': ('Apple', '苹果', 'apple_cn', 'apple_support'),
    '大疆': ('大疆', 'DJI', 'dji_mall_json'),
    '惠普': ('惠普', 'HP', 'hp_cn', '.hp_cn'),
    '富士': ('富士', 'FUJIFILM', 'FUJINON', 'fuji'),
    '比亚迪': ('比亚迪', 'BYD'),
    '戴尔': ('戴尔', 'Dell'),
    '华硕': ('华硕', 'ASUS'),
    '联想': ('联想', 'Lenovo'),
}
ALIASES = {alias.casefold(): brand for brand, aliases in BRAND_ALIASES.items() for alias in aliases}
# The trailing namespace separator prevents e.g. CN:mi_cn_fake from matching.
ID_RULES = (
    (r'^cn:(?:mi_ev|xiaomi_ev|小米汽车):', '小米汽车'),
    (r'^cn:mi_cn:', '小米'),
    (r'^(?:cn:apple[^:]*:|global:apple_support:)', 'Apple'),
    (r'^cn:dji[^:]*:', '大疆'),
    (r'^cn:(?:hp[^:]*|\.hp_cn):', '惠普'),
    (r'^cn:fuji[^:]*:', '富士'),
    (r'^cn:byd[^:]*:', '比亚迪'),
)
# Anchored manufacturer names only: no inference from specs/compatibility text.
NAME_RULES = (
    (r'^(?:小米汽车|Xiaomi\s+EV\b)', '小米汽车'),
    (r'^(?:小米|米家|红米|Redmi\b|RedmiBook\b|Xiaomi\b)', '小米'),
    (r'^(?:戴尔|Dell\b)', '戴尔'),
    (r'^(?:华硕|ASUS\b)', '华硕'),
    (r'^(?:联想|Lenovo\b)', '联想'),
)
# Exact IDs with separately reviewed evidence may be added here. Never use a
# default brand or a generic "unknown" entry to lower the unknown percentage.
MANUAL_OVERRIDES = {}


def canonical(value):
    return ALIASES.get(value.strip().casefold()) if isinstance(value, str) else None


def infer_brand(row):
    key = str(row.get('id') or '')
    for pattern, brand in ID_RULES:
        if re.search(pattern, key, re.I):
            return brand, 'id_prefix'
    source = row.get('source')
    # Some collectors carry the manufacturer explicitly inside source.
    if isinstance(source, dict):
        source = source.get('brand')
    if brand := canonical(source):
        return brand, 'source'
    for pattern, brand in NAME_RULES:
        if re.search(pattern, str(row.get('name') or '').strip(), re.I):
            return brand, 'name'
    if key in MANUAL_OVERRIDES:
        return MANUAL_OVERRIDES[key], 'manual'
    # A pre-existing, recognized explicit brand is evidence, not a name guess.
    if brand := canonical(row.get('brand')):
        provenance = row.get('brand_source')
        return brand, provenance if provenance in ('id_prefix', 'source', 'name', 'manual') else 'manual'
    return None, None


def normalize_brands(rows):
    output = deepcopy(rows)
    for row in output:
        row['brand'], row['brand_source'] = infer_brand(row)
    return output


def distribution(rows):
    return dict(sorted(Counter(r.get('brand') or '未知' for r in rows).items()))


def audit_brands(before, after):
    unknown = [dict(id=r['id'], name=r.get('name'), source=r.get('source'),
                    reason='No recognized ID namespace, source, manufacturer name or reviewed brand')
               for r in after if not r.get('brand')]
    prefixes = Counter(':'.join(r['id'].split(':')[:2]) for r in unknown)
    return dict(before=distribution(before), after=distribution(after),
                unknown_ratio=len(unknown) / len(after) if after else 0,
                unknown_prefix_top10=prefixes.most_common(10), manual_review=unknown)
