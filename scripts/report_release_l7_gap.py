"""Render the final L7 audit, with both frozen and currently published cohorts."""
import json,math,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/release-coverage/L7-gap'
def main():
 s=json.loads((OUT/'summary.json').read_text());f=json.loads((OUT/'fixed-cohort-coverage.json').read_text());old=json.loads((OUT.parent/'L7-scale/summary.json').read_text())
 current=s['after'];fixed=f['after'];total=current['total'];ft=fixed['total']
 start='## L7 补缺续跑：2026-11-06 最终验收'
 lines=[start,'',f"原 **3,682 行固定口径：1,475/3,682（40.06%）→ 1,657/3,682（{ft['ratio']:.2%}）**，两次放大合计净增182行，达到45%。上一轮已上线的116行，本次追加66行。",'',f"当前实际发布口径：**1,580/3,572（44.23%）→ {total['covered']}/3,572（{total['ratio']:.2%}）**。其他任务先前删除/排除了110行；分母变化不计为本次证据收益。固定口径保留全部原行，7个名字只变空格/大小写，其他身份字段完全一致，逐条用旧身份哈希重新校验捕获正文。证据见[固定口径复算](L7-gap/fixed-cohort-coverage.json)、[7条名称变更](L7-gap/identity-normalizations.json)。",'',f"本次追加 **{s['candidates']} 个唯一（规范型号、年月、URL）候选：{s['accepted']}通过、{s['rejected']}拒绝，净增{s['new_rows']}行**。另7条聚合/系列身份在计数前剔除。91个通过候选中25个为同型号同月的不同URL佐证，不重复增加覆盖。全部已有候选先与L7和L7-scale审核清单全局去重。通过来源为IT之家90候选、新浪科技1候选；不将转载算独立来源。",'',"从40.06%起，两次放大合计 **477候选 / 223通过 / 254拒绝 / 净增182行**；候选通过率46.75%，净增率38.16%。本次通过率57.96%、净增率42.04%，不把上一轮72%当作扩池后的保证。",'',"|品牌|原3682行最终覆盖|当前发布覆盖|当前覆盖率|",'|---|---:|---:|---:|']
 for b,d in current['brands'].items():
  z=fixed['brands'][b];lines.append(f"|{b}|{z['covered']}/{z['total']}|{d['covered']}/{d['total']}|{d['ratio']:.2%}|")
 lines+=['','### 每50个唯一候选的终审批次','','|追加批次|候选|通过|净增|当前口径起点→终点|','|---|---:|---:|---:|---|']
 for b in s['batches']:
  a,z=b['before'],b['after'];lines.append(f"|{b['batch']}|{b['candidates']}|{b['accepted']}|{z['covered']-a['covered']}|{a['covered']}/3572（{a['ratio']:.2%}）→{z['covered']}/3572（{z['ratio']:.2%}）|")
 lines+=['','批次按最终复核结果重放；后续找到同月首发原稿的互证，会更新原候选终审结论。第1批最初进度19通过/净增13，补齐互证后终审为22通过/净增16。实际抓取/模型提案每50条暂停5秒，网页请求全局间隔2.15秒；403/429仍退避并跳过。本次164条有日期URL原始提案，剔除7条非精确身份后审核157条。','', '### 拒因与验证边界','','|拒因|本次追加|两次放大合计|','|---|---:|---:|','|链接打不开|0|0|','|页面无精确型号|0|1|',f"|正文无候选月份|{s['reasons'].get('page_no_month',0)}|{20+s['reasons'].get('page_no_month',0)}|",f"|首发事件/精确版本未证实|{s['reasons'].get('event_or_identity_unproven',0)}|{167+s['reasons'].get('event_or_identity_unproven',0)}|",'','本次没有HTTP失败不表示所有检索URL都可用；这里只统计提交候选，检索分页和无URL弃权分开留存。事件拒绝包括：旧款同名新款、普通版借Pro/定制版日期、首销与更早公告跨月、促销/预告、多个容量或套装未精确证明。','',"修正了年月解析器的一处误拒：`2023年9月20日`中“月”已经分隔月份，原逻辑却拒绝“月”后面的日数字；数字形式仍禁止把`/11`匹配为`/1`。6条原误拒重新进入事件审核，仍未绕过语义审查；详见[解析纠正记录](L7-gap/month-parser-corrections.json)及新增回归断言。没有把仅今年9月的相对月份强行当作连续YYYY-MM命中。7个空格/大小写名称保留了11条额外的旧身份断言供finalizer重放，引用同一捕获，不增加候选、通过或覆盖计数；重放严格按完整姓名和身份哈希选择证据，硬件变动仍拒绝。",'', '完整逐条判定：[audit.json](L7-gap/audit.json)、[人工终审与身份哈希](L7-gap/review-decisions.json)、[新证据](L7-gap/new-entries.json)。所有新增为`llm_verified / medium / month / product`，HTTP200、正文、精确名称、同月日期、引文与SHA256均由生产`check`重新验证；官方首发/官方商城存档边界保持，未新增非官方电商/公众号等来源。','', '### 亚朵与品牌投递配额','','亚朵 **0/267 → 0/267**（当前发布集0/231），本次231个当前SKU身份全部查询，仍没有返回有精确月份和可核URL的候选，故没有合格入库来源。上一轮100个身份查询也没有变成100个有证据候选。官网IR的旧代/夏季产品不能套用当前Pro4.0、冬季/四季、尺寸、配色或组合装；官方商城createTime仍不等于发布日期。','', '配额如实验收：小米累计476个唯一候选，达到≥250；亚朵有证据候选0，**未达到≥100**；比亚迪累计1候选，**未达到20**，当前仅剩10个未覆盖产品身份，不能靠重复投同一URL凑数。本次查询包含全部14个比亚迪身份，未新增合格候选。原始弃权见[identity/proposals](L7-gap/identity/proposals/)。','', '全库45%目标已达到，因此全库补量估算为0；品牌目标仍未达到：固定口径小米50%需812，当前505，差307；亚朵30%需81，当前0，差81。当前口径小米50%需775，当前494，差281；亚朵30%需70，当前0，差70。仅作条件估算，按本次42.04%净增率，小米当前缺口需约669个合格待审候选；按72%也至少391个。亚朵未观察到有效候选，不能给出可信通过率或承诺“再投100即可补齐”。完整未覆盖品类分布见[summary.json](L7-gap/summary.json)。','', '### 随机12条新增命中样本','','随机种子20261106，按唯一ID抽样；每条链接及完整连续引文见[samples.json](L7-gap/samples.json)。下面只显示正文命中片段。','']
 for e in json.loads((OUT/'samples.json').read_text()):
  r=e['release'];q=r['evidence']['quote'];pattern=r'\s*'.join(re.escape(c) for c in re.sub(r'\s+','',e['name']));m=re.search(pattern,q,re.I)
  snippet=q[:240]
  if m and m.start()>210:snippet=q[:65]+' […] '+q[max(0,m.start()-20):m.end()+145]
  lines += [f"- **{e['name']} · {r['date']}** · [原页面]({r['evidence']['url']})",'  > '+snippet.replace('\n',' ').rstrip(),'']
 lines+=['### 测试、发布与后台','','全量离线回归、发布前重放和线上读回收据会随发布完成更新。当前发布集预期`llm_verified=209`，固定3682行口径为218；两者分别对应9个后来排除的已覆盖行，不能混用。']
 publication=OUT/'publication.json'
 if publication.exists():
  receipt=json.loads(publication.read_text())
  lines[-1]=(f"本地回归 **{receipt['local_tests']}**；后台日期统计 **{receipt['admin_tests']}**；发布前完整finalizer重放矩阵与审核清单完全一致。"
             f"发布代码 **{receipt['code_commit'][:8]}**，数据发布 [run {receipt['run_id']}]({receipt['url']}) **{receipt['conclusion']}**。"
             f"线上完整商品集SHA256、全部品牌矩阵、OSS及后台均已复核：**{receipt['covered']}/{receipt['total']}，llm_verified={receipt['llm_verified']}**；"
             f"后台HTTP200、statsStatus={receipt['admin_stats_status']}。固定3682行口径llm_verified=218，当前发布集为209；9条差异来自其他任务先前排除。"
             f"数据revision `{receipt['data_revision']}`。完整收据见[publication.json](L7-gap/publication.json)、[online-coverage.json](L7-gap/online-coverage.json)。")
 report='\n'.join(lines)+'\n';(OUT/'report.md').write_text(report)
 p=ROOT/'docs/release-coverage/2026-11-05.md';oldtext=p.read_text();oldtext=oldtext.split(start)[0].rstrip();p.write_text(oldtext+'\n\n'+report)
if __name__=='__main__':main()
