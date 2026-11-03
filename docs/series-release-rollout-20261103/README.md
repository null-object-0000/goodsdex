# 小米系列/发布批次铺开（2026-11-03）

本轮全量筛查当前线上小米 **1695 行**，保留试点5批17条，新增76批132条系列断言，最终 **81批149条**，其中本轮新增无单品日期的系列继承90条。单品 `release.date` 全部原样保留。

**分母差异没有掩盖。** 用户交接为1728，当前线上 `/api/goods` 与 `origin/data` 都实际为小米1695、全库2909。冻结快照及字节哈希见 `baseline-goods.json.gz`、`data-baseline.json.gz`、`report.json`。差额33条身份未知，未构造记录，也未声称完成1728条口径验收。本轮以实际1695行完成逐行清点，分类互斥取主品类；重复ID行保留原样，1690个不同小米ID，不静默去重。

**本轮证据范围。** 对当前每个ID回看上一轮当日官方接口扫描（2242个小米ID，含请求、状态、哈希、时间）；新增59个品类关键词的新闻检索，再对目标系列补查。品类检索原文见 `category-search.json`，目标入口见 `targeted-search.json`；报道完整HTTP响应及SHA256见 `evidence/`、`article-inventory.json`。所有当前行逐条纳入 `census.json`。这是一轮全量筛查，并不意味着1546条未获日期的记录都做了独立精确关键词或穷尽网络检索；未取得依据不等于没有任何公开依据。

本轮归档 236 个报道入口（正文取得 159，失败 77）。采用的新增批次均为IT之家第三方报道，明确标记 `third_party`，没有把报道转述官微或所附京东链接标成官方。没有使用京东同系列其它配置日期。官方商品页和扫描里只有单品参数/型号年份的，不提升为整个系列批次依据。

同一场发布会可聚批，容量、颜色或水箱/上下水版本仅在报道明确覆盖时纳入。型号年份不推导月份。基础款、Pro、至尊、白色新版本与多代容器分开；不能证明同批就留空。日期均为年月，预售/预约对应公开上架的 `announcement`，没有把计划开售当已发生 `availability`；已开售报道保留 `availability`。显示仍为独立 `series_release.display` 的“该系列 X 年 X 月发布/开售”，未写“发售时间”到单品日期。

## 覆盖率

小米系列字段：**17/1695（1.00%） → 149/1695（8.79%）**，增加132条、7.79个百分点。90条是新增无单品日期的继承，另42条与既有单品日期并存，不冒充新增单品日期。统计包含系列容器，不把容器另说成新增硬件型号。

汽车（小米汽车3、比亚迪14）单列，全部保持原状，不进入分母。其它品牌系列字段未改。当前发布集残留服务/耗材等记录也全部清点、保持空，不在本轮悄悄缩小分母或更改既有过滤策略。1728口径尚缺33条对应身份，因此不计算伪精确的1728覆盖率。

|品牌|当前行数|系列字段 前→后|
|---|---:|---:|
|Apple|635|0→0（本轮未改）|
|大疆|281|0→0（本轮未改）|
|富士|63|0→0（本轮未改）|
|小米|1695|17→149|
|小米汽车|3|0→0（本轮未改）|
|惠普|218|0→0（本轮未改）|
|比亚迪|14|0→0（本轮未改）|

完整主品类覆盖表见 [coverage.md](coverage.md)。

## 批次表

|批次名|日期 / 事件|依据（均第三方）|成员条数|本轮新增系列字段|本轮新增无单品日期继承|
|---|---|---|---:|---:|---:|
|米家空调（巨省电） / 双排挂机 2025-12 发布批次|2025-12 / announcement|[IT之家](https://www.ithome.com/0/902/637.htm)|3|0|0|
|米家空调（巨省电） / 2026 Pro 挂机 2026-02 发布批次|2026-02 / announcement|[IT之家](https://www.ithome.com/0/924/464.htm)|2|0|0|
|小米电视 S 系列 / S Mini LED 2025 中国大陆发布批次|2025-05 / announcement|[IT之家](https://www.ithome.com/0/855/247.htm)|6|0|0|
|米家扫地机器人 / M40 S 2025-05 上架发布批次|2025-05 / announcement|[IT之家](https://www.ithome.com/0/851/952.htm)|3|0|0|
|米家扫地机器人 / 5 Pro 2025-08 开售批次|2025-08 / availability|[IT之家](https://www.ithome.com/0/873/956.htm)|3|0|0|
|小米电视S Pro RGB-Mini LED 2027 / 小米电视S Pro 85 RGB-Mini LED 2027|2026-09 / availability|[IT之家](https://www.ithome.com/1/002/763.htm)|5|5|0|
|REDMI电视X RGB-Mini LED 2027 竞技版 / REDMI电视X55 RGB-Mini LED 2027 竞技版|2026-10 / announcement|[IT之家](https://www.ithome.com/1/009/624.htm)|5|5|0|
|米家电动剃须刀 Pro 套装版|2026-04 / announcement|[IT之家](https://www.ithome.com/0/938/884.htm)|1|1|1|
|Xiaomi 智能家庭屏 11|2025-12 / announcement|[IT之家](https://www.ithome.com/0/908/020.htm)|1|1|1|
|米家扫拖机器人 6 Pro / 米家扫拖机器人 6 Pro 薄嵌上下水版|2026-04 / announcement|[IT之家](https://www.ithome.com/0/935/245.htm)|3|3|3|
|米家商务双肩包|2024-06 / availability|[IT之家](https://www.ithome.com/0/773/683.htm)|1|1|1|
|Xiaomi Watch S5 41mm|2026-09 / announcement|[IT之家](https://www.ithome.com/1/006/432.htm)|1|1|0|
|米家电磁炉N1|2024-08 / announcement|[IT之家](https://www.ithome.com/0/788/014.htm)|1|1|1|
|米家三区洗衣机Pro 滚筒10kg 冰晶白|2026-04 / announcement|[IT之家](https://www.ithome.com/0/935/558.htm)|1|1|1|
|米家电水壶3|2025-05 / announcement|[IT之家](https://www.ithome.com/0/852/350.htm)|1|1|1|
|REDMI显示器 A27U Type-C 120Hz 2027|2026-09 / availability|[IT之家](https://www.ithome.com/1/002/146.htm)|1|1|1|
|米家空气净化器 6|2026-05 / announcement|[IT之家](https://www.ithome.com/0/946/678.htm)|1|1|1|
|米家智能IH电饭煲P1 4L|2026-04 / availability|[IT之家](https://www.ithome.com/0/936/863.htm)|1|1|1|
|米家洗衣机Pro 超电解新风 滚筒12kg / 米家洗衣机Pro 超电解新风 洗烘12kg|2026-09 / availability|[IT之家](https://www.ithome.com/1/000/430.htm)|2|2|2|
|米家无线直发梳 2|2026-09 / announcement|[IT之家](https://www.ithome.com/1/006/080.htm)|1|1|1|
|米家冰箱Pro 508L 自动制冰 / 米家冰箱Pro 法式508L 自动制冰 冰羽白|2026-05 / availability|[IT之家](https://www.ithome.com/0/954/285.htm)|3|3|3|
|米家洗衣机Pro 超电解智投 洗烘12kg|2026-01 / announcement|[IT之家](https://www.ithome.com/0/911/961.htm)|1|1|1|
|Xiaomi 18 Fold|2026-09 / announcement|[IT之家](https://www.ithome.com/0/999/555.htm)|1|1|0|
|米家智能洗碗机 台式 5套|2026-09 / availability|[IT之家](https://www.ithome.com/1/006/141.htm)|1|1|1|
|小米电视S Pro Mini LED 2026 / 小米电视S Pro 65 Mini LED 2026|2025-09 / announcement|[IT之家](https://www.ithome.com/0/882/563.htm)|4|4|0|
|米家电动剃须刀S101云纹刀网版|2026-09 / announcement|[IT之家](https://www.ithome.com/1/004/687.htm)|1|1|1|
|米家多向扫振电动牙刷|2025-08 / availability|[IT之家](https://www.ithome.com/0/877/121.htm)|1|1|1|
|米家电动直柄螺丝刀|2026-06 / availability|[IT之家](https://www.ithome.com/0/964/398.htm)|1|1|1|
|米家八电极体脂秤 S800|2025-04 / announcement|[IT之家](https://www.ithome.com/0/847/826.htm)|1|1|1|
|米家空气净化器 6 C|2026-09 / availability|[IT之家](https://www.ithome.com/1/005/563.htm)|1|1|1|
|米家智能IH电饭煲2 多功能版|2026-09 / availability|[IT之家](https://www.ithome.com/1/002/429.htm)|1|1|1|
|米家声波电动牙刷T302 缓震版|2026-09 / availability|[IT之家](https://www.ithome.com/1/007/140.htm)|1|1|1|
|Xiaomi 智能音箱|2025-04 / announcement|[IT之家](https://www.ithome.com/0/848/572.htm)|1|1|1|
|米家破壁机 3|2026-09 / availability|[IT之家](https://www.ithome.com/0/999/528.htm)|1|1|1|
|米家电动鼻毛修剪器Pro|2026-06 / availability|[IT之家](https://www.ithome.com/0/962/808.htm)|1|1|1|
|Xiaomi 智能家庭屏 Mini|2024-11 / announcement|[IT之家](https://www.ithome.com/0/807/956.htm)|1|1|1|
|米家除螨仪3 Pro|2026-03 / availability|[IT之家](https://www.ithome.com/0/933/279.htm)|1|1|1|
|米家智能洗碗机嵌入式 20套|2026-09 / availability|[IT之家](https://www.ithome.com/1/006/074.htm)|1|1|1|
|小米数字对讲机|2025-09 / announcement|[IT之家](https://www.ithome.com/0/885/942.htm)|1|1|1|
|米家扩容旅行箱|2024-07 / availability|[IT之家](https://www.ithome.com/0/779/780.htm)|1|1|1|
|米家空气净化器 6 Pro|2025-12 / announcement|[IT之家](https://www.ithome.com/0/908/835.htm)|1|1|1|
|米家自动洗手机1S套装|2023-09 / availability|[IT之家](https://www.ithome.com/0/722/395.htm)|1|1|1|
|米家体脂秤 4 Pro|2026-09 / announcement|[IT之家](https://www.ithome.com/1/004/906.htm)|1|1|1|
|米家扫拖机器人 6 / 米家扫拖机器人 6|2026-04 / availability|[IT之家](https://www.ithome.com/0/939/110.htm)|3|3|3|
|米家台灯2 清视版|2026-09 / announcement|[IT之家](https://www.ithome.com/1/002/473.htm)|1|1|1|
|米家智能洗碗机 独嵌两用 18套|2026-10 / availability|[IT之家](https://www.ithome.com/1/010/959.htm)|1|1|1|
|小米手环10 Pro|2026-05 / announcement|[IT之家](https://www.ithome.com/0/953/607.htm)|1|1|0|
|米家冰箱 256L三门 2026款|2026-09 / availability|[IT之家](https://www.ithome.com/1/004/821.htm)|1|1|1|
|小米智能门锁 5 Max / 小米智能门锁 5 Max 内外双摄 深锖色|2026-09 / announcement|[IT之家](https://www.ithome.com/1/006/044.htm)|3|3|3|
|小米智能插座4|2026-09 / announcement|[IT之家](https://www.ithome.com/0/997/385.htm)|1|1|1|
|米家空气净化器 6 Max|2026-04 / availability|[IT之家](https://www.ithome.com/0/939/263.htm)|1|1|1|
|小米电视S Mini LED 2026 / 小米电视S85 Mini LED 2026|2026-04 / announcement|[IT之家](https://www.ithome.com/0/936/839.htm)|6|6|0|
|米家无线吸尘器 4 C|2026-04 / availability|[IT之家](https://www.ithome.com/0/944/791.htm)|1|1|1|
|米家无线吸尘器 4 Max|2026-05 / announcement|[IT之家](https://www.ithome.com/0/952/625.htm)|1|1|1|
|米家毛球修剪器2|2025-05 / availability|[IT之家](https://www.ithome.com/0/855/294.htm)|1|1|1|
|米家冰箱 271L 三门|2026-09 / availability|[IT之家](https://www.ithome.com/1/004/822.htm)|1|1|1|
|米家扫拖机器人 6 Max / 米家扫拖机器人 6 Max 薄嵌上下水版|2026-03 / announcement|[IT之家](https://www.ithome.com/0/927/988.htm)|3|3|3|
|米家冰箱Pro 微冰鲜双系统 法式平嵌560L 冰晶白 / 米家冰箱Pro 微冰鲜双系统 法式平嵌560L 星缎银|2025-09 / announcement|[IT之家](https://www.ithome.com/0/885/842.htm)|2|2|2|
|米家冰箱Pro 至尊版 508L / 米家冰箱Pro 至尊版 十字508L 全域离子净化4.0 星缎银|2026-04 / availability|[IT之家](https://www.ithome.com/0/945/462.htm)|7|7|7|
|米家扫拖机器人 6 Max 上下水 白色 / 米家扫拖机器人 6 Max 白色|2026-09 / announcement|[IT之家](https://www.ithome.com/0/999/647.htm)|2|2|2|
|米家洗衣机 迷你双区洗烘1kg|2026-05 / announcement|[IT之家](https://www.ithome.com/0/952/110.htm)|1|1|1|
|米家筒灯射灯 3 Pro|2026-09 / announcement|[IT之家](https://www.ithome.com/1/006/031.htm)|1|1|1|
|小米对讲机3 畅聊版|2025-03 / announcement|[IT之家](https://www.ithome.com/0/837/196.htm)|1|1|1|
|米家洗衣机Pro 超电解智投 洗烘10kg|2026-01 / availability|[IT之家](https://www.ithome.com/0/916/286.htm)|1|1|1|
|米家加湿器 3|2025-08 / announcement|[IT之家](https://www.ithome.com/0/874/795.htm)|1|1|1|
|米家三区洗衣机Pro 洗烘14kg|2025-12 / announcement|[IT之家](https://www.ithome.com/0/903/746.htm)|1|1|1|
|米家双区洗衣机Pro 双洗烘10kg|2025-05 / announcement|[IT之家](https://www.ithome.com/0/851/424.htm)|1|1|0|
|米家扫拖机器人5C（水箱/薄嵌上下水）|2025-08 / announcement|[IT之家](https://www.ithome.com/0/878/384.htm)|3|3|3|
|2018小米8发布会：8/8 SE/透明探索版|2018-05 / announcement|[IT之家](https://www.ithome.com/0/362/532.htm)|3|3|2|
|红米5/5 Plus首发批次|2017-12 / announcement|[IT之家](https://www.ithome.com/0/337/624.htm)|6|6|6|
|小米MIX 2S首发（不含翡翠色）|2018-03 / announcement|[IT之家](https://www.ithome.com/0/352/847.htm)|1|1|1|
|柔风挂机1.5匹（APF5.27）|2023-03 / availability|[IT之家](https://www.ithome.com/0/680/310.htm)|1|1|1|
|巨省电Pro柔风版立式大3匹|2026-03 / availability|[IT之家](https://www.ithome.com/0/932/018.htm)|1|1|1|
|微冰鲜双系统十字平嵌560L（三配色）|2026-01 / availability|[IT之家](https://www.ithome.com/0/910/018.htm)|3|3|3|
|2026秋季发布会：18 Pro系列/Pad9系列|2026-09 / announcement|[IT之家](https://www.ithome.com/1/006/476.htm)|4|4|0|
|Pad9 Pro Max（玄戒O3）|2026-09 / announcement|[IT之家](https://www.ithome.com/0/999/486.htm)|1|1|0|
|2026人车家发布会：17 Max/耳夹式耳机|2026-05 / announcement|[IT之家](https://www.ithome.com/0/953/645.htm)|2|2|0|
|Xiaomi Civi5 Pro|2025-05 / announcement|[IT之家](https://www.ithome.com/0/855/282.htm)|1|1|0|
|小米笔记本Pro14 2026（第三代酷睿Ultra）|2026-03 / announcement|[IT之家](https://www.ithome.com/0/930/804.htm)|1|1|0|
|17 Ultra/徕卡版/Buds6发布会|2025-12 / announcement|[IT之家](https://www.ithome.com/0/908/038.htm)|3|3|0|
|2025人车家发布会：K80至尊/K Pad/S4 41mm/开放耳机Pro/AI眼镜|2025-06 / announcement|[IT之家](https://www.ithome.com/0/863/991.htm)|5|5|0|

## 抽样与未获依据清单

[30条逐项核对](sample-30.md)列出型号、批次、依据、对错、正确值。24条已赋日期 + 6条应留空，最终30/30符合预期；目的抽样，不能外推为全库准确率。由执行者阅读正文复核，未声称已有独立人工签字。

[逐名未获日期清单](unresolved.md)与 [完整JSON](unresolved.json)列出1546行的名字、ID、实际试过的入口和未赋值原因。多代/容量不明的容器和服务/耗材保留空。不能以同名近似报道补齐。检索入口失败有实际错误记录，未将失败伪装为没有结果。

## 复现、测试与发布

```bash
PYTHONPATH=src python docs/series-release-rollout-20261103/build.py
python docs/series-release-rollout-20261103/sample_review.py
python docs/series-release-rollout-20261103/report.py
PYTHONPATH=src:scripts python -m pytest -q
```

基线470项通过。最终测试结果见 `tests-final.log`；完整正常 finalize 日志见 `finalize.log`。逐字段比对表明非series字段0变更、商品行数及汽车0变更、继承重放幂等。发布与真实详情API摘录见 [publication.md](publication.md)（发布完成后写入）。
