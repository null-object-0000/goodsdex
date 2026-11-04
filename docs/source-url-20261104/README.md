# 官方商品 source_url 补齐（2026-11-04）

冻结线上 `/api/goods` 和 `/api/meta`，与发布前 data 分支 `28ea3e34` 商品逐值相等：2856 行，1374 行有 URL；1482 行缺失均属小米。完整冻结数据见 baseline-goods.json.gz / baseline-meta.json.gz。

## 规则与采集源

|品牌|规则 / 来源|缺失时处理|
|---|---|---|
|小米|`CN:mi_cn:product:<数字>` → `https://www.mi.com/shop/buy/detail?product_id=<数字>`；从缺失池随机抽20行实时请求，页面商品标题匹配|20/20通过，达到80%门槛后全量补齐；冻结到本轮1477个唯一ID及名称，不授权未来未抽样批次|
|Apple|购买页使用采集源 `source_url` 中产品族 slug（`www.apple.com.cn/shop/buy-*/<slug>`）；历史型号使用官方支持文稿ID `support.apple.com/zh-cn/<文稿ID>`；不能从购买料号猜文稿ID|本轮639行均已有URL，不改|
|大疆|官方商城目录已有 slug + mall SKU，`https://store.dji.com/cn/product/<slug>?vid=<sku>`，非仅凭数值ID猜slug|本轮281行均已有URL，不改|
|富士|官方目录相机/镜头slug，如 `https://www.fujifilm-x.com/zh-cn/products/cameras/<slug>/`；套机不能凭名称猜网页|本轮63行均已有URL，不改；已有商城第三方链接也保留，未作为官方验证通过|
|惠普|官方源提供完整slug与SKU，`https://www.hpstore.cn/<官方slug>-<sku小写>.html`；仅SKU不足以生成完整slug|本轮218行均已有URL，不改|
|比亚迪|现行车 `CN:byd:car:goods-<goodsId>:…` → `https://www.bydauto.com.cn/cn/parameter-comparison?goodsId=<goodsId>`；历史车不得把第三方spec ID当官方goodsId|本轮14行均已有URL，不改；历史第三方URL保留但不计官方验证通过|
|小米汽车|采集源官方配置页 `https://www.xiaomiev.com/xiaomi/car-config`，共用配置页，不能从车ID拼独立商品页|本轮3行已有URL，不改|

## 验证方法

逐条请求，起始时间间隔至少2.15秒；curl GET、跟随跳转、保留HTTP状态、最终地址、响应SHA256、抓取时间和压缩原文。固定随机种子20261104；小米从缺失1482行抽20行，其它品牌各抽20行；比亚迪仅14行、小米汽车仅3行，均全查，不重复凑20。每条结果及标题片段见 [samples.md](samples.md)，机器记录见 samples.json，原始正文见 responses/。

只匹配商品页title/h1/h2，避免全站导航中的其它商品名制造假阳性。规范化标点、大小写和空格，SequenceMatcher相似度≥0.6，或商品型号/SKU数字关键字命中。HTTP非200、跳转首页、非官方域名和不能对应名称都不计通过。页面200但只有动态配置壳时本次未确认对应，不声称链接已失效；已有字段仍保持。

小米20个样本直接在服务端HTML标题里匹配（19条1.0，1条系列标题0.9412），无需用SPA空壳或存档冒充实时页面匹配。门槛后全量是**规则抽样授权**，并非声称其余1462行也逐页请求过。正式写入前后不变量：只改变1482个source_url，其它商品字段、顺序、行数、原有URL全部逐值不变，见 local-invariants.json。

## 覆盖率（行口径，非唯一ID）

|品牌|修前有URL / 总行数|修后有URL / 总行数|
|---|---:|---:|
|小米|156 / 1638|1638 / 1638|
|Apple|639 / 639|639 / 639|
|大疆|281 / 281|281 / 281|
|富士|63 / 63|63 / 63|
|惠普|218 / 218|218 / 218|
|比亚迪|14 / 14|14 / 14|
|小米汽车|3 / 3|3 / 3|
|合计|1374 / 2856（48.1%）|2856 / 2856（100%）|

meta增加 `source_url_coverage: {total, with_source_url, by_brand: {品牌: {total, with_source_url, missing, ratio}}}`。这是**非空字段覆盖率**，不等于所有原有URL都是官方且实时可访问。既有第三方地址和403没有被重新背书。

`CN:mi_cn:product:10000292` 已不在当前发布集（线上404），官方商品页标题为「新秀无畏」系列笔记本定制贴纸；不为通过验收复活已排除记录。正式验收选当前仍发布的真实商品，见 publication.md。

## 实现与测试

共享finalizer在品牌规范化后重放冻结审核清单 `data/official/source-url-backfill.json`。仅补空值，保留原有URL；商品ID或名称变化不继承旧授权。门槛由代码重新计算；低于80%只允许实际验证通过的样本，明确失败的样本即使整体达标仍禁止写入。覆盖率在共享metadata生成，索引及详情仍使用原有source_url字段。

新增7项回归覆盖门槛边界、403/低分/首页跳转/第三方假成功、失败样本排除、已有值和其它字段保护、范围冻结及品牌统计。既有日期finalizer测试预期增加同一正式URL重放步骤，保留其逐字段全等断言和重复finalize幂等断言，没有删断言或降低日期门禁。修前759 passed / 8 deselected；修后结果见 tests-final.log。首次发现的旧finalizer预期差异保留于 tests-first-attempt.log。

复现：

```sh
python3 scripts/verify_source_urls.py
python3 docs/source-url-20261104/build.py
PYTHONPATH=src:scripts ~/.cache/goodsdex-testenv/bin/python -m pytest -q -m 'not live'
```

发布与线上验收、全品牌命中率与反例统计见 publication.md / sample-summary.json。
