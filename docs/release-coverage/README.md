# 日优先、月为底线：常设采集与验收

基线取自线上 data 分支 goods.json，共3682发布行、惠普791行（比任务提供基线新增一条真实货号）。本目录before.json.gz冻结开工前数据，after.json.gz为本轮本地候选；最终正式读回见publication.md。

严格新口径：day/month、来源证据可复核、第三方须已独立交叉验证；不计LLM估算、网页首存、disabled/internal断言。旧“任一日期1050条”不能直接与新口径比较。严格口径前868/3682，后980/3682；day=0、month=980。当前数据没有可用的日级单品日期，此轮没有为了凑日级数量修改已有月份。

**112条新增均为2023-03全球ProBook G10平台公告月份**，只进入release_inherited，release_source=series_inherit、level=series、market=GLOBAL；不是中国SKU首售日。原有release及release_series不改。系列继承覆盖子集208（既有系列96+新增HP112），应与单品日期772分开看。L1真正商品日期仍为0/791。

优先品类全部纳入：笔记本/台式/电脑/工作站及旧款电脑1040；显示器56；键鼠12；宠物4（含空气净化器）；床品234（含40组合装）；汽车17。历史手机虽归旧款机型不进入电脑。各类前后与10条URL、原文、精度理由见[日报](2026-11-05.md)及samples.json。

L1实测788精确货号、40批POST，HTTP200业务406 invalid captcha；570份精确货号原响应无商品发布字段，218条访问失败无合格旧响应，3条系列无唯一货号，404=0。当前访问失败与历史无字段分开记录；任何一种都不代表官方不存在日期。L2全部38 SPU/267 SKU原文成功、0日期；createTime拒收。L3优先小米102条、83 URL（82成功/1 TLS失败）、0新日期；找到2021大陆RedmiBook Pro开售原文，但当前型号跨代，拒绝继承。L4 exact平台成员112+既有系列成员3，系列证据最多到月。详见各线README与逐条诊断。

每条缺失默认not_obtained；后台按要求显示“可得未取到”，并解释为待采集、不保证确实可得。没有明确官方否认原文时，“官方无此信息”恒为0。无字段、404、访问失败或型号不符都不擅自升级为官方无。

```bash
python3 scripts/release_dates_run.py --lane L1
python3 scripts/release_dates_run.py --lane all --goods /path/to/goods.json --apply
python3 scripts/release_dates_run.py --lane all --goods /path/to/goods.json --no-live
```

--no-live明确离线重放已保存诊断，不假称刷新。每线可独立跑；all用线程并行执行。每轮写docs/release-coverage/YYYY-MM-DD.md，CI把报告和coverage.json随同一候选送入data分支，原始证据另存30天artifact。新日期通过原共享发布锁、测试、ID门禁和OSS哈希读回发布；访问失败只保留缺口，不猜日期。每次普通finalize也重放已审sidecar，因此日常品牌采集不会擦掉本轮补证。

workflow **release-dates-daily**，cron `17 19 * * *`（UTC，每日北京时间03:17）；本次配置后的下一次计划为**2026-11-06 03:17 +08:00**，平台排队可能延后。GitHub Actions支持手动选择L1/L2/L3/L4/all，默认all。

测试：日期策略/边界12通过，完整finalizer单测通过。两项旧year接受用例已改为必须拒绝；没有扩大跳过。最终完整云端测试、发布run及后台截图详见publication.md。
