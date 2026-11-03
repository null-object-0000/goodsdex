# 发布字段接线修复

公开字段统一为 `release_series`，旧 `series_release` 在每次 finalize 时清理；审核输入 `data/official/series-releases.json` 保留原有格式和证据，不重新推断日期。其 81 批、149 个商品 ID 与 `docs/series-release-rollout-20261103/batches.json` 逐项对照由回归测试验证。

`inherited` 表示该记录无单品级 `release.date`。有单品日期时为 false，两字段并存。系列日期始终保留 `level: series`、月粒度、证据、市场、批次及“系列推出时间”口径，不写入 `release`。

共享发布入口的 `scripts/finalize_public.py` → `goodsdex.dedupe.finalize_public` 每次应用审核成员映射，再生成完整详情分片、manifest 和数据文件。新增集成测试实际调用该入口，验证 149 个成员、全部原 release 对象不变及采集器清掉系列字段后的重放恢复。meta.release_series 单独统计全部系列断言及批次，避免与单品日期覆盖率混用。

API 位于相邻 `spend-good/services/api` 仓库。其现有 hydrate 保留完整详情字段，因此无需部署代码即可透出新字段；添加同步→惰性详情及批量详情测试。分页及分组搜索列表不携带系列证据，避免每页重复证据文本；原始 `/api/goods` 导出仍包含。API 契约测试提交：`7c05a56`，278 项通过。

发布与线上实际验收见本目录 publication.json、verification.json 和 samples.md；旧 rollout 目录是历史记录，不作为本次验收依据。

## 实际发布与验收

实现提交 `b692521981fdf074d3b60f5a3f50326be6e91747`；[正常发布任务](https://github.com/null-object-0000/goodsdex/actions/runs/41634939063)成功，门禁 172 项通过，data 提交 `5fb0db91fba72dc9aac76165abf2e78155780c76`，OSS 所有分片、goods、manifest 读回校验成功。

2026-11-03 20:24:50（北京时间）完成真实线上核对：2909 条商品，release 非空 671→671，release_series 非空 0→149，共 81 批；101 条 inherited=true，48 条与原单品日期并存。发布前基线实际上已有旧拼写 series_release 149 条，本次统一迁移至明确要求的字段名，旧字段全部清理。所有单品 release 对象及其余商品字段逐值不变。

OSS goods 与 data 逐字节一致；线上完整目录与 data 逐值一致，meta 商品 SHA256 一致。首次请求仍为旧代，随后调用现有 createSync().primeCatalog() 完成同步，返回 ok=true/count=2909；未替换服务端代码或手写线上数据。[五条真实详情及并存反例](samples.md)、[149 个逐条成员及核验结果](verification.json)、[同步结果](api-sync.log)均保留。

基线离线 464 通过；最终离线 465 通过，8 项 live 未选中；[云端离线测试](https://github.com/null-object-0000/goodsdex/actions/runs/41634936267)成功；API 全量 278 项通过。

复验命令（将基线和发布快照先解压至对应路径）：

```bash
python3 docs/release-series-wiring-20261103/verify_publication.py --before /tmp/goods-series-before.json --published /tmp/goods-series-published.json --data-commit 5fb0db91fba72dc9aac76165abf2e78155780c76
```

发布商品 SHA256：`fb541b9affd35a8f6090ffe33217237e28b78167e43e3f84af59e21230c2ff1a`。
