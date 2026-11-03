# Actions 采集线状态验收

实现：`scripts/generate_sources_status.py`。统一发布在 finalize 前生成 `sources-status.json`；finalize 将它的 sha256/bytes/count 写入 `meta.files`；OSS 通过该 manifest 同时镜像不可变 blob 和公开 alias，meta 最后上传并回读验证。

另有 `sources-status.yml` 每 15 分钟巡检，不依赖采集成功，持 `goodsdex-data-publication` 同一把锁，从最新 data 分支仅更新状态文件及其 manifest 描述，不修改 goods、商品统计或 `generated_at` 的原有含义。普通发布也会刷新此状态。

四条采集线：最新运行查询 `actions/workflows/<file>/runs?per_page=1`；最近成功独立查询同 endpoint 加 `status=success`，使用 GitHub `updated_at`（run 完成更新时间）作为 `lastSuccessAt`。最近尝试使用 `run_started_at`。失败时优先逐失败 job 查日志第一条 `##[error]`，再回退失败注解；错误最长 200 字且脱敏。API 不可用或缺 token 均明确 unknown。

`publish-release` 是复用 workflow，自己的 runs endpoint 返回空。此时从仓库 runs 的 `referenced_workflows` 定位调用方，取实际 `publish / publish` job，排除采集失败导致的 skipped 发布。其 `lastAttemptAt` / `lastSuccessAt` 分别使用该 job 的 `started_at` / `completed_at`；允许只记录最近一次，未完成/失败时不填历史成功，也不设置固定周期或 stale。

stale 严格采用 `now - lastSuccessAt > interval * 2`；没有可确认成功的采集线也标 stale 并说明原因。汽车每日一次，其他三条每 60 分钟。固定时间单测结果见 `stale-test.json`。

凭证仅从环境读取，下载签名日志 URL 不转发 GitHub Authorization。所有复用调用方已授予 actions:read、checks:read，采集 job 原有 contents:read 权限保持。

本地示例：`python3 scripts/generate_sources_status.py --public /tmp/sources-status --repository null-object-0000/goodsdex`。不设置 GITHUB_TOKEN 时，五项均为 unknown，error 为“缺少 GITHUB_TOKEN”。

## 线上验收过程

- 代码提交：`3ffc89c59ac23adad81c567feff9e21f97463408`。
- 完整离线测试：基线 474 passed / 8 deselected；修改后 491 passed / 8 deselected。线上 tests run `41650759210` 同样 491 passed / 8 deselected；没有新增失败测试。
- 独立状态 workflow `41650792200` 成功，首次发布已核实 HTTP 200，data/OSS/meta.files SHA256 三方一致。
- 为额外覆盖普通发布入口，手动运行 refresh-prices。首次 run `41650786852` 与恰好已在执行的定时 prices 候选重叠，被现有 `data/prices/latest.json.fetched_at` 并发门禁拒绝；尚未运行测试或新增状态生成步骤。
- 重新采集的 run `41652101033` 第一次发布尝试遇 GitHub ArtifactService/ListArtifacts 超时，actions/download-artifact 自动重试五次仍失败，同样尚未运行新增逻辑；只重跑该 run 的失败发布 job。
- 并行的旧代码 HP run `41650568393` 采集失败，真实状态应如实呈现；未修改 HP 采集器或绕过门禁。

## 最终结果

- 普通采集 + 统一发布：[41652101033](https://github.com/null-object-0000/goodsdex/actions/runs/41652101033)，重跑失败 job 后成功；发布门禁 198 passed。状态生成、finalize 收录及 OSS alias 回读证据见 `normal-publish-excerpt.log`。
- 最后一轮独立巡检：[41653377310](https://github.com/null-object-0000/goodsdex/actions/runs/41653377310)，成功；快照生成于 `2026-11-03T14:25:38Z`。
- data 提交：`c5edd060914b2f4ebb0bd970d015c8a3a1303b68`。实际确认该状态提交仅修改状态文件及 meta 中它的描述，其他 meta 字段和所有商品描述符完全相同。
- `curl https://spend-good.oss-cn-shanghai.aliyuncs.com/data/public/sources-status.json`：HTTP **200**。
- data 文件 / OSS 文件 / meta.files SHA256 均为 `f8cf8fe369ebb60a0688b2df8ca88ccb7d8b29300a34677b64c2b362d568cfdd`。
- 五条记录的 GitHub 成功时间逐一核对一致。`github-run-comparison.json` 记录最近尝试 run、最近成功 run，发布另记实际 job id `125975817195`。完整发布 JSON 见 `sources-status.json`，OSS 回读原文见 `oss-sources-status.json`，自动核对脚本为 `verify.py`，汇总为 `verification.json`。
- 真实异常：HP 最新采集失败；汽车最新采集失败且已 87.0 小时无成功运行，stale=true。均如实发布，未将失败改为成功。
