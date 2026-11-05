"""Replay verified official HP history by exact part number, never by fuzzy name."""
import json
import re
from copy import deepcopy
from pathlib import Path
from urllib.parse import urlparse
from .hp_configurations import apply_configurations

DEFAULT = Path(__file__).resolve().parents[2] / 'data/official/hp-history.json'


def literal_generation(text, url=''):
    match = re.search(r'(?<![A-Za-z0-9-])G[1-9]\d?(?:i|a|ah|ak)?(?![A-Za-z0-9])', text, re.I)
    if match:
        return 'G' + match[0][1:]
    # Official series slugs retain G7 even in translated titles with no space
    # between the token and Chinese characters. Never parse CPU/submodel codes.
    match = re.search(r'(?:^|-)g([1-9]\d?)((?:i|a|ah|ak)?)(?:-|$)', urlparse(url).path, re.I)
    return 'G' + match[1] + match[2].lower() if match else None


def official_url(url):
    p = urlparse(url or '')
    return p.scheme == 'https' and (p.hostname == 'hp.com' or
           (p.hostname or '').endswith('.hp.com') or
           p.hostname in ('www.hpstore.cn', 'media.hpstore.cn', 'hp.widen.net',
                          'ssl-product-images.www8-hp.com'))


def validate(row):
    if row.get('brand') != '惠普' or row.get('source') != 'hp_cn':
        raise ValueError('HP history brand/source mismatch')
    if not all(row.get(k) for k in ('id', 'name', 'series', 'category', 'source_url')):
        raise ValueError('HP history lacks identity or provenance')
    if not official_url(row['source_url']):
        raise ValueError('HP history must use an official source')
    sku = row.get('part_number')
    if sku:
        if not re.fullmatch(r'[A-Z0-9]{5}(?:PC|PA)', sku) or row['id'] != 'CN:hp_cn:sku:' + sku:
            raise ValueError('HP part-number identity mismatch')
        if row.get('record_level') != 'configuration' or not row.get('support_evidence'):
            raise ValueError('SKU history lacks support evidence')
    elif not row.get('part_number_missing') or row.get('record_level') != 'model_family':
        raise ValueError('Missing HP part number needs an explicit family-level reason')
    if not row.get('generation') and not row.get('generation_missing'):
        raise ValueError('Missing generation needs a reason')
    if row.get('image'):
        if not official_url(row['image']) or 'fallback_product' in row['image']:
            raise ValueError('Not an official product image')
    elif not row.get('image_missing'):
        raise ValueError('Missing HP image needs a reason')
    if row.get('status') == 'retired' and not (row.get('retired_at') and row.get('retirement_evidence')):
        raise ValueError('Retirement requires dated evidence')


def apply_history(rows, path=DEFAULT):
    if not Path(path).exists():
        return rows
    bundle = json.loads(Path(path).read_text())
    if bundle.get('schema') != 1:
        raise ValueError('Unknown HP history evidence schema')
    history = bundle['rows']
    seen = set()
    for row in history:
        validate(row)
        if row['id'] in seen:
            raise ValueError('Duplicate historical HP identity')
        seen.add(row['id'])
    # Live store observations own existing SKUs. Only fill absent history fields;
    # replaying a frozen support observation must never erase newer store facts.
    by_id = {r['id']: r for r in history}
    result = []
    for original in rows:
        row = deepcopy(original)
        prior = by_id.pop(row['id'], None)
        if prior:
            for key in ('series', 'generation', 'generation_missing', 'part_number_missing',
                        'image_missing', 'support_evidence'):
                if not row.get(key) and prior.get(key):
                    row[key] = deepcopy(prior[key])
        result.append(row)
    result.extend(deepcopy(list(by_id.values())))
    return apply_configurations(result)


def enrich_store_fields(row):
    """Only literal series/generation tokens from the existing official title."""
    row = deepcopy(row)
    # The generated display name can contain CPU generation wording. Prefer
    # the official product title so a CPU generation cannot become a model one.
    text = str(row.get('source_name') or row.get('model') or row.get('name') or '')
    if not row.get('series'):
        match = re.search(r'战66\+?|战\s*99|战X|星Book|星\s*Desk|星Studio|星[0-9]+(?:\s*Pro)?|锐[0-9]+|光影精灵|暗影精灵|EliteBook|ProBook|ZBook|Dragonfly|OmniBook|OmniStudio|EliteDesk|ProDesk|ProOne|EliteOne|Pavilion|ENVY|Spectre|Pro', text, re.I)
        row['series'] = re.sub(r'\s+', '', match[0]) if match else '其他惠普电脑'
    if not row.get('generation'):
        generation = literal_generation(text, row.get('source_url', ''))
        match = re.search(r'([一二三四五六七八九十]+代|(?:暗影精灵|光影精灵)\s*\d+(?!\d|\s*(?:英寸|inch|["”]|L\b)))', text, re.I)
        if generation or match:
            row['generation'] = match[0] if match else generation
        else:
            row['generation'] = None
            row['generation_missing'] = 'official_title_has_no_explicit_generation'
    if not row.get('part_number'):
        row.setdefault('part_number_missing', 'official_source_has_no_single_orderable_part_number')
    if not row.get('image'):
        row.setdefault('image_missing', 'official_image_not_observed_or_not_validated')
    if not row.get('status'):
        row['status'] = 'available' if row.get('sale_status') != 'delisted' else 'retired'
    return row
