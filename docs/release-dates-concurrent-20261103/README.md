# 并发 LLM：100族真实验收

**速度验收通过，质量验收未通过，未启动2813族全量。新增发布0。**

100次真实请求全部返回非空正文，71弃答、28个格式合法日期候选、1个非法日期字符串（2017-05或null）。6路worker、全局4 QPS、连续3次429熔断；实测429=0，退避=0秒。

整批墙钟 **38.327秒**；输入28741、输出11597、总40338 tokens。第六轮38.459秒/20族=每族1.922957秒；100族串行等效192.296秒，本次加速 **5.017倍**。样本类别和响应长度不同，这是按用户指定基线计算的观测比值，不是同输入A/B测试；不线性承诺全量耗时。

原始逐族响应、实际model、usage、captured_at和attempts在 responses/；状态在states/，原始响应未删减，未把弃答算成功日期。首次运行详见sessions/；没有补问或修正后重抽。抽样在检索前冻结，选出全部4个非富士非空输出（含格式非法）并按固定seed抽16个富士，包含门禁所需3个富士样本。惠普25/25弃答，没有可评估日期，不能记成0%准确或100%正确。

|品牌|100族中的请求/弃答/合法日期/非法|20族审计数|月份相符|型号+月份+原依据合格|放行|
|---|---|---:|---|---|---|
|小米|25/22/2/1|3|1/3=33.33%|0/3=0%|禁用|
|大疆|25/24/1/0|1|1/1=100.00%|0/1=0%|禁用|
|惠普|25/25/0/0|0|不可评估|不可评估|禁用|
|富士|25/0/25/0|16|13/16=81.25%|0/16=0%|禁用|

月份准确率保留原始非法输出作为错误：小米1/3；只看格式合法日期为1/2。富士13/16=81.25%，单看月份也未达到90%。所有原引用均未完成“型号与首次月份”支持核验，不能拿事后找到的独立链接替换原引用来抬分。403/DNS失败表示本次无法取证，不断言日期不存在；即使官网存在同型号也不等于支持月份。门禁的可重复10%子样本另存reviews.json/brand-gates.json，均禁用。

|型号族|LLM年月|独立核对年月/依据|日期对错及原引用结论|
|---|---|---|---|
|红米5 Plus|2017-12|[2017-12](https://m.21jingji.com/article/20171207/herald/39632cbe1b2efc81da5c7d434135357a.html)|月份相符；原引用跳转 err.www.mi.com/04.html；无月份原文。|
|REDMI Pad 2|2025-08|[2025-06](https://www.mi.com/my/support/faq/details/KA-572986/)|错误；候选填2025-08，且abstention_reason称无法确定月份；原产品页不支持其月份。|
|小米无人机4K版套装|2017-05或null|[2017-03](https://www.fimi.com/cn/about-fimi.html)|错误；date为“2017-05或null”，格式非法；无url/quote；制造商里程碑为2017-03。|
|DJI Focus Pro LiDAR|2024-04|[2024-04](https://www.mynewsdesk.com/uk/dji/pressreleases/dji-pro-launches-next-generation-tools-offering-swift-setup-intuitive-operation-seamless-integration-and-extended-focus-control-3315434)|月份相符；DJI自行发布的新闻稿支持月份与LiDAR组件；原引用404，不能事后替换抬分。|
|FUJIFILM X-S20|2023-05|[2023-05](https://www.fujifilm.com/ae/en/news/hq/9421)|月份相符；月份正确，6月为开售；原引用仅产品页、quote空，模型承认未核原句；直抓403，原依据未证实月份。|
|XF50mmF2 R WR|2017-01|[2017-01](https://www.dpreview.com/news/2919368831/fujifilm-expands-weather-resistant-lens-selection-with-xf-50mm-f2-r-wr/)|月份相符；现场新闻及内嵌原厂新闻稿支持1月公告；2月开售；原引用产品页未核月份。|
|XF70-300mmF4-5.6 R LM OIS WR|2021-01|[2021-01](https://www.fujifilm-x.com/global/news/fujifilm-announces-new-fujinon-xf70-300mmf4-5-6-r-lm-ois-wr-lens/)|月份相符；官方页头2021-01-27，正文年份2020疑为笔误；页头及同期报道支持2021-01公告，3月开售；原产品页月份未核准。|
|XF90mmF2 R LM WR|2015-05|[2015-05](https://fujifilm-korea.co.kr/support/notice/id/7173)|月份相符；官方分站5月公告、7月开售；原引用fujifilm.com.cn无www路径DNS失败；原句空。|
|XC35mmF2|2020-02|[2020-01](https://www.dpreview.com/news/4262945623/fujifilm-announces-more-affordable-xc-35mm-f2-prime-lens/)|错误；首次公告1月；候选2月是开售月，event=announcement时错误；原产品页无公告引文。|
|XF60mmF2.4 R Macro|2012-01|[2012-01](https://thelensdb.com/lenses/fujifilm-super-ebc-fujinon-xf-60mm-f24-aspherical-r-macro-2012)|月份相符；保留的原厂X-Pro1新闻稿明确包含该镜头；不能仅借机身日期。原产品页原句空，月份未回指。|
|FUJIFILM X-E5|2025-06|[2025-06](https://www.fujifilm.com/us/en/news/digital-cameras/fujifilm-introduces-fujifilm-x-e5-mirrorless-digital-camera)|月份相符；官方6月公告；8月为发售，原产品页/空quote未支持月份。|
|XF35mmF2 R WR|2015-10|[2015-10](https://www.fujifilm.co.jp/corporate/news/articleffnr_1016.html)|月份相符；官方10月21日公告；候选reason说15日但年月相符；原fujifilm.com.cn/2015/1015路径DNS失败，原依据未证实。|
|XF30mmF2.8 R LM WR Macro|2022-09|[2022-11](https://www.fujifilm-x.com/en-gb/news/fujifilm-launches-fujinon-xf30mmf2-8-r-lm-wr-macro/)|错误；候选2022-09误把X-H2同期事件混进来，正式产品公告为11月；原产品页无引文。|
|XF14mmF2.8 R|2012-09|[2012-09](https://www.dpreview.com/articles/9897321674/fujufilm-launches-xf-18-55mm-f2-8-4-0-ois-semi-fast-standard-zoom-and-xf14mm-f2-8-21mm-equivalent/)|月份相符；按正式产品公告9月核对；此前6月路线图已预告开发，不能称毫无更早信息；原产品页无月份引文。|
|XC15-45mmF3.5-5.6 OIS PZ|2018-01|[2018-01](https://www.chem-t.com/fax/images/tmp_file3_1517391530.pdf)|月份相符；存档原厂新闻稿支持1月公告，非3月单镜开售；原产品页无日期原句。|
|XF8mmF3.5 R WR|2023-05|[2023-05](https://www.fujifilm.com/kr/en/news/hq/9420)|月份相符；官方5月公告，6月29日开售；原产品页无原句且未核月份。|
|XF200mmF2 R LM OIS WR|2018-07|[2018-07](https://dc.watch.impress.co.jp/docs/news/1133999.html)|月份相符；原始发布报道支持7月公告，10月开售；候选reason提X-T100同期不准确，原产品页无月份支持。|
|XF18mmF1.4 R LM WR|2021-04|[2021-04](https://www.fujifilm-x.com/en-sg/news/fujifilm-announces-new-fujinon-xf18mmf1-4-r-lm-wr-lens/)|月份相符；官方4月公告，5月开售；原产品页无原句且模型承认无法回指。|
|XF23mmF2 R WR|2016-07|[2016-08](https://dc.watch.impress.co.jp/docs/news/1016454.html)|错误；现场发布报道为8月，10月开售；候选7月混淆X-T2，原引用fujifilm.com.cn路径DNS失败。|
|XF150-600mmF5.6-8 R LM OIS WR|2022-05|[2022-05](https://www.fujifilm-x.com/en-us/news/fujifilm-announces-fujinon-xf150-600mmf5-6-8-r-lm-ois-wr/)|月份相符；官方5月公告，7月开售；原产品页未回指月份，quote空。|

原始evidence链接、quote、reason及独立核对原文均完整见audit-review.json。20族15/20月份相符（75%），含证据合格0/20。并非全族随机总体准确率置信保证。

## 当前线上四列表（本轮增量0）

来自2026-11-03T07:57:50.466839+00:00实取/api/goods；不是全量跑完后的结果。此前跨源核查已改变第六轮历史覆盖，本次没有修改数据输入。日期字段覆盖688/3968=17.34%。

|品牌|真源 official+third_party|hidden|LLM|仍缺|
|---|---:|---:|---:|---:|
|Apple|419|0|39|182|
|比亚迪|0|0|0|14|
|大疆|107|0|0|676|
|富士|14|0|0|49|
|惠普|0|0|0|218|
|小米|106|0|0|2141|
|小米汽车|3|0|0|0|
|合计|649|0|39|3280|

LLM日期字段39/3968=0.98%，占688个非空日期5.67%；本轮新增LLM占比0%。上述四列沿用coverage()按非空date计数，包含被交叉核查禁用的留档日期，不应当成可用于判断的覆盖；线上另有30条release usage=disabled，剔除禁用项后可用日期664/3968=16.73%。

## 3个线上真实ID摘录

这是既有字段契约的实时检查，本轮没有新增候选上线，不声称新补齐已发布。

[GLOBAL:apple_support:model:111340](https://spend.snewbie.site/api/goods/GLOBAL%3Aapple_support%3Amodel%3A111340?release_check=2026-11-03T07%3A57%3A50.466839%2B00%3A00)

```json
{
  "date": "2023-02",
  "source": "llm",
  "usage": "disabled",
  "internal_only": true,
  "display_allowed": false,
  "estimate_notice": "按型号世代估算"
}
```

[GLOBAL:apple_support:model:111832](https://spend.snewbie.site/api/goods/GLOBAL%3Aapple_support%3Amodel%3A111832?release_check=2026-11-03T07%3A57%3A50.466839%2B00%3A00)

```json
{
  "date": "2023-09",
  "source": "llm",
  "usage": "reference",
  "internal_only": true,
  "display_allowed": false,
  "estimate_notice": "按型号世代估算"
}
```

[GLOBAL:apple_support:model:111838](https://spend.snewbie.site/api/goods/GLOBAL%3Aapple_support%3Amodel%3A111838?release_check=2026-11-03T07%3A57%3A50.466839%2B00%3A00)

```json
{
  "date": "2023-02",
  "source": "llm",
  "usage": "disabled",
  "internal_only": true,
  "display_allowed": false,
  "estimate_notice": "按型号世代估算"
}
```

## 断点续跑与停机

新计划先不带--run冻结families.json/plan.json，再带--run执行。--concurrency默认6（1..6），--qps默认4（0..4）；降低参数可控速。SIGINT/SIGTERM停止新增请求，等待已发送响应落盘。成功ok或已有response永不重发；429仅重试当前族，退避1/2/4/8秒并尊重Retry-After（取较大值），累计重试次数与全局连续429计数跨重启保留。进程级flock阻止同目录双进程派发；全部共享completion顺序429计数，连续3次触发持久circuit.json，已在途的最多6个请求允许完成，后续不再发送。显式--resume-after-circuit检查后重启才解除，单次成功响应不会解除已开的熔断。

状态pending/sent/ok/failed与响应使用fsync+原子替换落盘。异常中断的sent（无已保存response）续跑时标记interrupted_usage_unknown，再请求该未完成族；无法在网关不支持幂等键的情况下保证此类未知在途不重复计费，已成功落盘的族不受影响。明确非429失败终结failed，不做未经授权的网络/解析重试。

本次同目录再跑100族续跑验收实测0新增请求；结果见resume-check.json。100族质量验收failed，禁止把后续命令当成本次全量执行记录。

```bash
PYTHONPATH=src:scripts python3 scripts/release_family_llm.py \
  --rows _data/public/goods.json --out docs/release-dates-concurrent-20261103 \
  --run --limit 100 --concurrency 6 --qps 4
```

测试基线与最终结果见tests-baseline.log/tests-final.log；official/LLM输入hash及已有release不变量见invariants.json。

完整回归：基线387 passed；本轮395 passed，1个原有插件warning，无新增红项。本轮提交只含并发脚本、对应测试与本目录验收产物。
