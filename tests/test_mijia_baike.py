from copy import deepcopy
import pytest
from goodsdex.mijia_baike import apply_baike, hardware_models


def entry():
    return dict(id='CN:mi_cn:product:123', expected_name='米家洗衣机', model='mibx5.washer.x15',
                name_repair_hardware_model='XQG105MJ101', productName='米家洗衣机 Pro 10kg', product_sha256='a'*64,
                product_url='https://home.mi.com/cgi-op/api/v1/baike/v2/product?model=mibx5.washer.x15',
                mapping_method='baike_official_shop_link', mapping_evidence={'shop_url':'https://m.mi.com/mfbs/mstd/product?commodityId=123'}, manual_url='https://example.org/manual.pdf',
                manual_type='pdf', manual_status='downloaded', attribute_status='source_empty', manual_sha256='b'*64, hardware_models=['XQG105MJ101'],
                parameters=[], parameter_count=0, category_clue='洗衣机', materialPictures=[], image_missing=True)


def test_metadata_never_changes_release_category_or_existing_image():
    row=dict(id=entry()['id'], name='米家洗衣机', category='旧款机型', categories=['旧款机型'],
             release={'date':'2020-01'}, image='existing', params={'上市时间':'2020','产品型号':'XQG105MJ101'})
    before=deepcopy(row)
    out=apply_baike([row], {'schema':1,'items':[entry()]})[0]
    assert out['name']=='米家洗衣机 Pro 10kg'
    for k in ('release','category','categories','image','params'):assert out[k]==before[k]
    assert row==before
    assert apply_baike([out], {'schema':1,'items':[entry()]}) == [out]
    assert 'release_upper_bound' not in out


def test_no_fuzzy_match_or_sku_suffix_loss():
    e=entry();e['expected_name']='米家洗衣机 升级版'
    row=dict(id=e['id'],name=e['expected_name'])
    assert apply_baike([row],{'schema':1,'items':[e]})[0]['name']==row['name']
    row['name']='不同产品'
    assert apply_baike([row],{'schema':1,'items':[e]})==[row]


def test_reject_unscoped_evidence_and_duplicates():
    e=entry();e['product_url']='https://example.org/'
    with pytest.raises(ValueError):apply_baike([],{'schema':1,'items':[e]})
    with pytest.raises(ValueError):apply_baike([],{'schema':1,'items':[entry(),entry()]})


def test_models_require_label_not_watts_dates_or_certification():
    assert hardware_models('型号：XQG105MJ101、XQG105MJ102\n220V 50Hz\n2025-01-01')==['XQG105MJ101','XQG105MJ102']
    assert hardware_models('无线电发射设备型号核准代码：2025DP1234\nLED WIFI 220V')==[]
    assert hardware_models('产品型号：\nBHR1234CN')==['BHR1234CN']


def test_pd_id_collision_cannot_be_a_product_bridge():
    e=entry();e['mapping_evidence']['shop_url']='https://m.mi.com/?pd_id=123'
    with pytest.raises(ValueError):apply_baike([],{'schema':1,'items':[e]})


def test_container_is_not_renamed_to_one_device():
    row={'id':entry()['id'],'name':'米家洗衣机','is_container':True}
    assert apply_baike([row],{'schema':1,'items':[entry()]})==[row]


def test_shared_buy_link_alone_cannot_add_colour_or_size():
    row={'id':entry()['id'],'name':'米家洗衣机'}
    assert apply_baike([row],{'schema':1,'items':[entry()]})[0]['name']==row['name']


def test_unlabelled_cover_models():
    assert hardware_models('米家洗衣机\nXQG105MJ101、XQG105MJ102\n使用说明书')==['XQG105MJ101','XQG105MJ102']
    assert hardware_models('IPX4\nGB4706\nUSB3')==[]
