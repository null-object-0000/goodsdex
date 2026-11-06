from copy import deepcopy

from goodsdex.xiaomi_covers import apply_covers, apply_pdicons, PDICON_BASE


def test_pdicon_all_namespaces_exact_model_and_image_only():
    rows = [dict(id=key, miio_model='xiaomi.vacuum.c102cn', image='old',
                 image_width=168, image_note='old poster', image_mihome={'url':'device'},
                 params={'型号':'unchanged'}, release={'date':'2020-01'}, price=12)
            for key in ('mihome:13363', 'CN:mi_cn:product:42', 'youpin:42')]
    rows += [dict(id='unmapped', miio_model='other.model.v1', image='original'),
             dict(id='no_model', image='original')]
    before = deepcopy(rows)
    mapping = {'xiaomi.vacuum.c102cn': dict(pd_id=13363, usable=True, width=480, height=480)}
    after = apply_pdicons(rows, mapping)
    assert rows == before
    assert after[3:] == before[3:]
    for b, a in zip(before[:3], after[:3]):
        assert a['image'] == PDICON_BASE + '13363.png'
        assert a['image_source'] == 'mijia_pdicon'
        assert a['image_width'] == 480 and a['image_height'] == 480
        assert a['image_mihome'] == b['image_mihome']
        assert 'image_note' not in a
        assert {k:v for k,v in a.items() if not k.startswith('image')} == {k:v for k,v in b.items() if not k.startswith('image')}
    assert apply_pdicons(after, mapping) == after


def test_baike_remains_preferred_over_mtop_and_pdicon():
    row = dict(id='CN:mi_cn:product:42', miio_model='test.vacuum.v1',
               image='https://example.com/baike.png', image_source='mijia_baike_realIcon')
    mapping = {row['miio_model']: dict(pd_id=13363, usable=True)}
    assert apply_covers([row], {row['id']:dict(image='https://example.com/store.png')}, {}, mapping) == [row]
    original = dict(row, image='original', image_source='store')
    evidence = {row['miio_model']: dict(model=row['miio_model'], image=row['image'])}
    after = apply_covers([original], {}, evidence, mapping)
    assert after[0]['image'] == row['image'] and after[0]['image_source'] == row['image_source']


def test_failed_validation_or_invalid_id_retains_all_original_fields():
    row = dict(id='mihome:1', miio_model='test.fan.v1', image='old', image_source='store', image_width=168)
    for entry in (dict(pd_id=1, usable=False), dict(pd_id=1), dict(pd_id=-1, usable=True),
                  dict(pd_id='1', usable=True), dict(pd_id=True, usable=True)):
        assert apply_pdicons([row], {row['miio_model']:entry}) == [row]
