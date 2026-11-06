# sources + display 接手记录

## 上一次成果

接手先执行 git status 与 git diff --stat。工作区并非只有本任务：保留的图片、HP 配置、百科和各轮审计文件未作删除或混入发布。

先保存来源断言解析器与测试为 4dc05eb8；发布链路所依赖的既有官方名称、有品、L7 成果另保存为 24909112。

随后发现另一个同仓工作树 goodsdex-product-sources 已有商品来源策略 f7a4e3ba、测试修复 2c5d23ee，配套 API 工作树 spend-good-product-sources 已有来源列表、详情和后台统计（3b7b9d9、4993624）。这些属于上一次已有成果，不计作本次新写。

## 本次补充

- 4c34efba：独立 lineage 原型的唯一 primary、升级历史及统计测试。该原型中的 legacy_snapshot 仅供历史值审计；正式商品来源策略使用 product_sources 的证据门禁。
- 1586b4e7：将既有商品策略、迁移与回滚工具、发布专用入口整合进当前工作区；停止将日期 lineage 直接应用为商品主源策略。
- 当前工作区全量验证：971 passed，见 workspace-tests.log。
- 4468 条真实商品预演：旧字段零删除，1971 条无价商品全部保留。五条完整 sources/display 样本见 samples.json，含 mihome:23498。
- primary 分布与 1/2/3+ 源分布见 statistics.json；3949 条仅有主源，519 条双源。

远端主分支已推进至 733b11cf（包含更完整的 lineage 与来源整合），因此没有将本地旧分支强推覆盖远端。在 /tmp/goodsdex-source-integration 隔离工作树基于远端继续发布修复。

上次迁移 run 42149687990 失败于 price_comparable 与 display 价格不一致。本次 16c77402 在 display 镜像完成后重算可比性；新增测试覆盖有价及显式清价，30 条相关测试通过，4468 条真实迁移全部通过价格与唯一主源校验。

迁移和字节级回滚说明见 migration-and-rollback.md。正式发布状态在后续记录中更新。

## 发布存储限制修复

42153459630 已通过全部 finalize 校验，但 GitHub 拒绝 275.89 MB 的 goods.json，未推送 data。be238875 改为 Git 中保存无损 goods.json.gz（真实数据 21 MB），所有 data checkout 入口先还原原始字节，OSS 和 API 继续读取原 goods.json。完整 sources、display、field_history 不删减。其余真实产物最大 19 MB。全量测试最终 1102 passed，另 API product-sources 两条回归均通过。
