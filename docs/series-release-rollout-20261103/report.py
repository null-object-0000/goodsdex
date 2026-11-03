"""Render inspectable census, batch and review documents from frozen artifacts."""
import json,gzip,hashlib
from pathlib import Path
from collections import Counter,defaultdict
P=Path(__file__).parent

def run():
 report=json.loads((P/'report.json').read_text());batches=json.loads((P/'batches.json').read_text());pending=json.loads((P/'unresolved.json').read_text())
 baseline=json.loads(gzip.decompress((P/'baseline-goods.json.gz').read_bytes()))
 inventory=[]
 for f in sorted((P/'evidence').glob('*.json')):
  d=json.loads(f.read_text());inventory.append({k:v for k,v in d.items() if k not in ('text','header')})
 (P/'article-inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2)+'\n')
 md=['# 小米系列/发布批次铺开（2026-11-03）','',f"本轮全量筛查当前线上小米 **{report['actual_denominator']} 行**，保留试点5批17条，新增76批132条系列断言，最终 **81批149条**，其中本轮新增无单品日期的系列继承90条。单品 `release.date` 全部原样保留。",'',
'**分母差异没有掩盖。** 用户交接为1728，当前线上 `/api/goods` 与 `origin/data` 都实际为小米1695、全库2909。冻结快照及字节哈希见 `baseline-goods.json.gz`、`data-baseline.json.gz`、`report.json`。差额33条身份未知，未构造记录，也未声称完成1728条口径验收。本轮以实际1695行完成逐行清点，分类互斥取主品类；重复ID行保留原样，1690个不同小米ID，不静默去重。', '',
'**本轮证据范围。** 对当前每个ID回看上一轮当日官方接口扫描（2242个小米ID，含请求、状态、哈希、时间）；新增59个品类关键词的新闻检索，再对目标系列补查。品类检索原文见 `category-search.json`，目标入口见 `targeted-search.json`；报道完整HTTP响应及SHA256见 `evidence/`、`article-inventory.json`。所有当前行逐条纳入 `census.json`。这是一轮全量筛查，并不意味着1546条未获日期的记录都做了独立精确关键词或穷尽网络检索；未取得依据不等于没有任何公开依据。', '',
f"本轮归档 {len(inventory)} 个报道入口（正文取得 {sum(not x.get('error') for x in inventory)}，失败 {sum(bool(x.get('error')) for x in inventory)}）。采用的新增批次均为IT之家第三方报道，明确标记 `third_party`，没有把报道转述官微或所附京东链接标成官方。没有使用京东同系列其它配置日期。官方商品页和扫描里只有单品参数/型号年份的，不提升为整个系列批次依据。",'',
'同一场发布会可聚批，容量、颜色或水箱/上下水版本仅在报道明确覆盖时纳入。型号年份不推导月份。基础款、Pro、至尊、白色新版本与多代容器分开；不能证明同批就留空。日期均为年月，预售/预约对应公开上架的 `announcement`，没有把计划开售当已发生 `availability`；已开售报道保留 `availability`。显示仍为独立 `series_release.display` 的“该系列 X 年 X 月发布/开售”，未写“发售时间”到单品日期。', '',
'## 覆盖率', '',
f"小米系列字段：**17/{report['actual_denominator']}（{report['coverage_before']:.2f}%） → 149/{report['actual_denominator']}（{report['coverage_after']:.2f}%）**，增加132条、{report['coverage_after']-report['coverage_before']:.2f}个百分点。90条是新增无单品日期的继承，另42条与既有单品日期并存，不冒充新增单品日期。统计包含系列容器，不把容器另说成新增硬件型号。",'',
'汽车（小米汽车3、比亚迪14）单列，全部保持原状，不进入分母。其它品牌系列字段未改。当前发布集残留服务/耗材等记录也全部清点、保持空，不在本轮悄悄缩小分母或更改既有过滤策略。1728口径尚缺33条对应身份，因此不计算伪精确的1728覆盖率。','',
'|品牌|当前行数|系列字段 前→后|','|---|---:|---:|']
 for brand,n in sorted(Counter(r.get('brand') or ('小米' if r['id'].startswith('CN:mi_cn:') else '未知') for r in baseline).items()):
  md.append(f"|{brand}|{n}|{'17→149' if brand=='小米' else '0→0（本轮未改）'}|")
 md+=['','完整主品类覆盖表见 [coverage.md](coverage.md)。','', '## 批次表','', '|批次名|日期 / 事件|依据（均第三方）|成员条数|本轮新增系列字段|本轮新增无单品日期继承|','|---|---|---|---:|---:|---:|']
 for b in batches:md.append(f"|{b['series']}|{b['date']} / {b['event']}|[IT之家]({b['url']})|{b['members']}|{b['new_series']}|{b['new_inherited_without_product']}|")
 md+=['','## 抽样与未获依据清单','','[30条逐项核对](sample-30.md)列出型号、批次、依据、对错、正确值。24条已赋日期 + 6条应留空，最终30/30符合预期；目的抽样，不能外推为全库准确率。由执行者阅读正文复核，未声称已有独立人工签字。','','[逐名未获日期清单](unresolved.md)与 [完整JSON](unresolved.json)列出1546行的名字、ID、实际试过的入口和未赋值原因。多代/容量不明的容器和服务/耗材保留空。不能以同名近似报道补齐。检索入口失败有实际错误记录，未将失败伪装为没有结果。','','## 复现、测试与发布','','```bash','PYTHONPATH=src python docs/series-release-rollout-20261103/build.py','python docs/series-release-rollout-20261103/sample_review.py','python docs/series-release-rollout-20261103/report.py','PYTHONPATH=src:scripts python -m pytest -q','```','','基线470项通过。最终测试结果见 `tests-final.log`；完整正常 finalize 日志见 `finalize.log`。逐字段比对表明非series字段0变更、商品行数及汽车0变更、继承重放幂等。发布与真实详情API摘录见 [publication.md](publication.md)（发布完成后写入）。']
 (P/'README.md').write_text('\n'.join(md)+'\n')
 cats=['# 小米按主品类覆盖率','','分母取发布行的主品类，互斥可相加；不使用categories多值标签求和。汽车排除。','','|品牌 / 品类|分母|系列日期 前→后|覆盖率 前→后|','|---|---:|---:|---|']
 for c in report['categories']:cats.append(f"|小米 / {c['category']}|{c['total']}|{c['before']}→{c['after']}|{c['coverage_before']:.2f}%→{c['coverage_after']:.2f}%|")
 (P/'coverage.md').write_text('\n'.join(cats)+'\n')
 groups=defaultdict(list)
 for r in pending:groups[(r['name'],r['reason'])].append(r)
 unknown=['# 本轮未取得系列批次依据的清单','','1546行逐名归并；每组只按完全相同名称合并展示，未声称未知系列已辨清全部代际。精确请求与新闻检索范围见JSON。官方扫描为2026-11-03当日旧扫描复核；新闻为本轮按品类检索和正文比对，不冒称所有型号都做了独立精确搜索。','','|系列/型号名称（未证实可合并的仍按原名）|ID尾号|试过的入口|留空原因|','|---|---|---|---|']
 for (name,reason),rs in sorted(groups.items()):
  attempts=rs[0]['attempts'];entries=[]
  for a in attempts:
   if a['type']=='official_exact_id_scan':entries.append('[官方逐ID扫描]('+a['url']+')：'+a['result'])
   elif a['type']=='category_news_search':entries.append('品类新闻检索：`'+a['query']+'`')
   else:entries.append('已归档报道候选逐名比对')
  unknown.append('|'+name.replace('|','/')+'|'+', '.join(r['id'].split(':')[-1] for r in rs)+'|'+'；'.join(entries)+'|'+reason+'|')
 (P/'unresolved.md').write_text('\n'.join(unknown)+'\n')
 print('rendered report, categories, unresolved',len(groups))
if __name__=='__main__':run()
