# 字段级血缘验收

数据实现提交 `0464ae20`，后台最终实现提交 `c45afd8`。日期作为 sources 中的 release_date 观察，新增来源无需增加主表字段。来源信封的 observations 保留每次抓取；展示值的来源、字段、时间、URL、原文和方法取自同一次观察。

## 验收材料

- [五条真实完整样本](samples.json)：sources[]、display、field_history、conflicts 与证据缺项均未裁剪。
- [90天冲突测试商品](conflict-fixture.json)：2025-01-01 与2025-04-01，display.release_date=null，conflicts 保留两个来源，历史保留采纳后清空的变化。该商品明确标注fixture，URL未抓取，manual/verified=false/low，未写入生产。当前真实库没有符合规则的日期冲突。
- [完整校验](verification.json)、[真实分片详情回归](real-sharded-detail-verification.json)、[覆盖率](coverage.json)、[精确对账](reconciliation.json)、[历史证据缺项](issues.json)。
- 截图：[详情来源标记](detail-1440.png)、[血缘展开](lineage-1440.png)、[手机详情](detail-390.png)、[手机血缘](lineage-390.png)、[系列与样本](series-samples.png)、[来源覆盖率](coverage-1440.png)、[冲突](conflict-1440.png)、[完整变更链](conflict-history.png)。

截图来自CI前端产物及隔离的真实发布集回放。已逐文件确认：截图使用的前端与最终CI 42168219532的83个前端文件内容完全一致。分片详情修复以实际发布数据逐字段校验，防止精简列表索引覆盖完整详情中的方法、URL、observations和alternatives。

## 五个样本

| 商品 | 日期来源 | 采纳日期 |
|---|---|---|
| 比亚迪 汉2023款DM-i | ithome（第三方） | 2023-05-18 |
| iPad，MD3Y4CH/A | apple_newsroom（官方） | 2025-03 |
| MacBook Pro，MDE14CH/A | 无合格日期 | null |
| Osmo Mobile 6浅银灰 | series_inherit | 2022-09 |
| 比亚迪第三代秦PLUS DM-i | llm_verified（有核验URL） | 2026-10 |

## 选择规则与兼容

日期按精度、官方、登记顺序、最早实际捕获时间排序；日/月转换为区间，最小间隔>45天进入冲突。名称按官方商城、官方支持站、自有App目录、第三方；图片按官方主图、白底/规格图、明确标168×168的非主图设备图标，场景和宣传图排除；价格保留price_kind和promo。每个非空display有reason；候选保留alternatives，历史只在采纳value变化时新增。

旧release/release_llm/release_series/page_first_archived保留可读，release_effective为新日期视图的兼容镜像。五个样本均已验证仅凭sources独立重建display，无需旧release主列。新观察必须有真实带时区抓取时间、完整HTTP(S)证据URL和page_fetch/api/manual/series_inherit方法；llm_verified还须verified，系列推导须source_series和samples。

历史缺少抓取时间的观察不进入display。旧值只记录legacy_capture/legacy_directory_mapping时仍保留该方法，不擅自称为页面或API抓取：原始采集机制的历史回填尚未全部完成。verification.json含方法分布，issues.json保留缺项断言；非空display没有未知来源。

## 当前覆盖率

| 来源 | 有日期发布行 |
|---|---:|
| 官方 | 807 |
| 第三方 | 108 |
| 系列推导 | 522 |
| LLM核验 | 209 |
| 合计 | 1646 |
| 无日期 | 2821 |
| 全部发布行 | 4467 |

当前1646/4467=36.85%；题述46.08%为历史1646/3572。当前净增895个发布行，有日期数未变，不能沿用历史分母。统计单位为发布行，保留同ID不同配置。覆盖率及按发布者拆分见coverage.json，发布后meta计数已读回一致。

数据发布run **42165059775 success**，data提交ac0e877f，revision `6be9a2be31ca4ac8bf9d88a3749eebf8`。发布goods.json.gz的Git blob仍为c1897372，与抽样审计字节完全相同；全部原始观察保留。

## 验证与发布状态

Python完整非live测试1100通过、8项live未运行；API393通过、4按原规则跳过；后台14通过，类型检查通过。共享finalizer完整重放：4467行goods输入输出SHA256相同，价格历史新增0。17个汽车商品分别校验不可变配置证据和来源展示镜像；篡改配置、展示价格或删除必要结构字段仍拒绝发布。

后台最终CI **42168219532 success**（c45afd8）。修复分片详情血缘被列表摘要覆盖，并补有界启动等待，随后仍执行三次公网完整提交号检查。后台实际部署结果以[publication.json](publication.json)为准，构建通过不等于上线通过。较早aac48fd曾通过公网三次健康检查；最终c45afd8切换过程遇到SSH与公网超时，实例仍为Running，尚未确认上线。该项不能算部署验收通过。

## 新增一个来源

1. 在lineage.REGISTRY登记source、分组、允许域名和白名单顺序；日期源无需改商品主表。
2. 抓取页面或API，保存实际抓取时间、URL、原文、方法、HTTP状态和置信度；LLM核验附被核验URL，系列推导附来源系列与样本。
3. 构造kind=release_date的观察，fields放release_date、precision、quote，通过upsert_source提交。
4. 重放并核对reason、alternatives、conflicts、field_history，冲突不得静默丢弃一个来源。
5. 运行lineage/product_sources回归及发布门禁，经共享发布锁生成meta/分片，读回验收。

复现：`python3 scripts/audit_field_lineage.py --input /path/goods.json.gz --output /path/audit`。浏览器复现脚本在后台仓库services/admin-pro/scripts/verify-canonical-lineage.mjs，要求显式提供CI产物和真实快照，使用隔离数据库。
