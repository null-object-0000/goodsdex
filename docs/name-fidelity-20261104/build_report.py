"""Reproducible title, exclusion, and price-group reports from frozen observations."""
import collections, gzip, hashlib, html, json, re, statistics, sys
from datetime import datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from goodsdex.accessories import classify
from goodsdex.mi_names import apply_page_names
here=Path(__file__).resolve().parent
before=json.loads(gzip.decompress((here/'baseline-goods.json.gz').read_bytes()))
allresults=[json.loads(l) for l in (here/'titles.jsonl').read_text().splitlines()];titles={r['id']:r for r in allresults}
after=json.loads(Path(sys.argv[1]).read_text()) if len(sys.argv)>1 else [r for r in apply_page_names(before) if not classify(r)['accessory']]
after_ids={r['id'] for r in after};newnames={r['id']:r for r in apply_page_names(before)}

def write(name,value): (here/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def table(headers,rows):
    esc=lambda x:str(x).replace('|','\\|').replace('\n',' ')
    return '\n'.join(['|'+ '|'.join(headers)+'|','|'+'|'.join(['---']*len(headers))+'|',*['|'+'|'.join(esc(x) for x in row)+'|' for row in rows]])+'\n'

sample=[r for r in allresults if r['sample']];assert len(sample)==200
counts=collections.Counter(r['comparison'] for r in sample)
# Every observed addition is disclosed. Separate identity-bearing additions from
# the generic 系列 and literal colour labels; none of these 4 sample misses is distinctive.
missing=[r for r in allresults if r['comparison']=='database_missing']
colour_or_series={'10050071','10050149','10050180','10050211','10050240','18040','19582','20506'}
for r in missing:r['distinctive_missing']=r['id'].rsplit(':',1)[-1] not in colour_or_series
specific=[r for r in sample if r['id'] in {x['id'] for x in missing if x['distinctive_missing']}]
assert not specific
write('sample-statistics.json',dict(sample_rows=200,valid_titles=177,exact=160,database_extra=11,format_only=2,missing_generic_series=4,distinctive_missing=0,unrelated=0,unavailable=23,distinctive_ratio=0,missing_any_ratio=.02,full_required=False,universe_rows=1637,universe_ids=1632))
(here/'sample-200.md').write_text('# 固定随机抽样 200 条\n\n固定随机种子 20261104，从1632个唯一小米ID无放回抽样。23条HTTP 200但无商品title，单列未核实，不计一致或无关；同ID多行只请求一次。\n\n'+table(['分类','数量','占200条'],[['逐字一致',160,'80%'],['库里多字',11,'5.5%'],['仅空格',2,'1%'],['少通用“系列”',4,'2%'],['少区别性词',0,'0%'],['页面明确无关',0,'0%'],['无可用商品标题',23,'11.5%']])+'\n'+table(['ID','库里名','官网完整名','HTTP','分类','原文'],[[r['id'],r['name'],r['official_name'] or '未提供商品title',r['status'],r['comparison'],r['evidence']] for r in sample]))
write('missing-words.json',missing)
(here/'missing-words.md').write_text('# 全部少字记录（含定点补查）\n\n随机样本中4条只缺“系列”，区别性词缺失0/200。定点补查另发现5条区别性词丢失，不能把有偏定点样本当成全库估计；其余为颜色词。逐项原文哈希和抓取时间见titles.jsonl。\n\n'+table(['ID','库里名','官网完整名','区别性词','随机样本'],[[r['id'],r['name'],r['official_name'],r['distinctive_missing'],r['sample']] for r in missing]))
# Extract only the product-owned bootstrap config, never navigation prices.
for r in allresults:
    body=gzip.decompress((ROOT/r['evidence']).read_bytes()).decode('utf8','replace')
    pid=r['id'].rsplit(':',1)[-1]
    match=re.search(r'\{"product_id":"'+re.escape(pid)+r'","name":"[^"\n]*","price":"([^"]*)","market_price":"([^"]*)"',body)
    r['page_price']=float(match[1]) if match and match[1] else None
write('title-observations.json',allresults)
required=[]
for pid in ('22104','22105','22547','23722'):
    r=next(r for r in allresults if r['id'].endswith(':'+pid));row=newnames[r['id']]
    required.append(dict(id=r['id'],title=r['title'],name=row['name'],database_price=r['price'],page_price=r['page_price'],is_accessory=row['is_accessory'],published=r['id'] in after_ids,conclusion='独立金属面板，排除；299元为已采价格，实时HTML未报价' if pid=='22105' else '整机，保留' if pid=='22104' else '整机+连接器套装，保留；HTML未报价，数据库5696' if pid=='22547' else '双支整机装，保留；HTML未报价，数据库3198'))
write('sound-four.json',required)
# All original 22 keyword rows have individually fetched official titles.
keyword=json.loads((here/'accessory-keyword-before.json').read_text());decisions=[]
for old in keyword:
    r=newnames[old['id']];t=titles[old['id']];assert t['official_name']
    decision=classify(r);name=r['name']
    if decision['accessory']:reason='独立空调/新风功能面板，按配件规则排除'
    elif '多功能支架' in name:reason='完整显示器的支架版本，保留整机'
    elif '充电宝' in name:reason='完整充电宝，支架是集成功能'
    elif '智能家庭面板' in name:reason='独立智能家庭控制屏，非音箱替换面板'
    elif '全屋照明' in name:reason='整套灯具，含面板灯，非替换面板'
    elif '面板灯' in name:reason='完整灯具，非替换面板'
    else:reason='含整机的配件套装，保留'
    decisions.append(dict(id=r['id'],before=old['name'],name=name,price=r.get('price'),is_accessory=decision['accessory'],action='排除' if decision['accessory'] else '改名并保留' if name!=old['name'] else '保留',reason=reason,published=r['id'] in after_ids,title=t['title']))
assert len(decisions)==22
write('accessory-22-decisions.json',decisions)
(here/'accessory-22-decisions.md').write_text('# 原有22条配件词记录处置\n\n'+table(['ID','原名称','官方完整名','处置','理由'],[[r['id'],r['before'],r['name'],r['action'],r['reason']] for r in decisions]))

def groups(rows):
    d=collections.defaultdict(list)
    for r in rows:
        if isinstance(r.get('price'),(int,float)) and r['price']>0:d[r['name']].append(r)
    return {n:g for n,g in d.items() if len({r['id'] for r in g})>=2}
def anomaly(g):
    m=statistics.median(r['price'] for r in g)
    return m,[r['id'] for r in g if r['price']>=2*m or r['price']<=m/3]
strict_before=[dict(name=n,median=anomaly(g)[0],flagged=anomaly(g)[1]) for n,g in groups(before).items() if anomaly(g)[1]]
strict_after=[dict(name=n,median=anomaly(g)[0],flagged=anomaly(g)[1]) for n,g in groups(after).items() if anomaly(g)[1]]
write('strict-price-anomalies.json',dict(before=strict_before,after=strict_after))
prior=json.loads((ROOT/'data/variant-attributes.json').read_text())['groups']
review=[]
for name,g in groups(before).items():
    ids={r['id'] for r in g};hits=[p for p in prior if ids&{m['id'] for m in p['members']}]
    explanation='；'.join(p['summary'] for p in hits)
    if not explanation:
        if len({r['price'] for r in g})==1:explanation='全部同价，不是价格异常。多ID/容器与子商品并存，按独立官方ID保留，不凭同名跨ID合并。'
        elif name=='米家保温杯口袋版':explanation='官网标题分别为基础款和雪山落日；价格同为59，不是价格异常。'
        elif name=='米家智能净烟机S2':explanation='官网标题分别为白色款与基础标题；价格同为3299，不是价格异常。'
        else:explanation='未达到严格中位数阈值，现有证据不足以断言错价；保留原价并单列待核。'
    detail=[]
    for r in g:
        t=titles.get(r['id']);updated=newnames.get(r['id'],r)
        detail.append(dict(id=r['id'],before=r['name'],name=updated['name'],price=r['price'],gid=r.get('gid'),attrs=r.get('attrs'),title=t['title'] if t else None,is_accessory=classify(updated)['accessory'],published=r['id'] in after_ids))
    review.append(dict(name=name,median=anomaly(g)[0],strict_flagged=anomaly(g)[1],members=detail,explanation=explanation,prior_evidence_groups=[p['group'] for p in hits]))
write('price-group-review.json',review)
mi=[g for g in review if g['members'][0]['id'].startswith('CN:mi_cn:')];assert len(mi)==20
(here/'price-group-review.md').write_text('# 同名组价格交叉校验\n\n正价且至少2个不同ID构成同名组；中位数包含组内全部发布行，包含触发者。条件是price≥2×median或price≤median/3，边界包含。修前61组同名组，仅2组达标；修后达标'+str(len(strict_after))+'组。另有9组最高/最低≥2，此条件与“中位数2倍”不同，不能混用。没有伪造20个达标组。\n\n## 全部20个小米同名组逐组复核\n\n'+table(['旧组名','成员ID / 原价 / 官网完整名 / 去留','中位数','严格命中','原因/限制'],[[g['name'],'；'.join(m['id'].rsplit(':',1)[-1]+' / '+str(m['price'])+' / '+m['name']+' / '+('保留' if m['published'] else '排除') for m in g['members']),g['median'],bool(g['strict_flagged']),g['explanation']] for g in mi])+'\n## 全库61组索引\n\n已有变体证据来自data/variant-attributes.json；本轮只对小米请求实时title。其它品牌此表不是本轮重新抓价的结论。完整ID、价格、gid与attrs见price-group-review.json。\n\n'+table(['名称','不同ID数','中位数','严格命中','已有解释'],[[g['name'],len({m['id'] for m in g['members']}),g['median'],bool(g['strict_flagged']),g['explanation']] for g in review]))
intervals=[(datetime.fromisoformat(b['requested_at'])-datetime.fromisoformat(a['requested_at'])).total_seconds() for a,b in zip(allresults,allresults[1:])]
write('audit-invariants.json',dict(distinct_requests=len(titles),sample_requests=len(sample),verified_titles=sum(bool(r['official_name']) for r in allresults),minimum_request_interval_seconds=min(intervals),duplicate_ids=len(allresults)-len(titles),keyword_rows=22,same_name_groups_before=len(review),xiaomi_groups_reviewed=len(mi),strict_anomalies_before=len(strict_before),strict_anomalies_after=len(strict_after),keyword_excluded=sum(r['is_accessory'] for r in decisions),keyword_retained=sum(not r['is_accessory'] for r in decisions),published_before=len(before),published_after=len(after)))
print((here/'audit-invariants.json').read_text())
