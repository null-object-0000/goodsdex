# 第七轮发布及线上验收

- 实现提交：`25636a1b67bead0d4fa252b11f9a1dc9943d187a`，已推送 main。
- 正常发布：[refresh-release-dates 41760487947](https://github.com/null-object-0000/goodsdex/actions/runs/41760487947)，**success**。collect→持锁合并→376项门禁→finalize→data→OSS逐对象读回及manifest最后发布完成，未手改线上商品。
- data 提交：`7af795bb96a5b584b81dc5b72c56e8b43b2bc6e5`。
- 云端完整测试：[tests 41760491660](https://github.com/null-object-0000/goodsdex/actions/runs/41760491660)，**700 passed / 8 deselected**。本地同为700 passed，新增16个回归；没有新失败或新增跳过。推送自动启动的41760487259被同分支手动测试按既有concurrency规则取消，保留取消记录，不计为通过。
- API同步器真实返回：`{"ok":true,"count":2902,"errors":[]}`，见[api-sync.log](api-sync.log)。

## 真实线上响应

验证时间：2026-11-04T02:39:06.113759+00:00。

[线上 /api/meta](https://spend.snewbie.site/api/meta) 摘录：

```json
{"revision":"f5699bf587db43969d4b8169ed7c2907","total_published":2902,"release_scope":{"policy":"machine-release-v1","label":"整机口径覆盖率","denominator":"machine","tiers":{"machine":2554,"accessory":256,"third_party_selection":92}}}
```

3个实际`/api/goods/<id>`返回摘要；完整两份URL/原句/日级日期和对象见[online-excerpts.md](online-excerpts.md)，完整响应分别保留为online-detail-*.json。

|商品 / 真实ID|release.date|source|event|交叉 / 展示|线上链接|
|---|---|---|---|---|---|
|DJI ROMO P 水箱版 / `CN:dji:sku:192291`|2025-08|third_party|announcement|corroborated，0天，true|[详情](https://spend.snewbie.site/api/goods/CN%3Adji%3Asku%3A192291)|
|小米8 SE 6GB+64GB / `CN:mi_cn:product:8152`|2018-05|third_party|announcement|corroborated，0天，true|[详情](https://spend.snewbie.site/api/goods/CN%3Ami_cn%3Aproduct%3A8152)|
|汉2023 DM-i冠军版 / `CN:byd:car:han:2023:dmi`|2023-05|third_party|announcement|corroborated，0天，true|[详情](https://spend.snewbie.site/api/goods/CN%3Abyd%3Acar%3Ahan%3A2023%3Admi)|

线上meta与data产物逐值相等；线上`/api/goods`全量2902行与data产物逐值相等；3个详情release与对应产物逐字段相等，每条保留2份assertions。完整验证结果：[online-verification.json](online-verification.json)，真实全量响应：[online-goods.json.gz](online-goods.json.gz)，发布meta：[published-meta.json](published-meta.json)。

全量data商品SHA256：`55a78cde99a0e482a7cf117bef0cf44c5265d38420371d04f91c9c48b790502b`。第一次未压缩21MB API导出在45秒时超时（只收到部分正文，不采信）；改用压缩传输后完整读取并通过逐值核验。没有用本地产物冒充线上响应。

## 固定研究基线与持锁父版本

研究基线为ee076d95（线上首次冻结revision14707400f2c64332a4fa199f86c59d81）。本轮研究期间，独立定时流水线先后发布了apple、prices、hp数据，持锁读取的父版本实际为`b2a5e4981756e79fa7cfcdf383ca8cfb10b864ff`，不能声称线上其余字段对研究起点完全没变。

已逐字段归因：

- 研究基线→持锁父版本：544行fetched_at、544行price_fetched_at、11行params改变，由先前独立采集发布带入；不是本轮日期逻辑更改。商品ID、名字、分类、分层分母、日期投影保持一致。
- 持锁父版本→本轮发布：**仅55行release改变**（16行新增第三方、39行既有第三方应用新门禁，其中14行从可展示降级），所有其它字段、行数、ID及次序逐值不变。
- 当前产物完整逐值等于在持锁父版本重放`apply_series_releases(apply_release_dates(parent))`；日期投影也完整逐值等于冻结研究基线上的预期。没有忽略日期差异来放过并发发布。

[publication-invariants.json](publication-invariants.json)保存准确计数与父提交；[locked-parent-goods.json.gz](locked-parent-goods.json.gz)保存实际持锁父快照。API核验依此进行，`report.py`仍保持原固定基线以复算本轮增量。

## 抽样及剩余缺口

21个精确审核候选中16通过、5拒绝；固定随机20条抽样包含15条通过、5条拒绝，不冒充20条新增通过。所有16个实际写入候选另由离线测试逐项核验原响应hash、原句和版本片段。

目标四品牌剩余1611行是本轮限定源/精确双源规则下未获取，非全网永远无法获取；Apple/富士另241行本轮未扩展研究。分层表、逐品牌增量、原因分类和逐条清单见[主报告](README.md)。
