# 名称保真修复发布验收

- 代码提交：[`39882cf7b19186ab2f4a22af4fee938b07466fc3`](https://github.com/null-object-0000/goodsdex/commit/39882cf7b19186ab2f4a22af4fee938b07466fc3)。
- 正式发布：[run 41865048476](https://github.com/null-object-0000/goodsdex/actions/runs/41865048476)，completed / success，head 为上述提交；见[最终run状态](publication-run-final.json)。
- 数据提交：[`a49b7f0a4a865b74a728e1bcd00fd2c167c21f7a`](https://github.com/null-object-0000/goodsdex/commit/a49b7f0a4a865b74a728e1bcd00fd2c167c21f7a)。实际前一版为 `6dc7d76a`，不是审计开始时冻结的另一轮旧快照。
- 云端测试：[run 41865015733 / job 126696923087](https://github.com/null-object-0000/goodsdex/actions/runs/41865015733/job/126696923087)，completed / success；原始job状态见[JSON](tests-jobs-fresh.json)，日志摘录见[cloud-tests-summary.log](cloud-tests-summary.log)：828 passed, 8 deselected。本地全套同为828 passed / 8 deselected，修前801 passed / 8 deselected。

## 实际数据变化

2855→2842，精确新增排除13个ID；保留行221条仅名称策略相关字段有变化。所有价格及其它事实保持不变，无其它品牌/日期/汽车等意外变化，见[实际发布不变量](published-invariants.json)。原22条关键词记录10条排除、12条保留；另外恢复并排除3个此前丢失配件词的Sound配件。真套装、双支装保留。全库同名组按指定中位数阈值异常由2组降为0组，20个小米组及61组全库索引见[交叉校验](price-group-review.md)。

## 默认API核验

2026-11-05 00:36:54（上海时间）核验通过，见[线上机器结果](online-verification.json)、[完整日志](online-verification-final.log)、[线上meta](online-meta.json)。

- 默认 `/api/meta`、`/api/goods` 与OSS不可变blob一致，商品2842条、排除档案1140条。
- 当前revision为 `3e46ff8a56734ebba95ec01deaa819a0`。等待API同步期间，后续Apple定时发布已生成数据提交 `d58f7ea0a1a4a10ff7f4c69dd0b080f50fc16bc4`；用该提交重新归档后，数据分支商品文件、OSS和默认API三者全量相等。更早本次正式发布的 `a49b7f0a` 仍单独保留实际前后不变量，未与后续发布混淆。
- 234个已核官网名称、官方source_url与配件标记逐ID全部一致；原22条处置全部正确。所有指定保留的套装/双支整机及集成支架整机仍在列表中。
- 22104：`Xiaomi Sound 2 Max` / ¥1649 / false，默认详情保留。
- 22105：`Xiaomi Sound 2 Max 金属面板` / ¥299 / true，默认列表排除、详情404，排除档案保留全名和价格。
- 22547：`Xiaomi Sound 2 Max+2 Pro+无线连接器套装` / ¥5696 / false，默认详情保留。
- 23722：`Xiaomi Sound 2 Max双支装` / ¥3198 / false，默认详情保留。
- 22107和22544同样是配件，默认列表排除、详情404。

发布job本身的512项不变量检查全绿，配件门禁13/2833=0.459%绿色，见[发布检查日志](cloud-publish-checks.log)。最终两个发布job均completed / success，见[最终job状态](publication-jobs-final.json)。

## 发布时的外部状态

GitHub当时公告Actions/Pages故障，run汇总和job状态一度不一致；保留[官方状态记录](github-actions-incident.json)。最终以成功run、真实数据提交、OSS不可变blob及默认API字节比对共同验收，不以排队状态推断未发布。API每15分钟自动拉取一次数据；16:20 UTC轮次早于本次16:21 UTC发布，因此最初多次在线比对明确报revision不一致，日志留存，没有将其标成成功。
