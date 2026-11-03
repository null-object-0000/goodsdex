# 全库 LLM 发布时间填充率实验（仅 staging）

实际响应模型：**deepseek-v4.1-flash-1017**。全库 **3285 族 = 已有 official 跳过 266 族 + 实跑 3019 族**。给日期 **443 族**，实跑填充率 **443/3019 = 14.67%**；相对全库族数 **443/3285 = 13.49%**。

全部候选无条件采纳的机械上限：release.date 非空 **694/3968 = 17.49% → 1123/3968 = 28.30%**，净增 429 行。这只是非空覆盖预估，未经过质量门禁，不是可用事实覆盖。

实验未修改 public/goods.json、_data/public/goods.json、官方/LLM/交叉核查输入或 API 代码，未发布。生产文件逐项前后 hash 见 validation.json。

## 分母与结果

- 总行数 3968，唯一 ID 3963；5 次重复 ID 属于不同分类，保留原库行数，不缩分母。
- 聚族沿用现有 family_model，先对所有行聚族，再按 brand/category/去空白型号形成键，扩展到七品牌。惠普保留CPU/GPU、套机跟body_id。之前约2813是四品牌缺日期子集，不是本次七品牌全库分母。
- 任一族成员已有 source=official 且 date 非空，整族不请求；族内其他缺日期成员也不借官方日期自动填充。已有 third_party/llm 的族仍请求，覆盖预估不把旧日期重复计成新增。跳过的官方族内仍有185行缺日期（大疆156、Apple25、富士4），这些行不自动填充。
- 冻结重建基线与实取线上快照的 (id,brand,category,聚族型号,date,source) 多重集合一致；79条 release 展示/检查元数据不同，不影响本次分母、跳过或覆盖。见 live-baseline-comparison.json。

|实跑结果|族数|
|---|---:|
|成功返回非空正文（下三项之和）|3019|
|弃答：JSON date=null|2559|
|给日期：合法 YYYY-MM，是否有依据另列|443|
|格式非法：JSON解析失败、缺date或非法日期|17|
|请求失败/空响应|0|
|待执行/在途|0|

成功返回是传输/正文口径，不表示日期正确。弃答只算没有日期，不参与日期准确率。格式合法但没有依据也算填充候选，并在质量统计单列。

|品牌|总族|已有官方跳过|实跑|成功返回|弃答|给日期|非法|实跑填充率|日期/总族|
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|小米|2191|78|2113|2113|1900|197|16|9.32%|8.99%|
|大疆|567|62|505|505|490|14|1|2.77%|2.47%|
|惠普|157|0|157|157|157|0|0|0.00%|0.00%|
|富士|50|11|39|39|0|39|0|100.00%|78.00%|
|Apple|303|112|191|191|6|185|0|96.86%|61.06%|
|比亚迪|14|0|14|14|6|8|0|57.14%|57.14%|
|小米汽车|3|3|0|0|0|0|0|N/A|0.00%|

## 成本与执行

- 请求数 **3053**（包含429重试）；墙钟 **1639.873 秒 / 27.33 分钟**，以首个session开始到最后session完成计时，包含熔断后的暂停/冷却、初始化状态、请求等待与落盘；不含最后请求完成后的抽样核对及报告时间。
- input/prompt tokens **855,666**；output/completion tokens **306,308**；total **1,161,974**。
- 429 **34** 次；计划退避合计 **44.000 秒**，实际退避合计 **20.458 秒**（worker求和，不等于墙钟）。
- 共5个执行session、4次熔断，session内活动墙钟合计1059.427秒；每次解除均先检查429记录并冷却，历史保存在circuit-history/。
- 6个worker，全局4QPS，按完成顺序连续3次429持久熔断；仅429重试，1/2/4/8秒指数退避并尊重Retry-After。SIGINT/SIGTERM停止新派发并等待在途落盘；已成功族续跑不重发，未知中断计费沿用现有链路标记。
- Token合计只来自已记录的响应usage；429没有返回usage，不把未知计费断言为零。金额不可得：网关未提供本次计费单价，不能把token数折成虚构人民币金额。实际响应模型逐响应读取，不使用请求路由名作为模型身份。

## 抽样准确率与依据

每品牌完成后，按固定seed=20261103从排序后的合法日期族随机抽10条；日期不足10条则全取日期候选，并从余下结果补足10条。样本先冻结再检索，不替换错误条目。小米汽车只有3族且全部已有official，不请求，所以其LLM样本数0，无法满足10条，明确记N/A，不能伪造样本或破坏跳过要求。

“给过依据”仅指模型原evidence字面含URL或quote（不代表引用正确或网页已验证），reason自述不算依据；“原依据支持”要求读到模型原引用能支持准确型号与公告月份。事后找到的新链接仅核对日期，不补改模型原依据。日期准确率只以字面给过URL/quote且取得独立真值的日期样本作分母，错引仍留在此分母中，另由原依据支持率揭示；无原依据另外列出，不混入该准确率。另报“日期正确且原依据支持/全部日期样本”，防止日期猜对掩盖错引。原引用抓取失败只记未核实，不据此断言网页不存在。

|品牌|抽样数/日期数|日期准确率（给过URL/引文）|日期有值但无依据|原依据待核实|原依据支持/日期样本|日期对且原依据支持/日期样本|弃答样本|
|---|---:|---:|---:|---:|---:|---:|---:|
|小米|10/10|2/3 66.67%|7|2|0/10|0/10|0|
|大疆|10/10|8/10 80.00%|0|6|0/10|0/10|0|
|惠普|10/0|0/0 N/A|0|0|0/0|0/0|10|
|富士|10/10|9/10 90.00%|0|8|0/10|0/10|0|
|Apple|10/10|10/10 100.00%|0|3|1/10|1/10|0|
|比亚迪|10/8|2/3 66.67%|5|1|0/8|0/8|2|
|小米汽车|0/0|0/0 N/A|0|0|0/0|0/0|0|

全体日期候选中，没有URL/quote依据的计数：{'Apple': 1, '小米': 136, '比亚迪': 5}（合计142）。date非空却同时给abstention_reason的品牌计数：{'Apple': 2, '富士': 1, '小米': 80, '比亚迪': 2}。这些按实际date字段计入候选，不把文字自称弃答改写成date=null。完整原始evidence、逐条结论和核对来源在 reviews.json；本次60条样本（48条给日期、12条弃答）并不保证总体准确率，也不能把同一份来源下的多个型号当作独立质量保证。

|品牌|型号|LLM年月|给过依据/原依据支持|核对结果|正确值|核对说明与来源|
|---|---|---|---|---|---|---|
|Apple|iPad（第 9 代)|2021-09|有/未核实|对|2021-09|[官方9月14日发布第9代；原URL本次cache miss，未核实原引文。](https://www.apple.com/uk/newsroom/2021/09/apples-most-popular-ipad-delivers-even-more-performance-and-advanced-features/)|
|Apple|iPhone 4S|2011-10|有/否|对|2011-10|[官方10月4日发布；模型原URL缺少-iOS-5-iCloud，实读404。](https://www.apple.com/newsroom/2011/10/04Apple-Launches-iPhone-4S-iOS-5-iCloud/)|
|Apple|iPhone 6 Plus|2014-09|有/否|对|2014-09|[官方9月9日同时发布6与6 Plus；模型原Unveils URL为404。](https://www.apple.com/mu/newsroom/2014/09/09Apple-Announces-iPhone-6-iPhone-6-Plus-The-Biggest-Advancements-in-iPhone-History/)|
|Apple|Apple Watch Series 2|2016-09|有/是|对|2016-09|[官方9月7日发布Series 2；原URL被搜索索引抓取，正文支持型号与月份。](https://www.apple.com/newsroom/2016/09/apple-introduces-apple-watch-series-2/)|
|Apple|Mac mini (2007 年中)|2007-08|有/未核实|对|2007-08|[Apple原厂维修手册存档第7页记录Mid 2007于August 2007换Core 2 Duo；原新闻稿URL未核实，不用事后来源替换原证据。](https://www.informaticanapoli.it/download/MANUALI/APPLE/mac_mini_early_late_06.pdf)|
|Apple|MacBook（13 英寸，2009 年末机型）|2009-10|有/否|对|2009-10|[官方10月20日发布白色unibody 13.3英寸MacBook；模型自己承认原support页不支持月份，原页抓取429。](https://www.apple.com/newsroom/2009/10/20Apple-Updates-MacBook-With-LED-Backlit-Display-Multi-Touch-Trackpad-Built-in-Seven-Hour-Battery/)|
|Apple|iPhone 3GS|2009-06|有/未核实|对|2009-06|[官方6月8日发布3GS；模型原Introduces短URL未核实。](https://www.apple.com/uk/newsroom/2009/06/08Apple-Announces-the-New-iPhone-3GS-The-Fastest-Most-Powerful-iPhone-Yet/)|
|Apple|iPad mini 3|2014-10|有/否|对|2014-10|[原厂mini3环境报告标明2014年10月16日，官方Air2新闻稿亦点名mini3；原短URL404。](https://www.apple.com/cl/environment/pdf/products/archive/2014/iPadmini3_PER_oct2014.pdf)|
|Apple|MacBook Pro (Retina, 13 英寸, 2013 年初机型)|2013-02|有/否|对|2013-02|[官方2月13日更新13英寸Retina MBP；模型原support/112009实际为Apple Watch一代规格页，错引产品。](https://www.apple.com/newsroom/2013/02/13Apple-Updates-Processors-Prices-of-MacBook-Pro-with-Retina-Display/)|
|Apple|iMac (2009 年初机型)|2009-03|有/否|对|2009-03|[官方3月3日更新iMac；模型原support/112010实际为Apple Watch Sport一代规格页，错引产品。](https://www.apple.com/newsroom/2009/03/03Apple-Updates-Consumer-Desktop-Line/)|
|大疆|如影 Ronin 2|2017-04|有/未核实|对|2017-04|[DJI自行发出的4月23日新闻稿；原短URL未能读取，未核实原依据。](https://www.prnewswire.com/news-releases/dji-introduces-ronin-2-a-more-powerful-versatile-and-intelligent-stabilizer-for-film-and-video-professionals-300443974.html)|
|大疆|DJI Focus Pro LiDAR|2024-04|有/未核实|对|2024-04|[DJI原厂4月9日稿及组件Product Information同时点名LiDAR；原短URL不可访问，未核实原依据。](https://www.mynewsdesk.com/uk/dji/pressreleases/dji-pro-launches-next-generation-tools-offering-swift-setup-intuitive-operation-seamless-integration-and-extended-focus-control-3315434)|
|大疆|DJI Ronin 4D-8K 基础版|2023-10|有/否|错|2021-10|[按prompt的型号世代首次announcement：2021年10月20日原厂已同时宣布8K/6K combos；8K实际上市稿是2023年12月，均不支持2023-10。原规格页不能证明首次月份。](https://www.mynewsdesk.com/uk/dji/pressreleases/dji-revolutionizes-filmmaking-with-worlds-first-4-axis-cinema-camera-3137828)|
|大疆|DJI Ronin 4D-6K|2021-10|有/未核实|对|2021-10|[原厂2021年10月20日明确6K combo；模型只给产品页无首次月份引文，未核实原依据。](https://www.mynewsdesk.com/uk/dji/pressreleases/dji-revolutionizes-filmmaking-with-worlds-first-4-axis-cinema-camera-3137828)|
|大疆|DJI Focus Pro 手轮|2024-04|有/未核实|对|2024-04|[手轮Product Information日期2024-04-09，并由同日原厂发布稿点名；模型原产品页无月份原句，未核实。](https://www.dji.com/focus-pro/downloads)|
|大疆|DJI Air 3 系列充电管家|2023-07|有/否|对|2023-07|[官方视频目录2023-07-25已单列Battery Charging Hub，原厂同日Air3稿配套发布，非单借主机；模型承认原依据未找到配件首次月份。](https://www.dji.com/air-3/video)|
|大疆|Osmo Mobile 6|2022-09|有/未核实|对|2022-09|[官方2022-09-22发布Mobile6；模型原产品页无月份引文，未核实原依据。](https://www.dji.com/media-center/announcements/dji-osmo-mobile-6-pushes-smartphone-photography-further)|
|大疆|DJI LiDAR 焦点测距器|2021-10|有/否|对|2021-10|[商品vid111651官方商城定位Ronin4D配件，原厂2021-10稿明确LiDAR focusing system；月份相符，但模型reason错称2020年RS2配件，证据链不合格。](https://www.mynewsdesk.com/uk/dji/pressreleases/dji-revolutionizes-filmmaking-with-worlds-first-4-axis-cinema-camera-3137828)|
|大疆|DJI Matrice 4T|2025-01|有/未核实|对|2025-01|[官方2025-01-08稿同时点名4T/4E；原系列产品页无月份引文，未核实。](https://www.dji.com/media-center/announcements/matrice-4-series)|
|大疆|DJI RC Pro|2021-10|有/否|错|2021-11|[官方2021-11-05发布Mavic3且明确包含RC Pro，RC Pro下载页同日首次产品文档；候选2021-10错误。](https://www.dji.com/uk/newsroom/news/dji-mavic-3-release)|
|富士|FUJIFILM X100VI|2024-02|有/未核实|对|2024-02|[原厂2024-02-20公告；日本3月上市不能替代全球2月公告。模型原产品页仅回指型号，原月份依据未核实。](https://www.fujifilm.com/us/en/news/digital-cameras/fujifilm-debuts-x100vi-mirrorless-digital-camera)|
|富士|XF10-24mmF4 R OIS WR|2020-10|有/未核实|对|2020-10|[原厂2020-10-15明确WR更新版，非2013非WR旧款；原产品页月份未核实。](https://www.fujifilm-x.com/en-ph/news/fujifilm-introduces-fujinon-xf10-24mmf4-r-ois-wr-lens/)|
|富士|XF100-400mmF4.5-5.6 R LM OIS WR|2016-01|有/未核实|对|2016-01|[原厂2016-01-15发布，2月为上市；原产品页月份未核实。](https://fujifilm-korea.co.kr/support/notice/id/7193?p=27)|
|富士|XF80mmF2.8 R LM OIS WR Macro|2017-09|有/未核实|对|2017-09|[原厂页面2017-09-07公告11月上市，按announcement取9月；原产品页月份未核实。](https://fujifilm-korea.co.kr/support/notice/id/7251)|
|富士|XF150-600mmF5.6-8 R LM OIS WR|2022-05|有/未核实|对|2022-05|[原厂2022-05-31正式公告7月上市；原产品页月份未核实。](https://www.fujifilm-x.com/en-gb/news/fujifilm-announces-fujinon-xf150-600mmf5-6-8-r-lm-ois-wr/)|
|富士|XC50-230mmF4.5-6.7 OIS II|2015-01|有/否|对|2015-01|[内嵌FUJIFILM原厂2015-01-15新闻稿明确II代。date给2015-01同时abstention_reason自称date=null，保留实际字段按日期候选，原依据自称不足。](https://www.dpreview.com/articles/9503379114/fujifilm-unveils-fujinon-xc16-50mm-ii-and-xc50-230mm-ii-kit-lenses-for-x-a2/)|
|富士|FUJIFILM X-S20|2023-05|有/未核实|对|2023-05|[原厂2023-05-24公告6月29日上市；原产品页月份未核实。](https://www.fujifilm.com/ae/en/news/hq/9421)|
|富士|XF18-120mmF4 LM PZ WR|2022-09|有/否|错|2022-05|[原厂2022-05-31已正式公告9月上市，不是仅开发路线图；模型2022-09混淆上市与announcement。](https://www.fujifilm-x.com/fr-fr/news/fujifilm-annonce-le-fujinon-xf18-120mmf4-lm-pz-wr/)|
|富士|XF55-200mmF3.5-4.8 R LM OIS|2013-04|有/未核实|对|2013-04|[FUJIFILM Nordic原厂新闻稿2013-04-17明确该镜头；原产品页月份未核实。](https://www.mynewsdesk.com/se/fujifilm-nordic/pressreleases/launch-of-the-first-telephoto-zoom-for-the-xf-lens-series-fujinon-xf55-200mmf3-5-4-8-r-lm-ois-856842)|
|富士|XF27mmF2.8 R WR|2021-01|有/未核实|对|2021-01|[原厂2021-01-27明确R WR新版，非2013非WR旧版；原产品页月份未核实。](https://www.fujifilm-x.com/en-in/news/fujifilm-announces-new-fujinon-xf27mmf2-8-r-wr-lens/)|
|小米|米兔儿童手表S1|2023-04|无/否|错|2024-05|[同期2024-05-28发布报道；候选早一年。原evidence的URL与quote均null，单列无依据，不混入有依据准确率。](https://news.mydrivers.com/1/982/982548.htm)|
|小米|Xiaomi 智能家庭屏 11|2023-04|无/否|错|2025-12|[同期2025-12-25发布，明确11英寸新品；候选2023-04错误，无原依据。](https://www.ithome.com/0/908/020.htm)|
|小米|小米对讲机3|2022-04|无/否|对|2022-04|[同期2022-04-05公告小米对讲机3；日期相符，无原URL/quote，单列无依据。](https://www.ithome.com/0/611/344.htm)|
|小米|REDMI Pad 2|2025-08|无/否|错|2025-06|[官方英国FAQ明确2025年6月推出，先于候选全球2025-08；候选不是首次月份，无原依据。](https://www.mi.com/uk/product/redmi-pad-2/faq/)|
|小米|小米电视4C 32英寸|2018-05|无/否|对|2018-05|[同期2018-05-25四新品稿精确点名4C 32英寸，日期相符；无原URL/quote，单列无依据。](https://m.xdjd.cn/Article/525904/7CF87F862DDE/Article.aspx)|
|小米|小米电视4A 65英寸|2017-03|有/未核实|对|2017-03|[家电行业期刊2017年4月号记录3月21日发布会并点名43/49/55/65四尺寸；原global产品页月份未核实。](https://www.cheaa.org/upload/files/2017/5/1014484415.pdf)|
|小米|米家智能宠物饮水机 2|2023-04|有/否|错|2024-12|[同期2024-12-24新款上市稿明确二代，型号匹配；候选2023-04错误，原URL无首发月份引文。](https://www.ithome.com/0/819/782.htm)|
|小米|Xiaomi路由器BE7200 Pro|2024-12|无/否|错|2026-05|[同期2026-05-07发布BE7200 Pro，5月13日首销，非其他BE机型；候选2024-12错误，无原依据。](https://www.ithome.com/0/947/128.htm)|
|小米|红米6A|2018-06|有/未核实|对|2018-06|[同期官方促销转述稿回溯6月12日发布红米6A，另有同年发布会报道一致；原产品页月份未核实。](https://news.mydrivers.com/1/591/591743.htm)|
|小米|米动手表青春版|2017-04|无/否|错|2017-07|[同期2017年7月稿明确7月4日晚发布；原厂手册亦标2017.07.17，4月是米动健康手环，不能混为同一商品。无原依据。](https://www.eepw.com.cn/article/201707/361951.htm)|
|惠普|惠普 战99 台式机电脑 ／ 英特尔® 酷睿™ i5-14500 处理器 ／ 英特尔® UHD 显卡 770|—|无/未核实|不计（弃答或真值未取得）|—|模型弃答，无日期；不将弃答算错或算对。该具体型号首次月份未取得独立真值，不填猜测。|
|惠普|惠普 HyperX 暗影精灵MAX 16英寸游戏笔记本电脑 ／ 第二代英特尔®酷睿™ Ultra 9-290HX Plus 处理器 ／ NVIDIA® GeForce RTX™ 5090 独立显卡|—|无/未核实|不计（弃答或真值未取得）|—|模型弃答，无日期；不将弃答算错或算对。该具体型号首次月份未取得独立真值，不填猜测。|
|惠普|惠普 HyperX 暗影精灵PRO 15.3英寸游戏笔记本电脑 ／ 英特尔® 酷睿™ Ultra 7 255HX 处理器 ／ NVIDIA® GeForce RTX™ 5060 笔记本电脑 GPU|—|无/未核实|不计（弃答或真值未取得）|—|模型弃答，无日期；不将弃答算错或算对。该具体型号首次月份未取得独立真值，不填猜测。|
|惠普|惠普 HyperX 暗影精灵 PRO 16英寸游戏笔记本电脑 ／ 第二代英特尔®酷睿™ Ultra 9-290HX Plus 处理器 ／ NVIDIA® GeForce RTX™ 5060 独立显卡|—|无/未核实|不计（弃答或真值未取得）|—|模型弃答，无日期；不将弃答算错或算对。该具体型号首次月份未取得独立真值，不填猜测。|
|惠普|惠普 HyperX 暗影精灵MAX 16英寸游戏笔记本电脑 ／ 第二代英特尔®酷睿™ Ultra 9-290HX Plus 处理器 ／ NVIDIA® GeForce RTX™ 5070Ti 独立显卡|—|无/未核实|不计（弃答或真值未取得）|—|模型弃答，无日期；不将弃答算错或算对。该具体型号首次月份未取得独立真值，不填猜测。|
|惠普|惠普 战66迷你台式机电脑 ／ 第十三代英特尔® 酷睿™ i5-1335U 处理器 ／ 英特尔® Iris® Xᵉ|—|无/未核实|不计（弃答或真值未取得）|—|模型弃答，无日期；不将弃答算错或算对。该具体型号首次月份未取得独立真值，不填猜测。|
|惠普|惠普 星Book 14英寸 AI 笔记本电脑 ／ 酷睿™5-210H 处理器 ／ 英特尔® 显卡|—|无/未核实|不计（弃答或真值未取得）|—|模型弃答，无日期；不将弃答算错或算对。该具体型号首次月份未取得独立真值，不填猜测。|
|惠普|惠普 战66 16英寸商务笔记本电脑 ／ AMD 锐龙™ AI 7 450 处理器 ／ AMD Radeon™ 860M|—|无/未核实|不计（弃答或真值未取得）|—|模型弃答，无日期；不将弃答算错或算对。该具体型号首次月份未取得独立真值，不填猜测。|
|惠普|惠普 战X 16英寸商务笔记本电脑 ／ 英特尔® 酷睿™ Ultra 7 处理器 356H ／ NVIDIA® GeForce RTX™ 5060 独立显卡|—|无/未核实|不计（弃答或真值未取得）|—|模型弃答，无日期；不将弃答算错或算对。该具体型号首次月份未取得独立真值，不填猜测。|
|惠普|惠普 星Desk 9L台式机电脑 S03-020rcn ／ 英特尔®酷睿™ i3-14100 处理器 ／ 英特尔® UHD 730 集成显卡|—|无/未核实|不计（弃答或真值未取得）|—|模型弃答，无日期；不将弃答算错或算对。该具体型号首次月份未取得独立真值，不填猜测。|
|比亚迪|比亚迪 汉 2023款 DM-i|2023-03|有/否|错|2023-05|[同期5月18日发布汉DM-i冠军版；3月16日为汉EV冠军版与唐DM-i，不能借给汉DM-i。原URL不可访问。](https://auto.sina.com.cn/newcar/2023-05-18/detail-imyuetha5135727.shtml)|
|比亚迪|比亚迪 汉 DM-i 智驾版|2025-02|无/否|对|2025-02|[同期2025-02-10发布稿精确点名汉DM-i智驾版及5配置，不只用全系21款宣传；日期相符，无原依据。](https://www.pcauto.com.cn/nation/4694/46942205.html)|
|比亚迪|比亚迪 汉 2024款 EV|2024-02|无/否|对|2024-02|[同期2月28日比亚迪官博发布转述明确汉EV荣耀版；日期相符，无原依据。](https://www.yicai.com/brief/102007737.html)|
|比亚迪|比亚迪 汉 2024款 DM-p|2024-02|有/未核实|对|2024-02|[同期2月28日上市稿精确包含2024款汉DM-p战神版；日期相符，原URL本次不可访问，未核实。](https://www.autohome.com.cn/news/202402/1293796.html?from=m&platform-key=pc)|
|比亚迪|比亚迪 汉 2024款 DM-i|2024-02|无/否|对|2024-02|[同期2024-02-28转述官博明确汉DM-i荣耀版；日期相符，无原依据。](https://www.yicai.com/brief/102007737.html)|
|比亚迪|比亚迪 汉 2023款 DM-p|2023-03|无/否|错|2023-05|[同期2023-05-18正式发布汉DM-p战神版，非3月汉EV冠军版；无原依据，单列错误。](https://auto.sina.com.cn/newcar/2023-05-18/detail-imyuetha5135727.shtml)|
|比亚迪|比亚迪 汉 2022款 DM-i|2022-04|有/否|对|2022-04|[同期2022-04-10新汉家族发布稿明确DM-i/DM-p，日期相符；模型自称链接为示意，不是确知原链接，原依据不合格。](https://www.autohome.com.cn/news/202204/1242832.html?from=m&platform-key=pc)|
|比亚迪|比亚迪 汉 2023款 EV|2023-03|无/否|对|2023-03|[同期2023-03-16记者从官方获悉当晚发布汉EV冠军版，日期相符；无原依据。](https://www.nbd.com.cn/articles/2023-03-16/2714042.html)|
|比亚迪|比亚迪 夏 2026款 DM-i|—|无/未核实|不计（弃答或真值未取得）|2025-11|[LLM弃答，按要求不算错或对。官方直播目录明确2026款夏于2025-11-04上市发布，正确值独立记录。](https://www.byd.com/cn/live-list/livedetail138)|
|比亚迪|比亚迪 宋Pro DM-i 飞驰版|—|无/未核实|不计（弃答或真值未取得）|2026-04|[LLM弃答，按要求不算错或对。同期2026-04-22稿转述比亚迪官方宣布该精确版本上市；不是普通2026款宋Pro。](https://m.ithome.com/html/941912.htm)|

## 使用判断

这批结果适合作为人工核对候选。样本中存在错月份、把上市月当首次公告月、借系列日期、原URL指向其他商品及date与弃答说明自相矛盾；有URL不等于有可用证据。即使月份准确率较高，也不能把整批直接当作正式发布时间。此实验仅回答填充率和抽样质量，不执行采纳。

## 复现、断点与产物

冻结输入在 baseline-goods.json，实取API响应在 baseline-response.json；原始逐族响应（含原始JSON字符串、model、usage、captured_at、每次attempt）在 responses/，状态在 states/，发送标记在 sent/。这些文件均以字节原样收入 raw-artifacts.tar.gz，sha256清单为 artifact-manifest.json。冻结族与跳过名单、汇总和报告在同目录独立保存，未写正式字段。

```bash
# 如从提交恢复，先解开完整原始文件，再执行；成功族不重发
cd staging/release-full-20261103
tar -xzf raw-artifacts.tar.gz
cd ../..
python staging/release-full-20261103/experiment.py run
python staging/release-full-20261103/experiment.py assemble
python staging/release-full-20261103/review_verdicts.py
python staging/release-full-20261103/validate_experiment.py
python staging/release-full-20261103/make_report.py
```

如circuit.json存在，先检查原因，再显式传 --resume-after-circuit；不自动越过熔断。本次实际执行是否完整以summary/validation为准，不以复现命令冒充执行记录。

相关测试见 tests.log；抽样冻结和来源抓取记录在review-queue.json、verification/；生产不变量与全局派发间隔见validation.json。
