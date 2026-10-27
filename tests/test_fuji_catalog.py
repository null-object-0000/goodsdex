import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/fuji_catalog.py'
spec = importlib.util.spec_from_file_location('fuji_catalog', SCRIPT)
fuji = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fuji)
FIXTURES = Path(__file__).parent / 'fixtures/fuji'


def test_real_table_fixture_with_continuations():
    structure, params = fuji.specifications((FIXTURES/'x-t5-table.html').read_text())
    assert structure == 'table'
    assert len(params) == 47
    assert params['型号'] == 'FUJIFILM X-T5'
    assert params['有效像素数'] == '4020万像素'
    assert 'HEIF' in params['静止图像文件格式']
    assert '14bit RAW' in params['静止图像文件格式']
    assert 'NP-W235' in params['电池']
    assert '557g' in params['重量']
    assert params['连拍']


def test_real_div_fixture_including_deep_values():
    structure, params = fuji.specifications((FIXTURES/'x-e5-div.html').read_text())
    assert structure == 'div'
    assert len(params) == 46
    assert params['型号'] == 'FUJIFILM X-E5'
    assert '40.2' in params['有效像素数']
    assert 'NP-W126S' in params['电池']
    assert '400 frames' in params['电池']
    assert '6240 x 3510' in params['视频拍摄']
    assert '445g' in params['重量']
    assert all(any('\u4e00' <= c <= '\u9fff' for c in k) for k in params)


def test_stable_identity_on_two_independent_parses():
    source = (FIXTURES/'x-t5-table.html').read_text()
    first = fuji.identity(fuji.specifications(source)[1]['型号'].removeprefix('FUJIFILM ').lower())
    second = fuji.identity(fuji.specifications(source)[1]['型号'].removeprefix('FUJIFILM ').lower())
    assert first == second == 'CN:fuji:model:x-t5'
    assert fuji.identity('x100v') != fuji.identity('x100vi')
    assert fuji.identity('x-h2') != fuji.identity('x-h2s')
    assert fuji.identity('x-t30-ii') != fuji.identity('x-t30-iii')
    lens = 'xf16-80mmf4-r-ois-wr'
    assert fuji.identity('x-t5', lens) == fuji.identity('x-t5', lens)
    assert fuji.identity('x-t5', lens) != first
    assert len(set(fuji.identity(m,l) for (m,_),l in fuji.LENS_SLUGS.items())) == 13


def test_append_preserves_old_rows_even_duplicate_ids():
    old = [{'id':'existing','price':123}, {'id':'existing','params':{'a':1}}]
    additions = [{'id':'CN:fuji:model:x-t5','price':None}]
    merged, audit = fuji.append_only(old, additions)
    assert merged[:2] == old
    assert audit['existing_ids_missing'] == []
    assert audit['new_count'] == 3
    rerun, audit = fuji.append_only(merged, additions)
    assert rerun == merged
    assert audit['added_fuji'] == 0
    with pytest.raises(ValueError):
        fuji.append_only(old, additions * 2)


@pytest.mark.parametrize('status,body', [(403,b'Forbidden'),(429,b'Too many requests'),(200,b'<title>Just a moment...</title>')])
def test_block_halts_entire_run_and_resume(tmp_path, monkeypatch, status, body):
    calls = []
    def curl(args, **kwargs):
        calls.append(args[-1])
        Path(args[args.index('--dump-header')+1]).write_text('HTTP/1.1 '+str(status)+'\r\n')
        Path(args[args.index('--output')+1]).write_bytes(body)
        return SimpleNamespace(returncode=0,stdout=str(status),stderr='')
    monkeypatch.setattr(fuji.subprocess,'run',curl)
    fetch = fuji.Fetcher(tmp_path)
    with pytest.raises(fuji.Stop): fetch.get('http://example.test/a')
    with pytest.raises(fuji.Stop): fuji.Fetcher(tmp_path).get('http://example.test/b')
    assert len(calls) == 1
    assert json.loads((tmp_path/'requests.json').read_text())[0]['status'] == status


def test_cache_resume_no_network_and_budget(tmp_path, monkeypatch):
    url='http://example.test/a'
    dest=tmp_path/'cache'/fuji.hashlib.sha256(url.encode()).hexdigest()
    dest.parent.mkdir()
    dest.write_bytes(b'cached')
    monkeypatch.setattr(fuji.subprocess,'run',lambda *a,**kw: pytest.fail('network'))
    fetch=fuji.Fetcher(tmp_path)
    assert fetch.get(url) == b'cached'
    fetch.events=[{'at':0,'host':'example.test'}]*300
    with pytest.raises(fuji.Stop,match='budget'): fetch.get(url+'new')


def test_same_host_spacing_is_enforced(tmp_path, monkeypatch):
    now=[100.0]
    starts=[]
    monkeypatch.setattr(fuji.time,'time',lambda: now[0])
    monkeypatch.setattr(fuji.time,'sleep',lambda delay: now.__setitem__(0,now[0]+delay))
    def curl(args,**kwargs):
        starts.append(now[0])
        Path(args[args.index('--dump-header')+1]).write_text('HTTP/1.1 200\n')
        Path(args[args.index('--output')+1]).write_bytes(b'ok')
        return SimpleNamespace(returncode=0,stdout='200',stderr='')
    monkeypatch.setattr(fuji.subprocess,'run',curl)
    fetch=fuji.Fetcher(tmp_path)
    fetch.get('http://example.test/a')
    fetch.get('http://example.test/b')
    assert starts[1]-starts[0] >= 2.1


def test_publish_preserves_metadata_rows_and_is_idempotent(tmp_path):
    out, tree = tmp_path/'crawl', tmp_path/'data-branch'
    out.mkdir()
    (out/'images').mkdir()
    (out/'images/camera.jpg').write_bytes(b'jpeg fixture')
    (tree/'public').mkdir(parents=True)
    old=[{'id':'mi-existing','price':1,'params':{'unaltered':True}},
         {'id':'apple-existing','brand':'Apple','price':None}]
    fuji.dump(tree/'public/goods.json',old)
    fuji.dump(tree/'public/meta.json',{'count':2,'brands':{'小米':1,'Apple':1},
              'with_price':1,'by_kind':{'machine':2},'note':'keep'})
    rows=[]
    for i in range(24):
        rows.append({'id':f'CN:fuji:model:test-{i}','brand':'富士','kind':'machine',
            'category':'相机','price':None,'price_kind':'none','price_note':'官网不公开人民币价',
            'params':{'型号':'test'},'image':'data/fuji/images/camera.jpg',
            'image_local_path':'data/fuji/images/camera.jpg'})
    fuji.dump(out/'goods.json',rows)
    for name in ['enumeration.json','kit-matrices.json','requests.json']:
        fuji.dump(out/name,{})
    first=fuji.publish(out,tree)
    first_bytes=(tree/'public/goods.json').read_bytes()
    first_meta=(tree/'public/meta.json').read_bytes()
    second=fuji.publish(out,tree)
    assert first['added_fuji']==24 and second['added_fuji']==0
    assert (tree/'public/goods.json').read_bytes()==first_bytes
    assert (tree/'public/meta.json').read_bytes()==first_meta
    assert json.loads(first_bytes)[:2]==old
    assert (tree/'public/data/fuji/images/camera.jpg').exists()
    meta=json.loads(first_meta)
    assert meta['with_price']==1 and meta['count']==26
    assert meta['brands']=={'小米':1,'Apple':1,'富士':24}
    assert meta['note']=='keep'
