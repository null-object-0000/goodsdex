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


@pytest.mark.parametrize('name', ['吸顶灯安装服务', '路由器安装调试 安装服务', '上门安装', '客厅吸顶灯安装', '吸顶灯三室一厅套装安装', '筒射灯（不含开孔）安装服务-7个'])
def test_installation_service(name):
    from goodsdex.services import classify_service
    assert classify_service({'name': name})['reason'] == 'service:installation'


@pytest.mark.parametrize('name', ['免安装折叠衣架', '灯具安装尺寸', 'DJI 模块安装套件', '电机安装组件', '米家空调 Pro 3 安装', '空调含安装服务', '空调赠安装服务', '以旧换新手机', '小米手机', '小米电视'])
def test_service_keeps_products_and_uncertain_names(name):
    from goodsdex.services import classify_service
    assert classify_service({'name': name}) is None


def test_services_same_release_and_replay(tmp_path):
    rows = [dict(id='lamp', name='米家吸顶灯', category='灯具'), dict(id='service', name='吸顶灯安装服务', category='灯具', price=45), dict(id='inspection', name='空调检测服务', category='空调', price=50)]
    (tmp_path / 'goods.json').write_text(json.dumps(rows))
    for _ in range(2):
        finalize_public(tmp_path, previous=rows)
        meta = build_shards(tmp_path)
        excluded = read(tmp_path, 'goods-excluded.json')
        assert (meta['total_all'], meta['total_published'], meta['total_excluded']) == (3, 1, 2)
        assert excluded['reasons']['service:installation'] == 1
        assert excluded['reasons']['service:other'] == 1
        assert read(tmp_path, 'goods.json')[0]['id'] == 'lamp'


@pytest.mark.parametrize('name', ['延保服务', '上门清洗', '空调检测服务', '拆旧费', '米家中央空调上门勘测服务', '手机上门维修', '空调清洁保养服务', '空调清洁保养套装服务 挂机', '屏幕换新服务 Redmi K', '后盖换新服务', '家用净水器勘测服务'])
def test_confirmed_other_services(name):
    from goodsdex.services import classify_service
    assert classify_service({'name': name})['reason'] == 'service:other'


@pytest.mark.parametrize('name,word', [
    ('耳机新品1元权益定金（不发货）', '权益'),
    *[(f'新品{word}链接', word) for word in ('定金', '订金', '权益', '预约', '盲约', '预售', '占位', '不发货')],
])
def test_preorder_semantics(name, word):
    from goodsdex.services import classify_non_goods
    decision = classify_non_goods({'name': name})
    assert decision['reason'] == decision['matched_rule'] == 'preorder_deposit'
    assert decision['matched_text'] == word
    assert word in name


@pytest.mark.parametrize('word', ['安装服务', '延保', '上门', '以旧换新补贴', '充值卡', '贴膜服务'])
def test_non_physical_service_terms(word):
    from goodsdex.services import classify_non_goods
    decision = classify_non_goods({'name': word})
    assert decision['matched_rule'] == 'service'
    assert decision['matched_text'] == word


@pytest.mark.parametrize('name', [
    '空调含安装服务', '小米电视（赠延保服务）', '手机套装（含贴膜服务）',
    '电饭煲24小时预约', '智能插座预约功能', '手机含权益', '扫地机无需预约',
    '手机非预售', '音箱无需支付定金', '手机送货上门', '手机赠充值卡',
    '手机含以旧换新补贴', '车位占位传感器', '手机权益保障',
])
def test_non_goods_terms_in_product_descriptions_are_kept(name):
    from goodsdex.services import classify_non_goods
    assert classify_non_goods({'name': name}) is None


def test_non_goods_replay_and_future_collection_preserve_source_facts(tmp_path):
    from goodsdex.exclusions import validate_excluded
    rows = [dict(id='device', name='空调含安装服务', category='空调', price=1999),
            dict(id='offer', name='耳机新品1元权益定金（不发货）', category='耳机', price=1)]
    (tmp_path / 'goods.json').write_text(json.dumps(rows))
    for _ in range(2):
        finalize_public(tmp_path)
        meta = build_shards(tmp_path)
        excluded = read(tmp_path, 'goods-excluded.json')
        assert (meta['total_all'], meta['total_published'], meta['total_excluded']) == (2, 2, 0)
        offer = next(r for r in read(tmp_path, 'goods.json') if r['id']=='offer')
        assert offer['price_kind']=='deposit' and offer['price'] is None
        assert offer['source_price']==1 and not offer['price_comparable']
        assert offer['name']==rows[1]['name']
    fresh = dict(id='new-identity', name='新品订金', category='耳机', price=10)
    (tmp_path / 'goods.json').write_text(json.dumps([rows[0], fresh]))
    finalize_public(tmp_path)
    meta = build_shards(tmp_path)
    assert meta['total_published']==2 and meta['total_excluded']==0
    offer=next(r for r in read(tmp_path, 'goods.json') if r['id']=='new-identity')
    assert offer['price_kind']=='deposit' and offer['source_price']==10 and offer['price'] is None
    meta['total_excluded'] = 1
    with pytest.raises(ValueError):
        validate_excluded(meta, read(tmp_path, 'goods-excluded.json'), read(tmp_path, 'goods.json'))
