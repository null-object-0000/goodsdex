from copy import deepcopy

import pytest

from goodsdex.xiaomi_covers import apply_covers, BAIKE_SOURCE


@pytest.mark.parametrize('key', ['mihome:13363', 'youpin:13363', 'CN:mi_cn:product:42'])
def test_verified_baike_image_replays_exact_model_across_namespaces(key):
    row = dict(id=key, miio_model='xiaomi.vacuum.c102cn', image=None,
               image_missing=True, image_mihome={'url': 'device-icon'},
               params={'型号': 'unchanged'}, release={'date': '2025-01'})
    before = deepcopy(row)
    evidence = {row['miio_model']: dict(model=row['miio_model'],
                image='https://example.org/480.png', width=480, height=480)}
    after = apply_covers([row], {}, evidence, {})
    assert row == before
    assert after[0]['image'] == evidence[row['miio_model']]['image']
    assert after[0]['image_source'] == BAIKE_SOURCE
    assert after[0]['image_mihome'] == row['image_mihome']
    assert {k:v for k,v in after[0].items() if not k.startswith('image')} == {
        k:v for k,v in row.items() if not k.startswith('image')}
    assert apply_covers(after, {}, evidence, {}) == after
    mismatch = {row['miio_model']: dict(evidence[row['miio_model']], model='other.model.v1')}
    assert apply_covers([row], {}, mismatch, {}) == [row]


@pytest.mark.parametrize('size', [(168,168), (480,168), (399,480), (None,None)])
def test_unverified_baike_image_retains_mihome_original(size):
    row = dict(id='mihome:13363', miio_model='xiaomi.vacuum.c102cn', image='original')
    entry = dict(model=row['miio_model'], image='https://example.org/small.png')
    if size[0] is not None:
        entry.update(width=size[0], height=size[1])
    assert apply_covers([row], {}, {row['miio_model']: entry}, {}) == [row]
