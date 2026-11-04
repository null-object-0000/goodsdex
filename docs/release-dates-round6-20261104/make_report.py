"""Produce auditable coverage/outcomes from the pinned public baseline and reviews."""
import collections,csv,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
rows=json.load(open('/tmp/goodsdex-round6-before.json'));new=json.load(open(ROOT/'new-candidates.json'));added={c['ids'][0]:c for c in new};probes={p['id']:p for p in json.load(open(ROOT/'dji-product-probes.json'))}
assert hashlib.sha256(Path('/tmp/goodsdex-round6-before.json').read_bytes()).hexdigest()=='1977d863ec6c6258eba19a4efba268196cccffa90101d5b3fee4e5910d21101d'
base=dict(data_revision='d266728aecf8427f448561af0a603290462cbf2b',goods_sha256=hashlib.sha256(Path('/tmp/goodsdex-round6-before.json').read_bytes()).hexdigest(),record_count=len(rows))
def save(name,x):(ROOT/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
save('baseline.json',base)
ledger=[]
for p in sorted((ROOT/'evidence').glob('*.json')):
 o=json.loads(p.read_text());ledger.append({k:o.get(k) for k in ['url','request','http_status','final_url','sha256','captured_at','raw_file','evidence_file','error']})
save('request-ledger.json',ledger)
out=[]
for r in rows:
 if r.get('brand') not in ['惠普','比亚迪','大疆','Apple','富士'] or any((r.get(f) or {}).get('date') for f in ['release','release_llm']):continue
 key=r['id'];b=r['brand'];c=added.get(key);p=probes.get(key)
 if c: status='added';reason=c['identity_review']
 elif b=='惠普':status='unresolved_source';reason='中国产品入口指向禁止重试的hpstore.cn；精确SKU搜索及新闻索引没有唯一国行上市证据，未扩大采集。惠普日期暂无可靠源。'
 elif b=='大疆':
  if r.get('kind')=='accessory':status='no_release_per_requested_policy';reason='配件独立SKU，不继承整机/套装/系列日期；按本轮要求列无发布日期。'
  elif 'ROMO' in r['name']:status='unresolved_variant';reason='旧款脚注仅写ROMO系列2025年8月，未证明P/A/S及水箱/自动上下水各版本；ROMO 2页面也没有精确型号日期。'
  elif '浅银灰' in r['name']:status='unresolved_variant';reason='2022年发布稿明确暗岩灰，不能用于后来浅银灰。'
  else:status='unresolved_exact_product';reason='单品页面无该精确SKU的明确上市事件日期；固件、促销、测试日期、主机脚注或不同配置发布稿均不采。'
 elif b=='比亚迪':status='unresolved_official_launch';reason='已检查汽车站/集团站历史新闻与新增官方直播21条目录；未取得本车型年款/配置的官方上市日期。年款不作为日期。'
 else:status='outside_this_round';reason='仅报告既有缺口，本轮未扩展Apple/富士采集。'
 out.append(dict(id=key,name=r['name'],brand=b,kind=r.get('kind'),model_year=r.get('model_year'),status=status,reason=reason,source_url=c['release']['evidence']['url'] if c else r.get('source_url'),date=c['release']['date'] if c else None,event=c['release']['event'] if c else None,quote=c['release']['evidence']['quote'] if c else None,capture_file=c['capture_file'] if c else p['capture_file'] if p else None,http_status=200 if c else p['http_status'] if p else None))
save('outcomes.json',out)
save('outcome-counts.json',{b:dict(collections.Counter(r['status'] for r in out if r['brand']==b)) for b in ['惠普','比亚迪','大疆','Apple','富士']})
with (ROOT/'new-dates.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=['id','name','brand','date','event','source_url','quote'],lineterminator='\n');w.writeheader()
 for r in out:
  if r['status']=='added':w.writerow({k:r[k] for k in w.fieldnames})
lines=['# 新增全检（4/4）','', '本轮新增不足20条，全部核验4条；不把已有记录或拒绝项冒充20条新增样本。','', '| 商品 | 月份 / 事件 | 来源及原文 |', '|---|---|---|']
for c in new:
 e=c['release']['evidence'];lines.append(f"| {c['name']} | {c['release']['date']} / {c['release']['event']} | [{e['url']}]({e['url']})：{e['quote']} {' '.join(e.get('supporting_quotes',[]))} |")
(ROOT/'review-all-new.md').write_text('\n'.join(lines)+'\n')
byd=[r for r in out if r['brand']=='比亚迪'];lines=['# 比亚迪逐条核对（14条）','','仅夏取得官方上市发布会日期，保留announcement语义；其余13条未写入release。年款缺失仍为未知，不补推年份。','', '| 车型 | 年款 | 上市时间 | 来源 URL / 原文或未获取原因 |','|---|---|---|---|']
for r in byd:
 lines.append(f"| {r['name']} | {r['model_year'] or '官方未明确'} | {r['date']+'（上市发布会，日为2025-11-04）' if r['date'] else '未取得可靠官方证据'} | [{r['source_url']}]({r['source_url']})：{r['quote'] or r['reason']} |")
lines+=['','未获取项的链接是原商品身份来源，不冒充上市证据；历史汉的原商品身份来自太平洋汽车，未将其年款转成日期。','', '检查范围：前轮汽车站171篇、集团站25篇新闻捕获复用；本轮官方直播接口21条、车型页、2025年智能化战略稿；详见request-ledger.json和byd-live-index.json。','汉智驾版2025年10月加推发布会旧链接当前404，且“加推”不能用于首次上市。第三代元PLUS的2026-04-24是首发亮相/预售活动，不能冒充2026年5月上市；目录未取得对应上市活动。']
(ROOT/'byd-14.md').write_text('\n'.join(lines)+'\n')
skus=['7Y0Y4PC','7Z5S1PC','915D1PC','9X2Y9PC','A93SZPC','B0RC4PC','BL9C1PC','BZ8Y6PA','BZ8Y8PA','CF7V8PC']
save('hp-probes.json',dict(product_search_queries=10,news_search_queries=10,product_http_operations=4,news_http_operations=2,threshold=.6,product_hits=0,news_hits=0,expanded=False,conclusion='惠普日期暂无可靠源',samples=[dict(id='CN:hp_cn:sku:'+s,unique_eligible_product_date=False,unique_eligible_news_date=False,reason='无精确国行SKU上市证据；服务兼容列表/驱动/论坛帖日期不采') for s in skus],notes=['搜索请求与源站HTTP操作分开统计；搜索引擎不返回源站状态码，不伪造为200。','产品HTTP4次为hp.com.cn入口、最终中国首页、OmniBook 7产品页、桌面工作站产品入口；新闻HTTP2次为中国关于页及其指向的美国newsroom。','10条探针为10个精确SKU检索案例，未找到10个可取日期的独立产品页；不会用无关页面充数。','京东/天猫/hpstore.cn请求数均为0；源站重定向由curl跟随，状态码记最终响应。']))
print(json.dumps(json.load(open(ROOT/'outcome-counts.json')),ensure_ascii=False,indent=2))
