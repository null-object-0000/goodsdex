"""Car publication boundaries shared by daily and hourly jobs."""
from copy import deepcopy


def is_car(row):
    return row.get('product_type') == 'car' or str(row.get('id', '')).startswith(('CN:byd:car:', 'CN:xiaomi_ev:car:'))


def assert_cars_unchanged(before, after):
    counts = lambda rows: (sum(is_car(r) for r in rows), sum(r.get('product_type') == 'car' for r in rows))
    print(f'Hourly car counts before={counts(before)}, after={counts(after)}')
    if counts(before) != counts(after):
        raise ValueError('Hourly refresh changed car/type counts')
    old = {r['id']: r for r in before if is_car(r)}
    new = {r['id']: r for r in after if is_car(r)}
    if old != new:
        raise ValueError('Hourly refresh changed car objects')


def merge_cars(previous, cars, approved):
    if any(r.get('schema') == 'car-product-v2' for r in previous):
        from goodsdex.car_structure import migrate, expand_sources
        return migrate(merge_cars(expand_sources(previous), cars, approved))
    allowed = {r['id'] for r in approved}
    incoming = {r['id']: r for r in cars}
    if len(incoming) != len(cars) or incoming.keys() != allowed:
        raise ValueError('Car release must contain exactly the reviewed IDs')
    for row in cars:
        if not is_car(row) or row.get('brand') not in ('比亚迪', '小米汽车'):
            raise ValueError('Invalid car brand/identity')
        if row.get('price_kind') != 'msrp' or not isinstance(row.get('price'), (int, float)) or row['price'] <= 0 or not row.get('params'):
            raise ValueError('Unverified car price/specifications')
    result = [deepcopy(incoming.get(r['id'], r)) for r in previous]
    existing = {r['id'] for r in previous}
    result.extend(deepcopy(r) for r in cars if r['id'] not in existing)
    old_other = [r for r in previous if not is_car(r)]
    if old_other != [r for r in result if not is_car(r)]:
        raise ValueError('Car release changed other records')
    return result
