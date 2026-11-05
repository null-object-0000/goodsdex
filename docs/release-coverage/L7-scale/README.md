# L7 放大跑审核与复现

本目录对应代码提交 `0b565bd1`。最终计数以 `publication.json`、`summary.json` 和线上复算为准。

- `baseline.json.gz`：投递前 data 分支 3,682 行原始快照；`prior-evidence.json` 保留上一轮36条审核证据。
- `targets.json`：只给模型身份，不给内部已有日期。模型原始输入/响应在 `proposals/`、`grounded/`。
- `discovery.json`：公开新闻标签页抓到的正文，仅用于发现提案；不能直接发布。
- `verification.json`：每个合格唯一候选实际抓取的页面、HTTP状态、正文哈希及初审。
- `ineligible.json`：品牌名、系列名等预检排除；不计送审候选。`abstentions.json` 的空日期/空URL也不计候选。
- `review-decisions.json`：逐条读取原文后作出的显式终审，绑定冻结商品身份哈希。没有审核批准的候选不会入库。
- `captures/`：HTTP原文gzip与请求元数据；`identity/` 是辅助身份检查的原始API响应gzip，不是发布日期证据。
- `audit.json`、`new-entries.json`、`samples.json`：最终判定、入库证据和固定种子12个不同ID样本。
- `after.json.gz`：本地选择器复算结果；`finalized-coverage.json`：实际发布流程重放矩阵。

在仓库根目录离线重放（无模型调用、无网站请求）：

```sh
PYTHONPATH=src:scripts python3 scripts/assemble_release_l7_scale.py
PYTHONPATH=src:scripts python3 -m pytest -q
```

第一条命令验证所有批准条目的正文、哈希、型号、月份、来源和身份指纹，再把132个本轮通过URL与上一轮36条证据合并；同一型号同月的多个URL不会重复提高覆盖率。第二条是全量回归。

`propose_release_l7_scale.py`、`discover_release_l7_scale.py`、`extract_release_l7_scale.py`、`verify_release_l7_scale.py` 是本轮可续跑采集工具，属于在线操作；模型/正文缓存按内容哈希复用，验证程序按已保存顺序追加。网络抓取使用跨进程文件锁和2.15秒请求起点间隔，每50条批间休息5秒。启动阶段节流竞争及修复过程保留在原日志，并未声称启动日志全程严格间隔。

真正发布遵循 `publish-release.yml` 的 merge → publish → verify → finalize → OSS 顺序。`verify_goods_release.py` 是 finalize 之前的门禁；不要在最终移除已审核非商品之后把该门禁单独挪到末尾执行。
