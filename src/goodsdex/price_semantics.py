"""Separate whole-offer amounts from partial payments; keep original source facts."""
from collections import Counter
from copy import deepcopy
import math
import re
from statistics import median

KINDS = {'full', 'deposit', 'upgrade_diff', 'bundle_extra', 'unknown'}
PARTIAL = {'deposit', 'upgrade_diff', 'bundle_extra', 'unknown'}
# Pre-sale delivery times, included extras and ordinary upgrade models are not fees.
KEYWORDS = ((r'补差(?:价)?|差价', 'upgrade_diff'),
            (r'定金|订金', 'deposit'), (r'加购(?:价|款|链接|专享)|加价购', 'bundle_extra'))


def amount(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value > 0


def name_kind(row):
    text = str(row.get('name') or '')
    text = re.sub(r'(?:无需|免|非|不收|无需支付)(?:定金|订金)|(?:赠|含|送)加购', '', text)
    for pattern, kind in KEYWORDS:
        m = re.search(pattern, text)
        if m:
            return kind, m.group()
    if '仅升级' in text:
        return 'unknown', '仅升级'
    return None, None


def normalize(row):
    row = deepcopy(row)
    old = row.get('price_kind')
    if old not in KINDS:
        row['price_basis_kind'] = old  # Preserve former SKU/MSRP/starting semantics.
    kind, matched = name_kind(row)
    if old in PARTIAL:
        kind = old
    if not kind:
        kind = 'unknown' if old in ('none', 'not_applicable', 'msrp_historical') or not amount(row.get('price')) else 'full'
    # Reviewed selectable 28cm option: the same size label means upgraded model only.
    # Match amount too: a changed source amount requires renewed review.
    if (row.get('id') == 'CN:atour:spu:1984:sku:0105100044-2.0-JD28'
            and row.get('price') == 3079 and row.get('official_sku_status') == 1):
        kind, matched = 'full', None
        row['price_kind_evidence'] = dict(basis='official_h5_selectable_exact_sku',
            evidence='docs/price-kind-20261105/evidence/sku-0105100044-2.0-JD28.txt',
            note='同页28cm升级款200×200cm为整件规格；仅升级款不等于补差')
    row['price_kind'] = kind
    if matched:
        row['price_kind_evidence'] = dict(basis='official_name_literal', matched_text=matched,
            source_url=row.get('source_url'),
            note='仅升级语义不明；未获整件报价佐证，未证实补差或定金' if matched == '仅升级' else '名称中的部分支付语义')
    if row.get('id') == 'CN:atour:spu:1984:sku:0899000039-C2C-b':
        row['price_kind_evidence'] = dict(basis='official_h5_disabled_option_and_panel',
            source_url=row.get('source_url'),
            evidence='docs/price-kind-20261105/evidence/sku-0899000039-C2C-b.txt',
            note='22cm×200×200规格不可选；面板10元，页面未显示该SKU可成交价；不能确认补差或定金')
    if kind != 'full':
        if row.get('price') is not None:
            row['source_price'] = row['price']
        if row.get('promo_price') is not None:
            row['source_promo_price'] = row['promo_price']
        row['price'] = None
        if 'promo_price' in row:
            row['promo_price'] = None
    row['price_missing'] = not amount(row.get('price'))
    row['price_comparable'] = comparable(row)
    if 'trims' in row:
        row['trims'] = [normalize(t) for t in row['trims']]
        prices = [t['price'] for t in row['trims'] if comparable(t)]
        row['price'] = min(prices) if prices else None
        row['price_kind'] = 'full' if prices else 'unknown'
        row['price_missing'] = not prices
        row['price_comparable'] = comparable(row)
    return row


def comparable(row):
    return (row.get('price_kind') == 'full' and amount(row.get('price'))
            and row.get('price_status') not in ('stale', 'unavailable_option')
            and row.get('sale_status') not in ('delisted', 'unavailable', 'unavailable_option')
            and row.get('status') != 'retired')


def apply(rows):
    return [normalize(r) for r in rows]


def validate(rows):
    for row in rows:
        if row.get('price_kind') not in KINDS:
            raise ValueError('Missing/invalid price_kind: '+str(row.get('id')))
        if row['price_kind'] != 'full' and row.get('price') is not None:
            raise ValueError('Partial amount in public price: '+str(row.get('id')))
        if row.get('price_comparable') != comparable(row):
            raise ValueError('Incorrect comparison eligibility: '+str(row.get('id')))


def coverage(rows):
    validate(rows)
    return dict(price_kind=dict(sorted(Counter(r['price_kind'] for r in rows).items())),
                price_comparable_count=sum(comparable(r) for r in rows),
                price_missing_count=sum(r['price_missing'] for r in rows))


def candidates(rows):
    """Review queue, not automatic classification from statistical anomalies."""
    pools = {}
    for r in rows:
        if amount(r.get('price')):
            pools.setdefault(r.get('category') or '未分类', []).append(r['price'])
    output = []
    for r in rows:
        kind, matched = name_kind(r)
        reviewed = r.get('id') == 'CN:atour:spu:1984:sku:0105100044-2.0-JD28' and r.get('price') == 3079
        if reviewed:
            kind = 'full'
        p = r.get('price')
        category = r.get('category') or '未分类'
        sample = pools.get(category, [])
        mid = median(sample) if sample else None
        low = amount(p) and mid is not None and p < mid * .1
        # Broad text scan includes ordinary 加购 as requested; review prevents false positives.
        broad = re.findall(r'定金|订金|补差|差价|加购|仅升级', str(r.get('name') or ''))
        if not (broad or low):
            continue
        output.append(dict(id=r['id'], sku_no=r.get('sku_no'), name=r['name'], price=p,
            category=category, category_median=mid, category_sample_count=len(sample),
            ratio=round(p/mid, 6) if amount(p) and mid else None,
            reasons=([f'name:{s}' for s in broad] + (['price_below_category_median_10pct'] if low else [])),
            suggested_price_kind=kind or 'unknown',
            suggestion='已核官方整件规格，full；仅升级为型号限制' if reviewed else '核验官方部分支付规则' if kind else '待核页面；低价、配件、容量、组合数量可造成正常价差，不自动改价'))
    return sorted(output, key=lambda r: (not any(x.startswith('name:') for x in r['reasons']), r['id']))
