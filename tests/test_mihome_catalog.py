from copy import deepcopy
import pytest
from goodsdex.mihome_catalog import apply_catalog


def fixture():
    row=dict(id='CN:mi_cn:product:123',name='米家 净水器',brand='小米',category='家电',categories=['家电'],
             release={'date':'2020-01','source':'official'},params={'型号':'ABC123'},image=None)
    e=dict(id=row['id'],expected_name=row['name'],name='米家净水器',model='xiaomi.waterpuri.a1',pd_id=987,
           method='exact_name',category='净水机',classifications=[{'id':3,'name':'厨房电器'}],
           source_url='https://home.mi.com/cgi-op/api/v1/brand/h5/list?brandId=1520',source_sha256='a'*64,
           verified_icon=dict(url='https://cdn.cnbj1.fds.api.mi-img.com/icon.png',width=168,height=168,sha256='b'*64))
    return row,e


def test_preserves_dates_params_input_and_icon_role_on_replay():
    r,e=fixture();before=deepcopy(r);m=dict(schema=1,items=[e]);out=apply_catalog([r],m)[0]
    assert r==before
    assert out['release']==r['release'] and out['params']==r['params']
    assert out['name_raw']==r['name'] and out['category_raw']=='家电'
    assert (out['mihome_model'],out['mihome_pd_id'])==(e['model'],987)
    assert out['image_scope']=='device_icon' and out['image_source']=='mihome_icon'
    assert out['image_width']==out['image_height']==168
    assert apply_catalog([out],m)==[out]


def test_never_joins_ids_or_changes_other_variants_containers_or_images():
    r,e=fixture();m=dict(schema=1,items=[e])
    for changes in [dict(id='CN:mi_cn:product:987'),dict(name='米家净水器 Pro'),dict(is_container=True),dict(brand='别的品牌')]:
        other={**r,**changes};assert apply_catalog([other],m)==[other]
    r['image']='existing';out=apply_catalog([r],m)[0];assert out['image']=='existing' and 'image_source' not in out
    e['name']='米家净水器 Pro';assert apply_catalog([r],m)==[r]


def test_core_extension_requires_exact_existing_capacity_and_no_extra_suffix():
    r,e=fixture();r.update(name='米家洗衣机',params={'洗涤容量':'10kg'})
    e.update(expected_name=r['name'],name='米家洗衣机10kg',capacity='10kg',method='core_capacity')
    m=dict(schema=1,items=[e]);assert apply_catalog([r],m)[0]['name']==e['name']
    r['params']['洗涤容量']='12kg';assert apply_catalog([r],m)==[r]
    r['params']['洗涤容量']='10kg';e['name']='米家洗衣机Pro10kg';assert apply_catalog([r],m)==[r]


def test_invalid_proof_duplicate_identity_and_invalid_icon_fail_closed():
    r,e=fixture()
    with pytest.raises(ValueError):apply_catalog([r],dict(schema=1,items=[e,e]))
    e['source_url']='https://example.com/cgi-op/api/v1/brand/h5/list'
    with pytest.raises(ValueError):apply_catalog([r],dict(schema=1,items=[e]))
    r,e=fixture();e['verified_icon']['width']=0
    with pytest.raises(ValueError):apply_catalog([r],dict(schema=1,items=[e]))


def test_frozen_proofs_replay_and_never_change_any_date_field():
    import gzip,json
    from pathlib import Path
    root=Path(__file__).resolve().parents[1]
    rows=json.loads(gzip.decompress((root/'docs/mihome-catalog-20261106/goods-before.json.gz').read_bytes()))
    out=apply_catalog(rows)
    assert len(rows)==len(out)
    for old,new in zip(rows,out):
        keys={k for k in old.keys()|new.keys() if k.startswith(('release','page_first_archived'))}
        assert {k:old.get(k) for k in keys}=={k:new.get(k) for k in keys}
    assert apply_catalog(out)==out


def test_date_identity_restoration_is_scoped_to_verified_display_patch():
    from goodsdex.mihome_catalog import restore_catalog_identity
    r,e=fixture();m=dict(schema=1,items=[e]);out=apply_catalog([r],m)
    restored=restore_catalog_identity(out,m)
    assert restored[0]['name']==r['name']
    assert restored[0]['category']==r['category'] and restored[0]['categories']==r['categories']
    assert restored[0]['release']==r['release']
    assert apply_catalog(restored,m)==out
    out[0]['name']='米家净水器 Pro'
    assert restore_catalog_identity(out,m)==out


def test_scoped_publication_preserves_every_unowned_field(tmp_path):
    import json,gzip
    from pathlib import Path
    from goodsdex.dedupe import finalize_public
    root=Path(__file__).resolve().parents[1]
    rows=json.loads(gzip.decompress((root/'docs/mihome-catalog-20261106/goods-before.json.gz').read_bytes()))
    row=next(r for r in rows if r['id']=='CN:mi_cn:product:10330')
    row['release_unrelated_sentinel']={'date':'1900-01','note':'not owned by this patch'}
    for name,value in [('goods',[row]),('meta',{}),('prices',{})]:
        (tmp_path/(name+'.json')).write_text(json.dumps(value))
    finalize_public(tmp_path,previous=[row],mihome_catalog_only=True)
    actual=json.loads((tmp_path/'goods.json').read_text())
    assert actual==apply_catalog([row])
