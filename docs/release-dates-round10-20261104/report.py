"""Recompute full published-row census, additions and bounded-source absences."""
import collections,gzip,hashlib,json,pathlib,re,unicodedata
from goodsdex.release_dates import apply_release_dates
from goodsdex.series_release import apply_series_releases
from goodsdex.release_scope import scope_coverage,release_scope,displayable
ROOT=pathlib.Path(__file__).resolve().parent
before=json.loads(gzip.decompress((ROOT/'baseline.json.gz').read_bytes()))
after=apply_series_releases(apply_release_dates(before))
assert apply_series_releases(apply_release_dates(after))==after
for a,b in zip(before,after,strict=True):
 assert {k:v for k,v in a.items() if k not in ('release','release_series')}=={k:v for k,v in b.items() if k not in ('release','release_series')}
 if a.get('brand')=='Apple' and displayable(a.get('release')):assert a['release']==b['release']
(ROOT/'expected.json.gz').write_bytes(gzip.compress(json.dumps(after,ensure_ascii=False).encode()))
cs=json.load(open(ROOT/'new-candidates.json'))+json.load(open(ROOT/'apple-new-candidates.json'))
series=json.load(open(ROOT/'new-series-batches.json'));newids={i for c in cs for i in c['ids']}
assert len(newids)==len(cs)==159
summary=dict(before=scope_coverage(before),after=scope_coverage(after),new_product_assertions=len(cs),new_series_assertions=len(series),new_product_events=dict(collections.Counter(c['release']['event'] for c in cs)),new_series_events=dict(collections.Counter(c['series_release']['event'] for c in series)),apple_locked_unchanged=417)
summary['brands']={}
for brand in ('富士','大疆','Apple','小米'):
 old=[r for r in before if r.get('brand')==brand];new=[r for r in after if r.get('brand')==brand]
 summary['brands'][brand]=dict(new_product_assertions=sum(c['brand']==brand for c in cs),new_series_assertions=sum(len(b['members']) for b in series) if brand=='小米' else 0,before_all_displayable=sum(displayable(r.get('release')) or displayable(r.get('release_series')) for r in old),after_all_displayable=sum(displayable(r.get('release')) or displayable(r.get('release_series')) for r in new),total=len(new),machine_before=summary['before']['brands'][brand],machine_after=summary['after']['brands'][brand],new_events=dict(collections.Counter(c['release']['event'] for c in cs if c['brand']==brand)))
# Capture inventory distinguishes failures from source absence.
captures=[json.load(open(p)) for p in sorted((ROOT/'evidence').glob('*.json'))]
(ROOT/'source-inventory.json').write_text(json.dumps([{k:v for k,v in c.items() if k!='links'} for c in captures],ensure_ascii=False,indent=2)+'\n')
corpus={b:[] for b in ('富士','大疆','Apple','小米')}
for c in captures:
 if c['status']!=200:continue
 u=c['url'];brand='Apple' if 'apple.com/' in u else '大疆' if 'dji.com/' in u else '小米' if 'mi.com/' in u else '富士'
 corpus[brand].append(pathlib.Path(c['text_file']).read_text())
def norm(s):return re.sub(r'[^0-9A-Z\u4e00-\u9fff]+','',unicodedata.normalize('NFKC',s).upper().replace('FUJIFILM','').replace('FUJINON','').replace('DJI',''))
dji_history=norm(pathlib.Path(ROOT/'evidence/d3f980139926018edc50.txt').read_text())
ledger=[];unresolved=[]
for ordinal,(a,b) in enumerate(zip(before,after,strict=True)):
 brand=b.get('brand')
 if brand not in corpus:continue
 covered=displayable(b.get('release')) or displayable(b.get('release_series'))
 item=dict(ordinal=ordinal,id=b['id'],name=b['name'],brand=brand,tier=release_scope(b)['tier'],covered_before=displayable(a.get('release')) or displayable(a.get('release_series')),covered_after=covered,new_product=b['id'] in newids,new_series=any(b['id']==m['id'] for s in series for m in s['members']))
 if covered:item['status']='accepted_new' if item['new_product'] or item['new_series'] else 'locked_existing'
 elif brand=='富士':
  if ':kit:' in b['id']:
   item.update(status='exact_variant_not_listed_in_corpus',reason='未取得该完整机身+镜头组合自己的日期字段；只列机身的表格不能继承给套机')
  else:item.update(status='identity_or_event_ambiguous',reason='X-Pro3官方表按黑色/DR黑/DR银列出2019-11、2019-12、2020-01；本行无颜色身份，不擅自统一')
 elif brand=='大疆':
  if norm(b['name']) in dji_history:
   item.update(status='model_present_without_month',reason='官方发展历程提到精确型号但仅有年份；比较页面/产品线目录没有可读月份')
  else:item.update(status='exact_variant_not_listed_in_corpus',reason='本轮官方发展历程/比较/产品线材料未列这个完整型号或加配组合的日期；基础整机的推出年/月不能继承')
 elif brand=='Apple':
  if (b.get('release') or {}).get('source')=='official':item.update(status='locked_official_internal',reason='既有官方记录仍被原门禁禁用/保留；未改写已锁定断言')
  elif b['id'].startswith('CN:apple_cn:commodity:'):item.update(status='identity_or_event_ambiguous',reason='历史公告不足以证明该购买料号/配置的availability；不凭泛系列名或当前页发布时间推断')
  else:item.update(status='no_eligible_availability_statement',reason='已纳入Newsroom全量目录匹配，但未审核到该精确代/尺寸/端口/版本的一致availability原句；有年份/发布不代替发售')
 else:
  if b['name']=='Redmi':item.update(status='identity_or_event_ambiguous',reason='发展历程提及Redmi品牌独立，不是此泛名称商品的发布；商品型号不能唯一确定')
  elif b['name'] in ('米家 LED 智能台灯','小米米家电动滑板车'):item.update(status='model_present_without_month',reason='官网历史确实提及型号，但年月对应设计获奖，不是推出/上市/开售；不以获奖日补发布日期')
  elif '小米笔记本Air' in b['name']:item.update(status='identity_or_event_ambiguous',reason='发展历程只说2016首款小米笔记本Air，不能唯一匹配12.5英寸/四核增强的具体代')
  else:item.update(status='exact_variant_not_listed_in_corpus',reason='小米官网发展历程2010—2023未列此完整型号的年月+发布/开售陈述；不向后续代、精选品牌或配件传播')
 ledger.append(item)
 # Fuji audit includes lenses; the other brands' acceptance uses the fixed machine denominator.
 if not covered and (item['tier']=='machine' or brand=='富士'):unresolved.append(item)
(ROOT/'census.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n')
(ROOT/'unresolved.json').write_text(json.dumps(unresolved,ensure_ascii=False,indent=2)+'\n')
summary['unresolved_reasons']={b:dict(collections.Counter(r['status'] for r in unresolved if r['brand']==b)) for b in corpus}
summary['captured_requests']=len(captures);summary['capture_statuses']=dict(collections.Counter(str(c['status']) for c in captures));summary['census_rows']=len(ledger)
(ROOT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
# A deterministic stratified sample, favouring different URLs and explicit dated headlines.
idx={c['ids'][0]:c for c in cs};pick=['CN:fuji:model:x-s20','CN:fuji:model:x100vi','CN:fuji:kit:x-e5-xf23mmf28-r-wr','CN:fuji:kit:x-h2-16-80mm']
lenses=[c['ids'][0] for c in cs if c['ids'][0].startswith('CN:fuji:lens:')]
import random
pick+=random.Random(20261104).sample(sorted(lenses),8)
pick+=['GLOBAL:apple_support:model:'+str(i) for i in [111940,111891,111984,111855,111994,112019,112025,112024]]
assert len(pick)==len(set(pick))==20
sample=[];md=['# 20条实际新增断言抽样','', '固定分层样本：两条财报回溯、两条独立套机页、seed=20261104的八条镜头、八条不同Newsroom页面。不是20条随机成功率估计。日本原文“発売日”即发售日期；美国/日本日期不表示国行。标题/日期上下文与正文分别标示，不拼造连续原句。','']
for number,key in enumerate(pick,1):
 c=idx[key];r=c['release'];e=r['evidence'];cap=next(a for a in captures if a['url']==e['url']);lines=pathlib.Path(cap['text_file']).read_text().splitlines()
 if c['brand']=='Apple':
  # Prefer an exact dated availability headline; retain the full body in candidate JSON.
  title=lines[0].removesuffix(' - Apple');snippet=title;context=next(t for t in e['supporting_quotes'] if re.fullmatch('[A-Z][a-z]+ \\d{1,2}, \\d{4}',t))
 else:snippet=(e.get('identity_quote','').splitlines() or [''])[0];snippet=(snippet+'；' if snippet else '')+e['quote'];context=''
 sample.append(dict(id=key,name=c['name'],date=r['date'],event=r['event'],market=r['market'],url=e['url'],fragment=snippet,date_context=context,full_evidence=e))
 md += [f'## {number}. {c["name"]}', '', f'`{key}` → {r["date"]} / `{r["event"]}` / `{r["market"]}`', '', f'[官方原文]({e["url"]})', '', '> '+snippet.replace('\n','\n> ')]
 if context:md += ['', '> 原文日期上下文：'+context]
 md += ['']
(ROOT/'sample-20.json').write_text(json.dumps(sample,ensure_ascii=False,indent=2)+'\n');(ROOT/'sample-20.md').write_text('\n'.join(md)+'\n')
# The Top 20 are unique exact names not listed in this bounded corpus; other failure causes stay separate.
absent=[r for r in unresolved if r['status']=='exact_variant_not_listed_in_corpus'];top=[]
for brand in ('富士','大疆','小米','Apple'):
 for r in absent:
  if r['brand']==brand and r['name'] not in {x['name'] for x in top}:top.append(r)
(ROOT/'absent-top20.json').write_text(json.dumps(top[:20],ensure_ascii=False,indent=2)+'\n')
print(json.dumps({b:{'new':summary['brands'][b]['new_product_assertions'],'machine':summary['after']['brands'][b]['covered'],'denominator':summary['after']['brands'][b]['machine']} for b in summary['brands']},ensure_ascii=False));print(json.dumps(summary['unresolved_reasons'],ensure_ascii=False));print('requests',len(captures),'census',len(ledger))
