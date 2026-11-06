# 字段级血缘验收

`product_sources` 仍负责一商品一主源及来源升级，日期为独立 `kind=release_date` 观察，不参与主源竞争。来源信封下的 `observations[]` 是逐次抓取，信封头是聚合预览；解析器只从单条观察读取值、时间、URL和证据，不混用信封头时间。

每个 `display` 非空值具备 source/field/captured_at/method/evidence_url/quote/http_status/confidence/source_group/reason/alternatives。未返回的 HTTP 状态、未提供的原文保持 null，不捏造 200。参数递归生成 `params.xxx` 字段血缘。缺少真实抓取时间的历史观察保留在 sources，但不进入 display；历史名称主列仍可读，后台以 display 为准。缺证的日期估计和不满足系列样本要求的旧断言完整留在 lineage_issues，旧列也不删除。

日期：日优于月，同精度官方优先，再按注册顺序，最后最早捕获。日期按日/月区间计算，最小间隔超过45天即置 display.release_date=null，所有值保留在 conflicts。官方商城/支持站/自有目录/第三方的名称顺序，官方主图/白底规格图/168×168非主图设备图标的图片顺序，以及官方商城/渠道的价格顺序均有解释。场景图、宣传图禁止采纳。price_kind 与 promo 保留。source_group 供覆盖率按官方/第三方/系列/LLM归类。

field_history 只在 value 变化时追加，包含 at、from、to、reason、actor。新增 alternatives 或刷新证据不产生历史噪声；不会把迁移时刻当 captured_at。旧 release/release_llm/release_series/page_first_archived 继续可读；release_effective 是新 display 的兼容镜像。带 lineage_policy 的覆盖率只读 display，不回退旧日期。页面首存独立观察，不进入 release_date 候选。

## 样例与覆盖率

- [5条完整样例](audit/samples.json)：第三方、官方、无日期、系列、LLM。
- [90天冲突 fixture](conflict-fixture.json)：显式测试商品，display.release_date=null，conflicts 保留两来源，未写入生产。当前真实发布库无符合新规则的日期冲突，不虚构实际商品。
- [覆盖率及逐行差异](audit/coverage.json)、[口径对账](audit/reconciliation.json)、[证据缺项](audit/issues.json)。

题述46.08%是 **1646/3572**；已发布的896条新增设备无日期，当前相同旧规则为 **1646/4468=36.84%**。当前发布来源分桶为 **官方807 + 第三方108 + 系列522 + LLM209 =1646**。41条旧 llm_crossed 依据真正抓取的发布者归类，模型交叉核对仍留原证据。全部旧日期镜像保留，采纳日期的精度及来源可能按新规则调整；逐行差异可复核。不是通过更改分母伪造覆盖率。

新结构可独立解析：`product_sources.materialize({'id':..., 'sources':...})`；不需要 release* 主列。旧字段只由迁移适配器读取，新增源走 upsert_source。

## 新增一个来源

1. 在 lineage.REGISTRY 登记唯一 source 名称、official/third_party/series/llm 分组、允许域名和排序；仅新增日期源无需改商品表或 SOURCE_TIERS。
2. 抓取页面或 API，保存实际字段抓取时间（带时区）、原文片段、完整 URL、方法、实际 HTTP 状态和置信度；核验 LLM 必须带已核验 URL，不能拿模型响应时间当页面抓取时间。
3. 生成一条 `kind=release_date`、`fields={release_date,precision,quote}` 的 source 观察，使用 `upsert_source(row, observation)` 提交；系列推导附 source_series 与 samples。
4. 重放解析器，核对 display.reason、alternatives 和 conflicts；确认只在采纳值改变时生成历史。
5. 跑 test_lineage/test_product_sources 和发布门禁，通过共享发布锁生成完整分片和 meta 后发布，读回对账。

## 验证和发布

正式提交与 run、线上读回结果见 publication.json。回归命令：`PYTHONPATH=src:scripts python -m pytest -q -m 'not live'`。迁移沿用 `migrate-product-sources.yml`：同一发布锁读取最新 data，备份原发布集，运行 finalizer、门禁、OSS 不可变分片、最后切换 manifest，不使用本地旧快照覆盖现网。

当前4467行发布集、最新测试和截图验收见 [补齐验收](../field-lineage-acceptance-20261106/README.md)。上述4468行为较早审计快照，不能用作当前发布分母。
