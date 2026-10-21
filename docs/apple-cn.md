# Apple 中国大陆官方采集

`src/goodsdex/sources/apple_cn.py` 为独立官方源，入口为 `scripts/crawl_apple.py`。
不需要登录、cookie、第三方商品 API 或付费模型。运行时仍只用 Python 标准库。

## 范围

从中国大陆官方商店和产品系列导航的**实际链接**发现购买页：iPhone、iPad、Mac（含显示器）、Watch、AirPods、HomePod、AirTag、Vision。
不硬编码在售产品名称或价格；商品上新随导航链接发现。

本轮是当前官方页面列出的**中国大陆预配置购买料号**，不是 Apple 历代全产品库。
未穷举全部 Mac CTO 内存/存储组合、Watch 表带组合、所有配件。历史机型通过下述官方文稿源独立补采。
没有官方购买料号的可配置入口不会被伪造成一个独立 SKU。
`discovery.completeness` 因范围限制始终为 partial，缺席不能自动推定下架。

## 三路检查与取值依据

实测同时检查了 raw HTML、渲染后的 DOM、XHR/fetch 请求。
购买页原 HTML 已包含 `window.PRODUCT_SELECTION_BOOTSTRAP.productSelectionData`；
渲染 DOM 的容量/颜色选择器与其一致。网络请求中没有必要再调用用户的购物袋或个人信息接口。
采集端用 JSONDecoder 读取这一 JSON 值，不执行远程 JS。

- 产品：`familyType`、官方配置容器编号或带代际的官方页面名（最后才回退购买页 slug），主键带 `CN:apple_cn:product:`。
- 规格：`partNumber` / `btrOrFdPartNumber` / Watch 的 `part`，
  主键带 `CN:apple_cn:commodity:`，**容量/颜色料号不合并**。
- 价格：规格显式关联的 `displayValues.prices` / `mainDisplayValues.prices` 中
  `currentPrice.raw_amount`；不取分期月付、Trade In 抵扣后金额或首页起售价。
- Mac 预配置入口、Watch 表壳价格标为 `price_kind=starting`，不当作全部定制项/表带最终价格。
- 技术规格：沿已发现的官方产品介绍页链接访问技术规格页，保留 `specs_table.columns/rows`。
  同页多个型号的列保持独立，标为 `family_table`，不能直接当作每个料号均有同样参数。
  未识别到表结构或无可靠关联时明确 not_collected/parse_error，不拼出假参数。
- 图片：有明确 imageKey 时保留对应官方图片 URL。

每条事实带 capture_id、定位、原始值和解析器版本；完整 HTML 内容寻址保存在 `data/apple/raw/`。
记录中保留原始响应 SHA256 摘要和 raw_ref。raw_ref 指向完整文件，不能把截断的预览视为证据。
本地采集会保留原始文件；Actions 通过 apple-evidence artifact 保存每次原始页面与报告 **7 天**。
长期证据归档需要额外持久化存储，当前不承诺 artifact 永久保存。

## 运行

```bash
PYTHONPATH=src python3 scripts/crawl_apple.py --public public
# 仅一个系列 / 小规模连通性验证（报告明确 limited）
PYTHONPATH=src python3 scripts/crawl_apple.py --family iphone --limit 1
# 离线回归，pytest 仅为测试依赖
PYTHONPATH=src python3 -m pytest -q
```

产物：

- `data/categories/Apple_<family>.json`：本次可观测记录，与小米分类独立。
- `data/archive/Apple_<family>.json`：按料号累积的档案。
- `data/apple/report.json`：种子/购买页/规格页状态和覆盖范围。
- `public/goods.json`：与已有品牌增量合并，保留 `source/brand/market/variant_id/part_number`。
- `public/prices/apple/latest.json`、`<月>.jsonl`：独立 Apple 价格命名空间，按料号及真实观察时间去重。

整页请求失败、页面结构变化、没有解析出料号时，保留上次页面的商品、价格和观察时间。
仅价格解析失败时保留上次价格及其原始证据，标 `price_status=stale`；
`price_fetched_at` 保持旧观察时间，不因其他资料刷新而伪装成新报价。
首次没有价格则为 null / not_collected，绝不补 0。

## 自动刷新与兼容性

现有 `crawl-all`（每日）与 `refresh-prices`（小时级）工作流都增加 Apple 采集步骤。
每日发现新品并采集规格；小时任务用 `--prices-only` 复用购买页刷新价格，保留旧规格表及其证据，
已有目录时不重复抓系列导航和规格页。首次没有目录时仍会发现购买页。
合并代码后才会在默认分支的定时工作流中生效；当前分支的本地验证不等于已上线。
小米批量取价明确排除 Apple，Apple 料号不会送入小米 gid 接口。
两个产物写入工作流共用 concurrency group，防止同时写 data 分支互相覆盖。
Apple 部分失败输出 workflow warning 与报告，成功页面可更新，失败页保留旧值。
新加入 `tests` 工作流用于 PR 回归。

原小米公开字段与价格目录保持兼容。`publish.to_public` 仅对 Apple 增加来源、规格、价格范围与观察时间字段。
通用档案在存在 variant_id 时按变体建键，其他源继续按 product_id 建键。

## 2026-10-21 本地实测

- 30 个购买页、343 个不同中国大陆购买料号，全部取得价格。
- iPhone 73、iPad 160、Mac/显示器 51、Watch 39、AirPods 8、HomePod 7、AirTag 2、Vision 3。
- 253 条为规格价格，90 条明确标为 Mac/Watch 基准起价。
- 21 张官方规格表；另有 2 个已访问规格页的布局尚未解析，其余无可靠关联的规格页留缺口。
- 单独完成一次 prices-only 实采；旧规格表及证据保留。按原始响应哈希验证 51 份购买/规格页面证据。
- 对当前公开集做本地合并验证，原 3,888 条记录逐条保持不变，合并后 4,231 条。
- 193 项测试、lint、工作流 YAML 与 shell 语法检查通过。

上述是本地实测结果，未直接改写线上 data 分支。完整响应、公开集预览及验证日志在本地 `data/apple/validation/`、`data/apple/raw/` 和 `public/`，不混入代码分支。

PR 回归默认运行 `pytest -q -m "not live"`（185 条离线测试）；原有 8 条小米联网集成测试仅增加 live 标记，没有删除或改写判据。完整 `pytest -q` 仍运行全部 193 条，本地均已通过。


## 历史机型补采（Apple Support）

```bash
PYTHONPATH=src python3 scripts/crawl_apple_history.py --public public
# 只补一个系列；强制重取已有规格
PYTHONPATH=src python3 scripts/crawl_apple_history.py --family iphone --max-age-days 0
```

从 Apple Support 的 zh-cn 文稿目录发现真实机型卡片及技术规格链接；Watch 分组目录继续展开。
iPhone、iPad 同时核对官方“识别机型”页中的技术规格链接，兼容旧 `/kb/SP…?locale=zh_CN` 跳转。
支持 iPhone、iPad、Mac、Watch、AirPods、HomePod、Vision、显示器，以及配件目录中的 AirTag；不宣称所有历史 Apple 产品已穷举。
其他历史配件目录本轮不扩展。

- `Apple_history_<family>.json` 独立存放文档级机型参考，主键为 `GLOBAL:apple_support:model:<官方规格文稿编号>`。
  同一文稿的不同发现链接、不同语言入口不生成多份商品。
- 公开集带 `record_level=model_reference`、`catalog_scope=historical_and_current`、`sale_status=unverified`。
  文稿目录同时包含旧款和当前机型，缺席商店不能证明停售；不自动给全部参考记录贴“已停售”。
- 中文资料也可能包含多个地区型号；`market=GLOBAL`，实际语言路径保留为 `document_locale`。
  正文中的地区、型号及功能条件原样保留在相应规格段落，不能把所有 A 型号当成国行。
- `specs_sections` 保留官方正文标题层级、段落/列表行及脚注，不压成每个容量/颜色共用的平面参数表。
  容量和颜色是文档中列出的选项，不做笛卡尔积，不虚构购买料号；与当前在售 SKU 也不靠模糊名称合并。
- 只在官方明确写推出年份或机型标题包含年份时输出 `model_year`，不拿网页更新日期当发布日期。
- 历史记录 `price=null`，不补 0，不把发布价当现价，不写入 Apple 报价时间序列。
- `captures/assertions` 保留规格正文及发现页的完整响应引用、哈希、时间、定位与版本。
  原始 HTML 位于 `data/apple/history/raw/`，报告位于 `data/apple/history/report.json`。
  公开派生视图保留官方来源链接，内部证据与现有 Apple artifact 一起保存 7 天。

每日全量工作流已接入；成功历史记录默认 7 天内复用，目录继续查新。小时价格刷新只访问当前商店购买页。
网络/解析失败保留原记录及观察时间，错误进入 `errors`；文稿页无规格入口单列 `coverage_gaps`，不声称补齐。
`--limit` 会在报告标为 limited，限定机型目录页数量；识别页的规格补查仍会执行。


### 2026-10-21 历史补采实测

新增 **294 份官方机型规格参考**（包含历史及当前型号，不等同于 294 个已停售国行 SKU）：
iPhone 54、iPad 35、Mac 153、Watch 22、AirPods 14、HomePod 3、Vision 2、显示器 9、AirTag 2。
最早有明确年份的资料为 2007 年；217 份有可直接取证的机型年份，242 份有官方产品图。
292 份资料实际返回 zh-cn，2 份返回 en-us，均保留实际语言路径及 GLOBAL 范围。

完整规格及发现页共 512 个关联原始文件通过 SHA256 核对；历史价格全部为空。
真实目录仍有 70 个机型/分组文稿入口没有直接规格链接，报告逐个保留；
其中部分已由“识别机型”页补到同款规格，不能把这个入口数量当作缺少机型数量。
最后一次采集没有未恢复的网络/规格解析错误；这仍不是 Apple 全部历史产品的完整覆盖声明。

在已有小米数据与当前 Apple 配置上做本地合并，保留原 3,888 条小米记录（含既有重复 ID 的条目）
和 343 个 Apple 购买配置，合并后 4,525 条。用记录多重集逐条核对，避免以 ID 字典掩盖既有重复数据；
重复发布结果一致，Apple 报价集仍只有 343 个当前购买料号，没有历史参考混入。

全套 205 项测试通过（197 项离线、8 项已有小米联网测试）。
本地完整采集报告及验收在 `data/apple/history/report.json`、
`data/apple/history/validation/acceptance.json`；合并预览在该验证目录的 `merged-public/goods.json`。
代码合并到默认分支后才会进入定时发布流程，本次未直接改写生产 data 分支。
