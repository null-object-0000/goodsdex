# 独立页面首存与模型月份发布

## 字段与优先级契约

每次 `scripts/finalize_public.py` → `goodsdex.dedupe.finalize_public` 都在单品与系列证据重放后运行 `apply_date_enrichment`，再生成详情分片、索引、manifest。输入是已提交的 `data/enrichment/date-inputs.json.gz`，无需相邻目录或在线采集。发布门禁包含集成回归测试。

日期参考优先级：`release`（单品 official/third_party）> `release_series`（系列）> `release_llm`（模型）。并存时以更高优先级为准，模型永不回写两种原字段。

`page_first_archived` 是独立维度，只回答「该页面至少在此时已存在」，不是发售时间，不参与上述排序。URL 复用可能早于当前商品，改版和存档稀疏可能偏晚。

- `page_first_archived: {date,evidence_url,count_200,captured_at}`：只接 `status=archived`。`count_200=null` 是 prefix collapse 结果不提供精确计数，不伪造为 1。原结果无逐请求采集时刻，`captured_at` 明确定义为本轮冻结导入时间，不冒充 Wayback 抓取时间（抓取时间在证据 URL）。
- `release_llm: {date,granularity:'month',source:'llm',model,confidence,evidence,brand_accuracy}`：月份是模型对型号族首次公告月的估计，非国行开售日；品牌准确率以 0–1 表示。≥97% 标 high，允许作为最低优先级事实参考；90%–97% 标 medium，仅作候选参考；低于90%或未知一律不发布。忽略模型自评 confidence。原 evidence URL/quote/reason 原样保留，新增原响应文件、SHA256、捕获时刻与 family 回指；有 URL 不等于引用已核实。

`not_archived` 表示未观测到该页面的200存档，不能证明页面不存在；`error` 表示查询失败，不能等同未收录。两者均不写字段。每轮先清理这两个自有字段再按冻结输入重建，旧断言不会残留。

## 输入来源与分档

Wayback `results_final.jsonl` 的 id 是任务号 `full:xxxxx`，经同批 manifest 的 job_id → record_ids 精确映射，不按名称或模糊 URL 匹配。保留所有 3338 页结果及完整 manifest 和输入 SHA256。LLM 保留443个给日期族、品牌核验统计及原响应路径/哈希；模型为 `deepseek-v4.1-flash-1017`。原始逐响应可从 `staging/release-full-20261103/raw-artifacts.tar.gz` 恢复。

|品牌|本地核验准确率|策略|本轮发布记录数|
|---|---:|---|---:|
|Apple|10/10 = 100%|high，最低优先级事实参考|185|
|富士|9/10 = 90%|medium，仅候选参考|48|
|小米|2/3 = 66.67%|排除，低于90%|0|
|大疆|8/10 = 80%|排除，低于90%|0|
|比亚迪|2/3 = 66.67%|排除，低于90%|0|
|惠普|0/0，N/A|排除，无可评估准确率且无日期候选|0|
|小米汽车|0/0，N/A|排除，全部已有官方日期，未跑LLM|0|

需求摘要提到富士81%，但本机冻结实验 `accuracy.json`、`reviews.json` 与 README 均为9/10=90%；本实现采用这份实际核验输入，未修改或重跑核验。准确率分母是「给过原URL/引文且取得独立真值的日期样本」，样本很小，不代表总体保证；Apple原依据支持仅1/10，富士0/10，不能把品牌日期抽样准确率当作证据可用率。缺失、错误、待核实引用均保留原貌，不用事后证据替换。

## 验收数字

|字段|发布前|发布后|逐值保护|
|---|---:|---:|---|
|release|671|671|全部原对象不变|
|release_series|149|149|全部原对象不变|
|page_first_archived|0|1262|独立字段|
|release_llm|0|233|Apple185 + 富士48|

总发布记录2909。Wayback：Apple623、小米511、大疆79、惠普38、富士11。全量输入 archived1084页/1875记录，not_archived2254页/3680记录，error0页/0记录；当前发布库只匹配1262条archived记录、1376条not_archived记录，其余271条无此批页面结果。全量输入包含已被发布规则排除的配件等，不能把1875直接当作发布条数。548条页面首存和43条模型月份与单品日期并存。

数据分支基线 `43d2c66d`，与实取线上同为2909条，所有ID、release与release_series逐值相同；线上尚有209条旧采集时刻及2条旧params，使用最新data作为发布基础，未将旧线上快照覆盖回去。完整逐字段对照、状态统计在 [verification.json](verification.json)；每个新字段5条真实ID、名称、证据和并存情况在 [samples.md](samples.md)。

## 验证与复现

离线基线473通过；加入9项边界、真实finalize重放和详情分片测试后482通过。API同步/惰性详情/分页分组测试278通过，原有失败为0；API契约提交 `621e767`。API详情透传完整对象，无需服务代码升级；列表索引不含 release_series、release_llm、page_first_archived；完整 `/api/goods` 导出保持完整契约。

```bash
# 仅在需要显式换一批输入时冻结；不调用采集器或模型
python scripts/import_date_enrichment.py --wayback ../goodsdex-webarchive --llm staging/release-full-20261103
# 日常发布入口（CI共享流水线自动调用）
python scripts/finalize_public.py --public /path/to/data/public
# 线上发布验收
python docs/independent-dates-20261103/verify_publication.py --published /path/to/data/public/goods.json --online
```

## 真实发布与线上验收

2026-11-03 21:30（北京时间）完成线上验证。[正式流水线41644321802](https://github.com/null-object-0000/goodsdex/actions/runs/41644321802)成功，发布门禁181项通过；云端完整测试成功。代码提交 `9c2058ac`，数据提交 `c45a37a18a3b837c78edd173956a7a7ac5aea600`，API契约提交 `621e767`。

OSS goods.json读回字节与发布分支完全一致，SHA256=`5e927238d68150d7a1541dc6641262e7155c0a86d4b09161d3d8a10ad9f99f13`。服务端现有同步器 primeCatalog 返回 `{"ok":true,"count":2909,"errors":[]}`，线上 meta 引用同一 SHA256，完整目录逐值相同。上述四个验收计数及两路品牌数均已在真实发布产物验证。

十条新字段样本和一条release_series均逐字段对照真实HTTP返回，分页/分组列表均不携带三个详情日期字段。[线上真实返回摘录](live-excerpts.md)、[完整详情返回](live-api-samples.json)、[最终验收](verification.json)、[同步记录](api-sync.log)、[正式发布记录](publication.json)、[流水线日志](pipeline.log)保留完整证据。所有原release和release_series逐值不变；与其并存的模型日期永远优先级最低。
