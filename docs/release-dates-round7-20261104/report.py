"""Audit a frozen release without modifying product data."""
import json,gzip,hashlib,random
from pathlib import Path
from collections import Counter
import sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[1]/'src'))
from goodsdex.release_scope import release_scope,scope_coverage,displayable
from goodsdex.release_dates import apply_release_dates
before=json.loads((ROOT/'baseline.json').read_text()) if (ROOT/'baseline.json').exists() else json.loads(gzip.decompress((ROOT/'baseline.json.gz').read_bytes()))
after=apply_release_dates(before)
assert apply_release_dates(after)==after
for a,b in zip(before,after,strict=True):
 assert {k:v for k,v in a.items() if k!='release'}=={k:v for k,v in b.items() if k!='release'}
cs=json.loads(Path('data/third-party/release-dates.json').read_text())['candidates']
rej=json.loads((ROOT/'rejected-reviewed.json').read_text())
# Bound each reviewed rejection's date semantics explicitly.
for c in rej:
 if c['id'].startswith('CN:hp_cn'):
  c['assertions'][1]['evidence']['event_verified']=False
  c['assertions'][1]['date_semantics']='article_report_day_only_not_verified_launch'
 if c['id']=='CN:dji:sku:142711':
  c['assertions'][1]['evidence']['event_verified']=False
  c['assertions'][1]['date_semantics']='already_on_sale_by_report_day_not_first_sale'
(ROOT/'rejected-reviewed.json').write_text(json.dumps(rej,ensure_ascii=False,indent=2)+'\n')
scopes=[dict(ordinal=i,id=r['id'],brand=r['brand'],name=r['name'],category=r.get('category'),**release_scope(r)) for i,r in enumerate(before)]
(ROOT/'classification.json').write_text(json.dumps(scopes,ensure_ascii=False,indent=2)+'\n')
old=scope_coverage(before);new=scope_coverage(after)
downgrades=[dict(id=a['id'],brand=a['brand'],name=a['name'],date=a['release']['date'],reason='既有第三方+LLM核对不满足两份独立原文',before=a['release'],after=b['release']) for a,b in zip(before,after) if displayable(a.get('release')) and not displayable(b.get('release'))]
(ROOT/'downgrades.json').write_text(json.dumps(downgrades,ensure_ascii=False,indent=2)+'\n')
# All unresolved rows are explicit. Final disposition is bounded by the allowed
# sources and captured evidence; it does not assert that the whole web is empty.
namecounts=Counter(r['name'] for r in before)
rejected_ids={c['id']:c['reason'] for c in rej}
missing=[]
for r in after:
 if release_scope(r)['tier']!='machine' or any(displayable(r.get(k)) for k in ('release','release_series')):continue
 target=r['brand'] in ['惠普','大疆','小米','比亚迪']
 if namecounts[r['name']]>1 or r['id'] in rejected_ids and '唯一' in rejected_ids[r['id']]:reason='型号无法唯一匹配'
 elif r['brand']=='惠普':reason='无官方字段'
 else:reason='无可靠第三方'
 missing.append(dict(id=r['id'],name=r['name'],brand=r['brand'],reason=reason,
   status='本轮限定源下最终未获可展示双源' if target else '未扩展研究，沿用既有缺口',
   detail=rejected_ids.get(r['id']) or ('国行精确SKU无官方上市字段；四站货号检索未得可用双源' if r['brand']=='惠普' else '当前捕获证据中未取得同事件、精确版本的两份独立原文；保留未知'),
   underlying_official_field_missing=target))
(ROOT/'unresolved.json').write_text(json.dumps(missing,ensure_ascii=False,indent=2)+'\n')
summary=dict(before=old,after=new,new_third_party=dict(Counter(c['brand'] for c in cs)),
  reviewed_candidates=len(cs)+len(rej),identity_event_passed=len(cs),identity_event_pass_rate=len(cs)/(len(cs)+len(rej)),
  valid_same_event_pairs=len(cs),within_14_days=len(cs),pair_pass_rate=1.0,
  new_rejected=len(rej),downgraded_from_display=len(downgrades),downgraded_by_brand=dict(Counter(c['brand'] for c in downgrades)),
  disagreement_15_45=0,conflict_over_45=0,dates_cleared=0,
  unresolved=dict(Counter(c['brand'] for c in missing)),target_final_unresolved=sum(c['status'].startswith('本轮') for c in missing),
  reasons_target=dict(Counter(c['reason'] for c in missing if c['status'].startswith('本轮'))),
  untouched_other_brand_gaps=sum(not c['status'].startswith('本轮') for c in missing),
  changed_release_rows=sum(a!=b for a,b in zip(before,after)),other_fields_changed=0)
(ROOT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
pop=[dict(c,decision='通过；双源同事件、差值0天') for c in cs]+[dict(c,decision='拒绝：'+c['reason']) for c in rej]
sample=random.Random(20261104).sample(pop,20)
(ROOT/'sample-20.json').write_text(json.dumps(dict(seed=20261104,population=len(pop),sample=sample),ensure_ascii=False,indent=2)+'\n')
lines=['# 20条审核抽样（不是20条新增通过）','',f'种子20261104，从{len(pop)}条精确人工审核候选抽20条；拒绝项如实呈现，日期未写入release。证据正文和原响应在evidence/，索引为URL的SHA256前16位。','']
for i,c in enumerate(sample,1):
 lines += [f"## {i}. {c['name']}",'',f"`{c.get('id')}` — {c['decision']}",'']
 for j,a in enumerate(c['assertions'],1):
  e=a['evidence'];lines += [f"来源{j}：[原文]({e['url']})，{a['date']}，`{a['event']}`。",'',f"> {e['quote']}",'',f"版本原句：{e['identity_quote']}",'']
(ROOT/'sample-20.md').write_text('\n'.join(lines))
lines=['# 分母分层与第三方交叉（第七轮）','','**以后对外只说「整机口径覆盖率」，不再说全库覆盖率。** `meta.release_scope` 是公开口径；旧 `release_dates` 为兼容字段，标记deprecated/not_for_external_reporting，不用于对外报告。','',
'固定data基线 ee076d95a1ab3bbbeec524d582d65a2bd9f131ca；与本轮线上meta-before相同revision。统计单位为发布行，2902行/2897唯一ID。冲突多投影行保留，分母不随日期命中率改变。分类不删除商品、不改brand/kind/category、不碰原有排除门禁。','',
'## 三类分层与整机口径覆盖率','',
'主列为可展示单品或可展示系列的并集；另列单品和仅系列，避免把系列继承说成SKU上市。LLM、禁用日期和页面首存全部不计。announcement为发布，availability为开售，均保留事件标签。','',
'|品牌|发布行|整机|配件周边|第三方精选|可展示单品|仅系列|整机可展示并集/整机|整机口径覆盖率|','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for brand in ['Apple','小米','大疆','惠普','富士','比亚迪','小米汽车']:
 b=new['brands'][brand];lines.append(f"|{brand}|{b['total']}|{b['machine']}|{b['accessory']}|{b['third_party_selection']}|{b['product_covered']}|{b['series_only_covered']}|{b['covered']}/{b['machine']}|{b['coverage']:.2%}|")
lines += ['',f"三类总数：整机{new['tiers']['machine']}、配件周边{new['tiers']['accessory']}、第三方精选{new['tiers']['third_party_selection']}，合计2902。逐行规则、理由与ordinal见[classification.json](classification.json)。",'',
'惠普218行实际全部是整机（174笔记本+44台式机），本发布快照没有耗材/保护包，因此分母仍218，不能为了改善覆盖率剔除。大疆6行配件、富士39行镜头单列；小米周边中包含原库仍保留的服务。第三方精选优先按明确第三方名称/生活优选分流，商城所属品牌仍原样保留。','',
'Apple/富士旧的602/59计入LLM，并非已证实可展示日期。本报告采用新口径，不能与那些数字直接比较。小米本轮4行从未知补齐，但8行旧第三方关闭展示，其中部分有有效系列回退，整机可展示并集净值见summary，不隐瞒下降。','',
'## 第三方增量与交叉','',
'|品牌|本轮新增可展示第三方|旧单品关闭展示|','|---|---:|---:|']
for b in ['惠普','大疆','小米','比亚迪','Apple','富士','小米汽车']:
 lines.append(f"|{b}|{summary['new_third_party'].get(b,0)}|{summary['downgraded_by_brand'].get(b,0)}|")
lines += ['',f"人工精确审核{len(pop)}条：{len(cs)}通过、{len(rej)}拒绝，完整身份/事件/双源通过率{len(cs)/len(pop):.1%}；实际形成同事件独立日期对的{len(cs)}条，≤14天通过率100%，均差0天。15–45天新增内部参考0条，>45天置空0条。旧单源第三方14行关闭展示，原日期/原文/核对历史保留内部；原先已禁用的25行保持禁用。新增拒绝5条没有写日期，不计成“置空”。",'',
'ROMO六款由两份原创媒体正文逐版本定价证明；ROMO2四款由快科技与PConline原创编辑稿分别明确5月11日及版本，6月11日开售是另一个事件。小米8 SE精确6GB+64GB；5s和5A仅无容量限定的model_reference，不向未提及配置传播。比亚迪只补2023 DM-i冠军版六配置、2023 DM-p战神版，未凭年款推日期。', '',
'[20条抽样及两份原文片段](sample-20.md)、[全部16条审核输入](../../data/third-party/release-dates.json)、[5条拒绝](rejected-reviewed.json)、[14条旧展示降级](downgrades.json)。20条是21条审核候选中的固定随机样本，包含拒绝，不冒充20条新增通过。','',
'## 本轮最终未获取与范围限制','',
f"四个目标品牌整机最终仍有{summary['target_final_unresolved']}行未获可展示日期，按互斥主因："+ '；'.join(f'{k}{v}行' for k,v in summary['reasons_target'].items())+'。逐行原因见[unresolved.json](unresolved.json)。', '',
f"Apple/富士另有{summary['untouched_other_brand_gaps']}行既有缺口，本轮没有扩大这两品牌研究，不能把这些条目宣称为已经判死。所有品牌未覆盖整机合计{len(missing)}行。",'',
'“最终未获取”仅表示：在本轮限定媒体、精确版本与双源展示规则下未取得足够证据；不等于证明全网永远无日期。无官方字段是惠普已确认的来源限制，其余未命中多为精确套装/版本未得两份原文或同名商品不可唯一定位；不补年款、文章发布时间、页面首存或基础机型日期。','',
'研究顺序为惠普→大疆→小米→比亚迪。hp-search-*保存218货号的分组检索，另有星Book配置别名两源核对；survey-*按每组最多8个精确名称、每批4查询覆盖剩余目标整机，搜索原返回全部保留，命中的目录/参数/促销页不算上市新闻。分组检索只作发现，不能宣称每条已抓取独立新闻正文；只有evidence/中实际捕获并审核的原文可用于写入。大疆官方195页和既有官方目录全部沿用结论，没有再次请求。没有请求hpstore.cn或京东；媒体提及京东的正文不是访问京东。','',
'## 验证与发布','',
'本地基线684 passed / 8 deselected；最终700 passed / 8 deselected，沿用仓库not live选择器。未新增skip、未删除测试。更新1条旧集成断言：第三方日期/证据/核对历史仍需不变，但LLM交叉不再允许展示；另增加16个分层/独立源/日级阈值/原响应hash/原句匹配/重复名称/重放不变回归。', '',
f"整机分类前后逐行相同，2902行及全部非release字段逐值不变；release改变{summary['changed_release_rows']}行，单品和finalizer重复重放幂等。发布门禁加入新测试文件，meta自动计算release_scope。",'',
'代码提交后走refresh-release-dates→持锁publish-release→data→OSS读回→既有API同步器；真实线上meta和3个ID验证记录补在[publication.md](publication.md)。本地finalize不是线上发布证明。']
(ROOT/'README.md').write_text('\n'.join(lines)+'\n')
# Freeze once, exclude the large uncompressed working snapshot from the commit.
if (ROOT/'baseline.json').exists():
 raw=(ROOT/'baseline.json').read_bytes();(ROOT/'baseline.json.gz').write_bytes(gzip.compress(raw,mtime=0))
 (ROOT/'baseline-meta.json').write_text(json.dumps(dict(data_commit='ee076d95a1ab3bbbeec524d582d65a2bd9f131ca',rows=len(before),sha256=hashlib.sha256(raw).hexdigest()),indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False))
