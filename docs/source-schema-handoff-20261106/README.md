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

## 发布修复与最新快照

远端整合验证最终为 1100 passed（integration-tests.log）。发布 run 42152318633 的价格门禁已通过，但暴露出 schema-only 迁移重审有品历史排除记录的问题，未推送 data。61f3397a 修复迁移范围隔离：保留既有排除决定及归档，仅更新发布 revision/时间及其一致性元数据。

使用该失败 run 的完整回滚 artifact 在本地重放 finalize，成功且价格历史新增为 0（live-finalizer-replay.log）。最新快照 4467 行，ID 和旧字段无丢失，primary 唯一；与前述 4468 行审计快照时间不同，请以 live-snapshot-acceptance.json 为准。名称不变，图片变化 24 行、类目 406 行、价格 10 行；旧断言保留在 sources.observations，display 按远端已存在的证据规则派生，1971 条原无价商品全部仍在。源分布 2533 单源、1525 双源、409 三源及以上。

本次重新发布代码提交为 6bb806ff，重试 run 42153459630。主分支部署修复在 /tmp/goodsdex-source-integration 隔离工作树完成；当前工作区的接手检查点未强推覆盖已推进的远端历史。

42153459630 随后因 GitHub 100 MB 限制拒绝 goods.json（275.89 MB），未推送 data。be238875 将 Git 存储改为无损 goods.json.gz（21 MB），各 checkout 入口自动还原原始字节，OSS/API 原 JSON 契约不变，完整来源/外显/历史均保留。全量测试 1102 passed。最新发布代码 fb04a067，run 42154701910；启动时等待其他品牌发布持有的共享锁。

## 最终发布成功

run **42154701910**：prepare 与 publish 全部 success，含 data 推送、OSS 镜像与校验。发布代码 fb04a067；回执见 publication.json。发布 revision `a418336baeb8496ab9032feae559cede`，4467 行；最终主源分布见 published-meta.json（小米商城1550、米家895、惠普支持570等），单源2533、双源1525、3+源409，仅主源2533。

发布后再次读取五条真实商品详情：旧字段零缺失、每条一个 primary；米家独有商品价格仍 null 且保留缺价原因。见 post-publication-compatibility.json。配套 API 来源回归 2 passed；Python 全量 1102 passed。

当前工作区仍保留上次其他任务的未跟踪审计、缓存及日志，未删除或打包混入本次线上发布。独立代码工具均已按可验证范围提交保存。
