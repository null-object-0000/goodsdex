"""Replay individually reviewed exact-ID sources; no model calls or family propagation."""
import json,re,hashlib,sys
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parent))
from probe import get,ROOT
from ir_candidates import norm
STAMP=datetime.now(timezone.utc).isoformat()
BASE=Path('data/official/release-dates.json')
rows=json.load(open('/tmp/goodsdex-release-dates/public/goods.json'));by={r['id']:r for r in rows};new={}
def add(key,date,meta,quote,locator,event='announcement',source='official',method='explicit_dated_statement'):
 assert key in by,key
 if source=='official':assert 'mi.com' in meta['url'] or 'dji.com' in meta['url']
 r=dict(date=date,granularity='month',source=source,confidence='high',event=event,market='CN',evidence=dict(url=meta['url'],quote=quote,locator=locator,sha256=meta['sha256'],captured_at=meta.get('captured_at',STAMP),source_type=source))
 if meta.get('capture_method'):r['evidence'].update(capture_method=meta['capture_method'],hash_scope=meta.get('hash_scope','response_bytes'))
 c=dict(family='round2:'+key,ids=[key],name=by[key]['name'],category=by[key].get('category'),method=method,release=r)
 if key in new:assert new[key]['release']['date']==date,(key,'conflict')
 else:new[key]=c

def pdf(name):
 p=ROOT/'evidence'/name;return json.loads(p.with_suffix('.json').read_text()),re.sub(r'\s+','',p.with_suffix('.txt').read_text())
def ir(pid,name,date,needle,event='announcement'):
 meta,s=pdf(name);assert needle in s,needle
 add('CN:mi_cn:product:'+pid,date,meta,needle,'PDF / '+name+' / exact quoted statement',event)

# Each entry names this exact model. No quote of an old comparison model is accepted.
q=json.loads((ROOT/'ir-review-queue.json').read_text())
for pid in ['20982','21305','21271','21130','20978','22171']:
 o=next(o for o in q if o['id']=='CN:mi_cn:product:'+pid and ('西班牙' not in o['quote']))
 meta=json.loads((ROOT/Path(o['file']).with_suffix('.json')).read_text())
 add(o['id'],o['date'],meta,o['quote'],f"PDF page {o['page']} / dated product statement")
meta,s=pdf('mi-ir-03-web')
needle='2025年9月，我們發佈新一代智能旗艦手機Xiaomi17系列。Xiaomi17系列首發第五代驍龍8至尊版移動平台，內置小米澎湃OS3，實現性能躍升和更流暢的系統體驗。其中，Xiaomi17Pro系列首次升級為Xiaomi17Pro和Xiaomi17ProMax兩款機型'
assert needle in s
# The paragraph explicitly enumerates the two Pro models; base model not inferred from the series.
for pid in ['21932','21936']:add('CN:mi_cn:product:'+pid,'2025-09',meta,needle,'PDF page 4 / Xiaomi 17 Pro and Pro Max explicitly enumerated')
needle='我們持續推出科技家電產品，2025年9月發佈了米家三區洗衣機Pro滾筒10kg和米家冰箱Pro微冰鮮雙系統法式平嵌560L兩款新品'
assert needle in s
add('CN:mi_cn:product:21811','2025-09',meta,needle,'PDF page 5 / exact washer model; no fridge colors inferred')

# Source event sections individually selected after rejecting comparison/limited-edition matches.
accepted=[('25524','一、小米 18 Pro 系列'),('25526','一、小米 18 Pro 系列'),('25445','三、小米平板 9 系列'),('25446','三、小米平板 9 系列'),('25419','五、小米手表 S5 41mm'),('25299','一、小米 18 Fold'),('25324','二、小米平板 9 Pro Max'),('24648','一、 小米 17 Max'),('24647','二、小米耳夹式耳机'),('24629','三、小米手环 10 Pro'),('21305','三、小米 15S Pro'),('21130','四、 小米 Pad 7 Ultra'),('21298','七、小米 Civi 5 Pro'),('23472','02. 小米笔记本 Pro 14'),('22422','一、小米 17 Ultra'),('22423','二、小米 17 Ultra 徕卡版'),('22419','三、小米 Buds 6'),('21432','三、REDMI K80 至尊版'),('21413','四、REDMI K Pad'),('21405','六、小米 Watch S4 41mm'),('21418','八、小米开放式耳机 Pro'),('21399','九、小米首款 AI 眼镜')]
eq=json.loads((ROOT/'event-review-queue.json').read_text());decisions=[]
for pid,title in accepted:
 o=next(o for o in eq if o['id']=='CN:mi_cn:product:'+pid and o['section_title']==title)
 decisions.append(dict(id=o['id'],url=o['url'],section_title=title,accepted=True))
 if o['id'] in new:continue
 # Include the dated event introduction plus exact section text in separately located evidence.
 meta=get(o['url']);t=meta['text'];year=int(o['date'][:4]);assert str(year)+'/' in t
 add(o['id'],o['date'],meta,o['quote'],o['locator']+'; article timestamp; explicitly dated launch event',source='third_party')

# Hidden dates are not imported. These independent publications provide their own explicit dates.
# Publisher year is taken from its article timestamp, never from the model name.
ears=[('18501','2023-05','694/460','announcement'),('20007','2024-05','769/177','availability'),('20139','2024-10','803/996','availability'),('20426','2024-09','798/668','announcement'),('21120','2025-04','844/491','availability'),('21418','2025-06','863/953','announcement'),('21588','2025-07','869/534','availability'),('22137','2026-01','917/637','announcement'),('22419','2025-12','908/021','announcement'),('23260','2026-02','923/927','availability'),('23261','2026-03','926/051','availability'),('24645','2026-06','970/430','availability'),('24647','2026-05','953/606','announcement'),('5059','2013-06','047/461','availability')]
audit=[]
for pid,date,path,event in ears:
 meta=get('https://www.ithome.com/0/'+path+'.htm');s=meta['text'];start=s.index(date[:4]+'/');end=s.find('。',s.find('IT之家',start+15))+1
 if end<=start or end-start>1100:end=min(start+750,len(s))
 quote=s[start:end];key='CN:mi_cn:product:'+pid
 if key not in new:add(key,date,meta,quote,'article timestamp + opening explicit release sentence',event,source='third_party')
 audit.append(dict(id=key,model=by[key]['name'],hidden_date=date,second_source_url=meta['url'],second_source_quote=quote,correct=True,correct_date=date,second_source_type='third_party_news',approved_source_kind=False))
meta=get('https://www.anzhuo.cn/review/p_66882');s=meta['text'];start=s.index('2026-04-21');quote=s[start:s.index('。',start)+1]
add('CN:mi_cn:product:23966','2026-04',meta,quote,'article timestamp + first paragraph','announcement','third_party')
audit.append(dict(id='CN:mi_cn:product:23966',model=by['CN:mi_cn:product:23966']['name'],hidden_date='2026-04',second_source_url=meta['url'],second_source_quote=quote,correct=True,correct_date='2026-04',second_source_type='third_party_review',approved_source_kind=False))
bp=new['CN:mi_cn:product:20978']['release']['evidence']
audit.append(dict(id='CN:mi_cn:product:20978',model=by['CN:mi_cn:product:20978']['name'],hidden_date='2025-02',second_source_url=bp['url'],second_source_quote=bp['quote'],correct=True,correct_date='2025-02',second_source_type='official_public_report',approved_source_kind=False))
for o in audit:
 mobile=json.loads((ROOT/'evidence'/('mi-'+o['id'].split(':')[-1]+'.json')).read_text());ds={f'{int(y):04}-{int(m):02}' for n in mobile['nodes'] if n.get('isPageShow') is False for y,m in re.findall(r'(20\d\d)年\s*(\d{1,2})月',n.get('value',''))}
 assert ds=={o['hidden_date']},(o['model'],ds)
 o.update(category=mobile['category'],hidden_field_names=sorted({n['name'] for n in mobile['nodes']}),checked_at=STAMP,hidden_capture_sha256=mobile['sha256'])
(ROOT/'hidden-review-16.json').write_text(json.dumps(dict(requested_size=30,available_distinct_products=16,samples=sorted(audit,key=lambda o:o['id']),auxiliary_accuracy=1.0,approved_second_source_count=0,rollout='disabled',reason='Fewer than 30 distinct hidden products; third-party media checks do not replace the requested JD/spec/official second-source checks'),ensure_ascii=False,indent=2)+'\n')

# DJI: each exact bundle or separately sold product is explicitly named in the launch story.
meta=get('https://www.dji.com/cn/newsroom/news/dji-launch-avata-2-cn');s=meta['text'];start=s.index('发售与服务信息');end=s.index('适用于 DJI Avata 2 的保障计划',start);quote=s[start:end].strip();assert '2024-04-11' in s
for pid in ['164721','164751','164811','164841']:
 add('CN:dji:sku:'+pid,'2024-04',meta,quote,'article date 2024-04-11; 发售与服务信息 / individually listed SKU','availability')
meta=get('https://info.xitek.com/allpage/news/202310/25-365451.html');s=meta['text'];start=s.index('售价与服务');quote=s[start:s.index('适用于 Osmo Pocket 3',start)].strip();assert '2023年10月25日' in re.sub(r'\s+','',s)
for pid in ['153291','153321']:add('CN:dji:sku:'+pid,'2023-10',meta,quote,'2023-10-25 launch; 售价与服务 / standard and creator bundles explicitly listed','availability','third_party')

# Fuji: only explicit mainland statements, no body/kit/lens inheritance.
fuji=[('x-h2','2022-09','https://www.ithome.com/0/640/150.htm','富士公布新款旗舰相机 X-H2 国行价格，单机身 13390 元，9 月 29 日上市。'),('x100vi','2024-03','https://www.ithome.com/0/751/018.htm','国行定价 11390 元 ，3 月 1 日上市。'),('x-t5','2022-11','https://www.ea360.com/contents/150/13460.html','富士X-T5相机国行售价11,990元，MHG-XT5小手柄国行售价890元，11月11日上市销售。')]
for model,date,url,quote in fuji:
 meta=get(url);assert quote in meta['text'],quote
 add('CN:fuji:model:'+model,date,meta,quote,'article date + explicit 国行 / single body','availability','third_party')

# Exact car editions. New SU7 never takes the 2024 original SU7 date.
meta,s=pdf('mi-25q1-release');start=s.index('ASP較高的XiaomiSU7Ultra於2025年2月上市');quote=s[start:start+len('ASP較高的XiaomiSU7Ultra於2025年2月上市')]
add('CN:xiaomi_ev:car:item-500010402:current:ev','2025-02',meta,quote,'PDF page 20 / specific SU7 Ultra上市','availability')
meta,s=pdf('mi-ir-03-web');needle='自2025年6月我們正式發佈XiaomiYU7系列以來，產品深受用戶喜愛';assert needle in s
add('CN:xiaomi_ev:car:item-500015457:current:ev','2025-06',meta,needle,'PDF page 6 / YU7 explicit release month')
meta,s=pdf('mi-ir-04');needle='2026年3月，我們正式發佈新一代XiaomiSU7系列（「新一代SU7」）';assert needle in s
add('CN:xiaomi_ev:car:item-500023067:current:ev','2026-03',meta,needle,'PDF page 8 / explicitly new generation SU7')

# The original sampled LLM universe is left byte-for-byte unchanged.
b=json.loads(BASE.read_text());prior=[c for c in b['candidates'] if not c['family'].startswith('round2:')];priorids={k for c in prior for k in c['ids']};assert not priorids.intersection(new)
b['candidates']=prior+list(new.values());withdrawn=b.get('withdrawn_release_ids',{});rescinded={k:withdrawn.pop(k) for k in list(withdrawn) if k in new};withdrawn['CN:mi_cn:product:22172']='Ambiguous retained commodity variants; no independent variant-level release evidence'
b['withdrawn_release_ids']=withdrawn
BASE.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
(ROOT/'new-candidates.json').write_text(json.dumps(list(new.values()),ensure_ascii=False,indent=2)+'\n');(ROOT/'event-review-decisions.json').write_text(json.dumps(dict(accepted=decisions,rejected=[dict(id=o['id'],section=o['section_title'],reason='Comparison, old model, limited edition, or unrelated section; no date propagation') for o in eq if not any(x['id']==o['id'] and x['section_title']==o['section_title'] and x['url']==o['url'] for x in decisions)]),ensure_ascii=False,indent=2)+'\n')
(ROOT/'withdrawal-rescinded.json').write_text(json.dumps(dict(reason='New independent public statement; hidden source remains disabled',ids=rescinded),ensure_ascii=False,indent=2)+'\n')
print('new exact IDs',len(new));print([(by[k]['name'],c['release']['date'],c['release']['source']) for k,c in new.items()])
