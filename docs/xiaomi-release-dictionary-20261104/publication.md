# 提交、正常发布与线上验收

- 实现提交：`eacb5b5c3da60a7c18c1122ff8aeb8c93e2a0ffc`，main，已推送；字典、匹配、报告、测试日志均在该提交。
- 正常发布 [refresh-release-dates run 41755191377](https://github.com/null-object-0000/goodsdex/actions/runs/41755191377)：**success**。collect → 持锁 merge → 门禁 → finalize → data → OSS镜像读回完成，未手动改线上商品。
- data 提交：`ee076d95a1ab3bbbeec524d582d65a2bd9f131ca`。
- [云端完整离线测试 run 41755159702](https://github.com/null-object-0000/goodsdex/actions/runs/41755159702)：**684 passed / 8 deselected**；本地同为684 passed，沿用仓库not live选择器。
- 发布门禁 **360 passed**。见 [完整云端测试摘要](cloud-tests.json)、[测试日志摘录](tests-cloud-excerpts.log)、[发布运行记录](publication.json)、[发布门禁日志](publication-tests-excerpts.log)。
- 已调用既有API同步器，真实返回 `{"ok":true,"count":2902,"errors":[]}`，见 api-sync.log。

## 真实线上返回

[线上 /api/meta](https://spend.snewbie.site/api/meta) revision：`14707400f2c64332a4fa199f86c59d81`；total_published=2902；release_series.count=211、batch_count=129、inherited_without_product=163。

3条真实详情响应及相关日期对象摘录在 [online-excerpts.md](online-excerpts.md)。

|真实ID / 商品|日期|门禁结果|原始返回|
|---|---|---|---|
|CN:mi_cn:product:20618 / Xiaomi 15|2024-10-29|official，display_allowed=true|[详情响应](online-detail-20618.json) / [线上API](https://spend.snewbie.site/api/goods/CN%3Ami_cn%3Aproduct%3A20618)|
|CN:mi_cn:product:21765 / 小米电视S Pro 85 Mini LED 2026|2025-09|corroborated，display_allowed=true|[详情响应](online-detail-21765.json) / [线上API](https://spend.snewbie.site/api/goods/CN%3Ami_cn%3Aproduct%3A21765)|
|CN:mi_cn:product:25291 / 小米智能门锁5 Max深锖色|2026-09（内部断言）|unverified，usage=disabled，display_allowed=false，display=null|[详情响应](online-detail-25291.json) / [线上API](https://spend.snewbie.site/api/goods/CN%3Ami_cn%3Aproduct%3A25291)|

验证时间：2026-11-04T01:40:38.638988+00:00。线上全量2902行与发布产物**逐值相同**，meta也逐值相同。全量商品SHA256：`fbc90b3cc0f180c09f72ed676e51c4484f764796f18759f74fb074e999775526`。三条详情日期对象与对应发布行逐字段一致。见 [验证结果](online-verification.json)、[线上meta原文](online-meta.json)、[线上全量快照](online-goods.json.gz)。

## 隔离本轮结果与实际发布结果

仅重放本轮小米series输入时，小米断言267→274、展示141→178；全库断言827→834、展示655→692。断言与展示没有混算。

正常workflow会重放当前代码中的全部已审核输入。当前main原先有已提交未推送的`7a64e0eb`，其4条其它品牌日期尚未进入修前data：比亚迪夏2026款DM-i、DJI Ronin 4D-6K、Osmo Mobile 6暗岩灰、DJI Power Auro 2000 Elite。本次随正常finalize一并发布，故**实际全库断言827→838，可展示655→696**（分母均2902）。额外4行不能归功于小米字典。

发布产物已与 `apply_series_releases(apply_release_dates(baseline))` **全量逐值相等**，未通过忽略这4条来放过差异。除其4个release对象和本轮release_series外所有字段不变。门禁代码与本轮起点文件SHA256一致，详见 [发布不变量与4条差异](publication-invariants.json)、[完整finalizer期望](expected-finalizer.json.gz)。
