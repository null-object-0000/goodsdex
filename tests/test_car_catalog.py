"""Guard against promoting options, promotions and inferred years to car facts."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from car_catalog import byd_candidates


def test_car_candidate_keeps_promotion_and_unverified_price_out_of_msrp():
    info = {'goodsinfoList': {'items': [{'name': '汉EV智驾版'}]}}
    config = {'type': '车型', 'show_status': True, 'is_presell': '0',
              'attrId': '1567', 'name': '506KM尊贵型', 'price': 179800,
              'description': '限时补贴价：15.98万元', 'seriesImg': 'https://example.com/car.jpg',
              'appearance': [{'name': '白', 'price': 0}],
              'optional': [{'name': '轮毂', 'price': 6000}]}
    rows = byd_candidates(info, [config], '131')
    assert len(rows) == 1
    assert rows[0]['price'] is None
    assert rows[0]['price_kind'] == 'none'
    assert rows[0]['official_config_amount'] == 179800
    assert rows[0]['model_year'] is None
    assert rows[0]['params'] == {}
    assert rows[0]['review_status'] == 'staging_only'
    changed = dict(config, price=180000, description='优惠变更')
    assert byd_candidates(info, [changed], '131')[0]['id'] == rows[0]['id']


def test_options_hidden_and_presale_cannot_become_pilot_cars():
    info = {'goodsinfoList': {'items': [{'name': '车型'}]}}
    base = {'type': '车型', 'show_status': True, 'is_presell': '0', 'attrId': '1', 'name': '配置'}
    configs = [dict(base, type='外饰'), dict(base, show_status=False), dict(base, is_presell='1')]
    assert byd_candidates(info, configs, '1') == []


def test_xiaomi_joins_parameters_by_id_and_keeps_missing_photo_explicit():
    from car_catalog import xiaomi_candidates
    table = {'pdfFileName': 'SU7参数配置表', 'carItemId': 10,
             'headerTitle': '统一零售价', 'carImg': '',
             'carSsuDataList': [
                 {'carSsuId': 2, 'pcCarVersionName': 'SU7 Pro', 'pcCarVersionPrice': '¥ 249,900'},
                 {'carSsuId': 1, 'pcCarVersionName': 'SU7', 'pcCarVersionPrice': '¥ 219,900'}],
             'groups': [{'groupName': '动力', 'paramComparisonCols': [
                 {'carSsuId': 1, 'paramComparisonCells': [{'paramName': '续航', 'paramValue': '标准版数值'}]},
                 {'carSsuId': 2, 'paramComparisonCells': [{'paramName': '续航', 'paramValue': 'Pro数值'}]}]}]}
    rows = xiaomi_candidates({'code': 0, 'data': {'paramComparisonTableVOList': [table]}})
    assert rows[0]['params']['动力/续航'] == 'Pro数值'
    assert rows[0]['price'] == 249900
    assert rows[0]['image'] is None
    assert rows[0]['brand'] == '小米汽车'


def test_byd_msrp_requires_matching_trim_and_uses_label_not_promotion():
    from car_catalog import verify_byd_parameters
    info = {'goodsinfoList': {'items': [{'name': '汉EV智驾版'}]}}
    configs = [{'type': '车型', 'show_status': True, 'is_presell': '0', 'attrId': '1', 'name': '标准', 'price': 179800}]
    rows = byd_candidates(info, configs, '131')
    payload = {'code': 200, 'success': True, 'data': {'configs': [
        {'name': '身份', 'value': [
            {'name': '车型', 'value': ['高配', '标准']},
            {'name': '建议零售价(元)', 'value': ['215,800', '179,800']},
            {'name': '权益后价格(元)', 'value': ['205,800', '159,800']}]},
        {'name': '续航', 'value': [{'name': 'CLTC', 'value': ['705km', '506km']}]}]}}
    verified = verify_byd_parameters(rows, payload)
    assert verified[0]['price'] == 179800
    assert verified[0]['price_kind'] == 'msrp'
    assert verified[0]['params']['续航/CLTC'] == '506km'


def test_daily_release_rejects_unreviewed_ids_and_preserves_every_other_object():
    import json
    from copy import deepcopy
    from ci_refresh_cars import CATALOG
    from goodsdex.cars import merge_cars
    import pytest
    approved = json.loads(CATALOG.read_text())['rows']
    other = [{'id': 'CN:mi_cn:1', 'price': 9, 'nested': {'keep': [None, 'x']}},
             {'id': 'CN:apple_cn:1', 'brand': 'Apple'},
             {'id': 'CN:dji:1', 'brand': '大疆'}, {'id': 'CN:fuji:1', 'brand': '富士'}]
    before = deepcopy(other)
    result = merge_cars(other, approved, approved)
    assert result[:len(other)] == before == other
    assert len(result) == len(other) + 43
    assert {r['brand'] for r in result[len(other):]} == {'比亚迪', '小米汽车'}
    with pytest.raises(ValueError, match='reviewed IDs'):
        merge_cars(other, approved + [{**approved[0], 'id': 'unreviewed'}], approved)
    with pytest.raises(ValueError, match='reviewed IDs'):
        merge_cars(other, approved[:-1], approved)


def test_hourly_refresh_preserves_entire_car_even_with_colliding_mi_gid(tmp_path, monkeypatch):
    import json
    from copy import deepcopy
    import sys
    import ci_refresh_prices
    from ci_refresh_cars import CATALOG
    car = deepcopy(json.loads(CATALOG.read_text())['rows'][0])
    car['gid'] = '123'  # Even a future accidental gid must never reach the Xiaomi price API.
    public = tmp_path / 'public'; public.mkdir()
    (public / 'goods.json').write_text(json.dumps([car]))
    prices = tmp_path / 'data/prices'; prices.mkdir(parents=True)
    (prices / 'latest.json').write_text(json.dumps({'prices': {'123': {'price': 1, 'market_price': 2}}}))
    extra = tmp_path / 'extras.json'; extra.write_text('[]')
    called = []
    monkeypatch.setattr(ci_refresh_prices, 'refresh', lambda gids, out: called.append(gids) or {})
    monkeypatch.setattr(sys, 'argv', ['ci_refresh_prices', '--public', str(public), '--supplements', str(extra)])
    assert ci_refresh_prices.main() == 0
    assert called == [[]]
    assert json.loads((public / 'goods.json').read_text()) == [car]


def test_full_rebuild_carries_cars_without_replacing_fields():
    from goodsdex.supplements import merge
    car = {'id': 'CN:byd:car:1', 'product_type': 'car', 'opaque': {'all': ['fields']}}
    rows, _ = merge([], [], [car])
    assert rows == [car]
