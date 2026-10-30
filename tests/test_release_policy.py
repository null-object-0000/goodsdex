import copy
import json

import pytest

from goodsdex.release_policy import ALLOWED_DELETIONS, assert_no_empty_shells
from goodsdex.supplements import merge, publish
from goodsdex.dedupe import finalize_public

EXPECTED = {
    'CN:mi_cn:product:25077', 'CN:mi_cn:product:25078',
    'GLOBAL:apple_support:model:111980', 'GLOBAL:apple_support:model:111988',
    'GLOBAL:apple_support:model:112591', 'GLOBAL:apple_support:model:112593',
}


def test_only_six_reviewed_ids_removed_and_all_other_objects_kept():
    assert set(ALLOWED_DELETIONS) == EXPECTED
    assert all(ALLOWED_DELETIONS.values())
    old = [dict(id=k) for k in sorted(EXPECTED)] + [dict(id='keep', name='原样', params={'k': [1, 2]})] * 2
    original = copy.deepcopy(old)
    rows, audit = merge(old, [], old)
    assert rows == old[-2:]
    assert old == original
    assert audit['allowed_deletions'] == dict(ALLOWED_DELETIONS)
    assert audit['missing_ids'] == []
    assert audit['count'] == audit['rebuilt_count'] + audit['added_count']
    assert merge(rows, [], rows)[0] == rows
    with pytest.raises(ValueError, match='unapproved'):
        merge(rows, [], old + [dict(id='unapproved')])


def test_unknown_empty_xiaomi_fails_before_release_files_change(tmp_path):
    old = [dict(id='keep', name='原样')]
    (tmp_path / 'goods.json').write_text(json.dumps(old))
    (tmp_path / 'extra.json').write_text('[]')
    before = (tmp_path / 'goods.json').read_bytes()
    invalid = dict(id='CN:mi_cn:product:new', name='  ', params={'a': []}, image=None, price=None)
    with pytest.raises(ValueError, match='CN:mi_cn:product:new'):
        publish(old + [invalid], tmp_path, old, tmp_path / 'extra.json')
    assert (tmp_path / 'goods.json').read_bytes() == before
    assert not (tmp_path / 'meta.json').exists()
    (tmp_path / 'goods.json').write_text(json.dumps([invalid]))
    before = (tmp_path / 'goods.json').read_bytes()
    with pytest.raises(ValueError, match='CN:mi_cn:product:new'):
        finalize_public(tmp_path)
    assert (tmp_path / 'goods.json').read_bytes() == before


@pytest.mark.parametrize('field,value', [
    ('name', '有名字'), ('params', {'容量': '256GB'}), ('params', {'value': 0}),
    ('image', 'https://example.com/image.jpg'), ('image_url', 'https://example.com/image.jpg'),
    ('price', 0), ('market_price', 12), ('historical_price', 12),
])
def test_partial_record_is_not_an_empty_shell(field, value):
    assert_no_empty_shells([dict(id='CN:mi_cn:product:new', **{field: value})])


def test_final_gate_rejects_unapproved_loss_before_writes(tmp_path):
    row = dict(id='kept', name='商品', category='手机', params={})
    (tmp_path / 'goods.json').write_text(json.dumps([row]))
    original = (tmp_path / 'goods.json').read_bytes()
    with pytest.raises(ValueError, match='lost'):
        finalize_public(tmp_path, [row, dict(id='lost')])
    assert (tmp_path / 'goods.json').read_bytes() == original
    assert not (tmp_path / 'meta.json').exists()
