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

## 发布结果

- 功能提交：`e0c3efd6e190e3580f82bab633c4f0bd54c1c29d`。
- 发布 run：[41854260927](https://github.com/null-object-0000/goodsdex/actions/runs/41854260927)，成功，data + OSS 回读校验通过。
- data 提交：`927e1972f1b9266b3347f6afef7b560eb292f730`。
- 测试 run：[41854254185](https://github.com/null-object-0000/goodsdex/actions/runs/41854254185)，成功。本地完整离线回归 `771 passed, 8 deselected`，与基线相比无新增失败。
- 既有服务端同步器返回 `ok=true, succeeded=9, errors=[]`；见 `api-sync.log`。
- data/OSS/API revision：`f219f71dfcb04aebbf7073c09b004a4f`。
- 线上完整 2856 行商品与 data 逐值相同，OSS `goods.json` 与 data 字节相同；除了三个属性字段，其余商品字段与发布前逐值相同。
- 实际带 attrs **665 行**；冲突 id 对应的 **2 行均无属性**（人工清单仍只有 **1 个 id**）。
- 标注按品牌：Apple 514、大疆 86、惠普 25、小米 40。

线上 `meta.variant_attrs`：

```json
{
  "groups": 98,
  "members_tagged": 665,
  "by_kind": {
    "capacity": 31,
    "version": 34,
    "color": 5,
    "duplicate": 1,
    "bundle": 23,
    "unknown": 4
  },
  "source": "variant-attributes-20261104"
}
```

三个真实 `/api/goods/<id>` 返回片段（逐条与全量发布数据对比一致）：

```json
[
  {
    "id": "CN:mi_cn:product:10050230",
    "name": "米家高速水离子吹风机 Pro",
    "attrs": {
      "name": "米家高速水离子吹风机 Pro 单机 浅月白",
      "color": "浅月白",
      "variant": "单机"
    },
    "attrs_source": "variant-attributes-20261104",
    "attrs_confidence": "medium"
  },
  {
    "id": "CN:mi_cn:product:24248",
    "name": "米家高速水离子吹风机Pro",
    "attrs": {
      "name": "米家高速水离子吹风机 Pro 薄暮金",
      "color": "薄暮金"
    },
    "attrs_source": "variant-attributes-20261104",
    "attrs_confidence": "medium"
  },
  {
    "id": "CN:apple_cn:commodity:MD3Y4CH/A",
    "name": "iPad",
    "attrs": {
      "name": "iPad Wi-Fi 128GB - Silver",
      "color": "银色",
      "capacity": "128GB",
      "connectivity": "Wi‑Fi",
      "model": "iPad"
    },
    "attrs_source": "variant-attributes-20261104",
    "attrs_confidence": "high"
  }
]
```

完整校验结果见 [online-verification.json](online-verification.json)，独立人工清单见 [manual-review.md](manual-review.md)。
