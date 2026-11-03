# Actions 采集线状态验收

实现：`scripts/generate_sources_status.py`。统一发布在 finalize 前生成 `sources-status.json`；finalize 将它的 sha256/bytes/count 写入 `meta.files`；OSS 通过该 manifest 同时镜像不可变 blob 和公开 alias，meta 最后上传并回读验证。

另有 `sources-status.yml` 每 15 分钟巡检，不依赖采集成功，持 `goodsdex-data-publication` 同一把锁，从最新 data 分支仅更新状态文件及其 manifest 描述，不修改 goods、商品统计或 `generated_at` 的原有含义。普通发布也会刷新此状态。

四条采集线：最新运行查询 `actions/workflows/<file>/runs?per_page=1`；最近成功独立查询同 endpoint 加 `status=success`，使用 GitHub `updated_at`（run 完成更新时间）作为 `lastSuccessAt`。最近尝试使用 `run_started_at`。失败时优先逐失败 job 查日志第一条 `##[error]`，再回退失败注解；错误最长 200 字且脱敏。API 不可用或缺 token 均明确 unknown。

`publish-release` 是复用 workflow，自己的 runs endpoint 返回空。此时从仓库 runs 的 `referenced_workflows` 定位调用方，取实际 `publish / publish` job，排除采集失败导致的 skipped 发布。其 `lastAttemptAt` / `lastSuccessAt` 分别使用该 job 的 `started_at` / `completed_at`；允许只记录最近一次，未完成/失败时不填历史成功，也不设置固定周期或 stale。

stale 严格采用 `now - lastSuccessAt > interval * 2`；没有可确认成功的采集线也标 stale 并说明原因。汽车每日一次，其他三条每 60 分钟。固定时间单测结果见 `stale-test.json`。

凭证仅从环境读取，下载签名日志 URL 不转发 GitHub Authorization。所有复用调用方已授予 actions:read、checks:read，采集 job 原有 contents:read 权限保持。

本地示例：`python3 scripts/generate_sources_status.py --public /tmp/sources-status --repository null-object-0000/goodsdex`。不设置 GITHUB_TOKEN 时，五项均为 unknown，error 为“缺少 GITHUB_TOKEN”。
