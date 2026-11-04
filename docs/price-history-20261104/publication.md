# 正式发布验收

data commit: `93d7d90cec4ed4402c1ae43ccaf1682567654001`；release revision: `6bb90a62c4984428bb496b42a3e24bf5`。

两轮真实采集：[第一轮](https://github.com/null-object-0000/goodsdex/actions/runs/41801175404)、[第二轮](https://github.com/null-object-0000/goodsdex/actions/runs/41801761617)，各追加 1325 条，共 2650 条，均无请求错误。
最终兼容性修复通过现有空候选发布入口重新 finalize：[发布任务](https://github.com/null-object-0000/goodsdex/actions/runs/41803189995)。未再改写旧观测内容；商品清单/历史清单分离后，目录同步成功（2856 条，errors=[]）。

747 passed / 8 deselected；[GitHub tests](https://github.com/null-object-0000/goodsdex/actions/runs/41803189866) success。

## Index 读回

OSS HTTP 200，gzip 文件均按 index sha256、行数验证，index.revision = meta.revision。

data SHA-256: `2da8e86c65110b258d8daa95a2074d14633d046a4364f7447227fb17c0ba7c23`
OSS SHA-256: `2da8e86c65110b258d8daa95a2074d14633d046a4364f7447227fb17c0ba7c23`

## 三条实采样本

```json
{"gid": "CN:mi_cn:product:10000353", "at": "2026-11-04T16:40:13+08:00", "price": 467, "price_type": "price", "currency": "CNY", "missing_status": "ok", "source": "mi_cn", "revision": "89fe88ec34a347e5a85013bab0e72ede"}
{"gid": "CN:mi_cn:product:10000407", "at": "2026-11-04T16:40:13+08:00", "price": 799, "price_type": "price", "currency": "CNY", "missing_status": "ok", "source": "mi_cn", "revision": "89fe88ec34a347e5a85013bab0e72ede"}
{"gid": "CN:mi_cn:product:10015", "at": "2026-11-04T16:40:13+08:00", "price": 99, "price_type": "price", "currency": "CNY", "missing_status": "ok", "source": "mi_cn", "revision": "89fe88ec34a347e5a85013bab0e72ede"}
```

## 回填和三点趋势

回填 2700 条（有价 2173、缺价 527），总观测 5350。回填来自原 goods 实际 fetched_at，两个新增时间点来自两轮真实 HTTP 采集；价格未变并不代表插值。

gid: `CN:mi_cn:product:10015`

|时间（+08:00）|价格 CNY|来源|
|---|---:|---|
|2026-10-27T08:23:21+08:00|99|backfilled:true|
|2026-11-04T16:40:13+08:00|99|真实采集|
|2026-11-04T16:44:53+08:00|99|真实采集|

## 在线 API 摘要

```json
{
  "gid": "CN:mi_cn:product:10015",
  "observationCount": 3,
  "observationStart": "2026-10-27T08:23:21+08:00",
  "observationEnd": "2026-11-04T16:44:53+08:00",
  "missingPriceCount": 0
}
```

## 缺价与边界

全部 527 条缺价观测 price=null；518 条 no_price，9 条 unavailable。全部新 gzip 中 price=0 的记录为 0；同 gid/at 重复数为 0。

```json
{"gid": "CN:fuji:kit:x-e5-xf23mmf28-r-wr", "at": "2026-10-27T23:30:05.645638+08:00", "price": null, "price_type": "price", "currency": "CNY", "missing_status": "no_price", "source": "fuji", "backfilled": true, "revision": "89fe88ec34a347e5a85013bab0e72ede"}
{"gid": "CN:hp_cn:sku:D3RU2PC", "at": "2026-11-02T13:13:08.438673+08:00", "price": null, "price_type": "price", "currency": "CNY", "missing_status": "unavailable", "source": "hp_cn", "backfilled": true, "revision": "89fe88ec34a347e5a85013bab0e72ede"}
```

服务端目前仍通过旧 prices 月快照兼容投影导入，尚未自动消费新 index.revision，也会把缺价状态映射为 price_missing；完整缺价枚举保存在新 gzip。线上 HISTORY_RETENTION_ENABLED=false；采集侧热读 90 天清单与 cold 清单已发布，但数据库的自动 90 天清理/日聚合尚未开启，本次未改服务端配置。

第一轮目录同步遇到严格 meta.files 白名单错误的证据保留在 first-api-sync.log；最终 api-sync.log 显示修复后成功，没有将失败记录伪装成成功。
