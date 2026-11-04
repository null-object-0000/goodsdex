import copy
import hashlib
import json

import pytest

from goodsdex.accessories import classify
from goodsdex.identity import product_name, parse_variant_attrs, build_identity
from goodsdex.mi_names import page_name, apply_page_names
from goodsdex.publish import to_public
from goodsdex.kind import classify_product_kind


@pytest.mark.parametrize('suffix', ['金属面板', '金属落地支架', '无线连接器', '双支装', '单只', '套装', 'Pro', 'Max'])
def test_distinctive_suffix_survives(suffix):
    name = 'Xiaomi Sound 2 Max ' + suffix
    assert product_name(name) == name
    assert page_name('<title>' + name + '立即购买-小米商城</title>') == name
    assert parse_variant_attrs(name).get('color') != suffix


def test_title_parser_preserves_content_and_rejects_error_pages():
    assert page_name('<title>Xiaomi Sound 2 Max+支架套装立即购买-小米商城</title>') == 'Xiaomi Sound 2 Max+支架套装'
    assert page_name('<title>A &amp; B  单只立即购买-小米商城</title>') == 'A & B  单只'
    for document in ('<title>403 Forbidden</title>', '<title>小米商城</title>', '<title>立即购买-小米商城</title>'):
        with pytest.raises(ValueError): page_name(document)


@pytest.mark.parametrize('name, accessory', [
    ('Xiaomi Sound 2 Max 金属面板', True), ('Xiaomi Sound 金属落地支架', True),
    ('Xiaomi Sound 无线连接器', True), ('电视挂架', True), ('Xiaomi Sound 线缆', True),
    ('Xiaomi Sound 2 Max', False), ('Xiaomi Sound 2 Max双支装', False),
    ('Xiaomi Sound 2 Max+2 Pro+无线连接器套装', False),
    ('Xiaomi Sound 2 Max+支架套装', False), ('Xiaomi Sound 2 Max（含支架）套装', False),
    ('Xiaomi Sound 金属面板套装', True),
    ('小米智能家庭面板', False), ('米家面板灯 蓝牙Mesh版', False),
    ('全屋照明（三室两厅）（吸顶灯Pro+餐厅吊灯+面板灯）', False),
])
def test_accessory_and_real_bundles(name, accessory):
    assert classify(dict(name=name, category='其他配件'))['accessory'] is accessory
    assert (classify_product_kind(name, '其他配件') == 'accessory') is accessory


def evidence(name='Xiaomi Sound 2 Max 金属面板'):
    url='https://www.mi.com/shop/buy/detail?product_id=22105'
    return dict(schema=1, items=[dict(id='CN:mi_cn:product:22105', name=name,
        title=name+'立即购买-小米商城', status=200, url=url, final_url=url,
        requested_at='2026-11-04T00:00:00+00:00', sha256=hashlib.sha256(name.encode()).hexdigest())])


def test_replay_is_scoped_idempotent_and_keeps_price_and_original_name():
    rows=[dict(id='CN:mi_cn:product:22105', name='Xiaomi Sound 2 Max', kind='machine', price=299),
          dict(id='other', name='Xiaomi Sound 2 Max', price=1649)]
    before=copy.deepcopy(rows)
    result=apply_page_names(rows, evidence())
    assert rows==before
    assert result[0]['name']=='Xiaomi Sound 2 Max 金属面板'
    assert result[0]['is_accessory'] is True and result[0]['kind']=='accessory'
    assert result[0]['price']==299 and result[0]['name_before_title_repair']=='Xiaomi Sound 2 Max'
    assert result[1]==rows[1]
    assert apply_page_names(result, evidence())==result
    bad=evidence();bad['items'][0]['final_url']='https://www.mi.com/'
    with pytest.raises(ValueError):apply_page_names(rows,bad)
    bad=evidence();bad['items'][0]['name']='fake'
    with pytest.raises(ValueError):apply_page_names(rows,bad)
    # Local-zone lexical ordering must not make an older capture look newer.
    result[0]['name_source']['requested_at']='2026-11-04T07:00:00+08:00'
    assert apply_page_names(result,evidence())[0]['name_source']['requested_at']=='2026-11-04T00:00:00+00:00'
    result[0]['name']='New literal official name'
    result[0]['name_source']['requested_at']='2027-01-01T00:00:00+00:00'
    assert apply_page_names(result,evidence())[0]==result[0]


def test_published_cached_view_restores_complete_name():
    row=to_public(dict(product=dict(product_id='CN:mi_cn:product:22105', name='Xiaomi Sound 2 Max', kind='machine'),
                       view=dict(values=dict(name='Xiaomi Sound 2 Max 金属面板', price=299))))
    assert row['name']=='Xiaomi Sound 2 Max 金属面板' and row['is_accessory'] is True
    assert row['kind']=='accessory' and row['price']==299


def test_collection_overwrites_nonempty_variant_name_with_title(monkeypatch):
    from goodsdex import pipeline
    from goodsdex.facts import Capture, Assertion
    from goodsdex.sources import mi_cn
    monkeypatch.setattr(mi_cn,'fetch_mobile',lambda pid:([],[]))
    monkeypatch.setattr(mi_cn,'fetch_pc',lambda pid:([],[]))
    title='Xiaomi Sound 2 Max 金属面板'
    cap=Capture.make(mi_cn.SRC_TITLE,'https://www.mi.com/shop/buy/detail?product_id=22105', '<title>'+title+'立即购买-小米商城</title>')
    assertion=Assertion(assertion_id='title:name',subject_id='22105',capture_id=cap.capture_id,
        source=mi_cn.SRC_TITLE,attribute='name',raw_value=title,locator='title')
    monkeypatch.setattr(mi_cn,'fetch_page_title',lambda pid:([cap],[assertion]))
    rec=pipeline.collect_one('22105','old name','小爱音箱',variants=[dict(commodity_id=1,name='Xiaomi Sound 2 Max 金属面板 金属面板')])
    assert rec['product']['name']==title
    assert rec['view']['values']['name']==title
    assert rec['product']['is_accessory'] is True
    assert to_public(rec)['name']==title


def test_identity_does_not_turn_variant_common_prefix_into_name():
    product=build_identity('1',[dict(commodity_id=1,name='Sound 2 Max 单只'),dict(commodity_id=2,name='Sound 2 Max 双支装')])
    assert product.name=='Sound 2 Max 单只'
