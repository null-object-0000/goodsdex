# Apple 中国大陆官方采集

`src/goodsdex/sources/apple_cn.py` 为独立官方源，入口为 `scripts/crawl_apple.py`。
不需要登录、cookie、第三方商品 API 或付费模型。运行时仍只用 Python 标准库。

## 范围

从中国大陆官方商店和产品系列导航的**实际链接**发现购买页：iPhone、iPad、Mac（含显示器）、Watch、AirPods、HomePod、AirTag、Vision。
不硬编码在售产品名称或价格；商品上新随导航链接发现。

本轮是当前官方页面列出的**中国大陆预配置购买料号**，不是 Apple 历代全产品库。
未穷举全部 Mac CTO 内存/存储组合、Watch 表带组合、所有配件及历史停售机型。
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
