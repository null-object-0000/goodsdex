# crawl-all source 结转验收

基线 `0ad99988`；真实发布集取自 data 提交
`9d7971f5505c3325f5d616199491ed8342cd7f69` 的 `public/goods.json.gz`，共 4,491 行。

`merge()` 在追加 supplements、结转旧行之前，计算清理已审核删除项后的
rebuilt source 集合。旧行的 source 未被覆盖且 id 不在 rebuilt 中时，整行结转；
同 source 已覆盖时仍交给原来的 `assert_no_lost_ids` 拒绝缺失。
车、HP、Atour 原有的独立发布结转例外继续保留，即使它们的 source 被覆盖。
已审核删除项不会被结转复活。

结转沿用旧 HP/车行为，不另行调用只用于 supplements 的 `validate_row`；
仍经过默认 backfill、原封不动的丢 ID 门禁和空壳门禁。
审计新增去重、排序后的 `carried_ids`、`carried_sources`。
`rebuilt_count` 继续包含结转行，保持 `count = rebuilt_count + added_count` 的既有契约。
364 条 supplements 和 `assert_no_lost_ids` 均未修改。

## 可复现样本

运行：

```sh
PYTHONPATH=src python3 docs/carry-forward-20261106/verify.py
```

脚本用真实发布集构造只覆盖 `apple_cn`、`apple_support`、`mi_cn` 的 640 行重建样本，
其余 source 整类未参与重建，再用仓库真实 supplements 合并。
它是 source 范围测试样本，不是 run 42205818126 的原始分类快照。

- 正例：结转 3,846 个唯一 ID，目标 7 条全部结转；丢失 ID **0**，结果 4,587 行。
- 反例：删除已覆盖 `apple_cn` 的 `CN:apple_cn:commodity:MD3Y4CH/A`，
  source 仍被覆盖，门禁报 `Publication would drop 1 IDs`，准确指向该 ID。
- 实际 `carried_sources`：`null`（无 source）、`atour`、`dji_mall_json`、
  `earbuds_directory`、`fuji`、`goods_supplements:xiaomi_mobile_official`、
  `hp_cn`、`mihome`、`pcauto`、`xiaomi_archive_history`、`youpin`。

完整数字见 [acceptance.json](acceptance.json)。

## 无 source 的边界

真实发布集中的目标 7 条全部缺少 `source`。缺失值按 `None` 作为独立分组；
如果 rebuilt 中有任意无 source 行，则该组已覆盖，缺失的无 source ID 仍须报错。
上述正例省略的是整个无 source 分组，不能据此声称这 7 条在任意 crawl-all
输入中都会结转。不同采集线共用无 source 分组时，单靠本次 source 集合规则无法区分。

本地检查同一 data 提交的真实 `data/categories`：转换后 4,450 行，
其中 3,816 行无 source，且目标 7 条已经全部在快照中。
用这份快照直接 `merge`，结果 7,126 行（保留分类重复行），丢失 ID 为 0，
结转 2,576 个唯一 ID；这只能验证当前快照，不能冒充历史失败输入。

## 测试

新增 5 个回归测试，覆盖未覆盖 source 整类结转、已覆盖 source 缺行报错、
车/HP/Atour 既有例外、无 source 分组、已审核删除项不复活。
同时更新独立品牌发布测试，继续禁止全局字段回放，并验证新结转规则和原门禁。

```sh
PYTHONPATH=src python3 -m pytest -q -m 'not live'
```

结果：**1,118 passed，8 deselected，4 subtests passed**。
测试环境依赖与 CI 一致：pytest、Pillow、requests、beautifulsoup4；仅安装在临时 venv。
