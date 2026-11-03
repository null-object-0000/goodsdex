# 第二轮：发售／发布月份补齐（2026-11-03）

**本轮取得增量，但未达到用户要求的完整验收。** `release.date` 从 401/3968（10.11%）增至 **454/3968（11.44%）**，增加 **53 行 / 53 个唯一商品 ID，+1.34 个百分点**。新增 16 条 official、37 条 third_party；新增 LLM 调用 0 次。Apple 的 294 条真源和 40 条 LLM 均未重做或改变。

新增记录中 **35 条是发布时间（announcement）、18 条是发售／首销月份（availability）**；不把发布时间改称开售时间。本轮结果不是“新增 53 条已发售月”。既有 31 条 Apple 未来计划仍为 planned_availability/reference。

**关键未满足项：小米要求的 30 条 hidden 独立样本不能交付。** 对全库 2242 个唯一小米 ID 实际调用商城移动接口后，只找到 16 个带隐藏日期的型号；没有凑 30 个颜色、容量、重复参数节点。其字段实际叫“发布日期”，不是“发布时间”；可见的“发布时间”仍只出现在电视节点。16 个可做辅助核对，但其中 1 个第二来源是公开官方财报，其余为独立媒体正文；按用户指定的“京东上市时间／mi.com 规格页／官方新闻稿”严格口径，财报只作辅助，也不计入指定类型，**不以此宣称指定来源的 30 条核验通过，不放行 hidden**。惠普、比亚迪也未得到新增可入库日期。

## 1. 最终覆盖率（行口径）

真源 = official + third_party；LLM 即使引用官网也独立计数。四个分项之和逐品牌等于总行数。`official_hidden` 指通过门槛、实际入库的隐藏日期；本次为 0。

| 品牌 | 总行数 | 真源 | official_hidden | LLM | 仍缺 |
|---|---:|---:|---:|---:|---:|
| Apple | 640 | 294 | 0 | 40 | 306 |
| 比亚迪 | 14 | 0 | 0 | 0 | 14 |
| 大疆 | 783 | 6 | 0 | 0 | 777 |
| 富士 | 63 | 3 | 0 | 0 | 60 |
| 惠普 | 218 | 0 | 0 | 0 | 218 |
| 小米 | 2247 | 108 | 0 | 0 | 2139 |
| 小米汽车 | 3 | 3 | 0 | 0 | 0 |
| 合计 | 3968 | 414 | 0 | 40 | 3514 |

详细机器结果：[coverage.json](coverage.json)；逐条新增的型号、事件、原文、链接：[new-dates.csv](new-dates.csv)、[new-candidates.json](new-candidates.json)。

小米增加 41 行（67 → 108），大疆增加 6 行，富士增加 3 行，小米汽车增加 3 行；惠普、比亚迪增加 0。最终候选排除了 REDMI K90：同一商品 ID 留存 3 行、两个 commodity gid，报告没有分别给这些版本发售证据，因此三行全留空，见 [identity-exclusions.json](identity-exclusions.json)。初始回放曾显示 457 行，最终审核撤回后是 454 行。

## 2. 小米 hidden：全库扫描、逐条核对与放行结论

扫描 2247 行 / 2242 个唯一 ID：HTTP 均为 200；业务成功 1879 个、已下架 362 个、1 个 reference 型号 JZ2301 返回业务 500“系统繁忙，请稍后重试”（有界重试一次仍失败）。一次移动网络失败重试后成功。**仅能确认成功返回范围的 hidden 数量为 16**；362 个下架记录不能宣称它们从未有过日期。即便未解析的 1 个型号有隐藏日期，也不能满足 30 个独立样本。缓存扫描另检查过 1789 个 ID，同样只有这 16 个隐藏日期。

- 所有隐藏日期均为耳机；手机、家电在本次成功返回的命名日期节点中都没有 hidden 日期。
- 按品类统计：[mi-scan-summary.json](mi-scan-summary.json)。完整逐请求结果：[mi-scan.jsonl.gz](mi-scan.jsonl.gz)，包括业务码、精确 productId、原名、节点 locator、isPageShow、值、响应 hash。16 个隐藏源的单独 JSON 留在 evidence/。
- 同型号多个 goodsList 节点只计一次，未用重复颜色／容量节点凑数。
- 另从 4 个耳机媒体正文的京东链接继续核对，3 条最终跳到京东首页，1 条只返回 JS 跳转壳（均 HTTP 200），没有拿到型号规格和上市时间；不把 200 当核验成功。见 [hidden-jd-attempts.json](hidden-jd-attempts.json)。

| 品类 | 隐藏日期独立型号 | 辅助第二来源核对 | 指定来源类型核对 | 放行结论 |
|---|---:|---:|---:|---|
| 耳机 | 16 | 16/16，100%（媒体与官方材料合计，仅月级） | 0，无法给准确率 | 不放行 hidden；不能外推 |
| 手机 | 0 | 不适用 | 不适用 | 无 hidden 样本，不给准确率 |
| 家电及其他 | 0 | 不适用 | 不适用 | 无 hidden 样本，不给准确率 |

下面是实际 16 条明细，**不是用户要求的 30 条**。其余 14 条不存在可交付的独立 hidden 样本，不虚构“正确值”。“对”只表示第二来源给出的月与 hidden 月一致；不表示原始日级日期或发布／开售事件完全相同。Buds 5 Pro 的公开官方财报及其余媒体链接都不替代指定的 JD／mi.com 规格页／官方新闻稿核验门槛。

| 型号 | hidden 月 | 第二来源 | 对/错 | 正确月 | 辅助来源类型 |
|---|---|---|---|---|---|
| Xiaomi双磁超动态单元耳机 | 2023-05 | [原文](https://www.ithome.com/0/694/460.htm) | 对 | 2023-05 | 辅助：第三方媒体 |
| REDMI Buds 6 活力版 | 2024-05 | [原文](https://www.ithome.com/0/769/177.htm) | 对 | 2024-05 | 辅助：第三方媒体 |
| REDMI Buds 6 青春版 | 2024-10 | [原文](https://www.ithome.com/0/803/996.htm) | 对 | 2024-10 | 辅助：第三方媒体 |
| REDMI Buds 6 | 2024-09 | [原文](https://www.ithome.com/0/798/668.htm) | 对 | 2024-09 | 辅助：第三方媒体 |
| Xiaomi Buds 5 Pro | 2025-02 | [原文](https://ir.mi.com/system/files-encrypted/nasdaq_kms/assets/2025/03/18/5-39-22/%E4%B8%AD%E6%96%87%E5%85%AC%E5%91%8A.pdf) | 对 | 2025-02 | 辅助：官方财报 |
| REDMI Buds 7S | 2025-04 | [原文](https://www.ithome.com/0/844/491.htm) | 对 | 2025-04 | 辅助：第三方媒体 |
| Xiaomi 开放式耳机 Pro | 2025-06 | [原文](https://www.ithome.com/0/863/953.htm) | 对 | 2025-06 | 辅助：第三方媒体 |
| Xiaomi 骨传导耳机2 | 2025-07 | [原文](https://www.ithome.com/0/869/534.htm) | 对 | 2025-07 | 辅助：第三方媒体 |
| REDMI Buds 8 Pro | 2026-01 | [原文](https://www.ithome.com/0/917/637.htm) | 对 | 2026-01 | 辅助：第三方媒体 |
| Xiaomi Buds 6 | 2025-12 | [原文](https://www.ithome.com/0/908/021.htm) | 对 | 2025-12 | 辅助：第三方媒体 |
| REDMI Buds 8 青春版 | 2026-02 | [原文](https://www.ithome.com/0/923/927.htm) | 对 | 2026-02 | 辅助：第三方媒体 |
| REDMI Buds 8 活力版 | 2026-03 | [原文](https://www.ithome.com/0/926/051.htm) | 对 | 2026-03 | 辅助：第三方媒体 |
| REDMI Buds 8 | 2026-04 | [原文](https://www.anzhuo.cn/review/p_66882) | 对 | 2026-04 | 辅助：第三方媒体 |
| REDMI 头戴降噪耳机 | 2026-06 | [原文](https://www.ithome.com/0/970/430.htm) | 对 | 2026-06 | 辅助：第三方媒体 |
| Xiaomi 耳夹式耳机 | 2026-05 | [原文](https://www.ithome.com/0/953/606.htm) | 对 | 2026-05 | 辅助：第三方媒体 |
| 小米活塞耳机 | 2013-06 | [原文](https://www.ithome.com/0/047/461.htm) | 对 | 2013-06 | 辅助：第三方媒体 |

明细下载：[hidden-review-16.csv](hidden-review-16.csv)、[hidden-review-16.json](hidden-review-16.json)。后者保留第二来源原句、核对时间、隐藏源响应 hash 和门槛状态。

**16 个耳机有独立公开正文明确月份，因此按这些正文分别入库，而不是放行 hidden。** Buds 5 Pro 用公开官方报告，其他 15 个用 third_party；用公告日期的标 announcement，用首销／开售日期的标 availability。仍保留原始 hidden 值在内部核对文件，不写成 official，也不声称通过 30 条抽检。

另外从小米官方公开财报逐字抽取了 15S Pro、Pad 7 Ultra、双区／三区洗衣机 Pro、K90 Pro Max 等明确月份，并从有日期的国内发布会报道逐个型号匹配新增手机、平板、手表等。自动发现队列是**待审队列**，不是发布清单：对比机型（14 Ultra）、海外发布（17 系列巴塞罗那）、冰箱多容量容器、同名 Sound 多 ID、限定色和其他章节中的旧机全部拒收。决策见 [event-review-decisions.json](event-review-decisions.json)，最终仅以 new-candidates.json 为准。没有向其他容量、颜色、配件继承整机时间。

## 3. 大疆：三类来源均实试

| 来源 | 实际范围 / 状态 | 片段或失败证据 | 入库 |
|---|---|---|---:|
| 官方商城商品页 | 3 个配件 + 3 个整机商品直链均 HTTP 200 | 当前可读 HTML 中未取得明确上市／发布日期。含 mavic-2-enterprise-battery、GPS 模块连接线、补光手机夹、Ronin 4D、Transmission、Osmo Mobile 6；不把页面 JSON 创建／更新时间当发售 | 0 |
| 中国官方新闻稿 | Avata 2 新闻 HTTP 200，正文完整；另有多条 newsroom 返回 HTTP 200 但只有短 JS 跳转壳（约 74 字符可见文本），不误称成功拿到新闻正文 | [2024-04-11 原文](https://www.dji.com/cn/newsroom/news/dji-launch-avata-2-cn)的“发售与服务信息”分别列出单电池、三电池畅飞套装、单独销售的飞行眼镜 3、FPV 遥控器 3，并写即日起正式发货 | 4 |
| 大疆社区 / 产品页 | 社区首页和两个具体帖子 HTTP 200，但原始 HTML 未给可核的产品“发布日期”字段；动态内容未作为已验证证据 | bbs.dji.com/pro/detail?tid=300167、tid=365811；固件 PDF“发布日期”不作硬件上市证据 | 0 |
| 补充：公开中文发布稿转载 | 色影无忌 HTTP 200 | [2023-10-25](https://info.xitek.com/allpage/news/202310/25-365451.html)分别点名 Pocket 3 标准版／全能套装，并写中国大陆即日起正式发售；标 third_party | 2 |

Avata 2 单飞行器、智能飞行电池、螺旋桨、后续智选套装／140W 套装均未继承此日期。Pocket 3 后来的 Mic Mini / Mic 3 / 140W 套装也未继承。

## 4. 惠普：商品直链可读，规格接口实测被挡

本轮没有再用“京东搜索被挡”代替调查。读取具体京东移动商品页并从页面真实 JavaScript 找到它调用的 `getSpecification` 接口（`wq.jd.com/commodity/itembranch/getspecification`），逐个 SKU 实际请求。该接口返回 HTTP **403**，正文为 `403 Forbidden nginx`。移动页 HTTP 200 只证明商品身份页可读，**不证明已取到上市时间，更不证明与库内 HP part_number 已精确匹配**。

| 品类 / 来源 | 样本 | 状态及字段命中 | 可导入命中率 |
|---|---|---|---:|
| 笔记本：京东直链 + 参数 | 100402633052、100309924247、100286783609 | 商品页 3/3 HTTP 200；参数 3/3 HTTP 403；未取得可映射到库内精确产品编号的日期 | 0/3 |
| 台式机：京东直链 + 参数 | 100034859643、100094287790、100085956771 | 商品页 3/3 HTTP 200；参数 3/3 HTTP 403；未取得可映射到库内精确产品编号的日期 | 0/3 |
| 笔记本：惠普商城精确编号 | 7Y0Y4PC、BL9C1PC、CF7V8PC | 3/3 HTTP 200，可读规格没有明确上市时间节点 | 0/3 |
| 台式机：惠普商城精确编号 | 7Z5S1PC、9X2Y9PC、915D1PC | 3/3 HTTP 200，可读规格没有明确上市时间节点 | 0/3 |
| 惠普新闻入口 | hp.com/cn-zh/newsroom.html | HTTP 404；未取得精确产品编号同时给上市月的公告。其他系列新闻／报道未匹配到唯一编号，不扩散给同代配置 | 0 |

这些是有界来源试采命中率，不是断言全部 218 行都没有公开日期。仍缺 218。

## 5. 富士：国行来源单独处理

- 中国站产品目录 HTTP 200；其产品规格链接指向 fujifilm-x.com。实际试了 XC13-33、XC15-45、XC35 规格链接，本轮直接访问超时（状态 0），不再把上轮全球站 403 当本轮新结果。
- 中国站新闻目录按 2023—2026 年及分页实采；多条机型公告 HTTP 200。但 X-T50、GFX100S II、X100VI 等正文只有新品发布，缺明确国行开售月份；不拿新闻日期代替开售。X-E5 中国站正文写“全球范围内”预计 2025 年 8 月推出，不据此确认国行。
- [X-S20 中国新闻稿](https://www.fujifilm.com.cn/cn/zh-hans/news/detail/3786)直接 HTTP 403，正文为站内找不到页面；搜索索引虽残留“将于2023年6月上市”，本轮不把索引残留当成功抓到正文。
- 京东自营 X-S20 套机直链 `100053477906`、富士影像旗舰店 `10170879177338`：移动商品页 HTTP 200；前者规格接口 HTTP 403。后者页面当前选择项为 **X-E5 单机身**，不能把 URL 的旧套机归属当当前商品；未从该链接给套机填日期。
- 实际入库 3 个单机身，均为 **third_party / CN / availability**：[X-H2](https://www.ithome.com/0/640/150.htm)原句点名“国行价格…9月29日上市”（2022-09）；[X100VI](https://www.ithome.com/0/751/018.htm)原句“国行定价…3月1日上市”（2024-03）；[X-T5](https://www.ea360.com/contents/150/13460.html)原句“国行售价…11月11日上市销售”（2022-11）。没有向套机或镜头扩散。
- 其他 X-E5、X-S20、X-T50 套机等公开媒体月份缺少足够明确的国行指向，保留为内部 third_party 参考（[internal-references.json](internal-references.json)），不发布 release，也不展示。日本 6 月 29 日、美国等日期完全没有入库。

## 6. 比亚迪 / 小米汽车

17 行各自公开 source_url 均试读；首页、产品／参数页均保留 HTTP 状态及可见正文。比亚迪参数接口此前 401 的原因仍是验签失败；本轮没有生成验签或将车型年份改为月份。对本次访问的公开页面和新闻检索，**未获得这 14 个具体版本可直接入库的月份，记“本次公开源不可得”**，不把这个结论外推为互联网上绝无相关资料。

小米汽车找到公开官方财报：SU7 Ultra 句中明确“於2025年2月上市”（availability）；YU7 官方报告明确“自2025年6月…正式發佈”（announcement）；新一代 SU7 官方报告明确“2026年3月…正式發佈新一代”（announcement）。三条分别精确匹配版本，未将老 SU7 的 2024 年日期传给新一代，未将 YU7 的 5 月亮相当 6 月正式发布。

## 7. 成本与门禁

[usage.json](usage.json)：先确定外部 LLM 调用预算为 0，实际 0 次、0 input / output tokens、0 API 花费；全程没有调用网关补日期。规则提候选，当前交互会话阅读原文并审核，没有用模型记忆填日期；交互会话本身由宿主计费，本进程没有其 usage，**不把交互总成本说成 0**。上一轮 40 个 LLM 候选及其抽样全集哈希保持原样。

`official_hidden` 新增独立验证契约：全集哈希绑定、至少 30 个独立产品、每条第二来源及正确值、按品类分别计算准确率。≥97% 的品类仅能按 reference 和“推出月份（参考）”发布；90—97% 仅内部，<90% 禁用。未取样品类不能随其他品类解锁。测试覆盖门槛不足、全集修改、同源自证、跨品类错误率和参考标签；证据一旦有 isPageShow=false，即使改 method 也不能标 official 或 llm 绕过审核。实际 hidden 候选为 0，不存在绕过本次门槛的数据。

## 8. 界面展示口径（本轮之后）

- 可展示：有明确 CN 证据的 official / third_party，严格使用 `release.label` + `release.display`。announcement 显示“发布时间”，availability 显示“发售时间”，二者不能混称。
- LLM：保留既有“推断”标签，不改成官方。Apple 未来计划仍显示“预计／官方计划”，不当已发售事实。
- official_hidden：本次没有公开日期。原始隐藏值与不合格门槛样本只在内部核对文件；未来通过门槛也只显示“参考”，不能写“官方发售时间”。
- 富士地域未确认、惠普未精确匹配、比亚迪缺来源、K90 多 gid 版本：不展示任何新增日期。未知保持缺省。
- 此仓库负责数据/API，不含另一工作区的换新页。本轮没有声称修改了不存在于此仓库的 UI；发布数据的 label / display / source / usage 是消费端展示依据。

## 9. 测试、发布与验收状态

全量（含 live）**365 passed**，上一轮 361 passed，新增 4 项、无新增失败。只有既有 pytest 插件弃用 warning。最新 data 分支回放前后 3968 行、3963 个唯一 ID，所有非 release 字段逐值相同：[tests-full.log](tests-full.log)、[identity-invariants.json](identity-invariants.json)、[finalize.log](finalize.log)。

发布沿用 `refresh-release-dates.yml` → 共享 publication lock → merge/门禁/finalize/分片 → data → OSS。首轮发布成功并完成线上检查：[online-verification.json](online-verification.json)，3968 行全量相等，63 个详情逐字段相等（包含全部 53 个新增 ID）。发布记录见 [publication.json](publication.json)。重复发布曾因汽车结构校验把顶层 release 当作原始配置证据而失败，已补回归测试：仅排除顶层 release，继续严格校验其余字段及嵌套 source_record；原始证据不改动。[失败片段](republish-failure-excerpt.log)、[修复后重复 finalize 回放](finalize-replay.log)。最终修复版本 `9d4ac1875f8835d5f11863646b1a8fedf7fee77b` 的[正式发布](https://github.com/null-object-0000/goodsdex/actions/runs/41584990471)已成功，data 提交 `e4f2076a8f12855827335b8c4217b0dd8310bae5`；对应 goods.json 与线上验证的 SHA-256 完全相同。

离线重放已审输入（不重新调用模型或来源）：

```sh
PYTHONPATH=src:scripts python3 -m pytest -q
python3 scripts/finalize_public.py --public <最新data工作树>/public --previous <发布前goods.json>
```

来源全清单的状态、hash、错误和片段：[source-inventory.json](source-inventory.json)（2496 个采集记录，包含重试与失败，不当成独立成功源数量）。使用过的公开正文 / PDF、16 个隐藏节点保留在 evidence/；其余完整 HTTP 字节归档于本地忽略目录 `data/release-dates/round2/raw/`，inventory 同时保留审阅所需失败片段与状态。候选发现队列不是自动导入结果。

**验收结论：覆盖表、真实源证据、全量测试、发布、63 个线上详情及代码提交均可核对；“30 条指定来源 hidden 核验”仍不满足，不能声称六项全部完成。**
