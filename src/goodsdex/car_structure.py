"""Reviewed automotive product grouping. Source captures remain immutable evidence."""
from copy import deepcopy
import re
from goodsdex.cars import is_car

# Source product IDs are stable generation boundaries, never inferred launch years.
BYD = {
    '10030': ('海豚', None, 'EV', '智驾版', None),
    '130': ('汉', None, 'DM-i', '智驾版', None),
    '131': ('汉', None, 'EV', '智驾版', None),
    '151': ('夏', 2026, 'DM-i', None, None),
    '154': ('宋Pro', None, 'DM-i', '飞驰版', None),
    '159': ('元PLUS', None, 'EV', None, '第三代'),
    '165': ('秦PLUS', None, 'DM-i', None, '第三代'),
}


def migrate(rows):
    """Idempotent; retain every trim and every non-car object without modification."""
    products, output = {}, []
    for original in rows:
        if original.get('schema') == 'car-product-v2':
            expected = migrate([t['source_record'] for t in original['trims']])
            if len(expected) != 1 or expected[0] != original:
                raise ValueError('Canonical car product differs from source evidence')
        if not is_car(original) or original.get('trims') is not None:
            output.append(deepcopy(original))
            continue
        row = deepcopy(original)
        historical = row.get('model_year') == 2022 and ':han-dmi:2022:' in row['id']
        if row['brand'] == '比亚迪':
            source_id = row['id'].split(':goods-')[1].split(':')[0] if ':goods-' in row['id'] else None
            if historical:
                series, year, power, edition, generation = '汉', 2022, 'DM-i', None, None
                identity = 'han:2022:dmi'
            else:
                if source_id not in BYD:
                    raise ValueError('Unreviewed car identity: ' + row['id'])
                series, year, power, edition, generation = BYD[source_id]
                identity = f'goods-{source_id}:{year or "current"}:{power.lower().replace("-", "")}'
            prefix = 'CN:byd:car:'
        elif row['brand'] == '小米汽车':
            series, year, power, edition, generation = row['series'], None, 'EV', None, None
            source_id = row['id'].split(':item-')[1].split(':')[0]
            identity, prefix = f'item-{source_id}:current:ev', 'CN:xiaomi_ev:car:'
        else:
            raise ValueError('Unreviewed car brand')
        pid = prefix + identity
        official_name = '新一代 SU7' if row['brand'] == '小米汽车' and series == 'SU7' else row['series']
        name = ('小米汽车 ' + official_name if row['brand'] == '小米汽车' else
                ' '.join(filter(None, [row['brand'], generation, series, f'{year}款' if year else None, power, edition])))
        if pid not in products:
            product = {k: row[k] for k in ('brand', 'kind', 'category', 'product_type', 'sale_status', 'source_url') if k in row}
            product.update(id=pid, product_id=pid, schema='car-product-v2', record_level='car_product',
                           series=series, model_year=year, powertrain=power, edition=edition, generation=generation,
                           official_name=official_name, name=name, display_name=name,
                           model_year_source='pcauto' if historical else 'official_name' if year else 'official_absent',
                           model_year_confidence='third_party' if historical else 'official' if year else None,
                           model_year_source_url=row['source_url'] if year else None,
                           image=None if historical else row.get('image'),
                           image_status='official_unavailable' if historical else 'available' if row.get('image') else 'missing',
                           image_scope=None if historical or not row.get('image') else 'series' if row['brand'] == '小米汽车' else 'trim',
                           trims=[], legacy_ids=[])
            if historical:
                product['image_evidence'] = 'docs/汽车年款与图源-20261030.md#23-汉-dm-i-2022-款官方整车图拿不到'
            products[pid] = product
            output.append(product)
        product = products[pid]
        trim_name = ' '.join(filter(None, [row.get('range_tier'), row['trim']])) if historical else re.sub(r'(?i)(\d+)KM\s*', r'\1KM ', row['trim'])
        if re.search(r'DM-[ip]|\bEV\b', trim_name):
            raise ValueError('Powertrain must not be a trim')
        trim = dict(id=row['id'], name=trim_name, price=row['price'], price_kind=row['price_kind'],
                    params=deepcopy(row.get('params', {})), image=None if historical else row.get('image'),
                    image_status=product['image_status'], image_scope=product['image_scope'],
                    source_record=row)
        distance = re.search(r'(\d+)KM', trim_name, re.I)
        if distance:
            trim['range_km'] = int(distance[1])
        if historical:
            trim['range_std'] = 'NEDC'
        product['trims'].append(trim)
        product['legacy_ids'].append(row['id'])
    for product in products.values():
        prices = [t['price'] for t in product['trims'] if t['price'] is not None]
        product['price'] = min(prices) if prices else None
        product['price_kind'] = 'from' if prices else 'none'
    return output


def expand_sources(rows):
    """Recover byte-equivalent source objects for existing audited refreshers."""
    return [deepcopy(source) for row in rows for source in
            ([t['source_record'] for t in row['trims']] if row.get('schema') == 'car-product-v2' else [row])]


def mappings(rows):
    return [dict(old_id=t['id'], new_id=r['id'], trim_id=t['id'])
            for r in rows if r.get('schema') == 'car-product-v2' for t in r['trims']]


def assert_preserved(before, after):
    """No source identity or object may disappear in grouping."""
    if expand_sources(before) != expand_sources(after):
        # Grouping changes source order only within the car subset.
        other = lambda rows: [r for r in rows if not is_car(r)]
        cars = lambda rows: {r['id']: r for r in expand_sources(rows) if is_car(r)}
        if other(before) != other(after) or cars(before) != cars(after):
            raise ValueError('Car migration lost or changed source records')
