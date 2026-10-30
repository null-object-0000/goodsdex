"""Fail-closed image supplements, replay, and provenance inference."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import pytest
from goodsdex.backfill import apply
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('prepare_images',ROOT/'scripts/prepare_xiaomi_image_backfill.py')
prepare=importlib.util.module_from_spec(spec);spec.loader.exec_module(prepare)

def image_patch():
    return dict(id='x',field='image',source='live_official_page',source_url='https://www.mi.com/scale/',captured_at='2026-10-30T21:17:37+08:00',fields=dict(image='https://spend-good.oss-cn-shanghai.aliyuncs.com/goods/'+'a'*40+'.jpg',image_source='live_official_page',image_source_url='https://www.mi.com/scale/',image_captured_at='2026-10-30T21:17:37+08:00',image_note='existing checked_at: image GET observation, not archive time',image_scope='model'))

def test_owned_image_requires_full_consistent_provenance():
    p=image_patch()
    for url in ['https://c1.mifile.cn/a.jpg','https://spend-good.oss-cn-shanghai.aliyuncs.com.evil/goods/'+'a'*40+'.jpg']:
        bad=deepcopy(p);bad['fields']['image']=url
        with pytest.raises(ValueError):apply([dict(id='x',image=None)],[bad])
    for key in ['image_source_url','image_captured_at','image_source','image_note']:
        bad=deepcopy(p);del bad['fields'][key]
        with pytest.raises(ValueError):apply([dict(id='x',image=None)],[bad])
    bad=deepcopy(p);bad['fields']['image_captured_at']='2026-10-30'
    with pytest.raises(ValueError):apply([dict(id='x',image=None)],[bad])

def test_replay_and_existing_images_are_preserved():
    p=image_patch();old=[dict(id='x',image=None),dict(id='other',image='original')]
    result,audit=apply(old,[p]);assert len(audit['applied'])==1
    assert result[1]==old[1] and old[0]['image'] is None
    replay,audit=apply(result,[p]);assert replay==result and len(audit['unchanged'])==1
    original=[dict(id='x',image='original',image_scope='series')]
    result,audit=apply(original,[p]);assert result==original and audit['skipped'][0]['reason']=='existing_value'

def test_only_existing_evidence_can_resolve_source_and_time():
    candidate=dict(pid='1945',source='live_official_page',checked_at='2026-10-30T21:17:37+08:00')
    resolved,reason=prepare.resolve(candidate,dict(official_specs_url='http://www.mi.com/scale/specs/'))
    assert reason is None and resolved['source_url']=='http://www.mi.com/scale/'
    assert resolved['captured_at']==candidate['checked_at']
    assert resolved['captured_at_kind']=='image_get_observed_at'
    assert prepare.resolve(candidate,{})[1]=='missing_official_page_mapping'
    assert prepare.resolve(dict(candidate,checked_at=None),dict(official_specs_url='http://www.mi.com/scale/specs/'))[1]=='missing_captured_at'
    assert prepare.resolve(dict(candidate,source='wayback_api_product_get',archive_ts='20190708073213'),{})[1]=='archive_request_url_not_preserved'

def test_failed_public_readback_removes_only_new_objects(tmp_path,monkeypatch):
    import hashlib,io
    from PIL import Image
    spec=importlib.util.spec_from_file_location('transfer_images',ROOT/'scripts/upload_xiaomi_backfill_images.py')
    transfer=importlib.util.module_from_spec(spec);spec.loader.exec_module(transfer)
    monkeypatch.chdir(tmp_path)
    buf=io.BytesIO();Image.new('RGB',(600,600),'white').save(buf,format='JPEG');raw=buf.getvalue()
    row=dict(image_url='https://example.org/original.jpg',content_type='image/jpeg',bytes=len(raw),width=600,height=600,source='live_official_page',source_url='https://www.mi.com/scale/',captured_at='2026-10-30T21:17:37+08:00',captured_at_kind='image_get_observed_at')
    row['key']='goods/'+hashlib.sha1(row['image_url'].encode()).hexdigest()+'.jpg'
    class Bucket:
        def __init__(self,exists=False):self.exists=exists;self.deleted=[];self.puts=[]
        def object_exists(self,key):return self.exists
        def get_object(self,key):return io.BytesIO(raw)
        def put_object_from_file(self,key,path,headers):
            self.puts.append(key);assert Path(path).read_bytes()==raw
            return type('Result',(),{'status':200})()
        def delete_object(self,key):self.deleted.append(key)
    def bad_download(url):return raw if url==row['image_url'] else b'corrupt'
    new=Bucket()
    with pytest.raises(AssertionError,match='oss_public_readback_mismatch'):transfer.transfer(row,new,bad_download)
    assert new.deleted==[row['key']]
    existing=Bucket(True)
    with pytest.raises(AssertionError):transfer.transfer(row,existing,bad_download)
    assert existing.deleted==[] and existing.puts==[]
    good=Bucket();result=transfer.transfer(row,good,lambda url:raw)
    assert result['byte_equal'] and result['readback_bytes']==len(raw)
    changed=dict(row,bytes=len(raw)+1);unused=Bucket()
    with pytest.raises(AssertionError,match='candidate_bytes_changed'):transfer.transfer(changed,unused,lambda url:raw)
    assert unused.puts==[]
