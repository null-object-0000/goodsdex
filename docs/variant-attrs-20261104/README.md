# 属性标注发布（2026-11-04）

采纳已确认决定：冲突 id `CN:mi_cn:product:20425` 整体不标注，其余 665 条写入 `attrs` / `attrs_source` / `attrs_confidence`。不修改商品名称、价格、身份或原始参数。未知结论不猜测。

共享 finalizer 在归档完成后回放已审核输入，因此后续采集、价格更新与发布仍会保留标注。meta 的 `members_tagged` 按最终实际商品行计数；`by_kind` 是 98 个审核组的结论分布，含 4 个 unknown 组，并非商品数量分布。

## 待人工核对

共 1 个 id，两个 SKU：见 [独立清单](manual-review.md) 和 [完整证据](source-conflicts.json)。两份候选属性仍保留在输入的 `withheld_attrs`，不作为可发布属性。

## 本地验证

- `local-invariants.json`：对最新 data 基线完整 finalize，665 条有属性、98 组，其他字段逐值相同，原有冲突行仍保留。
- `tests.log`：完整离线回归；新增真实审核输入计数、冲突排除、冲突保护、finalizer 和 detail shard 回放验证。
- 发布使用现有 `refresh-release-dates.yml` 空候选 → 共享 `publish-release.yml`，同一发布锁内推 data 和校验 OSS。

## 线上验收

发布后用 `verify_publication.py --public <已发布 data/public> --run-id <run>` 核对实际 API、data/OSS manifest、完整商品逐值一致及三个真实详情。结果归档为 `online-verification.json`、`online-meta.json`、`api-samples.json`、`online-goods.json.gz`。
