# 集成独立审查（2026-11-05）

审查当时版本的发现已逐项通知主线；后续修复以最终提交为准，本文件不是最终缺陷清单。

1. scope：旧款机型仅匹配Mac，遗漏小米16条笔记本/游戏本；宠物用品遗漏宠物空气净化器1条；显示器须包含游戏电竞显示器。床品当前234条包含组合装40条，未发现当前床品组合遗漏。
2. L1真实命中时release应满足validate（confidence、evidence.captured_at/source_type）；原观察接口只有observed_at。
3. L4应先验证usable旧系列再继承，不能仅用有date与quote判定；日级继承禁止进入effective day统计。
4. L4 run内部写DEFAULT_EVIDENCE，总runner又覆盖该文件为result，会丢失顶层evidence/scope；需统一持久化责任并保证离线重放。
5. CI runner依赖requests/bs4，L2需Node+playwright+Chromium，不能依赖开发机Chrome绝对路径。
6. 当时尚无schedule；已有refresh-release-dates仅workflow_dispatch。最终必须查workflow实际cron及云端可跑记录。
7. by_id单值映射只能补同ID最后一个投影。线上当前存在5个重复投影，虽本轮不涉及优先品类，仍应按所有发布行处理。
8. 单lane运行会重放所有sidecar，报告须区别本轮采集结果与全部已审输入重放，不把其它lane历史结果算成本lane新增。

已实测：当前冻结基线apply_priority_dates连续执行两次结果相同；当前L4生成的115条继承候选均通过usable（未来disabled输入仍需门禁）。审查用offline run暴露隐藏默认文件写入，已即时通知主线。
