"""L5 audit artifacts and report, with explicit per-brand targets."""
from collections import Counter
import json
from goodsdex.release_coverage import effective, matrix

TARGETS={'小米':800,'惠普':300,'亚朵星球':100,'大疆':200}


def append_report(lines, before, after, result, directory):
    directory.mkdir(parents=True,exist_ok=True)
    a,b=matrix(after),matrix(before)
    hits=[]
    for row in after:
        r=effective(row)
        if not r or r.get('lane')!='L5':continue
        e=r['evidence']
        hits.append(dict(id=row['id'],name=row['name'],brand=row.get('brand'),release=r['date'],
                         release_precision=r['granularity'],release_source='third_party',
                         release_evidence=e['url'],release_quote=e['quote'],identity_quote=e['identity_quote'],
                         release_confidence=r['confidence'],event=r['event'],
                         why='原文明示月日及发布/开售，型号与专属配置逐项匹配' if r['granularity']=='day' else '首发报道明确该型号已推出；只有报道月份，未将今日/报道时间升为日',
                         capture_file=e['capture_file'],sha256=e['sha256']))
    from goodsdex.release_media import apply
    l5_only = matrix(apply(before, result))
    # Stratify brands before filling, avoid 15 configurations of one product.
    samples=[];seen=set()
    ordered=sorted(hits,key=lambda x:(x['brand'],x['id']))
    for brand in sorted({h['brand'] for h in hits}):
        for h in [h for h in ordered if h['brand']==brand]:
            if h['release_evidence'] not in seen:
                samples.append(h);seen.add(h['release_evidence']);break
    for h in ordered:
        if len(samples)>=15:break
        if h['release_evidence'] not in seen:
            samples.append(h);seen.add(h['release_evidence'])
    for h in ordered:
        if len(samples)>=15:break
        if h not in samples:samples.append(h)
    lines+=['','## L5：第三方首发报道','',
            '用户批准单一首发报道作为主来源。官方日期不可覆盖；精确型号与配置逐条核对；系列报道维持 L4；月为默认上限。',
            '兼容现有商品契约：`release` 仍为对象，日期在 `release.date`；同时写入 `release_precision / release_source / release_evidence / release_quote / release_confidence`。',
            f"本轮 L5 命中 {len(hits)} 个发布行；单独应用 L5 净增 {l5_only['total']['covered']-b['total']['covered']}；重放全部采集线后的净覆盖变化 {a['total']['covered']-b['total']['covered']}。命中与净增分别统计；官方交叉证据不算新增。",'',
            '| 品牌 | 原覆盖 | 后覆盖 | day | month | L5 命中 | 目标 | 验收 |','|---|---:|---:|---:|---:|---:|---:|---|']
    for brand,c in a['brands'].items():
        target=TARGETS.get(brand)
        lines.append(f"| {brand} | {b['brands'].get(brand,{}).get('covered',0)} | {c['covered']}/{c['total']} | {c['day']} | {c['month']} | {sum(h['brand']==brand for h in hits)} | {target or '无硬指标'} | {'达标' if target and c['covered']>=target else '未达标' if target else '已尝试'} |")
    lines += ['', '惠普实际发布行是 791（需求背景写 790），保持原始分母。线上读取快照为 980/月；需求给出的本地待发布 L1–L4 结果为 981（33/day + 948/month）。本表前列使用本轮实际线上快照；两套基线在 `L5/baselines.json` 并列保留。', '', '检索边界：本轮审核现存媒体语料及新增定向检索，尚未穷尽外部报道。定时任务刷新已审核证据并保存 IT之家 RSS 的新标题复核队列；新标题未经精确身份和事件审核不自动入库。惠普/亚朵代表性拒绝原文与配置缺口见 `L5/research-rejections.json`。']
    lines+=['',f"L5 精度：{dict(Counter(h['release_precision'] for h in hits))}",
            '',f"失败/跳过原因：`{json.dumps(result['summary']['reasons'],ensure_ascii=False)}`",'',
            '按品牌的命中、精度、失败原因明细：`L5/result.json` 的 `summary.brands`；全量命中 `L5/hits.json`；冲突及区间存疑 `L5/conflicts.json`；拒绝证据 `L5/rejected.json`。',
            '冲突以同事件实际日期比较；月份采用真实日历上下界，不能确定是否跨45天也进入待人工核对。转载保留上游，不将转载计作独立互证。',
            '',f"冲突/存疑 {len(result['conflicts'])} 行；尚未取得证据的行不等同于无首发报道。",'',f'### L5 人工可核样本（{len(samples)}/15）','']
    for h in samples:
        lines += [f"- {h['name']} · {h['id']} · {h['release']}（{h['release_precision']}）· {h['why']}\n  {h['release_evidence']}\n  原文：{h['release_quote']}\n  型号配置原文：{h['identity_quote']}"]
    for filename,value in [('hits.json',hits),('samples-15.json',samples)]:
        (directory/'L5'/filename).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
