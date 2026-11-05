# 发布验收

数据实现提交：2cc17195（分类、时间、系列）；随后补充冷缓存排除回放保护，冻结原URL及50张已核实型号图，只按同ID恢复缺失字段，不使用系列图填主图。后台/API实现提交：ca7c1c9。

后台构建与API测试 run：[42052784008](https://github.com/null-object-0000/spend-good/actions/runs/42052784008)，build/API tests均success；API本地371 passed / 原有4 skipped，后台12 passed，类型检查和生产构建通过。

截图为本地真实后台组件和真实API读取冻结线上记录，并非伪造DOM或在线登录截图：[3条Wayback+3条商城页](six-source-records-time.png)、[原始名称视图](six-source-records-left.png)、[红米5系列7个variants](redmi5-variants.png)、[Air系列8个variants](air-variants.png)。逐项DOM与真实接口断言见ui-verification.json；组原始响应见redmi5-group.json / air-group.json。

父组价格仅显示“旧款 · 无现价”，不会把首个配置的历史标价当作组代表价；历史标价仍在对应的variant单独展示。

首次排队发布42052492846已主动取消：线上审计发现旧采集缓存到排除清单路径可把8条已知source_url置空，已补充精确ID的冻结原URL回放。新发布与线上读回结果继续记录于此。

后台ECS已完成部署，内外分别连续3次HTTP200及完整gitCommit读回均通过，实际运行ca7c1c9f032e7277a5d40dca04f07d004aad7ca9；沿用上一轮已验证的60秒预热部署脚本，保留失败自动回滚与原生依赖检查。

修正后的数据实现提交为292a15c0a176751ea419cce048c9fc01fe969ffd；冷缓存URL/型号图与完整finalizer排除回放7项回归测试通过。本地全量1032项通过后另加1项完整finalizer冷缓存回归（包含在上述7项）；同提交云端[42055905031](https://github.com/null-object-0000/goodsdex/actions/runs/42055905031)全量1033 passed / 8原有deselected / 0 failed。正式本轮run为42055905569。

型号主图50张均已真实GET并通过图片解码与尺寸校验（全部HTTP200）；逐图URL、状态、SHA256、检查时间与尺寸见model-image-get-verification.json。


正式数据发布：[42055905569](https://github.com/null-object-0000/goodsdex/actions/runs/42055905569)，collect/publish均success；发布门禁651 passed / 0 failed。数据提交894e0d202358ee469e4cd67dddb23c22bba14e96，revision=1897cd24212245498994764da7ab3d51。goods.json及goods-excluded.json均按manifest引用的不可变blob重新下载并校验SHA256，随后独立逐ID审计，223条完整保留，182发布+41排除，所有已知URL与型号图一致，未丢链接或图片。详见online-hash-verification.json / online-oss/summary.json / online-oss/after-223.json。

部署服务同步成功：ok=true / count=3572 / succeeded=10 / errors=[]（api-sync.log）。后台/API代码仍为完整ca7c1c9f032e7277a5d40dca04f07d004aad7ca9。线上旧品类查询0条；红米5查询7条，Air查询8条，现价全null；原始线上响应另存online-old-category.json / online-redmi5.json / online-air.json。

线上最终：page_no_price=223；page_no_image=173；型号主图50；archived_at=139；captured_at有据84、未知139。服饰7/配件20/箱包14均在排除档案（原8+新增33）；米家内衣物洗烘一体机仍在主列表，ID见online-oss/summary.json。

正式域名逐字段读回验证另见online-api-verification.json：182个主列表目标的13个字段与已验哈希的发布记录完全一致，差异0；41条排除记录已通过同版本OSS排除清单核验。
