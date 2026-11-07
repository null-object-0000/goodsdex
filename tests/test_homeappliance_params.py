from copy import deepcopy
import pytest
from goodsdex.homeappliance_params import apply_params, parse_attribute_list, parse_robot_battery, parse_manual_scalars


def evidence(value='20 L', **kw):
    return dict(value=value, source_field='额定容积', raw_value=value,
        url='https://home.mi.com/cgi-op/api/v1/baike/v2/attribute?model=xiaomi.microwave.test',
        source_type='official', sha256='a'*64, locator='$.data.list[0]', method='structured_attribute', **kw)


def fixture():
    row=dict(id='mihome:1',name='测试微波炉',miio_model='xiaomi.microwave.test',category='微波炉',params={},release={'date':'2020-01'})
    entry=dict(id=row['id'],expected_name=row['name'],model=row['miio_model'],category='微波炉',identity_method='existing_model',params={'容量':evidence()})
    return row,dict(schema=1,items=[entry])


def test_replay_only_specs_is_idempotent_preserves_source_and_release():
    r,m=fixture();before=deepcopy(r);a=apply_params([r],m)
    assert r==before and a[0]['release']==r['release']
    assert a[0]['params']=={'容量':'20 L'}
    assert a[0]['params_sources']['容量']['source_type']=='official'
    assert apply_params(a,m)==a


@pytest.mark.parametrize('patch',[{'name':'测试微波炉 Pro'},{'miio_model':'xiaomi.microwave.other'},{'is_container':True},{'miio_model':None}])
def test_does_not_borrow_specs_across_names_models_or_containers(patch):
    r,m=fixture();r.update(patch);out=apply_params([r],m)[0]
    assert out['params']=={}
    if patch.get('is_container'):assert out['params_missing']=='container_scope_unverified'
    else:assert out==r


def test_conflict_is_evidence_not_an_overwrite():
    r,m=fixture();r['params']={'容量':'23L'};a=apply_params([r],m)[0]
    assert a['params']==r['params'] and a['params_conflicts']['容量']['value']=='20 L'
    assert 'params_sources' not in a


@pytest.mark.parametrize('patch',[{'source_type':'third_party'},{'method':'ocr'},{'url':'https://home.mi.com.evil.test/spec'},{'sha256':'bad'}])
def test_rejects_unverified_provenance(patch):
    r,m=fixture();m['items'][0]['params']['容量'].update(patch)
    with pytest.raises(ValueError):apply_params([r],m)


def test_attribute_preserves_multivalue_and_does_not_invent_fields_or_units():
    items=[dict(attributeName='容量',attributeValue=['20','23'],unit='L'),dict(attributeName='unmapped',attributeValue=['500'])]
    assert parse_attribute_list(items,{'容量'})['容量']['value']=='20L / 23L'
    items.append(dict(attributeName='容量',attributeValue=['other']))
    assert parse_attribute_list(items,{'容量'})=={}


def test_robot_battery_rejects_prose_conflicting_tables_and_keeps_qualifiers():
    assert parse_robot_battery('广告\n电池容量 5200mAh')=={}
    assert parse_robot_battery('基本参数\n电池容量 2500mAh  5200mAh')=={}
    v=parse_robot_battery('基本参数\n电池容量 4800mAh（额定容量），5200mAh（标称容量）   额定输入 220V')
    assert v['电池容量']['value']=='4800mAh（额定容量），5200mAh（标称容量）'
    assert parse_robot_battery('基本参数\n电池容量 2500mAh\f基本参数\n电池容量 5200mAh')=={}


def test_manual_separates_input_power_from_output_and_rejects_model_columns():
    v=parse_manual_scalars('基本参数\n额定容积   20 L     额定输入功率   1250 W\n微波输出功率   800 W\n能效等级    1级','微波炉')
    assert v['容量']['value']=='20 L' and v['额定功率']['value']=='1250 W'
    assert parse_manual_scalars('基本参数\n额定容积 20 L  23 L','微波炉')=={}


def test_missing_does_not_become_a_parameter_or_erase_existing_values():
    r,m=fixture();m['items'][0].update(params={},params_missing='page_no_spec',attempts=[{'url':'https://home.mi.com/'}])
    a=apply_params([r],m)[0];assert a['params']=={} and a['params_missing']=='page_no_spec'
    r['params']={'容量':'20L'};assert 'params_missing' not in apply_params([r],m)[0]


def test_export_replays_exact_audited_product_id_without_a_device_catalog():
    r,m=fixture();r['id']='CN:mi_cn:product:20545';r.pop('miio_model')
    e=m['items'][0];e.update(id=r['id'],identity_method='audited_product_id',identity_evidence=dict(id=r['id'],name=r['name'],model=e['model']))
    assert apply_params([r],m)[0]['params']=={'容量':'20 L'}
    e['identity_evidence']['id']='CN:mi_cn:product:21480'
    with pytest.raises(ValueError):apply_params([r],m)


def test_aircon_whole_unit_table_rejects_neighbor_model_columns():
    from goodsdex.homeappliance_params import parse_aircon_table
    text='基本参数\n整机型号    35GW-PG15/R2A1\n室内机型号   35G-PG15/R2A1\n能效等级    1\n适用面积（㎡）    16-20\n额定制冷量（W）   3530（150~5300）\n'
    out=parse_aircon_table(text)
    assert out['能效等级']['value']=='1级' and out['适用面积']['value']=='16-20㎡'
    assert out['制冷量（整机）']['value']=='3530（150~5300）W'
    assert parse_aircon_table(text.replace('35GW-PG15/R2A1','35GW-PG15/R2A1   26GW-PG15/R2A1'))=={}


def test_third_party_specs_are_labelled_and_require_reviewed_model():
    r,m=fixture();e=m['items'][0]['params']['容量']
    e.update(url='https://detail.zol.com.cn/1/123/param.shtml',source_type='third_party',method='third_party_html',reviewed_model=r['miio_model'])
    out=apply_params([r],m)[0]
    assert out['params_source_type']=='third_party'
    assert out['params_sources']['容量']['source_type']=='third_party'
    e['reviewed_model']='other'
    with pytest.raises(ValueError):apply_params([r],m)


def test_shared_manual_only_accepts_explicitly_identical_cells_in_all_columns():
    from goodsdex.homeappliance_params import parse_aircon_table
    text='基本参数\n整机型号    35GW-A1   26GW-A1\n能效等级    1   1\n适用面积（m2）    16-20   10-16\n'
    out=parse_aircon_table(text)
    assert set(out)=={'能效等级'}
    assert out['能效等级']['selection']=='all_columns_explicitly_equal'
    assert out['能效等级']['hardware_models']==['35GW-A1','26GW-A1']


def test_release_identity_pending_specs_remain_empty_without_changing_dates():
    r,m=fixture();m['items'][0]['deferred_reason']='release_identity_review_required'
    a=apply_params([r],m)[0]
    assert a['params']=={} and a['release']==r['release']
    assert a['params_missing']=='release_identity_review_required'
    assert 'params_sources' not in a


def test_third_party_html_keeps_both_host_and_base_dimensions():
    from pathlib import Path
    path=Path(__file__).resolve().parents[1]/'scripts/collect_homeappliance_third_party.py'
    import sys
    sys.path.insert(0,str(path.parent))
    try:
        from collect_homeappliance_third_party import parse
        title,fields=parse(b'<meta charset="utf-8"><title>test</title><span id="newPmName_1">size</span><span id="newPmVal_1">host<br />base</span>')
        assert fields['size']['value']=='host base'
    finally:sys.path.pop(0)


def test_fridge_does_not_assign_521l_specs_to_a_521l_523l_profile():
    from goodsdex.homeappliance_params import parse_fridge_table, named_capacities
    assert named_capacities('对开610/636L')=={'610L','636L'}
    text='基本参数\n产品型号    BCD-521TEST\n总容积    521L\n能效等级    1级\n'
    assert parse_fridge_table(text,'纤薄嵌（适用于521L/523L）')=={}


def test_fridge_shared_columns_prove_common_grade_but_not_differing_capacities():
    from goodsdex.homeappliance_params import parse_fridge_table
    text='参数信息 基本参数\n产品型号    BCD-606WKMPDN   BCD-600WKMPDN\n总容积   606L   600L\n能效等级    1级   1级\n冷冻室容积    225L   225L\n冷藏室容积    345L   339L\n'
    out=parse_fridge_table(text,'十字606L/十字600L')
    assert set(out)=={'能效等级','冷冻室容积'}
    assert out['能效等级']['covered_capacities']==['606L','600L']


def test_normal_crawler_export_replays_audited_specs(tmp_path, monkeypatch):
    import json
    from goodsdex import homeappliance_params
    from goodsdex.publish import to_public
    r,m=fixture();r['id']='CN:mi_cn:product:20545'
    e=m['items'][0];e.update(id=r['id'],identity_method='audited_product_id',identity_evidence=dict(id=r['id'],name=r['name'],model=e['model']))
    path=tmp_path/'params.json';path.write_text(json.dumps(m));monkeypatch.setattr(homeappliance_params,'DEFAULT',path)
    out=to_public(dict(product=dict(product_id=r['id'],name=r['name'],category='微波炉'),view={'values':{}}))
    assert out['params']=={'容量':'20 L'}
    assert 'params_sources' not in out
