# 第十轮发布与真实线上验收

- 实现与证据提交：`aa210997a6d004c9023c75661158d0efb2385ba2`，已推送main。
- 日期发布：[refresh-release-dates 41838811965](https://github.com/null-object-0000/goodsdex/actions/runs/41838811965)，**success**。collect→持锁合并→429项发布门禁→finalize→data→OSS逐对象GET/hash校验→manifest最后发布，全部完成。
- data提交：`f800a5f3aa554b660aef94de3f4bb23bb3d6333c`；持锁父版本：`669c7d59052402cd06f2af91ed60df6c79c33958`。
- 云端完整测试：[tests 41838755998](https://github.com/null-object-0000/goodsdex/actions/runs/41838755998)，**759 passed / 8 deselected**。本地修前753、修后759，无新红或新跳过。完整日志见[ci-tests.log](ci-tests.log)。
- 既有服务端同步器真实返回：`{"ok":true,"succeeded":9,"errors":[]}`，见[api-sync.log](api-sync.log)。沿用primeCatalog与现有数据库同步回调；没有手写线上商品、放宽日期门禁或重新部署API。

## 真实线上meta

核验时间：`2026-11-04T13:37:29.405033+00:00`。

[实际 /api/meta](https://spend.snewbie.site/api/meta) 返回：

```json
{
  "revision": "c31f94772e2c4df9a94fc6a61f952a96",
  "total_all": 3982,
  "total_published": 2856,
  "total_excluded": 1126
}
```

|品牌|实际整机可展示|实际整机覆盖率|
|---|---:|---:|
|富士|13/24|54.17%|
|大疆|96/275|34.91%|
|Apple|535/639|83.72%|
|小米|178/1381|12.89%|

富士全目录含39条镜头：52/63可展示；不能拿全目录比例替代整机比例。meta的固定整机总分母为2554，全发布行2856（2851唯一ID）；5个重复投影受既有冲突门禁保护，不删除、不改分母。

## 三个实际详情

三个模型来源均没有数值gid，使用API实际接受的canonical ID；保留真实`gid:null`，不虚构数字。

- [FUJIFILM X-S20](https://spend.snewbie.site/api/goods/CN%3Afuji%3Amodel%3Ax-s20)：`CN:fuji:model:x-s20` → `2023-06` / `announcement` / `GLOBAL_REPORTED_BY_CN_OFFICIAL`，label=`全球推出月份（官方回溯）`。
- [FUJIFILM X-E5 + XF23mmF2.8 R WR 套机](https://spend.snewbie.site/api/goods/CN%3Afuji%3Akit%3Ax-e5-xf23mmf28-r-wr)：`CN:fuji:kit:x-e5-xf23mmf28-r-wr` → `2025-08` / `availability` / `JP`，label=`日本发售时间`。
- [iPhone 6 Plus](https://spend.snewbie.site/api/goods/GLOBAL%3Aapple_support%3Amodel%3A111940)：`GLOBAL:apple_support:model:111940` → `2014-10` / `availability` / `CN`，label=`发售时间`。

[三个完整响应及原文摘录](online-excerpts.md)；响应原件：[1](online-detail-1.json)、[2](online-detail-2.json)、[3](online-detail-3.json)。[线上完整meta](meta-after.json)、[完整线上商品响应](online-goods.json.gz)、[机器核验结果](online-verification.json)。线上meta与发布文件逐值相等，整库2856行与data提交逐值相等，三个详情完整对象亦逐值相等。

## 持锁发布不变量

- 持锁父版本→本次data：恰好159行`release`、2行`release_series`改变，所有非日期字段、行数、ID、顺序逐值不变。
- 本次data完整逐值等于在持锁父版本重放`apply_series_releases(apply_release_dates(parent))`。
- 159条新增官方断言的日期、事件、市场、原文与SHA256均在真实线上逐项核验；原Apple417条可展示断言完整不变。
- 研究起点→持锁父版本可能包含独立价格/采集发布；本轮不把它们归因于日期操作。发布比较使用实际持锁父版本，不以研究起点冒充父版本。

[不变量结果](publication-invariants.json)、[持锁父快照](locked-parent-goods.json.gz)、[发布完整日志](publication-run.log)。

本轮目标结论与逐品牌缺口、未列出条目数及Top20、159条单品和2条系列事件统计、20条样本见[主报告](README.md)。未达到富士55/63和大疆150/275；这是受证据和精确套装门禁约束后的实际结果。
