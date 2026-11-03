# 发布字段接线修复

公开字段统一为 `release_series`，旧 `series_release` 在每次 finalize 时清理；审核输入 `data/official/series-releases.json` 保留原有格式和证据，不重新推断日期。其 81 批、149 个商品 ID 与 `docs/series-release-rollout-20261103/batches.json` 逐项对照由回归测试验证。

`inherited` 表示该记录无单品级 `release.date`。有单品日期时为 false，两字段并存。系列日期始终保留 `level: series`、月粒度、证据、市场、批次及“系列推出时间”口径，不写入 `release`。

共享发布入口的 `scripts/finalize_public.py` → `goodsdex.dedupe.finalize_public` 每次应用审核成员映射，再生成完整详情分片、manifest 和数据文件。新增集成测试实际调用该入口，验证 149 个成员、全部原 release 对象不变及采集器清掉系列字段后的重放恢复。meta.release_series 单独统计全部系列断言及批次，避免与单品日期覆盖率混用。

API 位于相邻 `spend-good/services/api` 仓库。其现有 hydrate 保留完整详情字段，因此无需部署代码即可透出新字段；添加同步→惰性详情及批量详情测试。分页及分组搜索列表不携带系列证据，避免每页重复证据文本；原始 `/api/goods` 导出仍包含。API 契约测试提交：`7c05a56`，278 项通过。

发布与线上实际验收见本目录 publication.json、verification.json 和 samples.md；旧 rollout 目录是历史记录，不作为本次验收依据。
