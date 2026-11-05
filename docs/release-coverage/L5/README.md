# L5 验收记录 · 2026-11-05

本次未达到覆盖目标，不能标记全项验收通过。小米 228/1624（目标800）、惠普112/791（目标300）、亚朵星球0/267（目标100）、大疆100/281（目标200）。

- 需求所述本地 L1–L4 基线：981/3682，day33/month948。
- 本轮实时线上快照：980/3682，全部month，SHA256记录于日报。二者不混为同一发布版本。
- 重放 L1–L5 后：1033/3682（28.06%），day33/month1000；L5 对已准备的 L1–L4 基线净增52。
- L5实际接受64发布行：小米61、大疆3，全部month。含12个已有系列日期转为精确产品证据；不能把64称为净新增。
- 没有第三方覆盖官方已有日期。官方、第三方、系列继承互斥计数为779/80/174（第三方80含旧管线16条）。
- 本轮合格精确型号证据无 >45天冲突；`conflicts.json`为空。测试覆盖真实日历45/46天边界与月份区间存疑。
- `samples-15.json`保存15条可核型号、日期、URL、原文、配置片段和精度理由；`hits.json`为完整命中清单。
- `research-rejections.json`保存惠普、亚朵代表性拒绝原文。惠普报道未精确对应当前CPU/内存/容量/货号；亚朵“近期推出”不确定月份，且缺SKU颜色、尺寸、套装。其余未审核型号仍留空，未声称外部报道已穷尽。
- `dashboard-sources.png` / `dashboard-1600.png` / `dashboard-390.png`是修改后的真实后台代码、本地验收服务器、完整3682行候选快照截图；不是线上截图。配套响应为`dashboard-catalog.json`。
- 已安装独立L5 cron：北京时间03:47，沿用flock；`GOODSDEX_RELEASE_LANE=L5`。任务刷新已审核来源，新的IT之家RSS标题写入待审队列。没有把待审发现自动当日期。
- HTTP正文GZIP与原始字节哈希在`data/third-party/l5-captures/`；抓取起点日志与最小间隔验证见`requests.jsonl`、`throttle-verification.json`。

执行：`PYTHONPATH=src:scripts python3 scripts/release_dates_run.py --lane L5`；离线重放用`--goods docs/release-coverage/L5/before.json.gz --no-live`。

现有商品`release`是对象，日期写在`release.date`；保留兼容契约，同时增加`release_precision/release_source/release_evidence/release_quote/release_confidence`。L5原文只能到月；day分支要求明确的月日及发布/开售句、准确型号和非未来事件。报告内的33条day均是既有L3官方证据。
