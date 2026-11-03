# 发售月份覆盖与发布验收（2026-11-03）

基线：`origin/data@7d7099ca`，3968 行，3963 个唯一 ID。使用最新发布产物，未重新调查用户提供的旧线上 5448 条现状；旧的 5448 与本次分母不可直接相除。既有去重/冲突保留口径未改变。HP 218 包括 209 条存续和 9 条已留档下架记录。

## 结果

`release.date` 非空 **401/3968 = 10.11%**。其中 official **359（89.53%）**、third_party **2（0.50%）**、llm **40（9.98%）**，括号为占有日期记录的比例。

有 31 条是官网明确公布的未来开售计划（2026-11-06），标 `event=planned_availability`、`usage=reference`、`预计…（官方计划）`；不是已发售。排除这 31 条，非计划日期为 **370/3968 = 9.32%**。另区分 66 条明确“发布时间”（announcement）与 304 条 availability，不把公告时间静默叫作开售日。

| 品牌 | 总行数 | 真源覆盖（官方/第三方） | LLM 补齐 | 仍缺 |
|---|---:|---:|---:|---:|
| Apple | 640 | 294 | 40 | 306 |
| 比亚迪 | 14 | 0 | 0 | 14 |
| 大疆 | 783 | 0 | 0 | 783 |
| 富士 | 63 | 0 | 0 | 63 |
| 惠普 | 218 | 0 | 0 | 218 |
| 小米 | 2247 | 67 | 0 | 2180 |
| 小米汽车 | 3 | 0 | 0 | 3 |
| 合计 | 3968 | 361 | 40 | 3567 |

“真源”表示页面/接口明确声明日期，包含已标明 third_party 的第三方；不把模型映射提升为 official。每品牌三列相加等于该品牌行数。LLM 一栏按来源划分，即使引的是官网也仍标 llm。

## 第一步：来源试采与实际落库

试采范围与实际覆盖分开；非随机的源验证样本不外推到整品牌。完整请求 URL、状态、原文片段/JSON locator 与响应哈希在 [evidence/](evidence/)。只接受成功来源的明确月份；HTTP 403、验签失败和登录/浏览器提示页不记作“官网没有”。

| 品类/来源 | 验证范围与观察 | 本轮覆盖行数 | 证据形态 |
|---|---|---:|---|
| 小米电视：商城移动接口 | 70 个电视族请求；66 个日期可展示且能唯一归一；4 个多值/格式无法唯一确定，留空 | 66 | `isPageShow=true`、`name=发布时间`、`value=2024年 10月`；保留 JSON path、POST productId、商品链接 |
| 小米手机：商城移动接口 | 1 个型号请求成功，未得到明确月份节点 | 0 | 保留商品身份和参数摘要，不从型号代数推月份 |
| 小米生态链耳机：商城移动接口 | 16 个型号均只有 `isPageShow=false` 的日期节点；不满足“页面明确写出”的标准 | 0 | 显示标记与原文值均保留；不把既有 params 别名直接搬成 release |
| 小米手机：mi.com 规格页 | Xiaomi 14 页面取到规格，无明确发售日期命中 | 0（该源） | `Xiaomi 14` 页面文本，非页面更新时间/测试时间 |
| 小米家电：H501 官方接口 | `productId=18520` 成功，未取得结构化日期；不对图文内容宣称无日期 | 0（官网） | 商品身份与参数节点摘要；[mi-18520.json](evidence/mi-18520.json) |
| 小米家电：IT之家 H501 | 原文“2023/5/27 … H501 今年 5 月上市” | 1（third_party） | [文章](https://www.ithome.com/0/695/691.htm)；用文章年份解释“今年”，未用促销/礼盒时间代替原机上市 |
| Apple 支持技术规格 | iPhone 14 只给“推出年份：2022 年”，不能补月份 | 0（该源） | [支持页](https://support.apple.com/zh-cn/111850) |
| Apple 中国官网 Newsroom | 先测正文开售语句，再抓官网 sitemap 中产品公告；用审核过的精确 product_id 共享颜色/容量证据 | 293（含 31 条计划） | “3 月 4 日起接受订购，3 月 11 日起正式发售”；发布年份与开售月份分别定位 |
| Apple：GSMarena | 验证 iPhone 14 Released 行 | 1（third_party） | [原文](https://www.gsmarena.com/apple_iphone_14-11861.php) `Released 2022, September 16`，仅输出 2022-09 |
| HP：hpstore | 7Y0Y4PC 商品页成功；未取到明确上市时间 | 0 | 保留正文与参数，不能把 Magento 创建时间、CPU 代际当上市日期 |
| HP：京东 | SKU 搜索返回提示页；未找到可核对的精确 SKU 商品日期 | 0 | [实际搜索 URL](https://search.jd.com/Search?keyword=7Y0Y4PC)；不能套战66同代其他配置日期 |
| 富士：fujifilm-x.com 规格与官方新闻 | 中国/全球规格页和官方中/日/英文新闻请求均遇 403；搜索索引能找到 X-S20 日本 2023-06-29 发售，不能据此冒充国行发售 | 0 | 403 失败证据保留；套机/机身/镜头也不互借日期 |
| 汽车：比亚迪官网参数页/API | 两个参数页 HTML 未取得明确上市月份；真实 goodsParams 接口返回 401“验签失败” | 0 | 完整实际 URL、响应状态与原文；不把车型年份、图片路径时间当上市时间 |
| 大疆、小米汽车 | 本轮未扩大专门日期采集；既有商城记录不能证明型号/配件各自开售 | 0 | 保持缺失，不把整机日期传给兼容配件 |

66 条小米 + 293 条 Apple 官方 + 2 条第三方 = 361 条真源；LLM 输出另计。

## 第二步：LLM、成本与启用范围

先执行零成本型号族计划，再尝试网关 `flowlet-flash`。初始剩余 Apple SKU 归并成 338 族，原计划最多 6 次请求、总输入约 682 KB、每次最多 7000 output tokens（总上限 42000），单请求 UTF-8 输入硬限 400000 bytes。没有公开单价，未虚报人民币费用。

**实际最多 6 次网关请求**：5 次完成并保存原响应，第 4 次中断、仍按一次及 7000 output tokens 预算计入；无无限重试。已完成的 usage 合计 input **101615 tokens**、output **27591 tokens**，中断请求的真实用量未返回，不能称为零成本。3 批仅有推理、没有完整 JSON，被拒收。`reasoning_effort=low` 在本次网关上未可靠避免耗尽推理预算，因此不适合直接铺开此批次配置。

网关最终留下 3 个有完整 JSON、逐字可回指的型号族候选；其余候选由**本次 Codex 交互会话 LLM**在阅读原文后整理，未新增网关 API 调用。去重后共 **40 族/40 行**（3 个 flowlet-flash、37 个 codex-interactive-session），均保留真正的模型来源、原文、链接、理由。不是声称外部 API 成功补出了 40 条。

现有源不能给出可核依据的 HP、富士、其他小米型号不让模型凭印象猜；未知保持空。型号年份、CPU 代际、配件兼容列表只能帮助分组，不能变成月份。

候选导入先拒绝不完整 JSON、未知型号、伪造链接/原文和覆盖真源的候选。随后固定 seed `20261103`，对 40 个 LLM 型号族做无放回随机抽样 30 个；不会抽 30 个颜色/容量来凑样本。候选全集 SHA-256 与每个样本候选哈希绑定，任何扩大/修改都必须重新复核。

本轮由 agent 逐条阅读对照官网，重新抓取抽中来源验证原句仍在，**30/30 相符 = 100% 样本准确率**。这是可供人工复查的 agent 核验记录，不冒充独立人工签字，也不表示未知品牌或未来候选准确率为 100%。按用户阈值，当前这 40 族可用作事实依据；来源仍是 llm，展示仍必须带“推断”。

| 样本正确数 | 经验准确率 | 发布策略 |
|---|---:|---|
| ≤26/30 | <90% | 禁用 LLM 日期 |
| 27–29/30 | 90–96.67% | 仅参考 |
| 30/30 | 100%（≥97%） | 当前受检全集可作事实依据，仍显示推断 |

## 30 条逐条核验

可下载 [sample-30.csv](sample-30.csv)；含每行核验原文，另有 [sample-review.json](sample-review.json) 与重抓哈希。

| 型号 | 给的日期 | 依据链接 | 对/错 | 正确值 |
|---|---|---|---|---|
| HomePod (第二代) | 2023-02 | [官网](https://www.apple.com.cn/newsroom/2023/01/apple-introduces-the-new-homepod-with-breakthrough-sound-and-intelligence/) | 对 | 2023-02 |
| AirPods Max 1 | 2020-12 | [官网](https://www.apple.com.cn/newsroom/2020/12/apple-introduces-airpods-max-the-magic-of-airpods-in-a-stunning-over-ear-design/) | 对 | 2020-12 |
| AirPods 3 | 2021-10 | [官网](https://www.apple.com.cn/newsroom/2021/10/introducing-the-next-generation-of-airpods/) | 对 | 2021-10 |
| iPad（第 8 代） | 2020-09 | [官网](https://www.apple.com.cn/newsroom/2020/09/apple-introduces-eighth-generation-ipad-with-a-huge-jump-in-performance/) | 对 | 2020-09 |
| iPhone 13 Pro Max | 2021-09 | [官网](https://www.apple.com.cn/newsroom/2021/09/iphone-13-lineup-new-ipad-mini-and-ninth-generation-ipad-arrive-worldwide/) | 对 | 2021-09 |
| iPhone 14 Plus | 2022-10 | [官网](https://www.apple.com.cn/newsroom/2022/09/apple-introduces-iphone-14-and-iphone-14-plus/) | 对 | 2022-10 |
| 12.9 英寸 iPad Pro（第 6 代） | 2022-10 | [官网](https://www.apple.com.cn/newsroom/2022/10/apple-introduces-next-generation-ipad-pro-supercharged-by-the-m2-chip/) | 对 | 2022-10 |
| iPhone 12 Pro Max | 2020-11 | [官网](https://www.apple.com.cn/newsroom/2020/10/apple-introduces-iphone-12-pro-and-iphone-12-pro-max-with-5g/) | 对 | 2020-11 |
| Apple Watch Ultra | 2022-09 | [官网](https://www.apple.com.cn/newsroom/2022/09/introducing-apple-watch-ultra/) | 对 | 2022-09 |
| Mac Pro (2019) | 2019-12 | [官网](https://www.apple.com.cn/newsroom/2019/11/apple-introduces-16-inch-macbook-pro-the-worlds-best-pro-notebook/) | 对 | 2019-12 |
| iPhone 13 | 2021-09 | [官网](https://www.apple.com.cn/newsroom/2021/09/apple-introduces-iphone-13-and-iphone-13-mini/) | 对 | 2021-09 |
| 12.9 英寸 iPad Pro（第 5 代） | 2021-05 | [官网](https://www.apple.com.cn/newsroom/2021/04/apple-unveils-new-ipad-pro-with-m1-chip-and-stunning-liquid-retina-xdr-display/) | 对 | 2021-05 |
| AirTag | 2021-04 | [官网](https://www.apple.com.cn/newsroom/2021/04/apple-introduces-airtag/) | 对 | 2021-04 |
| MacBook Pro（16 英寸，2023 年 11 月） | 2023-11 | [官网](https://www.apple.com.cn/newsroom/2023/10/apple-unveils-new-macbook-pro-featuring-m3-chips/) | 对 | 2023-11 |
| iPad mini (第 6 代) | 2021-09 | [官网](https://www.apple.com.cn/newsroom/2021/09/apple-unveils-new-ipad-mini-with-breakthrough-performance-in-stunning-new-design/) | 对 | 2021-09 |
| iPad Pro 11 英寸 (第 1 代) | 2018-11 | [官网](https://www.apple.com.cn/newsroom/2018/10/new-ipad-pro-with-all-screen-design-is-most-advanced-powerful-ipad-ever/) | 对 | 2018-11 |
| iPad Air（第 4 代） | 2020-10 | [官网](https://www.apple.com.cn/newsroom/2020/09/apple-unveils-all-new-ipad-air-with-a14-bionic-apples-most-advanced-chip/) | 对 | 2020-10 |
| iPad（第 9 代) | 2021-09 | [官网](https://www.apple.com.cn/newsroom/2021/09/iphone-13-lineup-new-ipad-mini-and-ninth-generation-ipad-arrive-worldwide/) | 对 | 2021-09 |
| Studio Display | 2022-03 | [官网](https://www.apple.com.cn/newsroom/2022/03/apple-unveils-all-new-mac-studio-and-studio-display/) | 对 | 2022-03 |
| MacBook Pro（14 英寸，2021 年机型） | 2021-10 | [官网](https://www.apple.com.cn/newsroom/2021/10/apple-unveils-game-changing-macbook-pro/) | 对 | 2021-10 |
| iPad Air（第 5 代） | 2022-03 | [官网](https://www.apple.com.cn/newsroom/2022/03/apple-introduces-the-most-powerful-and-versatile-ipad-air-ever/) | 对 | 2022-03 |
| 11 英寸 iPad Pro（第 3 代） | 2021-05 | [官网](https://www.apple.com.cn/newsroom/2021/04/apple-unveils-new-ipad-pro-with-m1-chip-and-stunning-liquid-retina-xdr-display/) | 对 | 2021-05 |
| Mac Studio（2022 年机型） | 2022-03 | [官网](https://www.apple.com.cn/newsroom/2022/03/apple-unveils-all-new-mac-studio-and-studio-display/) | 对 | 2022-03 |
| MacBook Air (Retina, 13 英寸, 2018) | 2018-11 | [官网](https://www.apple.com.cn/newsroom/2018/10/all-new-macbook-air-takes-flight/) | 对 | 2018-11 |
| iPad Pro 12.9 英寸 (第 3 代) | 2018-11 | [官网](https://www.apple.com.cn/newsroom/2018/10/new-ipad-pro-with-all-screen-design-is-most-advanced-powerful-ipad-ever/) | 对 | 2018-11 |
| MacBook Pro（14 英寸，2023 年） | 2023-02 | [官网](https://www.apple.com.cn/newsroom/2023/01/apple-unveils-macbook-pro-featuring-m2-pro-and-m2-max/) | 对 | 2023-02 |
| Apple Watch Ultra 2 | 2023-09 | [官网](https://www.apple.com.cn/newsroom/2023/09/apple-unveils-apple-watch-ultra-2/) | 对 | 2023-09 |
| 11 英寸 iPad Pro（第 4 代） | 2022-10 | [官网](https://www.apple.com.cn/newsroom/2022/10/apple-introduces-next-generation-ipad-pro-supercharged-by-the-m2-chip/) | 对 | 2022-10 |
| iPhone 13 mini | 2021-09 | [官网](https://www.apple.com.cn/newsroom/2021/09/apple-introduces-iphone-13-and-iphone-13-mini/) | 对 | 2021-09 |
| MacBook Pro（14 英寸，M3，2023 年 11 月） | 2023-11 | [官网](https://www.apple.com.cn/newsroom/2023/10/apple-unveils-new-macbook-pro-featuring-m3-chips/) | 对 | 2023-11 |

## 数据及使用契约

`release: {date, granularity, source, evidence, confidence, event, market, usage, inferred, display, label}`。date 只到月；confidence 是高/中/低的定性提取置信度，不是假定校准过的概率。evidence 保存 URL、原文、定位、响应 SHA-256、采集时间与底层官方/第三方来源。LLM 还保存模型、prompt_version、reasoning 与受检全集标识。

- 用 `release.label` + `release.display` 展示，LLM 固定为“推出月份（推断） / 约 2023 年 5 月（推断）”，不向 params 写“发售时间”别名。
- `usage=reference`、`event=planned_availability` 不当作已发售事实排序。比较月份时应同时核对 event 与 market，不混用发布/开售和不同地域。
- 本仓库不包含正在另一工作区编辑的换新页。旧客户端不读新字段时不会展示 LLM 日期；接入时必须使用上述口径，不能无条件把 date 显示为“发售时间”。
- 补齐在统一 `finalize_public` 中重放，详情分片和轻索引都保留 release，meta 记录覆盖率；后续任意品牌/价格刷新不会抹掉字段。当前集合外的 LLM 字段不能绕过抽检进入发布。

发布前额外核对 `isPageShow`，16 条仅存在于隐藏节点的小米耳机日期全部排除，`withdrawn_release_ids` 确保旧发布集也会撤销这些 release 字段。前一轮 run 41579536954 已请求取消，不把它当最终发布。

## 测试

全量（包含网络 live 检查）**361 passed**；离线 **353 passed, 8 deselected**。基线离线 332 passed，本轮新增 21 项，无新增失败。只有既有 pytest 插件弃用 warning。发布前后行数与全部非 release 字段逐值相同。

## 复现与发布

离线回放无需再次调用模型：

```sh
PYTHONPATH=src:scripts python3 -m pytest -q -m 'not live'
python3 scripts/finalize_public.py --public <data工作树>/public --previous <发布前goods.json>
```

网关计划与原始输入/输出在 [llm/](llm/)；源试采/会话候选整理脚本在 [pilot/](pilot/)。默认 `collect_release_candidates.py` 只输出计划，显式 `--run` 才调用；不应照搬失败的大批配置全量运行。

线上发布及 API 验证见后续 [publication.json](publication.json) 和 [online-verification.json](online-verification.json)。

最终发布：[success](https://github.com/null-object-0000/goodsdex/actions/runs/41580056352)，代码 `2285ce313a91a7d727086d54711014bddfa25a68`，data `3cfce28f6a4e450fb378e3bacf99871a74337ea3`。

线上整库与此 data 发布集逐值相等；7 个真实详情接口的 release 对象逐值相等，包括 H501、官方、LLM、未来计划、HP 未知和隐藏耳机撤销。16 个隐藏日期全部缺省，其他字段与发布前逐值一致。完整证据见 [online-verification.json](online-verification.json)、[publication.json](publication.json)、[publish-excerpts.log](publish-excerpts.log)。
