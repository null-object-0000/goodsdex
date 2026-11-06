# 采集线持续失败修复与验收记录（2026-11-06）

## 1. 修复范围与根因

### A. `mi_store` → `.github/workflows/refresh-prices.yml`
- **现象**：06:07Z / 07:01Z / 08:07Z / 09:07Z 连续 4 次运行 `conclusion: cancelled`（上次成功为 05:07Z），导致 `publish` job 被 `skipped`，小米/大疆/富士每小时价格回灌中断。
- **根因**：`collect` job 内四步（`checkout` / `collect-base` / `Refresh prices` / `upload-candidate`）全部 `success`，但总耗时在 `3m05s ~ 3m13s` 之间，触发了 `.github/workflows/refresh-prices.yml` 中 `collect.timeout-minutes: 3` 的 job 级硬超时（此前成功运行实测耗时 `2m22s ~ 2m50s`）。
- **修复**：将 `.github/workflows/refresh-prices.yml` 中 `collect.timeout-minutes` 从 `3` 调至 `8`（约为正常耗时 `2m50s` 的 `2.8` 倍）。
- **同类工作流排查（仅报告、未修改无关文件）**：
  - `.github/workflows/refresh-hp.yml` 存在完全相同的「贴着实测耗时」风险：`collect.timeout-minutes: 15`（步骤 `hp.timeout-minutes: 13`），实测成功耗时 `10m42s ~ 13m39s`，且在 `2026-11-06T05:07:38Z`（run `42166532317`）已发生过 `15m20s` 超时 `cancelled`、`publish` 被 `skipped` 的同型故障。

### B. `all_catalogs` → `.github/workflows/crawl-all.yml`
- **影响面**：
  - **整个商品库并未停更**：其他发布工作流（`refresh-mihome-catalog`、`refresh-earbuds`、`refresh-images`、`release-dates-daily` 等）当日均正常产出并发布到 `data` 分支。
  - **实际受损范围**：仅 `crawl-all.yml`（每日 UTC 19:37 全量类目发现，单次耗时 60~70 分钟）在 `Rebuild public dataset`（`python3 -m goodsdex.publish --cats data/categories --out _data/public`）阶段因 `assert_no_lost_ids` 报错 `ValueError: Publication would drop 364 IDs` 而整趟丢弃，自 2026-10-27 起连续 10 天未能将全量类目发现结果合入 `data` 分支。
- **方案选择（选路径 (a)：固化进受版本管理的 `data/supplements/goods-supplements.json`）**：
  - **为什么不选 (c)**：`apple_cn`（16 条）与 `mi_cn`（4 条）本身属于 `crawl-all.yml` 重建覆盖的 source；若修改 `merge()` 对这些 source 做无条件整类结转，会实质性削弱 `assert_no_lost_ids` 对 `apple_cn` / `mi_cn` 真实掉数的门禁保护。
  - **为什么选 (a) 而非另起文件 (b)**：`data/supplements/goods-supplements.json`（`DEFAULT_SUPPLEMENTS`）已是主干受版本管理的标准补充集入口，被 `goodsdex.publish`、`ci_refresh_prices.py`、`verify_goods_release.py` 和 `supplements.merge()` 统一消费；在 `merge()` 中，`rebuilt` 优先级高于 `supplements`（一旦主干合入大疆/富士采集器或重新抓到某条商品，自动以 `rebuilt` 最新结果为准并打印 `supplement conflict (keep rebuilt)`），不会覆盖新鲜采集数据。
- **364 条记录的 `source` 与 `catalog_identity` 依据**：
  1. `CN:dji:sku:*`（281 条）：线上发布集已具备 `source: "dji_mall_json"`、`catalog_identity: "dji_mall_json"`，原样保留。
  2. `CN:fuji:*`（63 条，含 39 `lens` / 13 `kit` / 11 `model`）：线上发布集已具备 `source: "fuji"` 及 `catalog_identity`（`"fuji:camera-schema-v2:20261027"` 52 条、`"fuji:kit-restoration:20261027"` 11 条），原样保留。
  3. `CN:apple_cn:commodity:*`（16 条）：线上发布集已有 `source: "apple_cn"`、`product_id`、`variant_id`、`part_number`、`source_url`，且全部归档于 `data` 分支 `public/archive/Apple_mac.json`（因该批次 `discovery.completeness == "partial"`、`stop_reason == "scope_limited"`，未被 `retirement.archive_observations` 标为 `missing_since`）。据此补齐 `catalog_identity: "goods_supplements:apple_cn:archive_Apple_mac"`。
  4. `CN:mi_cn:product:*`（4 条：`18472`、`20155`、`20895`、`23692`）：在 `data` 分支 `data/categories/家电.json`（及 `牙刷.json`）和 `public/archive/家电.json`（`last_seen_at: 2026-10-27`，`completeness: "partial"`，`stop_reason: "no_sellable_items"`）中均有原始抓取记录，原始 `product.source` 为 `"mi_cn"`（`to_public()` 未将其透传到顶层）。据此补齐 `source: "mi_cn"`、`catalog_identity: "goods_supplements:mi_cn:archive_20261027"`。

---

## 2. 真实 `data` 分支发布集验收证据

使用 `gh api repos/null-object-0000/goodsdex/contents/public/goods.json.gz?ref=data -H 'Accept: application/vnd.github.raw' > /tmp/goods.json.gz` 获取线上真实发布集（4,491 条记录，4,486 个唯一 ID），执行两阶段验证（完整统计见同目录 [`verification-summary.json`](./verification-summary.json)）：

### 阶段 1：`crawl-all.yml` 原失败命令 `python3 -m goodsdex.publish --cats data/categories --out _data/public`
- `previous_count`: `4491`
- `rebuilt_count`: `5661`
- `added_count`: `1465`
- `pre_finalize_total_rows` (`count`): `7126`（唯一 ID 数 `5188`）
- `missing_ids`: `[]`（0 条丢失，门禁通过）
- **364 个缺口 ID 保留数**：`364 / 364`（0 丢失）
- **`7,126`（重建合并初稿）与 `4,491`（线上发布集）的差值精确拆解**：
  1. `data/categories/*.json` 中同一商品跨多个类目文件重复出现：`7,126 - 5,188 = 1,938` 条跨类目重复行（在 `finalize_public()` 的 `dedupe_rows` 阶段合并为单条记录的 `categories: [...]` 数组，仅对 `PROTECTED_IDS` 保留 5 条多行记录）。
  2. `data/categories/*.json` 与补充集中包含配件/服务/服饰记录：`5,188 - 4,486 = 702` 个唯一 ID（其中 `goods-supplements.json` 历史配件 96 个），在发布流水线 `finalize_public()` 阶段被归档至 `public/archive/*.json` 与 `public/goods-excluded.json`。
  3. 归档与去重后：`4,486` 个非配件唯一 ID + `5` 条受保护多类目行 = **`4,491` 条**。

### 阶段 2：端到端「重建（模拟丢弃全部 364 个 ID）+ 合并 + `verify_goods_release.py` 门禁 + `finalize_public()`」
- 输入 `previous`：`4,491` 条（`4,486` 个唯一 ID）
- 模拟重建 `rebuilt_without_364`：`4,127` 条（剔除全部 364 个缺口 ID）
- 经 `supplements.publish()` 合并后：`4,587` 条（含 364 条恢复记录 + 96 条历史补充集配件，364 个缺口 ID `364 / 364` 全部在列）
- 经 `scripts/verify_goods_release.py` 校验：`PASSED`（退出码 `0`）
- 经 `finalize_public()` 归档去重后：
  - 最终 `public/goods.json` 总行数：**`4,491` 条**（与线上 `4,491` 完全一致，差值为 `0`）
  - 最终唯一 ID 数：**`4,486` 个**
  - 364 个缺口 ID 最终保留数：**`364 / 364`**
  - 配件门禁：`{"excluded_count": 73, "newly_excluded_count": 0, "denominator": 4469, "newly_excluded_ratio": 0.0, "threshold": 0.05, "gate": "green"}`

---

## 3. 本机测试结果原文

- 定向测试：
  ```text
  $ PYTHONPATH=src:scripts python3 -m pytest -q tests/ -x -k "supplement or publish or release or registry"
  ........................................................................ [ 25%]
  ........................................................................ [ 51%]
  ........................................................................ [ 77%]
  ..............................................................           [100%]
  278 passed, 843 deselected in 39.10s
  ```
- 全量测试：
  ```text
  $ PYTHONPATH=src:scripts python3 -m pytest -q
  ........................................................................ [  6%]
  ...
  .........................................                                [100%]
  1121 passed in 87.71s (0:01:27)
  ```

