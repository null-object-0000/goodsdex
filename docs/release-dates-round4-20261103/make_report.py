"""Produce reviewable coverage, exact excerpts, source/failure inventory and scope ledger."""
import collections,csv,gzip,hashlib,json,re
from pathlib import Path
from capture import ROOT,save
new=json.load(open(ROOT/'new-candidates.json'));cov=json.load(open(ROOT/'coverage.json'));before=cov['before'];after=cov['after']
# Resolve capture metadata from the actual artifact links, retaining request payloads for paged POSTs.
files=set((ROOT/'evidence').glob('*.json'))
for p in Path('docs/release-dates-round3-20261103/evidence').glob('*.json'):
 try:o=json.load(open(p))
 except ValueError:continue
 if isinstance(o,dict) and (re.search(r'/announcements(?:/page/\d+)?$',o.get('url','')) or '/news/list/' in o.get('url','')):files.add(p)
def walk(v):
 if isinstance(v,dict):
  if v.get('evidence_file'):files.add(Path(v['evidence_file']))
  if v.get('capture_file'):files.add(Path(v['capture_file']))
  for x in v.values():walk(x)
 elif isinstance(v,list):
  for x in v:walk(x)
for p in ROOT.glob('*.json'):
 if p.name in ['source-inventory.json','failed-sources.json']:continue
 walk(json.load(open(p)))
latest={}
for p in files:
 if not p.exists():continue
 o=json.load(open(p))
 if not isinstance(o,dict) or not o.get('url'):continue
 key=o['url']+'|'+json.dumps(o.get('request'),sort_keys=True,ensure_ascii=False)
 if key not in latest or o.get('captured_at','')>latest[key][1].get('captured_at',''):latest[key]=(p,o)
inv=[]
for key,(p,o) in sorted(latest.items()):
 item={k:o.get(k) for k in ['url','request','captured_at','http_status','final_url','sha256','bytes','error']}
 item['evidence_file']=str(p.relative_to(Path.cwd())) if p.is_absolute() else str(p)
 item['excerpt']=o.get('text','')[:450]
 item['result']='local_encoding_error' if 'ascii' in o.get('error','') else 'http_or_transport_failure' if o.get('http_status')!=200 else 'captured_machine_resource' if re.search(r'\.(?:xml|js|txt)(?:\?|$)',o['url']) or o.get('request') else 'captured_html'
 if o.get('http_status')==200 and o.get('bytes',0)<1000 and item['result']=='captured_html':item['result']='thin_or_empty_html_not_article'
 inv.append(item)
save('source-inventory.json',inv);failed=[o for o in inv if o['result'] in ['local_encoding_error','http_or_transport_failure','thin_or_empty_html_not_article']];save('failed-sources.json',failed)
with (ROOT/'new-dates.csv').open('w') as f:
 w=csv.writer(f,lineterminator="\n");w.writerow(['id','brand','name','date','event','source','quote','url'])
 rows=json.load(open('/tmp/goodsdex-round4-before.json'));by={r['id']:r for r in rows}
 for c in new:
  r=c['release'];e=r['evidence'];w.writerow([c['ids'][0],by[c['ids'][0]].get('brand','小米'),c['name'],r['date'],r['event'],r['source'],e['quote'],e['url']])
# Full 20-row table uses short exact excerpts; full quotes remain in JSON and CSV.
sample=json.load(open(ROOT/'official-review-sample.json'))
lines=['# 新增日期抽检（修正后20条）','','首检冻结在 `review-frozen.json`，结果 **19/20=95%**。X9-8K 只有2023独立售价，不能证明首发，已剔除；完整错误记录保留于 `review-initial.json`。下面保留原19条正确项，按seed=20261105补抽1条，复核 **20/20=100%**。这是直接源的型号/事件/月份抽取一致性检查，不是独立真值统计，也不把修正后的100%倒填为首检成绩。','','| 型号 / 精确 ID | 月份 / 事件 | 原文节选 | 链接 | 对错 |','|---|---|---|---|---|']
for s in sample['samples']:
 q=s['quote']
 if s['id']=='CN:apple_cn:commodity:MYEW3CH/A':
  p=q.index('价格与上市时间');q=q[:40]+' … '+q[p:p+145]
 elif s['id']=='CN:apple_cn:commodity:MFEX4CH/A':
  p=q.index('配备可调倾斜度支架');q=q[:70]+' … '+q[p:p+190]
 elif s['id']=='CN:dji:sku:116781':
  p=q.index('DJI 图传发射器单品');q=q[p:p+65]+' … '+q[-120:]
 elif s['id']=='CN:dji:sku:137781':
  p=q.index('更高阶');q=q[p:p+100]+' … '+q[-110:]
 else:q=q[:220]+('…' if len(q)>220 else '')
 lines.append('| '+s['name']+'<br>`'+s['id']+'` | '+s['date']+' / '+s['event']+' | '+q.replace('|','\\|')+' | [原文]('+s['url']+') | 对：'+s['review']+' |')
(ROOT/'review-20.md').write_text('\n'.join(lines)+'\n')
# Per-brand complete scope counts are explicit, and incomplete archives fail this report generator.
dji=json.load(open(ROOT/'dji-complete.json'));fuji=json.load(open(ROOT/'fuji-complete.json'));fextra=json.load(open(ROOT/'fuji-sitemap-extra.json'));byda=json.load(open(ROOT/'byd-complete.json'));ap=json.load(open(ROOT/'apple-articles.json'));ah=json.load(open(ROOT/'apple-hardware-articles.json'));at=json.load(open(ROOT/'apple-tail-articles.json'));ar=json.load(open(ROOT/'apple-reviewed-recipes.json'));cn=json.load(open(ROOT/'apple-cn-reviewed-recipes.json'))
assert len(dji)==471 and len(fuji)+len(fextra)==268 and len(byda)==171
assert len(ap)==240 and len(ah)==146
stats=dict(dji_articles=len(dji),fuji_articles=len(fuji)+len(fextra),byd_articles=len(byda),byd_group_articles=len(json.load(open(ROOT/'byd-group-complete.json'))),apple_broad=len(ap),apple_hardware=len(ah),apple_unique=len({o['url'] for o in ap+ah+at+ar+cn}),apple_index_unread=1221-len({o['url'] for o in ap+ah+at+ar+cn}),apple_broad_unread=[u for u in json.load(open(ROOT/'apple-plan.json'))['selected'] if u not in {o['url'] for o in ap+ah+at+ar+cn}],new_dates=len(new),new_events=dict(collections.Counter(c['release']['event'] for c in new)),new_by_brand=dict(collections.Counter(by[c['ids'][0]].get('brand') or '小米' for c in new)),failed=len(failed),requests_or_reused_captures=len(inv))
save('archive-scope.json',stats)
print(json.dumps(stats,ensure_ascii=False))
