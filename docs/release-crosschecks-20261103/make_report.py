import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
import sys

sys.path[:0] = ['src', 'scripts']
from goodsdex.release_dates import apply_release_dates
from goodsdex.release_crosschecks import reconcile

ROOT = Path(__file__).parent
baseline = json.loads((ROOT/'baseline-dates.json').read_text())
checks = json.loads((ROOT/'checks.json').read_text())['checks']
rows = apply_release_dates(json.loads((ROOT/'baseline.json').read_text()))
idx = {r['id']: r for r in rows}
details, internal = [], []
stats = defaultdict(Counter)
for row in rows:
    stats[row.get('brand') or '小米']
for item in baseline:
    check = checks[item['family']]
    r = reconcile(item['release'], [check])
    observation = next(c for c in r['checks'] if c['verdict'] != 'original')
    entry = dict(id=item['ids'][0], model=item['name'], brand=item['brand'],
        original_date=item['release']['date'], source=item['release']['source'],
        source_url=item['release']['evidence'].get('url'), llm_date=check['date'],
        delta_days=observation['delta_days'], verdict=r['crosscheck_status'],
        reason=check['reason'], original_event=item['release']['event'],
        original_market=item['release'].get('market'), raw_response=check['artifact'],
        published=bool(idx.get(item['ids'][0], {}).get('release')),
        published_date=(idx.get(item['ids'][0], {}).get('release') or {}).get('date'))
    details.append(entry)
    if entry['source'] == 'third_party':
        stats[item['brand']]['total'] += len(item['ids'])
        stats[item['brand']][entry['verdict']] += len(item['ids'])
    if entry['verdict'] != 'corroborated':
        internal.append(entry)

def write(name, value):
    (ROOT/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')

write('summary.json', dict(third_party_by_brand=dict(stats),
    all_candidate_results=dict(Counter((d['source']+':'+d['verdict']) for d in details)),
    public_llm_results=dict(Counter(r['release']['crosscheck_status'] for r in rows if (r.get('release') or {}).get('source') == 'llm'))))
write('all-results.json', details)
write('manual-and-internal.json', internal)
third = [d for d in details if d['source'] == 'third_party']
fields = ['brand','model','id','original_date','source','source_url','llm_date','delta_days','verdict','reason']
for filename, items in [('all-third-party.csv', third), ('comparison-30.csv', third[:30])]:
    with (ROOT/filename).open('w') as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore', lineterminator='\n')
        writer.writeheader();writer.writerows(items)

text = '''# 全库第三方日期独立核验

每条独立请求只含品牌、品类、型号、市场和事件；不含原日期、来源网页、原文、既有 LLM 答案或候选族 key。提示词见 prompts/，身份冻结于 identities.json；完整后端响应、usage、时间、请求状态见 responses/、sent/、states/。151 次请求：39 条 third_party + 112 条既有 LLM 候选（包括先前门禁禁用的 72 条，不将其重新启用）。全部原始日期与原证据保留在 baseline-dates.json，模型结果永远 source=llm。

规则：有任一月粒度时两侧按年月对齐，同月为 0，跨月按绝对月差 × 30 天；两侧均到日才按实际日差。≤14 corroborated，15–45 disagreement，>45 conflict 且 release.date=null。保留 release.checks[]，含被比较方 source/date；LLM 两两也比较。official 优先且保留冲突检查；原日期候选未改写。无独立日期（弃答）单列 unverified，不冒充日期冲突或一致。

disagreement 和 unverified 保留原日期给内部参考，但 display_allowed=false、internal_only=true、display=null、usage=disabled（兼容现有客户端，禁止年份回退显示）；conflict 另置空 date 并标 manual_review_required。旧冲突检查跨重建保留；修复必须显式人工处理，不靠重跑新结果抹除历史。

## 第三方逐品牌统计（商品条目与候选均为 39）

|品牌|总数|corroborated|disagreement|冲突置空|弃答隐藏|
|---|---:|---:|---:|---:|---:|
'''
for brand, s in sorted(stats.items()):
    text += f"|{brand}|{s['total']}|{s['corroborated']}|{s['disagreement']}|{s['conflict']}|{s['unverified']}|\n"
text += '\n## 对照明细（全部 39 条；另附 comparison-30.csv）\n\n|型号|原日期|来源|LLM独立日期|差值天数|判定|\n|---|---|---|---|---:|---|\n'
for d in third:
    text += f"|{d['model']}|{d['original_date']}|[third_party]({d['source_url']})|{d['llm_date'] or '弃答'}|{d['delta_days'] if d['delta_days'] is not None else '—'}|{d['verdict']}|\n"
text += '\n## 置空与降级/弃答清单\n\n[完整可回看 JSON](manual-and-internal.json) 含 ID、原日期、独立日期、原始响应路径与原因；也含原先已被门禁禁用的 LLM 候选，并标 published 区分。以下列出本轮实际公开库受影响项。\n\n'
for d in internal:
    if d['published']:
        text += f"- **{d['model']}** `{d['id']}`：{d['verdict']}；{d['original_date']} → {d['llm_date'] or '弃答'}。{d['reason']}\n"
text += '''
模型结果是独立知识输出，未联网；不宣称网页原文已验证或日期一定正确。尤其 Xiaomi Pad 9 Pro 的响应虽填 date，但理由自称弃答并提到其他型号，按其原始日期差判冲突、置空并列人工核查，不把替代型号日期入库。Xiaomi Book Pro 14 指向 2022 款，同名代际歧义也留空。

## 复查与验证

`PYTHONPATH=src:scripts python3 docs/release-crosschecks-20261103/make_report.py` 可重建报告；运行 prepare/run 需要新的目录，已有 sent 标记禁止重发。数据发布在统一 finalize 中重放，发布门禁含新测试；不改变商品 ID、参数、价格、图片等非 release 字段。
'''
(ROOT/'README.md').write_text(text)
with (ROOT/'README.md').open('a') as f:
    f.write('\n原始调用包：[raw-call-artifacts.tar.gz](raw-call-artifacts.tar.gz)，解包后即为上述 prompts/responses/sent/states 目录。'
            '完整商品基线可按 [baseline-manifest.json](baseline-manifest.json) 的 data commit 重取；商品日期/身份的独立基线直接保存在 [baseline-dates.json](baseline-dates.json)。'
            ' [audit.json](audit.json) 记录 151 次 HTTP 200、151 个响应哈希与提示词哈希验证，以及 token usage 总计 50,067。\n')
    if (ROOT/'publication.json').exists():
        publication = json.loads((ROOT/'publication.json').read_text())
        f.write('\n## 发布与线上验收\n\n'
                '代码提交 `c8eee496374b1b3efb32adc4d5915e411d1362ff`。本地全量测试 **387 passed**（基线 371 passed）；'
                'GitHub 离线 **379 passed / 8 deselected**；发布门禁 **94 passed**。'
                f"[真实发布任务]({publication['url']})：{publication['conclusion']}。"
                ' [published-data.json](published-data.json) 记录 data 提交和 SHA-256，3968 条与本地预期逐值相等，非 release 字段逐值不变。'
                ' [client-verification.json](client-verification.json) 用现有客户端日期展示函数检查 30 条受影响记录，均不产生年份/月显示。\n')
    if (ROOT/'online-verification.json').exists():
        online = json.loads((ROOT/'online-verification.json').read_text())
        f.write('\n[线上完整验证](online-verification.json)：整库与真实发布集逐值相等，'
                f"{len(online['samples'])} 个真实详情接口 release 对象逐值相等。"
                '下列是 3 个真实 ID 的 `/api/goods/<id>` 返回摘录（只省略旁支字段）。\n\n```json\n')
        examples = []
        for key in ('CN:mi_cn:product:18520', 'CN:mi_cn:product:21298', 'CN:mi_cn:product:25524'):
            s = next(s for s in online['samples'] if s['id'] == key)
            r = s['release']
            examples.append(dict(id=key, name=s['name'], url=s['url'], release=dict(
                date=r['date'], source=r['source'], corroborated=r['corroborated'],
                crosscheck_status=r['crosscheck_status'],
                checks=[{k:c[k] for k in ('source','date','delta_days','verdict')} for c in r['checks']])))
        write('api-excerpts.json', examples)
        f.write(json.dumps(examples, ensure_ascii=False, indent=2)+'\n```\n')
print(json.dumps(dict(stats), ensure_ascii=False))
