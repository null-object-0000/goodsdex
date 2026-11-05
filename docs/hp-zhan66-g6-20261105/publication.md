# 最终发布与线上验收

数据提交：[479de401](https://github.com/null-object-0000/goodsdex/commit/479de401005bdafc5094eb62a0d8dab87d8520e0)。正式数据发布run：[41943000356](https://github.com/null-object-0000/goodsdex/actions/runs/41943000356)，collect与publish均success；共享发布门禁580 passed，OSS按文件哈希读回成功。曾误触发旧提交的41941798431已取消，不作为本次发布依据。

后端最终提交：[a91503d](https://github.com/null-object-0000/spend-good/commit/a91503d352205714fc9010daaf9c43bbbb8d70e5)，包含[生产分片补证修正17ac29b](https://github.com/null-object-0000/spend-good/commit/17ac29b9f568d3ab9ae338f95c766d775c5cebc8)。最终构建run：[41945032792](https://github.com/null-object-0000/spend-good/actions/runs/41945032792)，success；ECS已部署同一完整gitCommit，服务器与外部共6次HTTP200版本读回通过。见api-build-final.json、api-deploy-final/run.json、api-deploy-final.log；不是仅构建成功。

小程序候选选择提交：[857de68](https://github.com/null-object-0000/spend-good/commit/857de6821c8c33057eba9e73dae32e49337e320a)。真实浏览器验证先显示两候选且不绑定，点击机身货号才绑定该SKU；实付价保持空，京东6799保持独立标价。见ui/hp-candidates.png、ui/hp-selected.png和tests-ui.log。微信CI预览编译成功，主包1782815 bytes；预览二维码仅保存在本地ui/wechat-preview.png，没有上传至公共Git仓库。此为预览，不声称已发布微信正式版本。

## 正式服务读回

最终revision：`321ba7cdaf10422c87d67e4200c708ae`；goods.json SHA256：`db7c8368ce62d8db2631ce16e756c4932396afb8a902d7bda3e3858262cce3f4`。

线上3682行，HP791行；112条配置逐条核对货号、官方名称、平台代际、尺寸/容量/屏幕、状态与证据哈希。所有旧HP ID保留；7P2D5PC、7Z8L4PC、9T0Q0PC的实际API详情与OSS不可变发布记录逐值相等。服务器同步返回`ok=true,count=3682,succeeded=10,errors=[]`，见api-sync.log。

原文标题的正式GET /api/goods/match返回`match=null`，两个候选`7P211PC`与`7P2D5PC`，均0.90；已排除同CPU/内存/硬盘但FHD的9T0Q0PC。原始完整JSON及规则在match-after-online.json / README.md；与本地整库HTTP结果逐值相等。线上读取112条配置及最终候选的断言全部通过，见online-verification.json / online-verification.log。没有绕过营销映射或120Hz的证据缺口。

首次线上读回暴露轻索引省略证据的问题，曾安全返回空候选；17ac29b修正为按需读取HP详情后通过生产分片HTTP回归与最终线上复验。中间版本的空候选不当作成功报告。

## 测试

- 数据全量：884 passed / 8 deselected / 0 failed；同提交云端run [41942984469](https://github.com/null-object-0000/goodsdex/actions/runs/41942984469)，success，见tests-cloud.log。
- 后端全量：362 passed / 4 skipped / 0 failed，包含真实轻索引省略source、证据和完整params的分片HTTP回归，见tests-api-final.log。
- 小程序全量：132个测试文件，883 passed / 0 skipped / 0 failed，见tests-miniprogram-summary.json、tests-miniprogram-files.json.gz。早期整体执行因本机内存压力中断；最终按文件串行、独立进程完整执行全部文件，未增跳过。
- 微信预览编译：成功；主包在原有1950KiB门限内，见preview-build.log。

本地不变量见local-invariants.json：非HP记录逐值不变；原14英寸系列记录逐值不变；111条旧HP仅补证配置，官方name/series/generation未改写；新增1个真实货号，没有丢ID。
