# Git 价格历史回填验收

数据提交：`6d0cbc51`。回溯固定输入 `3136366cc89d7831dfe34c45eff335229b47310f`，共 259 次 `public/goods.json` 提交。

|项目|结果|
|---|---:|
|扫描商品行|995,176|
|合并前已有观测|5,687|
|合并后总观测|104,011|
|净新增观测|98,324|
|不同 gid|4,038|
|至少 3 点的 gid|2,271|
|数据时间范围|2026-10-13T09:45:44+08:00 至 2026-11-04T17:11:05+08:00|
|fetched_at 时间来源|63,692|
|commit 时间来源|40,319|
|suspicious|1,182|
|冲突出现次数 / 不同冲突键|18,588 / 282|

## 每 gid 观测数分布

|观测数|gid 数|
|---:|---:|
|1|1560|
|2|207|
|3|609|
|4|557|
|5|199|
|6|121|
|7|14|
|8|1|
|10|4|
|11|5|
|12|11|
|41|9|
|63|1|
|64|208|
|102|2|
|115|4|
|124|11|
|125|320|
|150|36|
|171|2|
|217|1|
|219|145|
|222|11|

## 十个完整序列

[完整序列：10 个 gid，从 10-27 至 11-04，逐点时间、价格和时间来源](sequences.md)。选择覆盖两个端点且有变化的商品；没有省略中间点，没有插值。

## 异常价隔离

规则严格使用 `0 < price < 200000`；超界、非数值或非有限报价均设 `suspicious: true`，原值保留在 `raw_price`，标准 `price=null`，不进入本次新增兼容投影的有效价格。空值原本表示缺价，不因缺价本身标 suspicious。这个统一阈值也会标记价格确实超过 20 万元的汽车，原值保留供复核，不意味着已证实数据错误。

[全部异常记录](suspicious.jsonl)，以下是 10 条完整样本：

```jsonl
{"gid":"CN:byd:car:goods-131:unknown:attr-1662","at":"2026-10-28T21:35:05.545672+08:00","price":null,"price_type":"price","currency":"CNY","missing_status":"no_price","source":"byd","backfilled":true,"time_source":"fetched_at","git_commit":"da548d7f80531d200b1fab0fd2cb52f54cbe0499","revision":"da548d7f80531d200b1fab0fd2cb52f54cbe0499","market_price":null,"price_kind":"msrp","raw_price":215800,"original_missing_status":null,"suspicious":true,"suspicious_reason":"price_outside_0_200000_or_non_numeric"}
{"gid":"CN:byd:car:goods-151:unknown:attr-1677","at":"2026-10-28T21:35:05.545672+08:00","price":null,"price_type":"price","currency":"CNY","missing_status":"no_price","source":"byd","backfilled":true,"time_source":"fetched_at","git_commit":"da548d7f80531d200b1fab0fd2cb52f54cbe0499","revision":"da548d7f80531d200b1fab0fd2cb52f54cbe0499","market_price":null,"price_kind":"msrp","raw_price":206800,"original_missing_status":null,"suspicious":true,"suspicious_reason":"price_outside_0_200000_or_non_numeric"}
{"gid":"CN:byd:car:goods-151:unknown:attr-1678","at":"2026-10-28T21:35:05.545672+08:00","price":null,"price_type":"price","currency":"CNY","missing_status":"no_price","source":"byd","backfilled":true,"time_source":"fetched_at","git_commit":"da548d7f80531d200b1fab0fd2cb52f54cbe0499","revision":"da548d7f80531d200b1fab0fd2cb52f54cbe0499","market_price":null,"price_kind":"msrp","raw_price":219800,"original_missing_status":null,"suspicious":true,"suspicious_reason":"price_outside_0_200000_or_non_numeric"}
{"gid":"CN:byd:car:goods-151:unknown:attr-1679","at":"2026-10-28T21:35:05.545672+08:00","price":null,"price_type":"price","currency":"CNY","missing_status":"no_price","source":"byd","backfilled":true,"time_source":"fetched_at","git_commit":"da548d7f80531d200b1fab0fd2cb52f54cbe0499","revision":"da548d7f80531d200b1fab0fd2cb52f54cbe0499","market_price":null,"price_kind":"msrp","raw_price":246800,"original_missing_status":null,"suspicious":true,"suspicious_reason":"price_outside_0_200000_or_non_numeric"}
{"gid":"CN:byd:car:goods-151:unknown:attr-1680","at":"2026-10-28T21:35:05.545672+08:00","price":null,"price_type":"price","currency":"CNY","missing_status":"no_price","source":"byd","backfilled":true,"time_source":"fetched_at","git_commit":"da548d7f80531d200b1fab0fd2cb52f54cbe0499","revision":"da548d7f80531d200b1fab0fd2cb52f54cbe0499","market_price":null,"price_kind":"msrp","raw_price":269800,"original_missing_status":null,"suspicious":true,"suspicious_reason":"price_outside_0_200000_or_non_numeric"}
{"gid":"CN:byd:car:goods-151:unknown:attr-1681","at":"2026-10-28T21:35:05.545672+08:00","price":null,"price_type":"price","currency":"CNY","missing_status":"no_price","source":"byd","backfilled":true,"time_source":"fetched_at","git_commit":"da548d7f80531d200b1fab0fd2cb52f54cbe0499","revision":"da548d7f80531d200b1fab0fd2cb52f54cbe0499","market_price":null,"price_kind":"msrp","raw_price":269800,"original_missing_status":null,"suspicious":true,"suspicious_reason":"price_outside_0_200000_or_non_numeric"}
{"gid":"CN:xiaomi_ev:car:item-500010402:unknown:ssu-600014078","at":"2026-10-28T21:35:05.545672+08:00","price":null,"price_type":"price","currency":"CNY","missing_status":"no_price","source":"xiaomi_ev","backfilled":true,"time_source":"fetched_at","git_commit":"da548d7f80531d200b1fab0fd2cb52f54cbe0499","revision":"da548d7f80531d200b1fab0fd2cb52f54cbe0499","market_price":null,"price_kind":"msrp","raw_price":529900,"original_missing_status":null,"suspicious":true,"suspicious_reason":"price_outside_0_200000_or_non_numeric"}
{"gid":"CN:xiaomi_ev:car:item-500010402:unknown:ssu-600014079","at":"2026-10-28T21:35:05.545672+08:00","price":null,"price_type":"price","currency":"CNY","missing_status":"no_price","source":"xiaomi_ev","backfilled":true,"time_source":"fetched_at","git_commit":"da548d7f80531d200b1fab0fd2cb52f54cbe0499","revision":"da548d7f80531d200b1fab0fd2cb52f54cbe0499","market_price":null,"price_kind":"msrp","raw_price":814900,"original_missing_status":null,"suspicious":true,"suspicious_reason":"price_outside_0_200000_or_non_numeric"}
{"gid":"CN:xiaomi_ev:car:item-500015457:unknown:ssu-600019693","at":"2026-10-28T21:35:05.545672+08:00","price":null,"price_type":"price","currency":"CNY","missing_status":"no_price","source":"xiaomi_ev","backfilled":true,"time_source":"fetched_at","git_commit":"da548d7f80531d200b1fab0fd2cb52f54cbe0499","revision":"da548d7f80531d200b1fab0fd2cb52f54cbe0499","market_price":null,"price_kind":"msrp","raw_price":279900,"original_missing_status":null,"suspicious":true,"suspicious_reason":"price_outside_0_200000_or_non_numeric"}
{"gid":"CN:xiaomi_ev:car:item-500015457:unknown:ssu-600019694","at":"2026-10-28T21:35:05.545672+08:00","price":null,"price_type":"price","currency":"CNY","missing_status":"no_price","source":"xiaomi_ev","backfilled":true,"time_source":"fetched_at","git_commit":"da548d7f80531d200b1fab0fd2cb52f54cbe0499","revision":"da548d7f80531d200b1fab0fd2cb52f54cbe0499","market_price":null,"price_kind":"msrp","raw_price":329900,"original_missing_status":null,"suspicious":true,"suspicious_reason":"price_outside_0_200000_or_non_numeric"}
```

## 冲突与保留策略

按标准 gid 与规范化时间去重。已有观测默认来源为真实 fetched_at；冲突优先保留 fetched_at，优先级相同则保留已有观测；纯历史同优先级保留最早快照。18,588 次冲突涉及 282 个不同键，全部保留在 [压缩冲突明细](conflicts.jsonl.gz)，每项含 retained / rejected。未把同一商品同一 fetched_at 的价格编辑伪装为新点。独立校验确认 5,687 条已有记录的原字段值全部保留。

兼容投影按 gid/时间补入缺失键，保留已有价格；同一时间戳已有其他商品时也能补齐。旧月文件在磁盘暂存后重写为每时间戳一行，以满足线上旧 parser 的整快照冲突检查。

## 发布与校验

产物沿用 data 分支 `public/price-history/YYYY-MM.jsonl.gz` + `index.json`，OSS 前缀 `data/public/price-history/`；题目中的 `data/price-history` 不是本仓库实际发布路径，未另建平行格式。JSONL 保持现有 gid/at/price/price_type/currency/missing_status/source/revision 格式，并添加 time_source、git_commit、backfilled、market_price、price_kind、raw_price 等来源字段。meta 中只更新现有 price_history 描述，不改变 goods 或发布 workflow。

使用现有 [mirror-sharded-release](https://github.com/null-object-0000/goodsdex/actions/runs/41809899193)，继续执行 immutable blobs → 文件别名 → history index → meta 的 SHA 读回校验。线上仍使用 `prices/YYYY-MM.jsonl` 兼容投影导入，未修改服务端或发布链路。

本地独立验证：[local-validation.json](local-validation.json)。重复运行仍 104,011 条、legacy_added=0。离线测试 753 passed / 8 deselected，基线 747 passed / 8 deselected；[完整测试日志](tests.log)，新增 6 项测试覆盖分块边界、时间优先级、异常隔离、已有新观测不覆盖、兼容投影补键和重跑。

流式读取每次 `git show` 的 stdout，一行商品对象加 64 KiB 输入块；SQLite 在临时目录去重、排序。整次实跑 63.09 秒，time 报告进程树最大 RSS 136,852 KiB，未同时载入全部快照。[资源日志](resources.log)。

复跑：

```bash
python3 scripts/backfill_price_history_from_git.py --ref origin/data --public <data-checkout>/public --report <report-dir>
python3 docs/git-price-history-20261104/verify_publication.py --public <data-checkout>/public --online
```

## 限制

Git 快照最早提交为 2026-10-27T08:01:34Z，无法恢复更早 Git 快照或证明更早的完整价格变化。快照内部已有更早 fetched_at，因此保留的数据时间最早到 2026-10-13T09:45:44+08:00；这不是恢复了 10-13 的 Git 历史。不能把总数据范围等同于持续覆盖范围。

提交间隔不均，可能相隔几小时或超过一天；commit 回退点的密度就是相关提交密度。fetched_at 观测还会因多次提交同一采集结果而去重，因此采集时间曲线可以更稀疏。commit 来源只表明当时快照中存在该报价，不证明该时刻重新采价；价格不变的 commit 点也没有插值。

4,038 个 gid 包含历史已下架/排除的商品和旧 ID，不等于现售商品数量；没有按当前 goods 清单裁掉真实历史。服务端旧 parser 把缺价映射成 price_missing，time_source 与 suspicious 等完整来源信息保存在 gzip 文件；旧接口自身不暴露这些新增字段。

## OSS 与线上实际返回

OSS / data index SHA-256 均为：

`fff18bdef8146b2aaac5b0d517883b3a64d16917664258c9e262e09ce3003ffc`

两个月 gzip 的 SHA、字节数、行数均读回通过，data 提交 `6d0cbc51de7ea9127919abcff411aff3877a580b`。镜像 workflow 成功，[OSS 完整日志](oss-mirror.log)，[独立验收 JSON](acceptance.json)。

服务端 syncHistory：10 月 insertedPoints=28,442；11 月 insertedPoints=70,278；两月 lastError=null。目录同步 count=2,856、errors=[]。[服务端实际执行日志](api-sync.log)。本次未开启或修改 retention 设置。

下面是公开 `/api/price-history?gid=...` 的三个实际响应摘要；完整 points 与 HTTP 返回体见 [api-responses.json](api-responses.json)。时间保留接口返回的原始时区，最早 UTC 时间换算北京时间均在 10 月 27 日。

```json
[
  {
    "gid": "CN:mi_cn:product:19203",
    "observationCount": 6,
    "intervalMin": 449,
    "intervalMax": 479,
    "observationStart": "2026-10-26T23:50:24+00:00",
    "observationEnd": "2026-11-04T16:44:53+08:00"
  },
  {
    "gid": "CN:mi_cn:product:19226",
    "observationCount": 6,
    "intervalMin": 209,
    "intervalMax": 229,
    "observationStart": "2026-10-26T23:50:31+00:00",
    "observationEnd": "2026-11-04T16:44:53+08:00"
  },
  {
    "gid": "CN:mi_cn:product:19917",
    "observationCount": 6,
    "intervalMin": 7199,
    "intervalMax": 7999,
    "observationStart": "2026-10-26T23:23:32+00:00",
    "observationEnd": "2026-11-04T16:44:53+08:00"
  }
]
```
