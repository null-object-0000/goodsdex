# 确认下架留档

调用链：`crawl-all.yml` 在 Rebuild 前执行 `scripts/confirm_delisted.py` →
`publish.collect_public()` 用与发布一致的投影读取本轮分类 → 与上一版
`_data/public/goods.json` 比较 → `delisted.confirm_delisted()` 探测缺失 ID，
同时重新探测上次已确认下架的商品 → 写 `data/archive/_delisted.json`。

`ci_publish_archive.py` 原样复制该文件到 `_data/public/archive/`；
`goodsdex.publish.build()` → `supplements.publish()` → `delisted.apply_archive()`
补回最后完整发布行、设置 `on_sale:false`、`delisted_at`、`delisted_evidence` →
原有 `supplements.merge()` / `assert_no_lost_ids()`。
门禁及人工删除名单未改，商品始终在 current 中。archive 会随现有采集候选和
产物一起保留，供下轮恢复。既有 supplements 文件和 release/params 规则未改。

默认 urllib fetcher 使用 10 秒请求超时；最多四个并发，每次失败重试一次。
HTTP 错误、异常、超时和其他业务响应只写 unknown，不产生下架状态。
已确认下架商品后续探测失败时保留已有状态；没有历史下架证据的缺失项仍由原门禁检查。

恢复要求：本轮有完整采集行且再次探测 `code:0`，然后清除 `delisted_*`，
置 `on_sale:true`，报告 revived，并清除旧退休状态（保留退休历史）。
恢复事件只用于本轮，避免旧恢复证据覆盖后续网络失败或新的缺失。
成功的移动端采集也会在公开投影中带 `on_sale:true`。

每轮输出 `docs/delisted-<YYYY-MM-DD>/report.json`，含 confirmed / unknown /
revived 的逐项证据或原因及数量，并由 workflow 上传独立审计 artifact。
本目录 report.json 是对用户列出的五个 ID 直接调用真实接口的结果：全部返回
`400480502 / 该产品已下架`。本地没有本轮完整 categories 和发布基线，因此未运行
完整真实数据集重建；保留及门禁通过下述集成测试验证。

验证命令（环境需安装 pytest）：

```sh
PYTHONPATH=src:scripts python3 -m pytest -q \
  tests/test_delisted_carry.py tests/test_supplement_publish.py \
  tests/test_release_policy.py tests/test_publish.py tests/test_archive.py \
  tests/test_archive_coverage.py tests/test_retirement.py \
  tests/test_release_candidate.py tests/test_dedupe.py
```

结果：99 passed，4 subtests passed。覆盖下架、在售、超时、500、429、
失败后重试成功、并发上限、HTTP 错误、完整行留档、恢复与再次失败，
以及 archive 复制至真实 build/publish 的链路。
五个下架 ID 保留后通过原门禁；额外伪造的在售缺失 ID 仍触发原门禁。
