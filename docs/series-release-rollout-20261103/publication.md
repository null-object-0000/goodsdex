# 发布及线上验收

实现提交：`4565cf5ae66150d95b1e5e8c6974ee44dca9541a`。

[实际发布任务](https://github.com/null-object-0000/goodsdex/actions/runs/41621428338)成功，经过正常 collect → candidate → 持锁合并 → 发布门禁 → finalize → data → OSS 镜像及读回校验。没有直接修改API数据，也没有强制推数据分支。

data 提交：`78820eb2edfa566d5cdeb076c37ecf2b78da3349`；商品SHA256：`911345a6f52174e44cf0f2f186a24cedd58777e996a319b2b4e8ab530767bfd2`。发布商品与本地正常finalize逐值相同，2909行；小米1695行，149条独立series字段。发布前后除series字段外的每一个商品字段均相同；汽车全部保留。

本地基线470通过，最终472通过；[云端离线测试](https://github.com/null-object-0000/goodsdex/actions/runs/41621428507)464通过、8项既有live测试按配置跳过；发布门禁171通过。没有新增测试失败。详见测试日志、`cloud-tests.json`、`publication.json`、`publication-excerpt.log`。

线上验收时间：2026-11-03T10:50:35.788733+00:00。`/api/goods` 与 data 发布商品全量逐值相同，149条系列字段；3个真实详情接口的series及原release对象逐值相同。另核对21243、21378、23676三个应留空的型号详情，全部无series字段。线上API按15分钟周期同步，早先仍为17条的真实观测保留在 `online-attempts.jsonl`，不冒充发布失败或测试失败。

[完整线上核对JSON](online-verification.json)与 [真实API快照](api-goods-after.json.gz)。

## 三个真实ID摘录

以下从真实 `/api/goods/<id>` 返回提取；省略其他字段，完整series对象及原release见JSON。

[米家扫拖机器人 5C 水箱版](https://spend.snewbie.site/api/goods/CN%3Ami_cn%3Aproduct%3A21825)

```json
{
  "id": "CN:mi_cn:product:21825",
  "series_release": {
    "date": "2025-08",
    "granularity": "month",
    "level": "series",
    "batch_id": "mi-reviewed-0878384",
    "source": "third_party",
    "event": "announcement",
    "display": "该系列 2025 年 8 月发布"
  },
  "release": null
}
```

[米家扫拖机器人 6 Max 白色](https://spend.snewbie.site/api/goods/CN%3Ami_cn%3Aproduct%3A25466)

```json
{
  "id": "CN:mi_cn:product:25466",
  "series_release": {
    "date": "2026-09",
    "granularity": "month",
    "level": "series",
    "batch_id": "mi-reviewed-0999647",
    "source": "third_party",
    "event": "announcement",
    "display": "该系列 2026 年 9 月发布"
  },
  "release": null
}
```

[米家冰箱Pro 法式508L 自动制冰 冰羽白](https://spend.snewbie.site/api/goods/CN%3Ami_cn%3Aproduct%3A23577)

```json
{
  "id": "CN:mi_cn:product:23577",
  "series_release": {
    "date": "2026-05",
    "granularity": "month",
    "level": "series",
    "batch_id": "mi-reviewed-0954285",
    "source": "third_party",
    "event": "availability",
    "display": "该系列 2026 年 5 月开售"
  },
  "release": null
}
```

## 验收边界

1728口径尚未闭环：线上和data真实小米分母均为1695，缺少另外33条对应身份，未构造样本或虚报覆盖率。当前1695条全部进入清单；本轮完成当日官方逐ID扫描复核、品类检索与目标批次正文审核，未声称对1546条留空记录逐型号穷尽网络检索。具体检索层级与缺失原因已逐名列出。
