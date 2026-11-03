import json
import hashlib

import pytest

from goodsdex.dedupe import finalize_public
from goodsdex.shards import build_shards
from goodsdex.exclusions import REASONS


def read(root, name):
    return json.loads((root / name).read_text())


def test_same_run_full_inventory_reasons_and_no_leak(tmp_path):
    rows = [dict(id=f'CN:mi_cn:product:keep{i}', name='小米手机', category='手机') for i in range(20)]
    sticker = dict(id='CN:mi_cn:product:10000292', name='笔记本贴纸', category='笔记本', price=99)
    historical = dict(id='old-film', name='保护膜', category='手机', excluded_reason='accessory')
    shell = dict(id='CN:mi_cn:product:25077', name='', category='配件')
    (tmp_path / 'archive').mkdir()
    (tmp_path / 'archive/accessories.json').write_text(json.dumps([historical]))
    # A poisoned old generated view must never be read as an input.
    (tmp_path / 'goods-excluded.json').write_text('{"items":[{"id":"poison"}]}')
    (tmp_path / 'goods.json').write_text(json.dumps(rows + [sticker, shell]))
    finalize_public(tmp_path)
    meta = build_shards(tmp_path)
    excluded = read(tmp_path, 'goods-excluded.json')
    assert meta['total_all'] == 23 == meta['total_published'] + meta['total_excluded']
    assert meta['total_excluded'] == excluded['total'] == 3
    assert set(excluded['reasons']) == set(REASONS)
    assert excluded['reasons']['accessory:sticker'] == excluded['reasons']['invalid'] == 1
    assert excluded['reasons']['accessory:screen_film'] == 1
    assert excluded['revision'] == meta['revision']
    assert all(r['excluded_at'] == excluded['generatedAt'] == meta['generated_at'] for r in excluded['items'])
    assert not ({r['id'] for r in excluded['items']} & {r['id'] for r in read(tmp_path, 'goods.json')})
    assert next(r for r in excluded['items'] if r['id'] == sticker['id'])['category_l2'] == '笔记本'
    assert next(r for r in excluded['items'] if r['id'] == sticker['id'])['price'] == 99
    digest = hashlib.sha256((tmp_path / 'goods-excluded.json').read_bytes()).hexdigest()
    assert meta['files']['goods-excluded.json']['sha256'] == digest
    first_revision = meta['revision']
    finalize_public(tmp_path)
    meta = build_shards(tmp_path)
    assert meta['revision'] != first_revision
    assert meta['total_all'] == 23 and meta['total_excluded'] == 3
    assert read(tmp_path, 'archive/accessories.json')[0] == historical
    stale = read(tmp_path, 'goods-excluded.json')
    stale['revision'] = first_revision
    (tmp_path / 'goods-excluded.json').write_text(json.dumps(stale))
    with pytest.raises(ValueError, match='another release'):
        build_shards(tmp_path)


def test_safe_duplicate_reduction_has_details_and_balances_rows(tmp_path):
    row = dict(id='device', name='手机', category='手机')
    (tmp_path / 'goods.json').write_text(json.dumps([row, row]))
    finalize_public(tmp_path)
    meta = build_shards(tmp_path)
    assert (meta['total_all'], meta['total_published'], meta['total_excluded']) == (2, 1, 1)
    assert read(tmp_path, 'goods-excluded.json')['items'][0]['excluded_reason'] == 'duplicate'


def test_old_reviewed_shell_recovered_from_source_snapshot(tmp_path):
    root = tmp_path / 'public'
    root.mkdir()
    (root / 'goods.json').write_text('[]')
    source = tmp_path / 'data/categories'
    source.mkdir(parents=True)
    (source / 'x.json').write_text(json.dumps([dict(product=dict(product_id='CN:mi_cn:product:25077', name='', category='配件'))]))
    finalize_public(root)
    meta = build_shards(root)
    assert meta['total_all'] == meta['total_excluded'] == 1
    assert read(root, 'goods-excluded.json')['items'][0]['excluded_reason'] == 'invalid'
