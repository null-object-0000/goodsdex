"""Replay frozen proposals, independently recorded verdicts, and live snapshot."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import gzip
import json
from pathlib import Path
import sys
sys.path[:0]=['src','scripts']
from goodsdex.release_dates import brand_llm_gate
from release_family_llm import write
ROOT=Path(__file__).resolve().parent
# Independent checks never repair an original candidate citation.
FACTS=[
('2017-12','https://m.21jingji.com/article/20171207/herald/39632cbe1b2efc81da5c7d434135357a.html','2017-12-07 现场发布报道同时报道红米5和5 Plus。','原引用跳转 err.www.mi.com/04.html；无月份原文。'),
('2025-06','https://www.mi.com/my/support/faq/details/KA-572986/','The launch time of the REDMI Pad 2 is June 5th, 2025.','候选填2025-08，且abstention_reason称无法确定月份；原产品页不支持其月份。'),
('2017-03','https://www.fimi.com/cn/about-fimi.html','2017年3月 小米无人机4K版本发布','date为“2017-05或null”，格式非法；无url/quote；制造商里程碑为2017-03。'),
('2024-04','https://www.mynewsdesk.com/uk/dji/pressreleases/dji-pro-launches-next-generation-tools-offering-swift-setup-intuitive-operation-seamless-integration-and-extended-focus-control-3315434','9 April 2024; DJI Focus Pro; LiDAR','DJI自行发布的新闻稿支持月份与LiDAR组件；原引用404，不能事后替换抬分。'),
('2023-05','https://www.fujifilm.com/ae/en/news/hq/9421','May 24, 2023; FUJIFILM X-S20','月份正确，6月为开售；原引用仅产品页、quote空，模型承认未核原句；直抓403，原依据未证实月份。'),
('2017-01','https://www.dpreview.com/news/2919368831/fujifilm-expands-weather-resistant-lens-selection-with-xf-50mm-f2-r-wr/','January 19, 2017; FUJINON XF50mmF2 R WR','现场新闻及内嵌原厂新闻稿支持1月公告；2月开售；原引用产品页未核月份。'),
('2021-01','https://www.fujifilm-x.com/global/news/fujifilm-announces-new-fujinon-xf70-300mmf4-5-6-r-lm-ois-wr-lens/','01.27.2021; XF70-300mmF4-5.6 R LM OIS WR','官方页头2021-01-27，正文年份2020疑为笔误；页头及同期报道支持2021-01公告，3月开售；原产品页月份未核准。'),
('2015-05','https://fujifilm-korea.co.kr/support/notice/id/7173','2015-05-18; XF90mmF2 R LM WR','官方分站5月公告、7月开售；原引用fujifilm.com.cn无www路径DNS失败；原句空。'),
('2020-01','https://www.dpreview.com/news/4262945623/fujifilm-announces-more-affordable-xc-35mm-f2-prime-lens/','January 23, 2020; XC 35mm F2','首次公告1月；候选2月是开售月，event=announcement时错误；原产品页无公告引文。'),
('2012-01','https://thelensdb.com/lenses/fujifilm-super-ebc-fujinon-xf-60mm-f24-aspherical-r-macro-2012','Mississauga, ON, January 9, 2012; XF60mmF2.4 R Macro','保留的原厂X-Pro1新闻稿明确包含该镜头；不能仅借机身日期。原产品页原句空，月份未回指。'),
('2025-06','https://www.fujifilm.com/us/en/news/digital-cameras/fujifilm-introduces-fujifilm-x-e5-mirrorless-digital-camera','June 12, 2025; FUJIFILM X-E5','官方6月公告；8月为发售，原产品页/空quote未支持月份。'),
('2015-10','https://www.fujifilm.co.jp/corporate/news/articleffnr_1016.html','2015年10月21日; XF35mmF2 R WR','官方10月21日公告；候选reason说15日但年月相符；原fujifilm.com.cn/2015/1015路径DNS失败，原依据未证实。'),
('2022-11','https://www.fujifilm-x.com/en-gb/news/fujifilm-launches-fujinon-xf30mmf2-8-r-lm-wr-macro/','TOKYO, November 2, 2022; XF30mmF2.8 R LM WR Macro','候选2022-09误把X-H2同期事件混进来，正式产品公告为11月；原产品页无引文。'),
('2012-09','https://www.dpreview.com/articles/9897321674/fujufilm-launches-xf-18-55mm-f2-8-4-0-ois-semi-fast-standard-zoom-and-xf14mm-f2-8-21mm-equivalent/','September 6, 2012; XF14mm F2.8','按正式产品公告9月核对；此前6月路线图已预告开发，不能称毫无更早信息；原产品页无月份引文。'),
('2018-01','https://www.chem-t.com/fax/images/tmp_file3_1517391530.pdf','2018年1月31日; XC15-45mmF3.5-5.6 OIS PZ','存档原厂新闻稿支持1月公告，非3月单镜开售；原产品页无日期原句。'),
('2023-05','https://www.fujifilm.com/kr/en/news/hq/9420','May 24, 2023; XF8mmF3.5 R WR','官方5月公告，6月29日开售；原产品页无原句且未核月份。'),
('2018-07','https://dc.watch.impress.co.jp/docs/news/1133999.html','2018年7月20日; XF200mmF2 R LM OIS WR','原始发布报道支持7月公告，10月开售；候选reason提X-T100同期不准确，原产品页无月份支持。'),
('2021-04','https://www.fujifilm-x.com/en-sg/news/fujifilm-announces-new-fujinon-xf18mmf1-4-r-lm-wr-lens/','TOKYO, April 15, 2021; XF18mmF1.4 R LM WR','官方4月公告，5月开售；原产品页无原句且模型承认无法回指。'),
('2016-08','https://dc.watch.impress.co.jp/docs/news/1016454.html','2016年8月25日; XF23mmF2 R WR','现场发布报道为8月，10月开售；候选7月混淆X-T2，原引用fujifilm.com.cn路径DNS失败。'),
('2022-05','https://www.fujifilm-x.com/en-us/news/fujifilm-announces-fujinon-xf150-600mmf5-6-8-r-lm-ois-wr/','TOKYO, May 31, 2022; XF150-600mmF5.6-8 R LM OIS WR','官方5月公告，7月开售；原产品页未回指月份，quote空。')]

def main():
    selected=json.loads((ROOT/'audit-sample.json').read_text())['samples']
    captures={x['family']:x for x in json.loads((ROOT/'citation-captures.json').read_text())}
    assert len(selected)==len(FACTS)==20
    checked=[]
    for x,(date,url,quote,reason) in zip(selected,FACTS):
        checked.append(dict(**x,correct_date=date,date_correct=x['proposal']['date']==date,
            identity_match=True,evidence_supported=False,correct=False,
            verification_url=url,verification_quote=quote,verdict_reason=reason,
            original_citation_capture=captures[x['family']],checked_at=datetime.now(timezone.utc).isoformat()))
    write(ROOT/'audit-review.json',checked)
    candidates=json.loads((ROOT/'candidates.json').read_text())
    queue=json.loads((ROOT/'review-queue.json').read_text())
    by={x['family']:x for x in checked}
    reviews={}
    for brand,q in queue.items():
        if not q['samples']:continue
        samples=[]
        for s in q['samples']:
            x=by[s['family']]
            samples.append({**{k:x[k] for k in ['family','correct_date','date_correct','identity_match','evidence_supported','correct','verification_url','verification_quote','verdict_reason','checked_at']},'candidate_sha256':s['candidate_sha256']})
        reviews[brand]=dict(seed=q['seed'],universe_sha256=q['universe_sha256'],samples=samples)
    write(ROOT/'reviews.json',reviews)
    gates=brand_llm_gate(candidates,reviews)
    write(ROOT/'brand-gates.json',gates)
    outcomes=json.loads((ROOT/'outcomes.json').read_text())
    usage=json.loads((ROOT/'usage.json').read_text())['totals']
    sessions=[json.loads(p.read_text()) for p in (ROOT/'sessions').glob('*.json')]
    initial=min(sessions,key=lambda s:s['started_at'])
    baseline=json.loads(Path('docs/release-dates-round6-20261103/usage.json').read_text())['request_seconds']/20
    summary=dict(families=100,requests=usage['calls'],successful_responses=100,abstentions=71,valid_date_candidates=28,invalid_date_outputs=1,
        elapsed_seconds=initial['elapsed_seconds'],serial_baseline_seconds_per_family=baseline,speedup=100*baseline/initial['elapsed_seconds'],http_429=usage['http_429'],backoff_seconds=usage['backoff_seconds'],usage={k:usage[k] for k in ['prompt_tokens','completion_tokens','total_tokens']},
        sample_families=20,sample_date_matches=sum(x['date_correct'] for x in checked),sample_evidence_accepted=0,
        acceptance='failed',full_run_started=False,remaining_families_not_sent=2813-100,reason='Per-brand month and original-citation audit failed. No corrected dates or replacement citations were written to official/LLM inputs.')
    write(ROOT/'acceptance.json',summary)
    lines=['# 并发 LLM：100族真实验收','', '**速度验收通过，质量验收未通过，未启动2813族全量。新增发布0。**','','100次真实请求全部返回非空正文，71弃答、28个格式合法日期候选、1个非法日期字符串（2017-05或null）。6路worker、全局4 QPS、连续3次429熔断；实测429=0，退避=0秒。', '',f'整批墙钟 **{initial["elapsed_seconds"]:.3f}秒**；输入28741、输出11597、总40338 tokens。第六轮38.459秒/20族=每族{baseline:.6f}秒；100族串行等效192.296秒，本次加速 **{summary["speedup"]:.3f}倍**。样本类别和响应长度不同，这是按用户指定基线计算的观测比值，不是同输入A/B测试；不线性承诺全量耗时。','', '原始逐族响应、实际model、usage、captured_at和attempts在 responses/；状态在states/，原始响应未删减，未把弃答算成功日期。首次运行详见sessions/；没有补问或修正后重抽。抽样在检索前冻结，选出全部4个非富士非空输出（含格式非法）并按固定seed抽16个富士，包含门禁所需3个富士样本。惠普25/25弃答，没有可评估日期，不能记成0%准确或100%正确。', '', '|品牌|100族中的请求/弃答/合法日期/非法|20族审计数|月份相符|型号+月份+原依据合格|放行|','|---|---|---:|---|---|---|']
    for brand in ['小米','大疆','惠普','富士']:
        os=[x for x in outcomes if x['brand']==brand]; ss=[x for x in checked if x['brand']==brand]
        counts=Counter(x['result'] for x in os)
        month=f'{sum(x["date_correct"] for x in ss)}/{len(ss)}={sum(x["date_correct"] for x in ss)/len(ss):.2%}' if ss else '不可评估'
        evidence=f'0/{len(ss)}=0%' if ss else '不可评估'
        lines.append(f'|{brand}|25/{counts["abstention"]}/{counts["candidate"]}/{counts["invalid_or_failed"]}|{len(ss)}|{month}|{evidence}|禁用|')
    lines+=['','月份准确率保留原始非法输出作为错误：小米1/3；只看格式合法日期为1/2。富士13/16=81.25%，单看月份也未达到90%。所有原引用均未完成“型号与首次月份”支持核验，不能拿事后找到的独立链接替换原引用来抬分。403/DNS失败表示本次无法取证，不断言日期不存在；即使官网存在同型号也不等于支持月份。门禁的可重复10%子样本另存reviews.json/brand-gates.json，均禁用。','', '|型号族|LLM年月|独立核对年月/依据|日期对错及原引用结论|','|---|---|---|---|']
    models={f['family']:f['model'] for f in json.loads((ROOT/'families.json').read_text())}
    for x in checked:
        model=models[x['family']].replace('|','/')
        lines.append(f'|{model}|{x["proposal"]["date"]}|[{x["correct_date"]}]({x["verification_url"]})|'+('月份相符；' if x['date_correct'] else '错误；')+x['verdict_reason']+'|')
    online=json.loads((ROOT/'online-verification.json').read_text());cov=online['coverage']
    lines+=['','原始evidence链接、quote、reason及独立核对原文均完整见audit-review.json。20族15/20月份相符（75%），含证据合格0/20。并非全族随机总体准确率置信保证。','', '## 当前线上四列表（本轮增量0）','',f'来自{online["checked_at"]}实取/api/goods；不是全量跑完后的结果。此前跨源核查已改变第六轮历史覆盖，本次没有修改数据输入。日期字段覆盖{cov["covered"]}/{cov["total"]}={cov["coverage"]:.2%}。','', '|品牌|真源 official+third_party|hidden|LLM|仍缺|','|---|---:|---:|---:|---:|']
    for brand,x in cov['brands'].items():lines.append(f'|{brand}|{x["true_source"]}|{x["official_hidden"]}|{x["llm"]}|{x["missing"]}|')
    lines.append(f'|合计|{cov["sources"]["official"]+cov["sources"]["third_party"]}|{cov["sources"]["official_hidden"]}|{cov["sources"]["llm"]}|{cov["total"]-cov["covered"]}|')
    rows=json.loads(gzip.decompress((ROOT/'online-goods.json.gz').read_bytes()));disabled=sum(x.get('release',{}).get('usage')=='disabled' for x in rows)
    active=sum(bool(x.get('release',{}).get('date')) and x['release'].get('usage')!='disabled' for x in rows)
    lines += ['',f'LLM日期字段39/3968={39/3968:.2%}，占688个非空日期{39/688:.2%}；本轮新增LLM占比0%。上述四列沿用coverage()按非空date计数，包含被交叉核查禁用的留档日期，不应当成可用于判断的覆盖；线上另有{disabled}条release usage=disabled，剔除禁用项后可用日期{active}/3968={active/3968:.2%}。', '', '## 3个线上真实ID摘录','', '这是既有字段契约的实时检查，本轮没有新增候选上线，不声称新补齐已发布。']
    for x in online['samples']:
        excerpt={k:x['release'].get(k) for k in ['date','source','usage','internal_only','display_allowed','estimate_notice']}
        lines+=['',f'[{x["id"]}]({x["url"]})','', '```json',json.dumps(excerpt,ensure_ascii=False,indent=2),'```']
    lines+=['','## 断点续跑与停机','', '新计划先不带--run冻结families.json/plan.json，再带--run执行。--concurrency默认6（1..6），--qps默认4（0..4）；降低参数可控速。SIGINT/SIGTERM停止新增请求，等待已发送响应落盘。成功ok或已有response永不重发；429仅重试当前族，退避1/2/4/8秒并尊重Retry-After（取较大值），累计重试次数与全局连续429计数跨重启保留。进程级flock阻止同目录双进程派发；全部共享completion顺序429计数，连续3次触发持久circuit.json，已在途的最多6个请求允许完成，后续不再发送。显式--resume-after-circuit检查后重启才解除，单次成功响应不会解除已开的熔断。','', '状态pending/sent/ok/failed与响应使用fsync+原子替换落盘。异常中断的sent（无已保存response）续跑时标记interrupted_usage_unknown，再请求该未完成族；无法在网关不支持幂等键的情况下保证此类未知在途不重复计费，已成功落盘的族不受影响。明确非429失败终结failed，不做未经授权的网络/解析重试。', '', '本次同目录再跑100族续跑验收实测0新增请求；结果见resume-check.json。100族质量验收failed，禁止把后续命令当成本次全量执行记录。', '', '```bash', 'PYTHONPATH=src:scripts python3 scripts/release_family_llm.py \\', '  --rows _data/public/goods.json --out docs/release-dates-concurrent-20261103 \\', '  --run --limit 100 --concurrency 6 --qps 4', '```', '', '测试基线与最终结果见tests-baseline.log/tests-final.log；official/LLM输入hash及已有release不变量见invariants.json。']
    lines += ['', '完整回归：基线387 passed；本轮395 passed，1个原有插件warning，无新增红项。本轮提交只含并发脚本、对应测试与本目录验收产物。']
    (ROOT/'README.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
