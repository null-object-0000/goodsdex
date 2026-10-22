# 小米官方旧款资料

`python scripts/crawl_mi_legacy.py` 从 `data/official/mi_legacy_seeds.json` 中经过核验的官方旧产品页开始，读取实际 `$GLOBAL_PAGE_INFO.product_info` 身份及其产品脚本的 `specsArray`，再复用现有详情采集。脚本只解析静态数据，不执行远程 JS。

首条为用户实物 Redmi 显示器 G27Q 2025款：`P27QCA-RG`、`productId=19963`。型号由官方产品脚本确认，不把铭牌 ELA/BHR 编码猜作商城数字 SKU。此入口不是全部历史商品索引；新增种子必须先核实官方页面。

- 独立分类快照 `Mi_legacy.json`；字段 `record_level=model_reference`、`catalog_scope=legacy_seed`、`model`、`lookup_keys`、`source_url`。
- 保留既有产品身份，不虚构 SKU。官方脚本字段带断言、原始响应引用、哈希、观察时间和定位；完整页面/脚本/详情响应存入 `data/mi-legacy/raw`。
- 不从无货推出停售，`sale_status=unverified`。公开价格为空，接口报价仍留在原始证据，不代表可成交价格。
- 小时刷价明确排除 `model_reference`，防止旧款接口报价重新进入公开现价。
- 失败保留旧记录；报告 `data/mi-legacy/report.json`。每日 crawl-all 已接入。
- `refresh-legacy` 是共享发布锁下的定向补采工作流，只更新这组资料、meta 和对应内部分类快照，不重采其他品牌。
- 本地实测成功取得 27 英寸、2560×1440、180Hz、型号 P27QCA-RG；当前仅承诺核验过的种子，不承诺所有小米旧款或所有家中物品均可查到。
