from pathlib import Path
import json
p=Path(__file__).parent
x=json.load(open(p/'online-verification.json'));run=json.load(open(p/'final-run.json'));jobs=json.load(open(p/'final-jobs.json'))
assert run['id']==41883103308 and run['conclusion']=='success'
assert all(j['conclusion']=='success' for j in jobs['jobs'])
keep=('id','head_sha','status','conclusion','created_at','updated_at','run_started_at','html_url','run_attempt')
(p/'final-run.json').write_text(json.dumps({k:run.get(k) for k in keep},ensure_ascii=False,indent=2)+'\n')
(p/'final-jobs.json').write_text(json.dumps({'jobs':[{k:v for k,v in j.items() if k in ('id','name','status','conclusion','started_at','completed_at','steps')} for j in jobs['jobs']]},ensure_ascii=False,indent=2)+'\n')
data={'implementation_commit':'aa7bea9654ab47357856b74492d9af8e05da6a85','published_code_commit':'d430955773642a6460ec96a90315857ee2e35bf9','publication_run_id':41883103308,'publication_conclusion':'success','data_commit':'f16a874','publication_tests_passed':553,'cloud_full_tests':{'run_id':41888746881,'passed':851,'deselected_existing_live':8},'local_full_tests':{'passed':851,'deselected_existing_live':8},'rejected_stale_candidate':{'run_id':41881333830,'reason':'Concurrent change at data/hp/collection-status.json.checked_at; fresh collection rerun succeeded; no force merge'},'online':{k:v for k,v in x.items() if k not in ('queries','retired_samples')}}
(p/'publication.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
lines=['# 正式发布与线上验收','',
'惠普 **218 → 790**：787条有货号、3条为明确缺号原因的官方系列记录。新增569个历史货号；全部来自官方支持接口，不在本次完整商城目录。原有HP ID全部保留。','',
'实现提交：[aa7bea96](https://github.com/null-object-0000/goodsdex/commit/aa7bea9654ab47357856b74492d9af8e05da6a85)；已发布的留档边界修复：[d4309557](https://github.com/null-object-0000/goodsdex/commit/d430955773642a6460ec96a90315857ee2e35bf9)。全量采集入口另确保先复制本轮新档案，再执行重建/丢ID门禁，并有实际CLI重建回归。','',
'最终正式发布：[41883103308](https://github.com/null-object-0000/goodsdex/actions/runs/41883103308)，collect与publish均success；门禁 **553 passed**；data提交 `f16a874`；OSS逐文件GET哈希读回通过。原始完成状态摘录见final-run.json / final-jobs.json，发布日志见publication-final-excerpts.log。','',
'曾有一轮旧候选因 `collection-status.json.checked_at` 并发变化被门禁拦截（41881333830），未覆盖线上商品；以上最终任务从最新data重新采集后成功。没有绕过发布锁或强行合并冲突。','',
f"最新读回revision（共享库在本轮发布后也有其他任务更新，HP790及30条样本再次全部通过）：`{x['revision']}`；整库SHA256：`{x['goods_sha256']}`。部署端既有同步器返回 `{{\"ok\":true,\"count\":3414,\"succeeded\":9,\"errors\":[]}}`，未部署API代码。",'',
f"线上共{x['total']}行，HP{x['hp_count']}行；`retired_count={x['retired_count']}`，`retired_by_brand={json.dumps(x['retired_by_brand'],ensure_ascii=False)}`。原有9个HP下架记录的首次时间保留；抽查3条旧记录的原字段全部逐值保留。30条对照样本再次在正式线上核验通过。`/api/goods` 与不可变OSS blob逐值相等，详见online-verification.json。",'',
'## 两条实际API请求','',
'**兼容导出接口忽略q，返回完整3414行。下面是这两次原始响应中的目标记录摘录，不声称服务端执行了过滤。** 完整原文：api-zhan66.json.gz / api-omen.json.gz；对应单条详情也返回200并逐值相等。','']
for q in x['queries']:
 lines+=['`GET '+q['url']+'`','',f"HTTP200；返回{q['response_count']}行，其中惠普名称含关键字的记录{q['matching_hp_count']}条。",'', '```json',json.dumps(q['target'],ensure_ascii=False,indent=1),'```','']
lines+=['两个目标系列已可查。官方页没有唯一订购货号，故明确标注part_number_missing；销售状态未明示为unknown。它们不能替代机身货号的具体配置识别。','',
'## 测试与边界','',
'本地完整基线828 passed / 8 deselected；最终851 passed / 8 deselected。最终提交77ec42e8云端完整测试：[41888746881](https://github.com/null-object-0000/goodsdex/actions/runs/41888746881)，851 passed / 8 deselected；包含端到端回归验证全量采集先安装新档案再重建的入口顺序。原有8项live未新增跳过。','',
'历史支持目录的较旧分类缺席事件，不能覆盖另一分类的较新在场记录，也不能覆盖更晚的商品观察；新增回归防止先误下架再复活。冻结基线重放时非HP对象逐值不变，见local-invariants.json。','',
'星Book、光影精灵等消费系列的旧代仍有覆盖缺口；没有宣称穷尽所有系列/所有配置。新增SKU的未标存储单位/GPU不推测，默认占位图剔除，缺图写明原因。','',
'5候选入口、逐系列/代际分布、3条真实下架样本和30条对照见README.md / retired-samples.json / samples.md。','',
'```bash','python3 docs/hp-history-20261105/verify_online.py','```','']
(p/'publication.md').write_text('\n'.join(lines))
