import copy
import json
from pathlib import Path
import pytest
from goodsdex.mihome_intake import apply_intake, classify
from goodsdex.price_semantics import normalize, comparable


def entry():
    return dict(classification='A',directory_sha256='a'*64,channel_verified=False,row=dict(
        id='mihome:123',source='mihome',name='测试空气净化器A1',name_mihome='空气净化器A1',
        category='空气净化器',category_mihome='空气净化器',miio_model='test.airpurifier.a1',
        mihome_pd_id=123,source_channels=['mihome'],price=None,price_missing='no_channel_price',
        price_kind='unknown',price_comparable=False,image=None,image_mihome=dict(url='icon',scope='device_icon')))


def test_existing_fields_and_duplicates_are_immutable():
    e=entry();before=[dict(e['row'],name='渠道名',image='channel-image',category='渠道分类',price=123)]
    original=copy.deepcopy(before)
    assert apply_intake(before,dict(schema=1,items=[e]))==original
    assert before==original
    rows=apply_intake([],dict(schema=1,items=[e]))
    assert apply_intake(rows,dict(schema=1,items=[e]))==rows


@pytest.mark.parametrize('category,name', [('灯泡','智能灯泡'),('空调','小米智能空气管理面板'),('热水器','热水器遥控'),('摄像机','摄像机电源线'),('网关','网关'),('温湿度传感器','温湿度传感器'),('插座／插排','插座'),('路由器','路由器'),('台灯','台灯')])
def test_accessories_and_pending_devices_cannot_be_smuggled_into_A(category,name):
    e=entry();e['row'].update(category_mihome=category,name_mihome=name)
    with pytest.raises(ValueError,match='forbidden'):apply_intake([],dict(schema=1,items=[e]))


def test_unpriced_reference_stays_out_of_comparisons_after_replay():
    r=normalize(entry()['row'])
    assert r['price'] is None and r['price_missing']=='no_channel_price'
    assert not r['price_comparable'] and not comparable(r)
    assert r['image'] is None and r['image_mihome']['scope']=='device_icon'


def test_archive_cannot_publish_a_fake_price_or_main_image():
    for field,value in [('price',99),('image','device-icon')]:
        e=entry();e['row'][field]=value
        with pytest.raises(ValueError):apply_intake([],dict(schema=1,items=[e]))


def test_frozen_manifest_only_contains_allowed_devices_and_prices():
    path=Path(__file__).resolve().parents[1]/'data/official/mihome-intake.json'
    if not path.exists():pytest.skip('manifest not generated yet')
    m=json.loads(path.read_text());rows=apply_intake([],m)
    assert len(rows)==len(m['items'])
    assert len({r['id'] for r in rows})==len(rows)
    for r in rows:
        assert classify(dict(categoryName=r['category_mihome'],name=r['name_mihome']))[0]=='A'
        assert not r.get('release') and not r.get('release_date')
        if r['price'] is None:
            assert r['price_missing']=='no_channel_price' and not comparable(r)
        if r['source']=='mihome':assert r['image'] is None


def test_new_durable_devices_survive_existing_accessory_policy():
    from goodsdex.accessories import classify as accessory
    path=Path(__file__).resolve().parents[1]/'data/official/mihome-intake.json'
    if not path.exists():pytest.skip('manifest not generated yet')
    for e in json.loads(path.read_text())['items']:
        assert not accessory(e['row'])['accessory'], e['row']['name']
    assert accessory(dict(name='米家落地扇 电池',category='风扇'))['accessory']
    assert accessory(dict(name='小爱音箱 Art 电池',category='音箱'))['accessory']
