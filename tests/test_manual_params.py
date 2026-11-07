"""Three unmodified official PDFs, negative geometry cases and replay contract."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import pytest
from goodsdex.manual_params import parse_manual, apply_manual_params

FIXTURES = Path(__file__).parent / 'fixtures/manual_params'
URL = 'https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/test.pdf'


@pytest.mark.parametrize('model,page,expected', [
    ('xiaomi.vacuum.c102cn',14,{'尺寸':'Φ350×97mm','电池容量':'4800mAh（额定容量），5200mAh（标称容量）','主机净重':'3.67kg','额定功率':'75W'}),
    ('xiaomi.microwave.cm20l',13,{'额定容积':'20 L','额定输入功率':'1250 W','微波输出功率':'800 W','产品尺寸':'447 × 354 × 281 mm'}),
    ('midjd.fridge.bs60s',18,{'总容积':'600L','综合耗电量':'0.93kW·h/24h','产品净重':'97kg'}),
])
def test_real_official_pdf(model,page,expected):
    path=FIXTURES/(model+'.pdf')
    evidence=json.loads((FIXTURES/'sources.json').read_text())[model]
    assert hashlib.sha256(path.read_bytes()).hexdigest()==evidence['pdf_sha256']
    text=subprocess.run(['pdftotext','-layout',str(path),'-'],check=True,capture_output=True).stdout.decode()
    out=parse_manual(text,model,evidence['pdf_url'])
    for key,value in expected.items():
        v=out['params'][key]
        assert v['value']==value and v['page']==page
        assert v['quote'] in text.split('\f')[page-1]
        assert v['source']=='manual_pdf' and v['model']==model and v['pdf_url']==evidence['pdf_url']
    if model=='xiaomi.vacuum.c102cn': assert '额定输入' not in out['params']  # separate station


def test_missing_table_is_not_no_parameters():
    out=parse_manual('使用说明\n额定电压   220V\n', 'test.model',URL)
    assert out['params']=={} and out['status']=='table_not_found'


def test_misaligned_multiple_model_columns_never_selects_a_column():
    text='基本参数\n产品型号    BCD-350A    BCD-450A\n总容积    350L\n             450L\n额定电压    220V\n'
    out=parse_manual(text,'test.model',URL)
    assert out['params']=={} and out['status']=='parse_failed'
    assert out['rejected']==[{'page':1,'reason':'multiple_model_columns'}]


def test_contradiction_unknown_suffix_wrong_unit_and_wrapped_values():
    text='基本参数\n总容积    350L\n总容积    450L\n额定电压    220kg\n充电时间    约6.5小时 unknown\n产品尺寸\n   350×97mm\n'
    assert parse_manual(text,'test.model',URL)['params']=={}


def fixture():
    proof=parse_manual('基本参数\n额定电压    220V\n','test.model',URL)['params']
    for v in proof.values(): v['pdf_sha256']='a'*64
    row=dict(id='test:1',name='机器',miio_model='test.model',params={},release={'date':'2024-10'})
    manifest=dict(schema=1,items=[dict(id=row['id'],expected_name=row['name'],model='test.model',params=proof)])
    return row,manifest


def test_priority_identity_idempotency_and_unchanged_fields():
    row,m=fixture(); before=deepcopy(row); out=apply_manual_params([row],m)[0]
    assert row==before and out['params']=={'额定电压':'220V'}
    assert out['release']==row['release']
    assert apply_manual_params([out],m)==[out]
    row['params']={'额定电压':'230V'};row['params_sources']={'额定电压':{'source':'official_page'}}
    assert apply_manual_params([row],m)==[row]
    for field,value in [('name','other'),('miio_model','other.model'),('is_container',True)]:
        changed={**before,field:value}
        assert apply_manual_params([changed],m)==[changed]


@pytest.mark.parametrize('pid',['CN:mi_cn:product:20545','CN:mi_cn:product:21271'])
def test_existing_release_identity_gate_is_preserved(pid):
    row,m=fixture(); row['id']=pid;m['items'][0]['id']=row['id']
    assert apply_manual_params([row],m)==[row]


def test_invalid_evidence_fails_closed():
    row,m=fixture();m['items'][0]['params']['额定电压']['pdf_url']='https://example.com/test.pdf'
    with pytest.raises(ValueError): apply_manual_params([row],m)


def test_shared_capacity_profile_cannot_inherit_one_variant_pdf():
    row,m=fixture();row.update(name='冰箱 纤薄嵌（适用于521L/523L）',category='冰箱')
    m['items'][0]['expected_name']=row['name']
    assert apply_manual_params([row],m)==[row]


def test_adjacent_unknown_label_is_a_boundary_but_numeric_tail_is_not():
    out=parse_manual('基本参数\n产品净重    72kg    最大工作电流    10A\n','test.model',URL)
    assert out['params']['产品净重']['value']=='72kg'
    for line in ('产品净重    72kg    73kg','额定电压   额定频率    220V    50Hz','额定电压   220'):
        assert parse_manual('基本参数\n'+line+'\n','test.model',URL)['params']=={}


@pytest.mark.parametrize('state', [
    {'status': 'retired', 'on_sale': False, 'delisted_at': '2026-11-07'},
    {'on_sale': True, 'carried_forward_at': '2026-11-07'},
    {'image': 'https://example.com/real.png', 'image_source': 'mijia_baike_realIcon'},
    {'image': 'https://example.com/store.png', 'image_source': 'xiaomi_store'},
])
def test_public_projection_preserves_all_non_params_and_separates_audit(tmp_path, monkeypatch, state):
    from goodsdex import manual_params, homeappliance_params
    row, manifest = fixture()
    row.update(state, price=123, market_price=456, source='mi_cn',
               params_sources={'existing': {'source': 'prior'}},
               params_missing='existing_marker')
    before = deepcopy(row)
    manual_path = tmp_path/'manual.json'
    manual_path.write_text(json.dumps(manifest))
    appliance_path = tmp_path/'appliance.json'
    appliance_path.write_text(json.dumps({'schema': 1, 'items': []}))
    monkeypatch.setattr(manual_params, 'DEFAULT', manual_path)
    monkeypatch.setattr(homeappliance_params, 'DEFAULT', appliance_path)
    out, audit = manual_params.apply_public_params([row])
    assert row == before
    assert out[0]['params'] == {'额定电压': '220V'}
    assert {k: v for k, v in out[0].items() if k != 'params'} == {
        k: v for k, v in before.items() if k != 'params'}
    assert audit['outcomes'][0]['params_sources']['额定电压']['source'] == 'manual_pdf'
    assert audit['evidence']['manual'] == manifest
    assert manual_params.apply_public_params(out)[0] == out
