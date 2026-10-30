"""Read-only acceptance against the deployed public API and released data."""
import json
from pathlib import Path
from urllib.parse import urlencode, quote
from urllib.request import urlopen

OUT=Path(__file__).resolve().parent
BASE='https://spend.snewbie.site/api/goods'
responses={}
def get(name,suffix):
    with urlopen(BASE+suffix,timeout=45) as response:
        value=json.load(response)
    responses[name]=value
    return value
byd=get('byd','/search?'+urlencode({'brand':'比亚迪'}))
xiaomi=get('xiaomi','/search?'+urlencode({'brand':'小米汽车'}))
assert byd['total']==8 and xiaomi['total']==3
assert sum(len(r['trims']) for r in byd['items'])==38
assert sum(len(r['trims']) for r in xiaomi['items'])==10
assert all(r['model_year'] is None for r in xiaomi['items'])
assert all(r['image_scope']=='series' for r in xiaomi['items'])
su7=next(r for r in xiaomi['items'] if r['series']=='SU7')
assert su7['name']=='小米汽车 新一代 SU7'
assert {x['value']:x['count'] for x in byd['facets']['series']}=={'汉':3,'海豚':1,'夏':1,'宋Pro':1,'元PLUS':1,'秦PLUS':1}
assert {x['value']:x['count'] for x in byd['facets']['powertrain']}=={'DM-i':5,'EV':3}
assert xiaomi['facets']['powertrain']==[{'value':'EV','count':3}]
found=get('han121','/search?'+urlencode({'q':'汉 121','group_products':'1'}))
assert found['total']==1 and found['items'][0]['display_name']=='比亚迪 汉 2022款 DM-i'
pid='CN:byd:car:han:2022:dmi'
full=get('han2022','/'+quote(pid,safe=''))
assert full['model_year_source']=='pcauto' and full['model_year_confidence']=='third_party'
assert full['image'] is None and full['image_status']=='official_unavailable'
assert len(full['trims'])==5
assert all(t['image'] is None and t['image_status']=='official_unavailable' for t in full['trims'])
legacy_id='CN:byd:car:han-dmi:2022:121km-112979'
legacy=get('legacy121','/'+quote(legacy_id,safe=''))
assert legacy['product_id']==pid and legacy['trim_id']==legacy_id
assert legacy['trim']=='121KM 尊贵型' and legacy['price']==215800
assert legacy['params']['NEDC纯电续航里程(km)']=='121'
picker=get('picker','?'+urlencode({'product_ids':pid}))
assert len(picker['items'])==5 and picker['presentations'][0]['sku_count']==5
assert [d['label'] for d in picker['presentations'][0]['dimensions']]==['年款','动力','配置']
filtered=get('filtered','/search?'+urlencode({'brand':'比亚迪','series':'汉','powertrain':'DM-i'}))
assert filtered['total']==2
no_year=get('su7-picker','?'+urlencode({'product_ids':su7['id']}))
assert no_year['presentations'][0]['dimensions'][0]['options'][0]['label']=='不记得年款'
(OUT/'online-responses.json').write_text(json.dumps(responses,ensure_ascii=False,indent=2)+'\n')
report={'passed':True,'byd_products':8,'byd_trims':38,'xiaomi_products':3,'xiaomi_trims':10,'legacy_121_resolves':True,'historical_images_null':True,'su7_official_name':su7['name'],'su7_year':None,'series_facets':byd['facets']['series']+xiaomi['facets']['series'],'powertrain_facets':{'DM-i':5,'EV':6},'request_count':len(responses)}
(OUT/'online-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
