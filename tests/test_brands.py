import copy
import json

import pytest

from goodsdex.brands import audit_brands, infer_brand, normalize_brands


@pytest.mark.parametrize('key,brand', [
    ('CN:mi_cn:product:1', '小米'), ('CN:mi_ev:car:1', '小米汽车'),
    ('CN:xiaomi_ev:car:1', '小米汽车'), ('cn:apple:1', 'Apple'),
    ('CN:apple_cn:commodity:1', 'Apple'), ('GLOBAL:apple_support:model:1', 'Apple'),
    ('CN:dji:sku:1', '大疆'), ('CN:hp_cn:sku:1', '惠普'),
    ('CN:.hp_cn:sku:1', '惠普'), ('CN:fuji:model:1', '富士'), ('CN:byd:car:1', '比亚迪'),
])
def test_namespace_beats_conflicting_source_name_and_existing_brand(key, brand):
    assert infer_brand(dict(id=key, brand='未知', source='Dell', name='联想笔记本')) == (brand, 'id_prefix')


@pytest.mark.parametrize('source,brand', [('米家', '小米'), ('Redmi', '小米'),
    ('apple_support', 'Apple'), ({'brand': 'hp'}, '惠普')])
def test_source_beats_name(source, brand):
    assert infer_brand(dict(id='other:1', source=source, name='联想笔记本')) == (brand, 'source')


def test_name_manual_unknown_and_purity():
    rows = [dict(id='other:1', name='米家净水器'),
            dict(id='other:2', name='戴尔笔记本'),
            dict(id='other:3', name='商品', brand='ASUS'),
            dict(id='other:4', name='适用于小米的第三方保护壳', brand='未知'),
            dict(id='CN:mi_cn_fake:5', name='设备', source='unrecognized')]
    original = copy.deepcopy(rows)
    after = normalize_brands(rows)
    assert rows == original
    assert [(r['brand'], r['brand_source']) for r in after] == [
        ('小米', 'name'), ('戴尔', 'name'), ('华硕', 'manual'), (None, None), (None, None)]
    assert normalize_brands(after) == after
    audit = audit_brands(rows, after)
    assert audit['unknown_ratio'] == .4
    assert len(audit['manual_review']) == 2
    assert audit['unknown_prefix_top10'] == [('other:4', 1), ('CN:mi_cn_fake', 1)]


def test_finalize_brand_is_in_export_manifest_index_detail_and_replay(tmp_path):
    from goodsdex.dedupe import finalize_public
    from goodsdex.shards import build_shards, shard_for
    rows = [dict(id='CN:mi_cn:product:test', name='米家净水器', category='净水器', params={}),
            dict(id='unrecognized:1', name='设备', category='其它', params={})]
    (tmp_path / 'goods.json').write_text(json.dumps(rows))
    finalize_public(tmp_path)
    build_shards(tmp_path)
    goods = json.loads((tmp_path / 'goods.json').read_text())
    assert goods[0]['brand'] == '小米' and goods[0]['brand_source'] == 'id_prefix'
    assert goods[1]['brand'] is None
    meta = json.loads((tmp_path / 'meta.json').read_text())
    assert meta['brands'] == {'小米': 1, '未知': 1}
    assert meta['files']['index/mi_cn.json']['count'] == 1
    assert json.loads((tmp_path / 'index/mi_cn.json').read_text())['items'][0]['brand_source'] == 'id_prefix'
    assert json.loads((tmp_path / f'detail/{shard_for(rows[0]["id"]):02x}.json').read_text())[rows[0]['id']]['brand_source'] == 'id_prefix'
    assert len(json.loads((tmp_path / 'archive/brand-review.json').read_text())) == 1
    # Collector replay loses the brand, finalization restores it deterministically.
    (tmp_path / 'goods.json').write_text(json.dumps(rows))
    finalize_public(tmp_path)
    assert json.loads((tmp_path / 'goods.json').read_text()) == goods


# Every reviewed namespace, including those only present in archived exclusions.
from goodsdex.brands import NAMESPACE_ALIASES, id_namespace, namespace_brand


@pytest.mark.parametrize('scope,alias,brand', [
    (scope, alias, brand)
    for scope, brands in NAMESPACE_ALIASES.items()
    for brand, aliases in brands.items() for alias in aliases
])
@pytest.mark.parametrize('separator', ['_', '-', '.', ':', '-_.:'])
def test_complete_normalized_namespaces(scope, alias, brand, separator):
    variant = alias.replace('_', separator).swapcase()
    key = f'{scope.upper()}:{variant}:product:10000292'
    # Conflicting evidence must never turn Apple (or any other brand) into Xiaomi.
    assert infer_brand(dict(id=key, brand='小米', source='mi_cn', name='小米设备')) == (brand, 'id_prefix')
    assert id_namespace(key) == (scope.upper(), variant)


@pytest.mark.parametrize('namespace', [
    'mi_cn_fake', 'mi:cn:fake', 'apple_fake', 'apple:cn:fake', 'applepie',
    'dji_fake', 'hp_fake', 'hp:cn:fake', 'fujifake', 'byd_fake', 'xiaomi_ev_fake',
])
def test_unreviewed_namespace_does_not_inherit_brand(namespace):
    row = dict(id=f'CN:{namespace}:product:1', name='适用于小米或Apple的第三方配件')
    assert namespace_brand(row['id']) is None
    assert infer_brand(row) == (None, None)


@pytest.mark.parametrize('key', ['US:mi_cn:product:1', 'GLOBAL:mi_cn:model:1',
                                     'CN:unknown:mi_cn:product:1', 'mi_cn', 'CN:mi_cn'])
def test_scope_and_namespace_boundaries(key):
    assert infer_brand(dict(id=key, name='设备')) == (None, None)


def test_colon_sticker_and_original_identity_are_preserved():
    from goodsdex.exclusions import build_excluded
    row = dict(id='CN:mi:cn:product:10000292', name='「新秀无畏」系列笔记本定制贴纸',
               category='笔记本', params={})
    excluded = build_excluded([row], [], [], [], [], '2026-11-04T00:00:00Z', 'test')
    item = excluded['items'][0]
    assert item['id'] == row['id']
    assert item['brand'] == '小米' and item['brand_source'] == 'id_prefix'
    assert item['excluded_reason'] == 'accessory:sticker'
