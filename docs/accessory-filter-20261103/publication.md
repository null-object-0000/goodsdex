# 发布与验收记录

最终规则代码：`193922d229747da500ea98145d378565b4e2d424`。
首次实现 `4655b6fd`，留档快照保护修复 `19e9d921`。
规则过滤提交：`05c7a82a58a276079be01404080e7e4b753eff87`；最终留档修复 data 提交：`a14949f3cf0daa1026961c52946a2db16c618f4b`。

正式执行（全部成功）：

- [首批配件迁移](https://github.com/null-object-0000/goodsdex/actions/runs/41616337659)：新增排除 1029/3946 个非汽车身份，26.08%，红灯；仅对已核批次 SHA-256 精确放行。发布后 2939 行。
- [不带放行参数的缓存复跑](https://github.com/null-object-0000/goodsdex/actions/runs/41616757116)：缓存补充重放 51 条已排除记录，新增 0，绿灯，发布仍为 2939 行。
- [首次排除档案恢复](https://github.com/null-object-0000/goodsdex/actions/runs/41617477392)：复跑检查发现 15 条旧缓存覆盖档案字段。恢复第一轮完整快照，覆盖前的缓存观测存入 subsequent_observations；后续仅保留首次排除快照，禁止旧缓存覆盖。商品发布集未改变。
- [最终耗材与 Pro+ 修正发布](https://github.com/null-object-0000/goodsdex/actions/runs/41617707448)：新增排除 30/2917，1.03%，无放行参数，正常绿灯。最终 2909 行。补齐刷头、墨盒、硒鼓、钢化膜、替换套装与基座；修正 Pro+ 中的加号不能当赠品分隔符。完整儿童电动牙刷四刷头装继续保留。

- [清理旧任务后的最终档案恢复](https://github.com/null-object-0000/goodsdex/actions/runs/41618624457)：旧代码的惠普任务随后发布，重新覆盖 15 条档案。所有旧任务完成后，按新版规则恢复首次快照；保留惠普新采集数据、完整 1059 条配件档案和旧缓存观测。新增排除 0，正常绿灯。

各任务状态、步骤和原始日志摘录见同目录 publication-*.json / publication-*-excerpts.log。
最终 OSS meta.json PUT/GET SHA-256：`5e09edbf7cd2613414e3802b099d050598f83be72ce56a0bd2aea7facaf84b08`。

本地全量 **470 passed**（基线 414 passed），云端最终代码 **462 passed / 8 deselected**，发布关键门禁 **157 passed**。8 项为原有 live 标记测试，云端按既有配置跳过；本地全量均通过。未更改其它任务的测试范围或超时。

[留档核对](archive-verification.json)证明 1059 条首次排除记录的全部原字段与发布前快照逐值一致；15 条被覆盖观测也保留。规则过滤前后的 data 源目录 Git 树同为 `3f0d9a98502545295eecaa0365e97c3f3805b1bc`，raw、来源档案、public/prices 均无改动。其后独立惠普采集更新源目录；最终档案恢复前后该源目录仍同为 `5c5306a42ba741fd9baefb0a4ec0bc2c35453709`，惠普更新与价格历史完整保留。

[完整报告](README.md)分开列出其它品牌与整车表；附逐主品类分布、1059 条明细与 30 条复核样本。统计以真实发布前 3968 行为基线，不复用历史 5448/963 粗判。

旧 Apple 任务曾因并发修改已移除的 AirTag 被候选合并门禁拦截（任务 41616568217），未推数据；属于预期并发保护，不是测试失败。最终规则的本地/云端测试和以上五轮发布均成功。

## 线上实际返回

[完整接口验收](online-verification.json)、[实际 meta JSON](api-meta-after.json)、[实际 goods JSON（gzip）](api-goods-after.json.gz)。API 的商品字节哈希与最终 data 商品导出相同：`3d232e25f5d2dace417bea8cfbcd3cf27d9e1e0083b07dbf7ab0d23672471707`。元信息可能仍是前一轮惠普发布的生成时间；两轮商品字节、条数、品牌统计与日期覆盖率一致，最终留档修复没有再改商品内容。

```json
{
  "checked_at": "2026-11-03T10:24:47.195297+00:00",
  "meta_count": 2909,
  "goods_count": 2909,
  "brands": {
    "Apple": 635,
    "比亚迪": 14,
    "大疆": 281,
    "富士": 63,
    "惠普": 218,
    "小米": 1695,
    "小米汽车": 3
  },
  "ids_match": true,
  "no_accessories": true,
  "cars_unchanged": true,
  "goods_match_manifest": true,
  "sample_30_presence_correct": true
}
```

非汽车日期覆盖率：691/3951 = 17.49% → 668/2892 = 23.10%。汽车独立为 17 条，未排除；不可混作非汽车分母。四类关键整机详情均 HTTP 200，电池、滤芯、Pro+ 手机壳详情 HTTP 404，详见完整接口验收。
