import copy,json,base64,subprocess,sys
from pathlib import Path
import pytest
from goodsdex.catalog_discovery import discover
from goodsdex.mi_names import page_name
from goodsdex.sources import mi_cn


def enumeration(query):
    return {'items':[{'pid':'1','name':'old'},{'pid':'2','name':'new'},{'pid':'3','name':'excluded'}],
            'discovery':{'completeness':'complete','query':query}}


def record(pid,*args):
    return {'product':{'product_id':'CN:mi_cn:product:'+pid,'name':'New model','category':'音箱',
            'identity_evidence':{'mobile_product_id':pid},'name_source':{'kind':'mobile_api','identity_verified':True,'product_id':pid}},
            'view':{'values':{'name':'New model'},'parameters':{}},'captures':[],'assertions':[]}


def test_every_category_scanned_but_known_and_excluded_details_never_refetched():
    before=[{'id':'CN:mi_cn:product:1','name':'Approved model','price':299,'params':{'cpu':'original'}}]
    original=copy.deepcopy(before);calls=[]
    def collect(pid,*args):calls.append(pid);return record(pid)
    after,records,report=discover(before,[{'id':'CN:mi_cn:product:3'}],{'A':'a','B':'b'},enumerate_products=enumeration,collect=collect)
    assert before==original and after[:1]==original and calls==['2']
    assert len(records)==1 and len(report['categories'])==2 and report['added']==1


def test_failed_scan_and_wrong_identity_cannot_mutate_or_publish_products():
    before=[{'id':'CN:mi_cn:product:1','name':'Kept','price':300}]
    def failed(query):return {'items':[],'discovery':{'completeness':'failed'}}
    after,rows,report=discover(before,[],{'A':'a'},enumerate_products=failed,collect=lambda *a:pytest.fail('unexpected detail request'))
    assert after==before and not rows and not report['ok']
    def wrong(pid,*args):r=record(pid);r['product']['identity_evidence']['mobile_product_id']='foreign';return r
    after,rows,report=discover(before,[],{'A':'a'},enumerate_products=enumeration,collect=wrong)
    assert after==before and not rows and report['quarantined']


def test_page_title_requires_the_requested_embedded_identity(monkeypatch):
    def html(pid,name):return '<title>'+name+'立即购买-小米商城</title><script>var $GLOBAL_PAGE_INFO = '+json.dumps({'product_info':{'product_id':pid,'name':name}})+';</script>'
    assert page_name(html('10015','小米小爱音箱 Play'),expected_pid='10015')=='小米小爱音箱 Play'
    monkeypatch.setattr(mi_cn,'_get',lambda url:html('999','CyberDog电池及充电座'))
    caps,assertions=mi_cn.fetch_page_title('10015')
    assert not assertions and caps[0].status.value=='parse_error'
    with pytest.raises(ValueError):page_name('<title>假商品立即购买-小米商城</title>',expected_pid='10015')


def test_mobile_wrong_id_emits_no_price_or_name_assertions(monkeypatch):
    payload={'code':0,'data':{'product':{'productId':999,'name':'foreign','defaultGid':1}}}
    monkeypatch.setattr(mi_cn,'_mtop_call',lambda *args:(payload,json.dumps(payload),200,''))
    caps,assertions=mi_cn.fetch_mobile('10015')
    assert not assertions and caps[0].status.value=='source_error'


def test_single_foreign_sku_is_a_container_not_its_parents_data(monkeypatch):
    payload={'code':0,'data':{'product':{'productId':10,'name':'Parent'},'goodsInfo':{'goodsList':[{'productId':20,'price':500}]}}}
    monkeypatch.setattr(mi_cn,'_mtop_call',lambda *args:(payload,json.dumps(payload),200,''))
    caps,assertions=mi_cn.fetch_mobile('10')
    assert next(a.raw_value for a in assertions if a.attribute=='_container_children')==['20']


def test_container_expands_to_verified_new_child_without_publishing_parent():
    def enumeration(query):return {'items':[{'pid':'10'}],'discovery':{'completeness':'complete'}}
    def collect(pid,*args):
        r=record(pid)
        if pid=='10':r['product'].update(is_container=True,container_children=['20'])
        return r
    after,records,report=discover([],[],{'A':'a'},enumerate_products=enumeration,collect=collect)
    assert [r['id'] for r in after]==['CN:mi_cn:product:20']
    assert report['quarantined'][0]['pid']=='10'


def test_discovery_candidate_contains_only_additions_and_preserves_concurrent_prices(tmp_path):
    sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
    from release_candidate import pack,merge_candidate
    def git(*args):return subprocess.run(['git','-C',str(tmp_path),*args],check=True,capture_output=True)
    git('init','-q');p=tmp_path/'public/goods.json';p.parent.mkdir()
    old={'id':'CN:mi_cn:product:1','name':'old','price':300,'params':{'evidence':'x'*10000}}
    new={'id':'CN:mi_cn:product:2','name':'new','price':200,'name_source':{'identity_verified':True}}
    p.write_text(json.dumps([old]),encoding='utf-8');git('add','-A');git('-c','user.name=t','-c','user.email=t@t','commit','-qm','baseline')
    p.write_text(json.dumps([old,new]),encoding='utf-8');candidate=tmp_path/'candidate.json'
    pack(tmp_path,'all',candidate,'discovery');bundle=json.loads(candidate.read_text())
    assert bundle['collector_mode']=='discovery' and candidate.stat().st_size<2000
    assert json.loads(base64.b64decode(bundle['files']['public/goods.json']['before']))==[]
    latest={**old,'price':350};p.write_text(json.dumps([latest]),encoding='utf-8')
    merge_candidate(tmp_path,candidate);assert json.loads(p.read_text())==[latest,new]
    normalized={**new,'price':250,'normalized':True}
    p.write_text(json.dumps([latest,normalized]),encoding='utf-8')
    merge_candidate(tmp_path,candidate);assert json.loads(p.read_text())==[latest,normalized]
    p.write_text(json.dumps([{**old,'name':'corrupted'},new]),encoding='utf-8')
    with pytest.raises(ValueError,match='Discovery cannot change'):pack(tmp_path,'all',candidate,'discovery')


def test_discovery_preserves_every_existing_legacy_duplicate_version(tmp_path):
    sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
    from release_candidate import pack,merge_candidate
    def git(*args):return subprocess.run(['git','-C',str(tmp_path),*args],check=True,capture_output=True)
    git('init','-q');p=tmp_path/'public/goods.json';p.parent.mkdir()
    old=[{'id':'CN:mi_cn:product:1','name':'same product','price':100},
         {'id':'CN:mi_cn:product:1','name':'same product','price':120}]
    new={'id':'CN:mi_cn:product:2','name':'new','name_source':{'identity_verified':True}}
    p.write_text(json.dumps(old),encoding='utf-8');git('add','-A');git('-c','user.name=t','-c','user.email=t@t','commit','-qm','baseline')
    p.write_text(json.dumps([*old,new]),encoding='utf-8');candidate=tmp_path/'candidate.json'
    pack(tmp_path,'all',candidate,'discovery')
    p.write_text(json.dumps(old),encoding='utf-8');merge_candidate(tmp_path,candidate)
    assert json.loads(p.read_text())==[*old,new]
    p.write_text(json.dumps([old[0],new]),encoding='utf-8')
    with pytest.raises(ValueError,match='Discovery cannot change'):pack(tmp_path,'all',candidate,'discovery')
