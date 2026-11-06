# 周期采集验收记录

GitHub cron 使用 UTC；`schedules.log` 逐条列出表达式，北京时间每天 03:52 / 03:58 / 04:22 / 04:34 / 04:46；缺口发现为周日 04:10。发布日期主流程仍是 03:17，L6 已有实时采集；L7 当前只重新核验已审核捕获，尚未自动生成新提案。

注册表以 main 的定义为准、data 的运行状态为持久值。`sources-status` 每 15 分钟以及各采集 workflow 完成后读取 Actions API；失败源也写回，且独立持发布锁，不依赖采集成功。候选采集上传 metrics，发布 finalizer 后重新计算实际新增的唯一 ID、日期比例和明细。历史 run 没有 metrics artifact 时数量仍为初始值，不能当作历史采集数量证明。

Hermes profile spendpoint job `388f56ad0b3a`，每小时 `:07`；脚本路径 `~/.hermes/profiles/spendpoint/scripts/source_watchdog.sh`，本地锁 + dispatch lease + Actions 活跃任务检查。`watchdog.log` 是实测补跑日志，已触发四个真实 workflow。主调度和兜底均长期保留。

`two-failures.fixture.json` 与 `failure-and-additions.fixture.png` 是显式测试数据，仅用于本地隔离 API；没有污染商品库。测试验证最近两次失败标红，下一次成功时清零并恢复。实际错误恢复：修复该源后重新运行对应 workflow；状态流程会自动解除告警。页面截图 `sources-1440.png`、`sources-390.png` 为本地真实 API + 构建后后台，非线上部署证明。

目录刷新现在只对新型号做进一步核验：米家 A 类整机必须经百科型号和 pdId 二次核对；耳机必须有稳定型号和验证过的官方大图，均经既有 append-only intake 门禁。不确定身份留审核队列。商品图每日最多处理 100 个缺图商品，要求官方 API 产品名完全一致、唯一图片及尺寸验证，通过来源观察进入字段选择策略。L7 新提案仍受本机网关可达性限制；Actions 当前只重核已审核捕获。后台部署与本轮发布回执见后续 run 记录。

验证：集成最新主分支后 Python 1119 passed；后台类型检查、构建成功；后台 10 tests passed；API 针对性检查 58 passed、2 skipped。
