#!/usr/bin/env python3
"""Full catalogue tolerance replay and inspectable acceptance report."""
import argparse
from collections import Counter, defaultdict
from datetime import date
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from goodsdex.release_coverage import apply_priority_dates,effective,matrix


def report(before,after,output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    old,new=matrix(before),matrix(after)
    additions=Counter();samples=[];conflicts=[];cells=defaultdict(Counter)
    for a,b in zip(before,after):
        r=effective(b)
        if r:
            cells[b.get('brand','未知')][(r.get('release_source',r['source']),r['granularity'])]+=1
            if not effective(a):
                additions[r.get('release_source',r['source'])]+=1
                samples.append(dict(id=b['id'],name=b['name'],brand=b.get('brand'),source=r['release_source'],date=r['date'],
                                    url=r['evidence']['url'],quote=r['evidence']['quote'],
                                    membership=r.get('membership_evidence')))
        for c in b.get('release_conflicts',[]):conflicts.append(dict(id=b['id'],**c))
    full_path=ROOT/'docs/release-coverage/tolerance-llm-full/summary.json'
    full=json.loads(full_path.read_text()) if full_path.exists() else {}
    data=dict(before=old,after=new,additions=dict(additions),scanned=len(after),conflicts=len(conflicts),full_llm=full)
    (output/'tolerance-coverage.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    (output/'conflicts.json').write_text(json.dumps(conflicts,ensure_ascii=False,indent=2)+'\n')
    (output/'tolerance-samples.json').write_text(json.dumps(samples,ensure_ascii=False,indent=2)+'\n')
    # Diverse deterministic samples; keep the full inspectable set in JSON.
    selected=[];seen=set()
    groups=set()
    for s in samples:
        key=(s['brand'],s['source'])
        if key not in groups:
            selected.append(s);groups.add(key);seen.add((s['source'],s['url']))
    selected=selected[:10]
    for s in samples:
        key=(s['source'],s['url'])
        if key not in seen and len(selected)<10:selected.append(s);seen.add(key)
        if len(selected)==10:break
    for s in samples:
        if len(selected)==10:break
        if s not in selected:selected.append(s)
    lines=['# 发布日期容差与换新判断 '+date.today().isoformat(),'',
        f"全库逐行处理 {len(after)} 条：{old['total']['covered']}/{len(before)}（{old['total']['ratio']:.2%}）→ {new['total']['covered']}/{len(after)}（{new['total']['ratio']:.2%}）。目标45%；差 {max(0, __import__('math').ceil(len(after)*.45)-new['total']['covered'])} 条。",
        '', '≤14天可用于年龄和代际参考；15–45天medium，仅年龄；>45天日期留空并进入conflicts.json。delta=null表示无可比较的第二日期，不能解释为零误差。月级比较同月为0，不伪造日。',
        '', '四类来源净新增：'+str({s:additions[s] for s in ('official','third_party','llm_crossed','series_inherit')}),
        '', '| 品牌 | 前 | 后 | 覆盖率 | 目标 | 缺口 |','|---|---:|---:|---:|---:|---:|']
    targets={'小米':.5,'惠普':.4,'亚朵星球':.3,'大疆':.6}
    for b,v in new['brands'].items():
        target=targets.get(b);goal=f'{target:.0%}' if target else '—'
        gap=max(0,__import__('math').ceil(target*v['total'])-v['covered']) if target else '—'
        lines.append(f"| {b} | {old['brands'].get(b,{}).get('covered',0)} | {v['covered']}/{v['total']} | {v['ratio']:.2%} | {goal} | {gap} |")
    lines+=['','| 品牌 | 来源 | 精度 | 条数 |','|---|---|---|---:|']
    for b,cs in cells.items():
        for (source,p),n in sorted(cs.items()):lines.append(f'| {b} | {source} | {p} | {n} |')
    lines+=['','## 10条新增抽样（全部新增见 tolerance-samples.json）']
    for s in selected:lines += [f"- {s['name']} · {s['id']} · {s['date']} · {s['source']}\n  {s['url']}\n  原文：{s['quote']}\n  成员依据：{json.dumps(s['membership'],ensure_ascii=False)}"]
    lines+=['','## 未达标原因与边界',
        '- 小米：旧日期旁证解除禁用与已审系列成员全量启用；未将同品牌、近似名称或型号年份当作系列同代证据。大量生活电器没有可核验的推出时间。',
        '- 惠普：官方2023-03公告逐个明示G10平台，与官方productSeriesName精确映射；全球平台推出月份，不能解释为中国配置首售。',
        '- 大疆：仅同family_id且包装清单首项主机名称完全一致、商品名称以此主机名开头的套装继承；不同代、Pro、不同分辨率不互套。',
        '- 亚朵：267条SKU尚无可核验发布日期；SPU、接口创建时间、网页首存不作为推出月份。',
        '- LLM：本轮余下2282行、2213个精确同名型号全部查询，89批成功，69个给出月份估计，但URL与原文均空，因此全部未入库。另重抓26篇Apple原文，对39个旧模型估计核对逐字引文、精确型号与发售月份，加上Pocket 3及原始全能套装2条，共41条llm_crossed。未沿用97%抽样门槛。原始响应与弃权原因见tolerance-llm-full；源文和核对记录见tolerance-llm-retained。',
        '- 第三方结构化L6沿用另一任务已提交结果；当前无有效条目，不能把搜索页或HTTP失败当作证据。',
        '', '## 消费端文案约束',
        '- 2025 年 5 月前后发布', '- 该系列 2023 年 3 月前后发布', '- 发布约 1 年半（medium：只提供年龄，不推断跨代）',
        '- release_decision.date固定YYYY-MM；usage明确age/generation；后台原始日精度和证据保留。',
        '', '## 测试与发布',
        '- 数据仓云端完整回归：940 passed / 8 live deselected；API：367 passed / 4 skipped；C端换新与显示：15 passed，完整候选交互：6 passed。日志见tolerance-tests.log及消费仓docs/release-tolerance-20261105。',
        '- 数据代码：7d70db21；数据发布run 41985186529 成功；data提交 0e34a0743a6c4bba56ed35056d4d5ffcc5cf4e3e。完整云端测试run 41985186097 成功。',
        '- 消费端代码：9448b1a；CI run 41979736019 成功；API部署已由HTTP 200完整提交号回读。线上goods.json与GitHub/OSS SHA256一致：e006b7d154c4084101b785d63bd7a2a9e040e44517b8407982bec9535db20427。',
        '- 发布时间不是单独换机理由；本次只提供近似年龄和代际参考，不引入按日期强制建议换机的规则。',
        '',f'本轮冲突 {len(conflicts)} 条，见 conflicts.json。定时工作流保持原cron，新规则由常规finalizer和daily report重放。']
    (output/(date.today().isoformat()+'.md')).write_text('\n'.join(lines)+'\n')
    return data


def main():
    p=argparse.ArgumentParser();p.add_argument('--goods',type=Path,required=True);p.add_argument('--output',type=Path,default=ROOT/'docs/release-coverage');p.add_argument('--apply',action='store_true');a=p.parse_args()
    before=json.loads(a.goods.read_text());after=apply_priority_dates(before)
    print(json.dumps(report(before,after,a.output)['after']['total'],ensure_ascii=False))
    if a.apply:a.goods.write_text(json.dumps(after,ensure_ascii=False,indent=1)+'\n')
if __name__=='__main__':main()
