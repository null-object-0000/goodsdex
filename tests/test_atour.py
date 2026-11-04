import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import pytest
from goodsdex.atour import build_rows, merge_snapshot, coverage
from goodsdex.brands import infer_brand
from goodsdex.services import classify_non_goods
from goodsdex.supplements import merge
from release_candidate import merge_goods


def fixture():
    p=dict(id=1987,spuName='亚朵星球 慢回弹记忆绵枕')
    sku=dict(id=1,spuId=1987,skuNo='0123',skuName='两只装70*42*6cm',salesPrice=278,activityPrice=260,skuImgUrl='https://xbu-qiniu.yaduo.com/white.jpg',spuStatus=1)
    key='CN:atour:spu:1987:sku:0123'
    capture=dict(complete=True,pages=[dict(data=[p],pageInfo=dict(pageNo=1,totalPage=1,totalCount=1))],entries=[dict(listing=p,detail=dict(p),panel=dict(skuVOS=[sku]),captured_at='2026-11-05T00:00:00Z')],captured_at='2026-11-05T00:00:00Z')
    images={key:dict(url=sku['skuImgUrl'],classification='A',identity_verified=True)}
    cats={'1987':dict(category='枕芯',categories=['枕芯系列'],evidence='official navigation')}
    return capture,dict(images=images,categories=cats)


def test_sku_fidelity_package_specs_price_and_namespace():
    c,kwargs=fixture();r=build_rows(c,**kwargs)[0]
    assert r['name']=='亚朵星球 慢回弹记忆绵枕 / 两只装70*42*6cm'
    assert r['sku_no']=='0123' and r['price']==278 and r['promo_price']==260
    assert r['bundle'] and r['package_quantity']==2
    assert r['specs']['height']=='6cm' and r['specs']['filling'] is None
    assert infer_brand(r)==('亚朵星球','id_prefix')
    assert coverage([r])['sku_count']==1


@pytest.mark.parametrize('damage',['partial','total','panels','duplicate','wrongspu','image','interval'])
def test_failed_capture_never_produces_replacement(damage):
    c,k=fixture()
    if damage=='partial':c['complete']=False
    if damage=='total':c['pages'][0]['pageInfo']['totalCount']=2
    if damage=='panels':c['entries']=[]
    if damage=='duplicate':c['entries'][0]['panel']['skuVOS']*=2
    if damage=='wrongspu':c['entries'][0]['panel']['skuVOS'][0]['spuId']=123
    if damage=='image':k['images']={}
    if damage=='interval':c['requests']=[dict(started_at='2026-11-05T00:00:00Z'),dict(started_at='2026-11-05T00:00:01Z')]
    with pytest.raises(ValueError):build_rows(c,**k)


def test_completed_snapshot_retains_disappeared_sku_and_revives():
    c,k=fixture();current=build_rows(c,**k)
    absent=dict(current[0],id='CN:atour:spu:1987:sku:gone',sku_no='gone')
    other=dict(id='hp',source='hp_cn',name='HP',price=1)
    result=merge_snapshot([absent,other],c,**k)
    retired=next(r for r in result if r['id']==absent['id'])
    assert retired['status']=='retired' and retired['retired_at']==c['captured_at']
    assert retired['price']==278 and retired['specs']==absent['specs']
    old=dict(current[0],status='retired',retired_at='2026-11-01T00:00:00Z')
    revived=next(r for r in merge_snapshot([old,other],c,**k) if r['id']==old['id'])
    assert revived['status']=='available' and 'retired_at' not in revived
    assert revived['retirement_history'][0]['retired_at']==old['retired_at']


def test_other_collectors_preserve_atour_and_cannot_update_it():
    c,k=fixture();rows=build_rows(c,**k)
    assert merge([],[],rows,apply_backfills=False)[0]==rows
    with pytest.raises(ValueError,match='another responsibility'):
        merge_goods(rows,[dict(rows[0],price=1)],rows,'prices')
    assert merge_goods([],rows,[],'atour')==rows


def test_physical_sku_delivery_lead_time_is_not_deposit():
    c,k=fixture();r=build_rows(c,**k)[0]
    r['name']='亚朵星球 被芯（预售7天） / 150*200cm'
    assert classify_non_goods(r) is None
    assert classify_non_goods(dict(r,name='亚朵星球 预售定金'))['reason']=='preorder_deposit'
    assert classify_non_goods(dict(name='预售7天 名额'))['reason']=='preorder_deposit'


def test_household_bedding_category_is_not_a_spare_part():
    from goodsdex.accessories import classify
    assert not classify(dict(name='亚朵星球 深睡抱枕',category='抱枕',categories=['床品配件']))['accessory']
    assert classify(dict(name='无线电池',category='相机配件'))['accessory']


def test_other_brands_are_not_imported():
    c,k=fixture()
    c['pages'][0]['data'].append(dict(id=99,spuName='萨和 香薰'))
    c['pages'][0]['pageInfo']['totalCount']=2
    assert len(build_rows(c,**k))==1


def test_atour_archive_emits_generic_missing_observation(tmp_path):
    from goodsdex.archive import merge_archive
    from goodsdex.retirement import archive_observations, reconcile
    c,k=fixture();r=build_rows(c,**k)[0]
    def record(row):
        return dict(product=dict(variant_id=row['id'],name=row['name']),view=dict(values=dict(price=row['price'],specs=row['specs'])))
    gone=dict(r,id=r['id']+'-gone')
    evidence=dict(completeness='complete',total_reported=2,found=2,stop_reason='reached_total')
    merge_archive('atour',[record(r),record(gone)],archive_dir=tmp_path/'archive',now_iso='2026-11-05T01:00:00Z',discovery=evidence)
    evidence.update(total_reported=1,found=1)
    merge_archive('atour',[record(r)],archive_dir=tmp_path/'archive',now_iso='2026-11-06T01:00:00Z',discovery=evidence)
    observations=archive_observations(tmp_path,[r,gone])
    retired=next(x for x in reconcile([r,gone],[r],observations) if x['id']==gone['id'])
    assert retired['retired_at']=='2026-11-06T01:00:00Z' and retired['specs']==gone['specs']
