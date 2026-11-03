# 第六轮：20族调用与核对

{
  "families": 20,
  "requests": 20,
  "http_429": 0,
  "backoffs": [],
  "input_tokens": 5600,
  "output_tokens": 2144,
  "total_tokens": 7744,
  "successful_responses": 20,
  "empty_responses": 0,
  "abstentions": 9,
  "date_candidates": 11,
  "model_reference_candidates": 10,
  "verified_accepted": 10,
  "date_accuracy": "11/11=100% (CN/global as returned)",
  "evidence_inclusive_acceptance": "10/11=90.91%",
  "request_seconds": 38.459138980993885
}

按第五轮缺口族中每品牌未覆盖变体数降序取10/5/3/2；无额外探针调用。原始响应含后端usage、finish_reason；states保存状态。所有20族均只发送一次，重跑跳过已有sent标记。

## 逐条核对

|型号|LLM年月|核对依据|结论|
|---|---|---|---|
|小米6X|2018-04|[2018-04-25 的发布会现场原创报道，武汉发布6X。](https://mobile.zol.com.cn/686/6865715_all.html)|日期正确；另补独立月份依据|
|米家高速水离子吹风机 Pro|None|[2026-04-24 开售报道；只能证明该时已推出，不能单独确定首次发布月。](https://www.ithome.com/0/943/006.htm)|留空；不判日期错误，不计产出|
|小米Max 2|2017-05|[2017-05-25 发布会现场图文直播，Max 2。](https://www.ithome.com/0/310/477.htm)|日期正确；另补独立月份依据|
|红米5|2017-12|[2017-12-07 现场报道，红米5/5 Plus发布。](https://m.21jingji.com/article/20171207/herald/39632cbe1b2efc81da5c7d434135357a.html)|日期正确；另补独立月份依据|
|红米5 Plus|2017-12|[同场发布5 Plus，非后来的印度Note 5名称。](https://m.21jingji.com/article/20171207/herald/39632cbe1b2efc81da5c7d434135357a.html)|日期正确；另补独立月份依据|
|红米Note 5|2018-03|[2018-03-16 国行发布现场原创报道；按返回的CN市场核对。](https://mobile.zol.com.cn/681/6816826_all.html)|日期正确但无回指依据，拒收|
|米家扫拖机器人 6 Max|None|[2026-03-11 报道新推出6 Max；模型留空，不算日期错误，也不算有效产出。](https://www.ithome.com/0/927/988.htm)|留空；不判日期错误，不计产出|
|米家智能变压IH电饭煲 4L|None|[2025-09-16 报道昨晚开售；不足以单独确认首次发布月。](https://www.ithome.com/0/883/451.htm)|留空；不判日期错误，不计产出|
|米家手持风扇|None|[2026-06-05 新款报道；缺精确硬件型号，不能排除同名旧款。](https://g.pconline.com.cn/x/2166/21664211.html)|留空；不判日期错误，不计产出|
|Xiaomi全屋路由 BE3600Pro|None|[官网确认型号，未找到可确定首次月份的原文；不借网线版日期。](https://www.mi.com/xiaomi-routers/be-3600-pro)|留空；不判日期错误，不计产出|
|Osmo Nano|None|[官方下载页2025-09-23记录；不是首次发布证明，留空不判错。](https://www.dji.com/nano/downloads)|留空；不判日期错误，不计产出|
|Osmo Action 5 Pro|2024-09|[官方新闻2024-09-19宣布Action 5 Pro。](https://www.dji.com/no/media-center/announcements/dji-osmo-action-5-pro-en)|日期正确；另补独立月份依据|
|Osmo 360|2025-07|[官方新闻2025-07-31宣布Osmo 360。](https://www.dji.com/pr/newsroom/news/dji-release-osmo-360-us)|日期正确；另补独立月份依据|
|Osmo Action 4|2023-08|[官方新闻2023-08-02宣布Action 4。](https://www.dji.com/media-center/announcements/dji-introduces-osmo-action-4-for-capturing-adventure-in-stunning-clarity)|日期正确；另补独立月份依据|
|Osmo Action 6|None|[官方新闻2025-11-18宣布Action 6；可补查，但不冒充模型产出。](https://www.dji.com/media-center/announcements/dji-release-osmo-action-6)|留空；不判日期错误，不计产出|
|FUJIFILM X-S20|2023-05|[官方新闻2023-05-24宣布；6月29日开售，区分announcement。](https://www.fujifilm.com/ae/en/news/hq/9421)|日期正确；另补独立月份依据|
|FUJIFILM X-T5|2022-11|[官方新闻2022-11-02宣布X-T5。](https://www.fujifilm-x.com/en-sg/news/fujifilm-launches-fujifilm-x-t5/)|日期正确；另补独立月份依据|
|FUJIFILM X-T50|2024-05|[官方新闻2024-05-16宣布X-T50；6月起开售。](https://www.fujifilm.com/nz/en/news/hq/11349)|日期正确；另补独立月份依据|
|惠普 星Book Air 14英寸 AI 笔记本电脑 / 第三代英特尔® 酷睿™ 5 320 处理器 / 英特尔® 显卡|None|[2026-10-26酷睿5 320版本发售报道；不能按其他CPU版本推断首发。](https://www.ithome.com/1/017/946.htm)|留空；不判日期错误，不计产出|
|惠普 战99 Air 14英寸 AI笔记本电脑 / AMD 锐龙™ AI 7 PRO 450处理器 / AMD Radeon™|None|[2026年新款450平台报道；首发月份待更强原始材料，不借前代。](https://diy.zol.com.cn/1188/11889344.html)|留空；不判日期错误，不计产出|

原始候选正文完整保存于 review.json（包含原始依据链接/原文、market和reason）。以上独立检索链接不能冒充模型原始依据。多数原始链接只是型号产品页，不能直接证明月份；10族有型号回指且经独立资料核准，红米Note 5没有链接或原文，拒收。未对产品页链接真实性及月份支持率作100%声明。

## 全量决策与容量参考

不建议铺全量：尽管已给日期11/11核对正确，含依据约束的候选合格率只有10/11（90.91%），不足97%；另9族弃答。20族按覆盖数选取，不能当作全量随机精度保证。未请求剩余族，未写入正式日期或发布数据。

仅作容量参考、不是执行计划：2813族无429需2813次请求；扣除本次20族剩2793次。按本批均值线性外推，2813族 input约787,640 tokens，output约301,554，总约1,089,194；串行请求耗时约1.50小时，未含人工核对、网络波动与限流停机。单次输出预算4096，2813次输出预算上界11,522,048 tokens；默认连续3次429即停止，最长只重试2次并退避1/2秒，配置允许最多4次重试。任何429都会增加请求数，不能保证完成时间。价格未提供，不编造金额。

## 验证

PYTHONPATH=src:scripts pytest -q：371 passed，1 warning。初次未设PYTHONPATH导致收集失败，纠正路径后全绿。新增预算下限、429退避/熔断、断点不重发测试。
