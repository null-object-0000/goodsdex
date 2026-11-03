import copy
import json

import pytest

from goodsdex.accessories import classify, fingerprint, plan
from goodsdex.dedupe import finalize_public


@pytest.mark.parametrize('brand,name', [
    ('Apple', 'Apple 20W USB-C 充电器'), ('Apple', 'USB-C 数据线'),
    ('Apple', 'MagSafe'), ('大疆', 'DJI Mini 4 Pro 桨叶'),
    ('大疆', 'DJI Avata 2 智能飞行电池'), ('大疆', 'DJI 收纳包'),
    ('富士', 'XF 35mm 镜头盖'), ('富士', '遮光罩'), ('富士', '相机包'),
    ('惠普', '惠普 电源适配器'), ('惠普', '惠普 扩展坞'), ('惠普', '惠普电脑包'),
    ('新品牌', '净水器H1000G滤芯'), ('新品牌', '空调1.5匹滤网'),
    ('新品牌', '扫地机器人6 Max拖布'), ('新品牌', '电视移动支架'),
    ('新品牌', '手机18 Pro保护壳'), ('新品牌', '平板9键盘'),
    ('新品牌', '相机机身拓展板'), ('新品牌', 'Redmi Note 14 Pro+ 保护壳'),
    ('新品牌', '米家声波电动牙刷头 通用型'), ('新品牌', '打印机墨盒'),
    ('新品牌', 'Xiaomi 17 AR增透钢化膜'), ('新品牌', '扫拖基座 JZ2301'), ('新品牌', '镜头保护盖'), ('新品牌', '净水器（H1000G）滤芯'),
    ('新品牌', '手机（18 Pro）保护壳'), ('新品牌', '扫拖机器人G1 配件'), ('大疆', 'DJI Mic Mini 充电盒'),
])
def test_names_are_accessories(brand, name):
    assert classify(dict(name=name, brand=brand))['accessory']


@pytest.mark.parametrize('name', [
    '米家净水器 H1000G', '米家空调 1.5匹', '小米电视 S Pro 85',
    '米家扫地机器人 6 Max', '相机机身 X-T5', 'XF 35mm F1.4 镜头',
    'X-T5 套机', '新品牌笔记本', '新品牌平板', '新品牌手机',
    '新品牌无人机', '新品牌运动相机', '米家儿童电动牙刷 Pro 四刷头装', '小米手环11 NFC版',
    'DJI Avata 2 畅飞套装（三电池版）',
    'Osmo Action 4 徒步套装（1950mAh 电池）',
    'DJI Mic 3（两发一收，含充电盒）+ 手机连接头（Lightning）',
    'AirPods Pro 2 配 MagSafe 充电盒 (USB-C)',
    'REDMI显示器A27Q 多功能支架版 2026',
    '小米磁吸支架充电宝10000 7.5W', 'Xiaomi 户外蓝牙音箱 Camp',
])
def test_complete_products_override_category(name):
    assert not classify(dict(name=name, category='其他配件'))['accessory']


def test_categories_and_car_exemption_and_numbers_are_not_a_rule():
    assert classify(dict(name='无数字的物件', category='摄影器材配件'))['accessory']
    assert classify(dict(name='物件123', category='摄影器材配件'))['accessory']
    assert classify(dict(name='物件', category='家电', categories=['其他配件']))['accessory']
    assert not classify(dict(name='物件123', category='家电'))['accessory']
    for row in [dict(product_type='car'), dict(brand='比亚迪'), dict(brand='小米汽车')]:
        assert not classify(dict(name='充电器', category='配件', **row))['accessory']


def test_gate_boundary_new_records_repeat_and_exact_review():
    rows = [dict(id=str(i), name='商品', category='手机') for i in range(20)]
    rows[0]['name'] = '滤芯'
    original = copy.deepcopy(rows)
    kept, archive, audit = plan(rows, rows)
    assert audit['newly_excluded_ratio'] == .05 and audit['gate'] == 'green'
    rows[1]['name'] = '充电器'
    with pytest.raises(ValueError, match='exceeds 5%'):
        plan(rows, rows, reviewed_sha256=fingerprint([rows[0]]))
    kept, archive, audit = plan(rows, rows, reviewed_sha256=fingerprint(rows[:2]))
    assert audit['gate'] == 'red' and audit['reviewed']
    assert all(r['excluded_reason'].startswith('accessory:') for r in archive)
    _, _, audit = plan(rows, kept, archive)
    assert audit['newly_excluded_count'] == 0
    # Already archived but actually restored in a release: count it again.
    with pytest.raises(ValueError):
        plan(rows, rows, archive)
    assert original[0]['name'] == '滤芯'
    # Cars cannot dilute the exclusion denominator.
    with pytest.raises(ValueError):
        plan(rows + [dict(id='car', product_type='car')]*100, rows)


def test_finalize_fails_before_writes_and_preserves_archive_and_sources(tmp_path):
    rows = [dict(id='device', name='米家净水器1000G', category='净水器', params={}),
            dict(id='filter', name='米家净水器1000G滤芯', category='净水器', params={'a': 1})]
    path = tmp_path / 'goods.json'
    path.write_text(json.dumps(rows))
    (tmp_path / 'raw').mkdir()
    raw = tmp_path / 'raw' / 'evidence.json'
    raw.write_text('original raw')
    baseline = path.read_bytes()
    with pytest.raises(ValueError):
        finalize_public(tmp_path, rows)
    assert path.read_bytes() == baseline
    assert not (tmp_path / 'archive').exists()
    finalize_public(tmp_path, rows, reviewed_accessory_sha256=fingerprint(rows[1:]))
    assert [r['id'] for r in json.loads(path.read_text())] == ['device']
    archived = json.loads((tmp_path / 'archive/accessories.json').read_text())
    assert {k: v for k, v in archived[0].items() if k not in ('exclusion', 'excluded_reason', 'categories', 'brand', 'brand_source')} == rows[1]
    assert raw.read_text() == 'original raw'
    finalize_public(tmp_path)
    assert json.loads((tmp_path / 'archive/accessories.json').read_text()) == archived


def test_known_cached_accessories_do_not_dilute_new_exclusion_ratio():
    kept = [dict(id=f'keep{i}', name='商品') for i in range(18)]
    cached = [dict(id=f'old{i}', name='滤芯', excluded_reason='accessory') for i in range(100)]
    new = [dict(id='new', name='滤芯')]
    with pytest.raises(ValueError, match='exceeds 5%'):
        plan(kept + cached + new, kept, cached)


def test_stale_supplement_cannot_overwrite_first_exclusion_evidence():
    first = dict(id='a', name='滤芯', price=99, image='original', params={'spec': 'full'}, excluded_reason='accessory')
    stale = dict(id='a', name='滤芯', price=None)
    _, archive, audit = plan([stale], [], [first])
    assert archive == [first]
    assert audit['newly_excluded_count'] == 0


def test_archive_repair_preserves_displaced_observation_and_extra_identities():
    from scripts.restore_accessory_archive import restore
    first = dict(id='a', name='滤芯', price=99, excluded_reason='accessory')
    stale = dict(id='a', name='滤芯', price=None, excluded_reason='accessory')
    extra = dict(id='b', name='充电器', excluded_reason='accessory')
    result = restore([stale, extra], [first])
    assert result == [{**first, 'subsequent_observations': [stale]}, extra]
    assert stale['price'] is None and first['price'] == 99


@pytest.mark.parametrize('name', [
    '「新秀无畏」系列笔记本定制贴纸',
    '【定制】小米笔记本Pro 15 OLED 机车女孩款贴纸',
    '小米笔记本Pro 15 OLED 宇航员款贴纸',
    '【定制】RedmiBook Pro 15 机车女孩款贴纸',
    '【定制】RedmiBook Pro 15 宇航员款贴纸',
    'Redmi Pad Pro 类纸膜 透明色', '小米MIX 2S 标准高透膜',
    '小米8 标准钢化玻璃膜', '日常元素地面清洁剂（自动添加版）',
])
def test_observed_missing_accessories(name):
    assert classify(dict(name=name, category='笔记本'))['accessory']


@pytest.mark.parametrize('name', [
    'RedmiBook Pro 15', '小米笔记本Pro 15 OLED', '米家扫拖机器人',
    '米家洗地机', '空调清洁保养套装服务 挂机', '洗衣机清洁保养服务',
    '小米笔记本Pro 15 OLED（赠贴纸）', 'Redmi Pad Pro（含保护膜）',
    'FUJIFILM X-E5 + XF23mmF2.8 R WR 套机', 'XF 35mm F1.4 镜头',
])
def test_missing_accessory_rules_preserve_products_and_services(name):
    assert not classify(dict(name=name, category='家电'))['accessory']


def test_sticker_reason_and_shared_finalizer(tmp_path):
    from goodsdex.accessories import exclusion_reason
    rows = [dict(id=f'CN:mi_cn:product:keep{i}', name='小米笔记本Pro 15 OLED', category='笔记本') for i in range(20)]
    sticker = dict(id='CN:mi_cn:product:10000292', name='「新秀无畏」系列笔记本定制贴纸', category='笔记本', price=99)
    assert exclusion_reason(sticker) == 'accessory:sticker'
    (tmp_path / 'goods.json').write_text(json.dumps(rows + [sticker]))
    finalize_public(tmp_path, rows + [sticker])
    assert len(json.loads((tmp_path / 'goods.json').read_text())) == 20
    archived = json.loads((tmp_path / 'archive/accessories.json').read_text())
    assert archived[0]['id'] == sticker['id'] and archived[0]['price'] == 99
    assert archived[0]['excluded_reason'] == 'accessory:sticker'
