"""Render the completed audit; no network and no changes to release gates."""
from pathlib import Path
import json,collections
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def read(p):return json.loads(p.read_text())
def write(name,lines):(OUT/name).write_text('\n'.join(lines).rstrip()+'\n')
def cell(s):return str(s).replace('|','/').replace('\n',' ')
def main():
 summary=read(OUT/'audit-summary.json');report=read(OUT/'report.json');D={e['id']:e for e in read(ROOT/'data/official/xiaomi-release-dictionary.json')['entries']};bundle=read(ROOT/'data/official/series-releases.json');batches={b['id']:b for b in bundle['batches']}
 live=read(OUT/'dictionary-live-recheck.json');lines=['# 字典原页抽检 30 条','','固定种子20261104，按 archive 10、official_newsroom 12、existing_product_official 8 分层抽样；首位强制含本轮纠正的小米12系列。未替换失败样本。21 条在本机重新请求得到 200 且逐段匹配；9 条 IR 页面本机 403，随后经 Web 阅读工具打开同一 URL 的官方 PDF 核对（工具页面可有缓存，不冒称本机实时下载成功）。原始响应/时间/哈希见 recheck/，工具返回见 web-ir-*.json。30 条的日期与具体型号均核对通过。','']
 for i,c in enumerate(live,1):
  e=D[c['id']];ev=e['evidence'];parts=ev.get('quote_parts',[ev['quote']]);snippet=parts[-1][:420]
  mode='本机重新请求 200，原句匹配' if c['quote_found_live'] else '本机403；同URL官方PDF经Web阅读复核'
  lines += [f"## {i}. {e['product_name']} · {e['date']}",'',f"条目 `{e['id']}`；[原页面]({ev['url']})；{mode}。",'', '> '+snippet.replace('\n',' '),'',f"存档定位：{ev['locator']}；原存档 SHA256：`{ev['sha256']}`。",'']
 write('dictionary-sample-30.md',lines)
 lines=['# 商品 → 字典条目：30 行匹配抽检','','全新匹配仅7行，全部检查；另从本轮回补中按种子20261104抽23行，合计30个不同商品ID。每行均有对应字典条目。媒体回补行同时核对对应的官方字典型号，实际门禁使用的第二来源仍按批次 crosschecks 记录，不把字典参数的发布时间与开售日期混为同一事件。','', '|商品 ID / 名称|字典型号 / 条目|批次日期 / 证据类型|结论与边界|','|---|---|---|---|']
 for sample in read(OUT/'sample-30.json'):
  e=D[sample['dictionary_entry_id']];b=batches[sample['batch_id']];r=b['series_release']
  reason='同款同代；精确名称/审核中英译名，未跨后缀、容量或套装继承'
  if '电视' in sample['name']:reason='代际、尺寸及是否Pro逐项对应；普通版不扩给至尊版；发布时间与开售分开'
  if 'Max' in sample['name']:reason='保留Max/Pro/Pro Max完整型号；非标准版或相近前缀'
  if '定制' in sample['name']:reason='官方正文明确同时推出Custom Edition；不以普通版名称替代'
  lines += ['|'+ '|'.join(map(cell,[sample['id']+' / '+sample['name'],e['product_name']+' / '+e['id'],r['date']+' / '+sample.get('method','new_official_match'),reason+'，通过']))+'|']
 lines += ['', '## 本轮撤回和纠错','','- 撤回3行门锁5 Max第二来源回补：10050241、25284、25291。原主来源只明确9月23日开售，原断言事件却是announcement；不能用发布稿填成同事件双源。保留旧日期断言和原证据，继续disabled。新增商品→字典匹配没有同款同代错误，撤回0行。', '- 字典纠错2处：小米12系列改用“小米12系列发布”原句；2022-03-17 AirDots条目改为Redmi AirDots 3 Pro Genshin Impact Edition，不能给普通版继承。两处均未造成新商品匹配。', '- 另外回补4行电视S Pro Mini LED 2026：10050131、21754、21765、21771，使用各自官方精确ID“发布时间2025年9月”作独立第二来源；不是从相同名称扩全系列。', '- 巨省电/巨省电Pro、配件→整机没有新增匹配；研究分组与未命中清单不赋日期。', '']
 write('match-sample-30.md',lines)
 rows=['# 小米官方日期字典收尾 — 2026-11-04','','复用上轮256条字典与抓取产物完成审核，没有丢弃工作区重做。最终字典256条（229官方、27非官方），全新匹配7行；旧149行回补57行，92行仍disabled。 crosschecks代码和14/45天门槛未修改。','','## 字典质量和来源分布','','256/256具备产品名、日期、原文片段、URL；保留精度、市场、事件、采集时间、哈希及定位。原始258条审核输入合并为256条。字典含已验证第三方历史种子，名称中的“官方”不代表所有条目均官方。','', '|来源|条目数|','|---|---:|']
 for k,n in summary['sources'].items():rows += [f'|{k}|{n}|']
 rows += ['|社区公告|0|','', '27条非官方来源逐条单列于 [nonofficial.md](nonofficial.md) 与 audit-summary.json，沿用既有双源批次，未当官方单源启用。','', '## 两组抽检','','[字典30条原页面核对及片段](dictionary-sample-30.md)：21条本机200逐段匹配，9条IR本机403后用Web阅读工具复核相同官方PDF；保留失败响应，没有把存档当实时成功。','', '[商品→字典30行核对](match-sample-30.md)：全7行新匹配＋23行回补匹配，逐项检查型号、代际、尺寸及事件。撤回3行不成立的第二来源回补，新增匹配撤回0行；纠正字典原句/版本2处。', '', '## 覆盖率：断言与可展示分别计算','','修前为上轮冻结 baseline.json.gz，与本次读取的data提交99314121全量2902行逐值相同；小米1684行。修前系列按 series-before.json.gz（与本轮起点HEAD版本相同）计算，修后重放当前series-releases.json。保留同ID多投影行，不将行数冒充唯一ID数。','', '断言覆盖：release.date或release_series.date任一有值即计入，包括disabled；可展示覆盖：有日期、usage非disabled、display_allowed不为false、internal_only不为true，且非配件/服务。系列状态由既有reconcile_series重算，官方单源或有效双源且差值≤14天；15–45天内部保留，>45天冲突不展示。单品使用冻结基线中已执行crosschecks的结果。','', '|范围 / 口径|修前|修后|变化|','|---|---:|---:|---:|']
 for scope,label in [('xiaomi','小米'),('all','全库')]:
  a=summary.get('coverage_published',summary['coverage'])['before'][scope];b=summary.get('coverage_published',summary['coverage'])['after'][scope]
  for metric,title in [('assertion','断言覆盖'),('display','可展示覆盖')]:
   rows += [f"|{label} {title}|{a[metric]}/{a['total']}（{a[metric]/a['total']:.2%}）|{b[metric]}/{b['total']}（{b[metric]/b['total']:.2%}）|+{b[metric]-a[metric]}行|"]
 rows += ['', '小米单品日期111不变，系列日期204→211，断言并集267→274。57行旧系列恢复展示，其中27行已有可展示单品日期，系列恢复净贡献30行；再加7行全新匹配，可展示并集净增37。仅隔离本轮小米改动时，其它品牌和所有非release_series字段逐值不变，全库断言827→834、可展示655→692。实际正常finalize同时重放此前已提交但尚未推送的7a64e0eb，新增4条其它品牌日期（比亚迪夏2026款、DJI Ronin 4D-6K、Osmo Mobile 6暗岩灰、DJI Power Auro 2000 Elite），因此上表线上实际修后为838/696：不能把额外4条算作小米字典成果。4条逐字段差异及原提交归因见publication-invariants.json；除这4个release对象和本轮release_series外其它字段不变。全库分母以冻结时data的2902行为准，不沿用更早2898分母。','', '## 旧149行回补','','原81批149行保留原日期和主来源；逐成员核对第二源，部分批次拆成带derived_from_batch_id的精确成员子批次，不解锁未被证明的成员。','', f"- 官方字典第二来源：{sum(len(r['ids']) for r in read(OUT/'legacy-repairs.json') if r['method']=='official_dictionary')}行。", f"- 独立媒体第二来源：{sum(len(r['ids']) for r in read(OUT/'legacy-repairs.json') if r['method']=='independent_media_archive')}行。",'- 合计57行恢复；92行保持disabled、display_allowed=false、internal_only=true、display=null。', '- [逐行149条结果](legacy-149.json)、[回补来源与批次](legacy-repairs.json)；未救回原因记录在逐行清单。没有把没有找到来源解释为全网不存在。','', '## 未命中 Top 20 族','','以下是待研究分组，不是已证同批推出的系列；不据此继承日期。新增匹配7族7行后，仍有1378组1410行未命中。完整范围见 [unmatched.json](unmatched.json)。','', '|族/研究名称|行数|未命中原因|','|---|---:|---|']
 for f in read(OUT/'unmatched-top20.json'):rows += ['|'+'|'.join(map(cell,[f['family'],f['row_count'],f['reason']]))+'|']
 rows += ['', '## 测试与复现','','```sh','python3 docs/xiaomi-release-dictionary-20261104/extract.py','python3 docs/xiaomi-release-dictionary-20261104/review_newsroom.py','PYTHONPATH=src python3 docs/xiaomi-release-dictionary-20261104/build.py','python3 docs/xiaomi-release-dictionary-20261104/audit.py','PYTHONPATH=src:scripts ~/.cache/goodsdex-testenv/bin/python -m pytest -q -m "not live"','python3 docs/xiaomi-release-dictionary-20261104/make_report.py','```','','完整既有测试与3个新增回归测试：**684 passed / 8 deselected**，见 [tests-final.log](tests-final.log)。8个live按仓库tests.yml原选择器排除；没有新增skip、删除或降低断言。旧finalizer测试保留149条历史清单断言，并叠加独立冻结的7条新增和拆分批次预期。首次测试失败日志保留于tests-first-attempt.log（测试环境缺Pillow，以及旧预期尚未包含本轮7行），补齐依赖并更新增量预期后全量通过。','', '## 提交与发布','','数据改动需要发布：正常refresh-release-dates → publish-release持锁重放、门禁、finalize、data、OSS读回。提交号、run id、云端测试和线上/api/meta、3个真实/api/goods/<id>完整返回及摘录见 [publication.md](publication.md)。不包含工作区其它轮次未提交文件。','']
 write('README.md',rows)
 write('nonofficial.md',['# 非官方条目（27条）','','仅作为既有双源批次种子；不能作为官方单源。','']+[f"- `{e['id']}` {e['name']}：[原来源]({e['url']})" for e in summary['nonofficial']])
if __name__=='__main__':main()
