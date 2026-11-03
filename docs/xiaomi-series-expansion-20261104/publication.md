# 正式发布与线上验收

- 实现提交：`a5c31c2ccb090bbe388f317e8e5ecfee20dfbcf7`（main，已推送）。
- data 提交：`d266728aecf8427f448561af0a603290462cbf2b`。
- [正式发布流水线](https://github.com/null-object-0000/goodsdex/actions/runs/41742051476)：success；发布门禁359 passed；正常collect → 持锁merge → finalize → data → OSS读回校验全部完成。
- [云端完整离线测试](https://github.com/null-object-0000/goodsdex/actions/runs/41742051264)：680 passed / 8 deselected；本地相同。
- 同步接口返回：`{"ok":true,"count":2898,"errors":[]}`（api-sync.log）。
- 线上验收时间：`2026-11-03T23:53:20.171574+00:00`；revision：`d7e96c69134c400a99dc4eb8fffbc4e8`。
- 完整 `/api/goods` 与本次data提交逐值完全相同；其字节SHA256为 `1977d863ec6c6258eba19a4efba268196cccffa90101d5b3fee4e5910d21101d`，与OSS读回一致。API meta与本次发布meta逐值相等。

小米分母1684保持不变，单品111不变，系列149→204，日期断言并集212→267（12.6%→15.9%），新增55行、53个不同ID。无日期断言仍有1417行。旧81批149行缺第二独立来源，转为不可展示内部参考；严格展示并集200→141（11.9%→8.4%）。不将原断言保留统计冒充可展示覆盖。

**未达到1200条已证同批覆盖目标。** 全量清单盘点1472行，已证32批55行，其余1385研究分组1417行未完成补全；不是已穷尽逐族网络检索。

## 随机5条真实search返回

基础search保持轻索引；使用已经存在的ids参数补全详情。本轮无API代码修改，无goods/meta语义修改。固定种子20261104从本轮53个不同ID抽取，随后一次请求获取以下5条；没有替换样本。

[真实search请求](https://spend.snewbie.site/api/goods/search?brand=%E5%B0%8F%E7%B1%B3&ids=CN%3Ami_cn%3Aproduct%3A7897%2CCN%3Ami_cn%3Aproduct%3A6632%2CCN%3Ami_cn%3Aproduct%3A20350%2CCN%3Ami_cn%3Aproduct%3A21659%2CCN%3Ami_cn%3Aproduct%3A21872)；[完整原始响应](search-five-after.json)；[日期对象摘录](online-five.md)；[逐字段验证](online-verification.json)。

|真实ID|商品|release_series.date|granularity|来源 / 交叉核验|
|---|---|---|---|---|
|CN:mi_cn:product:7897|小米6X 6GB+128GB|2018-04-25|day|third_party / corroborated|
|CN:mi_cn:product:6632|小米电视4A 43英寸|2017-03-21|day|third_party / corroborated|
|CN:mi_cn:product:20350|米家吸顶灯套系|2024-08-29|day|third_party / corroborated|
|CN:mi_cn:product:21659|REDMI Note 15 Pro|2025-08-21|day|third_party / corroborated|
|CN:mi_cn:product:21872|Xiaomi Pad 8|2025-09|month|official / official|

五条search的完整release_series对象都与发布产物及各自真实详情接口逐字段一致；均display_allowed=true。Xiaomi Pad8只显示到月，未补成9月某日。

## 核对入口

- [全量族清单](families.md) 与 [未找到官方/可靠来源清单](unresolved.md)；JSON保留全部成员ID和检索范围。
- [30条来源原句对照](sample-30.md)，保留主/第二来源原句、日期差、代际/规格边界。
- [完整线上快照](online-goods.json.gz)、[发布产物快照](published-goods.json.gz)、[发布摘要](published-data.json)。

```sh
python docs/xiaomi-series-expansion-20261104/verify_online.py \
  --expected docs/xiaomi-series-expansion-20261104/published-goods.json.gz
```
