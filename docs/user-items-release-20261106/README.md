# 用户录入的 12 件物品：发布日期定向补证

本地完成：12 件可展示 **4 → 11**。原来 7 条空白补入 6 条日期，H501 保持 2023-05 并补成双源（展示事件改为发布）；空调伴侣 2 仍空、未验证。同品类仅新增 **2** 条原空缺（BE6500 Pro、小爱音箱 Play）。合计新增 8 条日期、补证更新 1 条，共新增 9 个可展示单品。

依据：**official 1 条**（富士套机美国公布月份），**third_party 双原始来源 8 条**（用户 6 件 + 同类 2 件）。所有第三方均交由现有 `third_party_release.assess` 判定；同事件、不同媒体原始域、不同正文哈希，均 corroborated / delta_days=0。没有用 LLM 作第二来源。

**日期事件不可混读**：富士 2024-05 是美国官方公告单独列出的 X-S20 + XF16–50 完整套机公布月份，显示“美国推出月份（官方回溯）”，不是国行首销；公告中预计 2024-06 上市没有当作实际首销写入。音箱 Pro、H501 也是 announcement，其余本轮新增为 availability。沿用仓库 event/market 定义及既有门禁。

| # | 物品 | 之前 | 之后 | 依据 / 事件 |
|---|---|---|---|---|
| 1 | [米家智能宠物饮水机 2](items/01-20833.md) | 空 | 2024-12 | 双源 / availability |
| 2 | [小米无线键鼠套装 舒适版](items/02-21630.md) | 2025-07 | 2025-07 | 沿用发布集 |
| 3 | [FUJIFILM X-S20 16-50套机](items/03-x-s20-16-50mm.md) | 空 | 2024-05 | official / 美国 announcement |
| 4 | [米家空调伴侣2](items/04-9726.md) | 空 | 空（未验证） | 未验证 |
| 5 | [米家空气净化器 4 Lite](items/05-15061.md) | 2021-10 | 2021-10 | 沿用发布集 |
| 6 | [小米中枢网关](items/06-15755.md) | 2022-03 | 2022-03 | 沿用发布集 |
| 7 | [米家智能微波炉P1](items/07-20545.md) | 2024-10 | 2024-10 | 沿用发布集 |
| 8 | [米家智能变频除湿机 30L](items/08-20807.md) | 空 | 2024-12 | 双源 / availability |
| 9 | [米家高速吹风机 H501](items/09-18520.md) | 2023-05（不可展示） | 2023-05（补证解锁） | 双源 / announcement |
| 10 | [Xiaomi 智能音箱 Pro](items/10-20981.md) | 空 | 2025-02 | 双源 / announcement |
| 11 | [小米智能门锁 2](items/11-19409.md) | 空 | 2023-11 | 双源 / availability |
| 12 | [Xiaomi路由器 BE6500](items/12-20276.md) | 空 | 2024-08 | 双源 / availability |

## 同品类扩展与边界

| id | 商品 | 新增日期 | 依据 |
|---|---|---|---|
| `CN:mi_cn:product:19332` | Xiaomi路由器 BE6500 Pro | 2023-10 / availability | third_party 双源 |
| `CN:mi_cn:product:10015` | 小米小爱音箱 Play | 2019-06 / availability | third_party 双源 |

两条扩展的每个 URL、原句、抓取时间和 SHA256 见 [新增双源清单](new-media-candidates.json)。BE6500 Pro 采用其自己 2023-10-31 开卖证据，与用户的 BE6500（2024-08-16 开卖）分别核实；Play 不与增强版 / Redmi Play 合并。

扩展官方探测范围限定宠物饮水机、路由器、智能门锁、小爱音箱、除湿机、智能家庭/插座的当前空缺，加上 12 件中的小米条目，共 77 个精确产品。完整 [范围](official-scope.json)、[官网探测](official-probes.json)、[带 gid 重试](official-gid-probes.json) 均落盘；未扩展相机同类或其他全库品类。

未进入生产数据的发现：米家智能除湿机 22L 有 2021-10 众筹发布、2021-12 再次“推出/预售”的报道，未贸然统一事件；13L 只抓到单一媒体明确首销与另一家预售，未混事件凑双源。智能插座基础版未找到满足规则的原始日期双源。饮水机 2 除菌版在当前发布快照已可展示，未覆盖原数据或计新增。其余类别探测未取到日期的不编值；这不表示全互联网均无资料。

## 落地与验证

主输入：`data/official/release-dates.json` 新增 8 条候选、替换 H501 1 条（保存旧候选）；依照已有链路，同时在 `data/third-party/release-dates.json` 新增 8 组双源断言。只写主输入无法通过既有第三方门禁，因此必须保留这份 sidecar。没有新增导入逻辑，没有改发布门禁、release_policy、允许来源或判定阈值。

冻结基线：代码 `5b6dddc7`；已在本地的 data 分支快照 `2cd5f4173b420a8c51b674a293313f544233f4e7:public/goods.json.gz`，4491 行。本轮未 fetch / push、未开 PR、未触发 workflow、未部署；主仓未写入。

[本地验收结果](verification.json)：实际 `finalize_public` + `build_shards` 生成 4491 行；9 个本轮条目的 release 与详情分片一致，原 4 件可展示值完整不变。输入重放幂等，相对旧代码输入恰好 9 个 release 变化，非 release 字段不变。此为本地生成验收，不声称已上线。

测试命令：
```bash
PYTHONPATH=src:scripts /var/tmp/user-items-release-venv/bin/python -m pytest -q tests/test_release_dates.py tests/test_release_crosschecks.py tests/test_release_scope_media.py tests/test_official_retrospective_release.py tests/test_release_candidate.py tests/test_release_policy.py tests/test_dedupe.py tests/test_shards.py tests/test_date_enrichment.py tests/test_series_release.py tests/test_series_release_rollout.py tests/test_release_precision.py tests/test_product_sources.py tests/test_lineage.py
```

结果：`162 passed in 49.43s`（[原始日志](tests.log)）。原始工具文本改为 gzip 留档以完整保留空白字节后，针对证据格式再次验证：`22 passed in 1.98s`（[日志](capture-format-tests.log)）。3 个测试文件只更新新增证据的固定期望、留档路径与旧证据保留断言；没有放宽生产规则。

复算：`PYTHONPATH=src:scripts python docs/user-items-release-20261106/verify.py`；需要已存在的上述冻结 data git 对象。`capture.py` / 采集脚本另需 beautifulsoup4，产品运行时无新依赖。

## 提交状态

提交后实际执行的 `git log --oneline -2` 与 `git status --porcelain` 原文见最终交付消息，避免在同一提交内伪造自引用 commit hash。
