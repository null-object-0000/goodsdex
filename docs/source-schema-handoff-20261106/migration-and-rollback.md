# 商品来源集合与外显派生

完整五条真实样本见 [samples.json](samples.json)，每条包含完整 `sources[]`、`display`、主源和历史；首条 `mihome:23498` 是米家发现、没有商城匹配和价格的真实商品。未经重新抓取，旧证据时间缺失保留 null 和 `capture_time_missing`，不使用迁移执行时间补造采集时间。

全量预演输入：data 分支 4,468 行、4,463 个不同 ID。既有重复配置行原样保留。`statistics.json` 有输入 SHA256、主源分布、源数量分布和逐条外显值差异。未删除任何旧字段，1,971 条缺价记录均保留。名称、主图、价格没有变更；294 条类目按明确策略采用目录细分类，原商城类目仍保留在商城源字段中。

## 代码规则

`src/goodsdex/product_sources.py` 是唯一来源策略入口：

- `SOURCE_TIERS`：商城 1、官方支持/规格 2、自有目录和有品 3、结构化第三方 4。未登记媒体/LLM 为 5，只保留其证据，不参与商品身份或价格采纳。
- `materialize` 只从有名称、登记 publisher、证据 URL、证据 method 的来源选择一个主源；URL 域名须匹配 publisher。日期观察不能充当商品身份。没有商城证据时，米家目录能合法成为主源，`discovered_by` 留下发现来源。
- `upsert_source` 是采集接入接口；给出真实来源对象，不添加新商品顶层字段。商城补入后按优先级升级，`source_history` 追加 at/from/to/reason；同源不同捕获时间和冲突字段保留在 observations。每个 publisher 只有一个 envelope 和一个顶层 role。
- `derive` 独立于 primary，默认名称/图片/价格按来源层级，类目优先目录。可通过 rules 参数按字段配置，输出 source/field/source_url/captured_at/policy/reason。设备图标保留 icon，缺少商品图则 display.image 为 null。没有合格价格则 price=null、price_missing 保留。
- 现有顶层 name/image/category/price 是 display 镜像。旧 `*_mihome` 等来源列继续保留。后续采集旧字段刷新在边界转换成该来源的新观察；显式 null 会清除该来源旧外显值。

规则回归：`tests/test_product_sources.py`，覆盖默认优先级、独立类目、米家发现、缺价、商城升级与历史、同源冲突、未知证据拒绝、后续价格刷新、迁移幂等、字节级回滚。

## API 与后台

详情保留完整来源及历史；列表新增 sources/display/primary_source/discovered_by/source_history/source_policy。列表来源省略 observations、params 和 parameters，详情保留全部。旧字段不删，旧 API 的缩略图 URL 和商品族展示逻辑保留。API 回归和实际字段清单见配套 spend-good 提交的 `services/api/test/product-sources.test.js`。

后台商品详情按 display 显示名称/图片/类目和每个字段证据链接；总览展示主源分布、1/2/3+ 来源分布、只有主源没有第二源的行数。统计口径为发布商品行，与 meta.product_sources 一致。

## 迁移、发布、回滚

只读预演：

```bash
python3 scripts/migrate_product_sources.py audit --input public/goods.json --output audit/product-sources
```

本地完整发布集迁移（先保存可恢复快照）：

```bash
python3 scripts/migrate_product_sources.py snapshot --public public --backup before-sources.tar.gz
cp public/goods.json before-goods.json
python3 scripts/finalize_public.py --public public --previous before-goods.json --product-sources-only
```

线上运行 `migrate-product-sources.yml`。共享发布锁内读取最新 data，不采用过时本地快照。迁移专用 scope 从 previous 构建，仅改来源结构及 display 镜像；保留 ID、商品行和日期。沿用既有丢 ID 门禁、排除清单门禁、分片 SHA256 校验、OSS 不可变对象及最后提交 manifest 的发布顺序。迁移前完整 public 备份保存在 run 的 `product-sources-rollback-<run_id>` artifact，保留 30 天。

完整回滚（会恢复迁移前快照，包含它之后的价格变化，请以备份 revision 为准）：

```bash
python3 scripts/migrate_product_sources.py restore --public public --backup before-sources.tar.gz
```

恢复的是 goods/meta/detail/index/价格历史和其他 public 文件的原始字节，并清除迁移后新增文件。线上将恢复后的完整 public 提交到 data，然后运行 `mirror-sharded-release.yml` 同步旧 manifest；不要只删 sources/display，因为旧的类目镜像和 SHA256 也必须一起恢复。另将本次代码提交 revert 后发布，可停止后续自动双写。API 新字段均为可选，旧数据快照仍可读取。
