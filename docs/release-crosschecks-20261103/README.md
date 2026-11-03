# 全库第三方日期独立核验

每条独立请求只含品牌、品类、型号、市场和事件；不含原日期、来源网页、原文、既有 LLM 答案或候选族 key。提示词见 prompts/，身份冻结于 identities.json；完整后端响应、usage、时间、请求状态见 responses/、sent/、states/。151 次请求：39 条 third_party + 112 条既有 LLM 候选（包括先前门禁禁用的 72 条，不将其重新启用）。全部原始日期与原证据保留在 baseline-dates.json，模型结果永远 source=llm。

规则：有任一月粒度时两侧按年月对齐，同月为 0，跨月按绝对月差 × 30 天；两侧均到日才按实际日差。≤14 corroborated，15–45 disagreement，>45 conflict 且 release.date=null。保留 release.checks[]，含被比较方 source/date；LLM 两两也比较。official 优先且保留冲突检查；原日期候选未改写。无独立日期（弃答）单列 unverified，不冒充日期冲突或一致。

disagreement 和 unverified 保留原日期给内部参考，但 display_allowed=false、internal_only=true、display=null、usage=disabled（兼容现有客户端，禁止年份回退显示）；conflict 另置空 date 并标 manual_review_required。旧冲突检查跨重建保留；修复必须显式人工处理，不靠重跑新结果抹除历史。

## 第三方逐品牌统计（商品条目与候选均为 39）

|品牌|总数|corroborated|disagreement|冲突置空|弃答隐藏|
|---|---:|---:|---:|---:|---:|
|Apple|1|1|0|0|0|
|大疆|2|2|0|0|0|
|富士|3|3|0|0|0|
|小米|33|8|0|5|20|
|小米汽车|0|0|0|0|0|
|惠普|0|0|0|0|0|
|比亚迪|0|0|0|0|0|

## 对照明细（全部 39 条；另附 comparison-30.csv）

|型号|原日期|来源|LLM独立日期|差值天数|判定|
|---|---|---|---|---:|---|
|米家高速吹风机 H501|2023-05|[third_party](https://www.ithome.com/0/695/691.htm)|2023-08|90|conflict|
|iPhone 14|2022-09|[third_party](https://www.gsmarena.com/apple_iphone_14-11861.php)|2022-09-16|0|corroborated|
|Osmo Pocket 3|2023-10|[third_party](https://info.xitek.com/allpage/news/202310/25-365451.html)|2023-10-26|0|corroborated|
|Osmo Pocket 3 全能套装|2023-10|[third_party](https://info.xitek.com/allpage/news/202310/25-365451.html)|2023-10-26|0|corroborated|
|FUJIFILM X-H2|2022-09|[third_party](https://www.ithome.com/0/640/150.htm)|2022-09-29|0|corroborated|
|FUJIFILM X-T5|2022-11|[third_party](https://www.ea360.com/contents/150/13460.html)|2022-11|0|corroborated|
|FUJIFILM X100VI|2024-03|[third_party](https://www.ithome.com/0/751/018.htm)|2024-03|0|corroborated|
|Xiaomi双磁超动态单元耳机|2023-05|[third_party](https://www.ithome.com/0/694/460.htm)|弃答|—|unverified|
|REDMI Buds 6 活力版|2024-05|[third_party](https://www.ithome.com/0/769/177.htm)|弃答|—|unverified|
|REDMI Buds 6 青春版|2024-10|[third_party](https://www.ithome.com/0/803/996.htm)|弃答|—|unverified|
|REDMI Buds 6|2024-09|[third_party](https://www.ithome.com/0/798/668.htm)|2024-09-26|0|corroborated|
|REDMI Buds 7S|2025-04|[third_party](https://www.ithome.com/0/844/491.htm)|弃答|—|unverified|
|Xiaomi Civi 5 Pro|2025-05|[third_party](https://www.ithome.com/0/855/282.htm)|2025-05-22|0|corroborated|
|小米AI眼镜|2025-06|[third_party](https://www.ithome.com/0/863/991.htm)|2025-06-26|0|corroborated|
|Xiaomi Watch S4 41mm|2025-06|[third_party](https://www.ithome.com/0/863/991.htm)|2025-06|0|corroborated|
|REDMI K Pad|2025-06|[third_party](https://www.ithome.com/0/863/991.htm)|2025-06-26|0|corroborated|
|Xiaomi 开放式耳机 Pro|2025-06|[third_party](https://www.ithome.com/0/863/991.htm)|2025-06-26|0|corroborated|
|REDMI K80 至尊版|2025-06|[third_party](https://www.ithome.com/0/863/991.htm)|2025-06-26|0|corroborated|
|Xiaomi 骨传导耳机2|2025-07|[third_party](https://www.ithome.com/0/869/534.htm)|弃答|—|unverified|
|REDMI Buds 8 Pro|2026-01|[third_party](https://www.ithome.com/0/917/637.htm)|弃答|—|unverified|
|Xiaomi Buds 6|2025-12|[third_party](https://www.ithome.com/0/908/038.htm)|弃答|—|unverified|
|Xiaomi 17 Ultra|2025-12|[third_party](https://www.ithome.com/0/908/038.htm)|弃答|—|unverified|
|Xiaomi 17 Ultra 徕卡版|2025-12|[third_party](https://www.ithome.com/0/908/038.htm)|2025-12-25|0|corroborated|
|REDMI Buds 8 青春版|2026-02|[third_party](https://www.ithome.com/0/923/927.htm)|弃答|—|unverified|
|REDMI Buds 8 活力版|2026-03|[third_party](https://www.ithome.com/0/926/051.htm)|弃答|—|unverified|
|Xiaomi Book Pro 14|2026-03|[third_party](https://www.ithome.com/0/930/804.htm)|2022-07|1320|conflict|
|REDMI Buds 8|2026-04|[third_party](https://www.anzhuo.cn/review/p_66882)|弃答|—|unverified|
|小米手环10 Pro|2026-05|[third_party](https://www.ithome.com/0/953/645.htm)|弃答|—|unverified|
|REDMI 头戴降噪耳机|2026-06|[third_party](https://www.ithome.com/0/970/430.htm)|弃答|—|unverified|
|Xiaomi 耳夹式耳机|2026-05|[third_party](https://www.ithome.com/0/953/645.htm)|弃答|—|unverified|
|Xiaomi 17 Max|2026-05|[third_party](https://www.ithome.com/0/953/645.htm)|弃答|—|unverified|
|Xiaomi 18 Fold|2026-09|[third_party](https://www.ithome.com/0/999/486.htm)|弃答|—|unverified|
|Xiaomi Pad 9 Pro Max|2026-09|[third_party](https://www.ithome.com/0/999/486.htm)|弃答|—|unverified|
|Xiaomi Watch S5 41mm|2026-09|[third_party](https://www.ithome.com/1/006/476.htm)|弃答|—|unverified|
|Xiaomi Pad 9 Pro|2026-09|[third_party](https://www.ithome.com/1/006/476.htm)|2024-02-22|930|conflict|
|Xiaomi Pad 9|2026-09|[third_party](https://www.ithome.com/1/006/476.htm)|2023-11-29|1020|conflict|
|Xiaomi 18 Pro|2026-09|[third_party](https://www.ithome.com/1/006/476.htm)|弃答|—|unverified|
|Xiaomi 18 Pro Max|2026-09|[third_party](https://www.ithome.com/1/006/476.htm)|弃答|—|unverified|
|小米活塞耳机|2013-06|[third_party](https://www.ithome.com/0/047/461.htm)|2013-09|90|conflict|

## 置空与降级/弃答清单

[完整可回看 JSON](manual-and-internal.json) 含 ID、原日期、独立日期、原始响应路径与原因；也含原先已被门禁禁用的 LLM 候选，并标 published 区分。以下列出本轮实际公开库受影响项。

- **米家高速吹风机 H501** `CN:mi_cn:product:18520`：conflict；2023-05 → 2023-08。米家高速吹风机 H501 于2023年8月小米发布会亮相，并在中国大陆小米商城等渠道同期开售；公开资料通常记为2023年8月上市/开售。未混淆为后续 H501 SE 等衍生型号。
- **MacBook Pro（14 英寸，2023 年）** `GLOBAL:apple_support:model:111340`：disagreement；2023-02 → 2023-01。Apple 于 2023 年 1 月 17 日发布搭载 M2 Pro/M2 Max 的 14 英寸与 16 英寸 MacBook Pro，中国大陆官网同日开放订购，1 月 19 日起正式发售。因此指定市场 CN 的首次正式开售日期为 2023-01-19。
- **MacBook Pro（16 英寸，2023 年）** `GLOBAL:apple_support:model:111838`：disagreement；2023-02 → 2023-01-19。Apple 于 2023 年 1 月 17 日发布搭载 M2 Pro/M2 Max 的 14/16 英寸 MacBook Pro，中国大陆官网显示 1 月 19 日起接受订购/发售；该日期对应中国市场的首次正式开售。
- **HomePod (第二代)** `GLOBAL:apple_support:model:111843`：disagreement；2023-02 → 2023-01-18。Apple 于 2023 年 1 月 18 日发布第二代 HomePod，并宣布中国大陆为首发市场之一，同日开启订购；中国大陆官网显示当日可订购、2 月 3 日起发货。按“首次正式开售（可下单购买）”口径，中国市场的 availability 为 2023-01-18；若将“开售”严格理解为到货/发货日，则为 2023-02-03，存在口径歧义。
- **iPad Pro 11 英寸 (第 1 代)** `GLOBAL:apple_support:model:111974`：conflict；2018-11 → 2020-03-25。iPad Pro 11 英寸（第1代）于2018年10月30日发布，2018年11月7日在美国等首批市场开售；中国大陆行货的首次正式开售日期为2020年3月25日（与2020款iPad Pro同批在中国大陆上市，但该日期对应的是2018款11英寸iPad Pro在中国大陆的首次正式开售）。需注意：2018款11英寸iPad Pro在中国大陆的上市时间晚于全球首发，且与2020款同月开售，存在型号代际混淆风险；此处依据为中国大陆苹果官网当时公布的上市信息。
- **Mac Pro (2019)** `GLOBAL:apple_support:model:118461`：disagreement；2019-12 → 2020-01。Apple 于2019年12月10日宣布新款 Mac Pro（2019）在中国大陆的上市安排，并确认国行版本于2020年1月起正式开售；该日期对应中国大陆市场的首次正式销售，而非全球发布或预售。
- **Xiaomi双磁超动态单元耳机** `CN:mi_cn:product:18501`：unverified；2023-05 → 弃答。无法独立确认“Xiaomi双磁超动态单元耳机”这一具体型号在中国市场的首次正式发布月份/日期；该名称可能对应小米某款耳机所用单元技术描述而非独立可核验的上市型号，存在同名/描述性命名歧义，故弃答。
- **REDMI Buds 6 活力版** `CN:mi_cn:product:20007`：unverified；2024-05 → 弃答。无法独立确认 REDMI Buds 6 活力版在中国大陆的首次正式开售日期；该型号发布与开售信息存在地区/渠道差异，且未联网无法核验官方公告，故弃答。
- **REDMI Buds 6 青春版** `CN:mi_cn:product:20139`：unverified；2024-10 → 弃答。无法独立确认 REDMI Buds 6 青春版在中国大陆的首次正式开售日期；该型号发布与开售信息存在地区/渠道差异，且不能由型号年份或同系列其他产品推算，故弃答。
- **REDMI Buds 7S** `CN:mi_cn:product:21120`：unverified；2025-04 → 弃答。无法独立确认 REDMI Buds 7S 在中国大陆的首次正式开售日期；该型号发布与开售信息不在可靠已知资料中，不能由型号年份或系列日期推算，故弃答。
- **Xiaomi 骨传导耳机2** `CN:mi_cn:product:21588`：unverified；2025-07 → 弃答。无法独立确认小米骨传导耳机2在中国大陆的首次正式开售日期；该产品发布与开售信息可能混淆于同名或同系列不同代型号，且未联网无法核实，故弃答。
- **REDMI Buds 8 Pro** `CN:mi_cn:product:22137`：unverified；2026-01 → 弃答。无法独立确认 REDMI Buds 8 Pro 在中国市场的首次正式发布（announcement）日期。该型号可能尚未发布或资料不足，不能依据型号年份或同系列其他代际产品推算，故弃答。
- **Xiaomi Buds 6** `CN:mi_cn:product:22419`：unverified；2025-12 → 弃答。无法独立确认 Xiaomi Buds 6 在中国市场的首次正式发布（announcement）日期。该型号可能尚未发布或信息不足，不能依据型号年份或系列惯例推算，故弃答。
- **Xiaomi 17 Ultra** `CN:mi_cn:product:22422`：unverified；2025-12 → 弃答。无法确认小米17 Ultra在中国市场的首次正式发布（announcement）日期。该型号属于较新一代数字旗舰，我的独立已知资料中没有可核实的中国发布会日期；不能依据型号年份或CPU年份推算月份，也不应改用全球发布日或其他地区事件。未联网，无法查证，故弃答。
- **REDMI Buds 8 青春版** `CN:mi_cn:product:23260`：unverified；2026-02 → 弃答。无法独立确认 REDMI Buds 8 青春版在中国大陆的首次正式开售日期。该型号发布信息不在可靠已知资料中，且不能由型号年份或同系列其他产品推算，故弃答。
- **REDMI Buds 8 活力版** `CN:mi_cn:product:23261`：unverified；2026-03 → 弃答。无法独立确认 REDMI Buds 8 活力版在中国大陆的首次正式开售日期；该型号发布信息不足，不能由型号年份或同系列其他产品推算，故弃答。
- **Xiaomi Book Pro 14** `CN:mi_cn:product:23472`：conflict；2026-03 → 2022-07。小米于2022年7月4日在中国发布Xiaomi Book Pro 14（2022款，12代酷睿），属于该型号在中国市场的首次正式发布。未将其与后续2024款或全球其他市场发布混淆。
- **REDMI Buds 8** `CN:mi_cn:product:23966`：unverified；2026-04 → 弃答。无法确认REDMI Buds 8在中国市场的首次正式发布月份。该型号可能尚未发布或信息不足，不能依据型号年份或同系列其他代际产品推算，故弃答。
- **小米手环10 Pro** `CN:mi_cn:product:24629`：unverified；2026-05 → 弃答。无法独立确认小米手环10 Pro在中国市场的首次正式发布月份或日期。该型号属于较新的穿戴配件，缺乏可确知的官方发布记录；不能依据型号年份或系列惯例推算，故弃答。
- **REDMI 头戴降噪耳机** `CN:mi_cn:product:24645`：unverified；2026-06 → 弃答。无法独立确认“REDMI 头戴降噪耳机”在中国大陆首次正式开售的具体日期。该名称可能对应不同代际或不同正式型号（如 Redmi Buds 系列或其他头戴式降噪型号），缺乏可唯一锁定的型号标识与发布/开售记录；不能由品牌、品类或年份推算月份，故弃答。
- **Xiaomi 耳夹式耳机** `CN:mi_cn:product:24647`：unverified；2026-05 → 弃答。无法独立确认“Xiaomi 耳夹式耳机”这一具体型号在中国市场的首次正式发布月份/日期；该名称可能对应不同代际或不同市场命名，且未联网无法核验官方发布记录，故弃答。
- **Xiaomi 17 Max** `CN:mi_cn:product:24648`：unverified；2026-05 → 弃答。无法确认小米在中国市场正式发布过名为 Xiaomi 17 Max 的机型；该型号不在已知的小米17系列发布信息中，可能为不存在或误传型号，故弃答。
- **Xiaomi 18 Fold** `CN:mi_cn:product:25299`：unverified；2026-09 → 弃答。截至我的知识截止时间，小米尚未发布 Xiaomi 18 Fold，也没有该型号在中国市场首次正式发布的独立可核实日期。无法从型号年份或前代产品推算，故弃答。
- **Xiaomi Pad 9 Pro Max** `CN:mi_cn:product:25324`：unverified；2026-09 → 弃答。无法确认小米在中国市场正式发布过名为 Xiaomi Pad 9 Pro Max 的平板型号；该名称与已知的小米平板产品线（如 Xiaomi Pad 6 Pro、Pad 6 Max 等）不符，疑似不存在或命名有误，故弃答。
- **Xiaomi Watch S5 41mm** `CN:mi_cn:product:25419`：unverified；2026-09 → 弃答。无法确认小米在中国市场正式发布过名为 Xiaomi Watch S5 41mm 的穿戴产品；该型号身份本身存疑，且不能由型号年份或同系列其他尺寸/代际推算发布日期，故弃答。
- **Xiaomi Pad 9 Pro** `CN:mi_cn:product:25445`：conflict；2026-09 → 2024-02-22。小米于2024年2月22日在中国发布Xiaomi Pad 6S Pro 12.4；但所给型号“Xiaomi Pad 9 Pro”并非已知的小米平板型号，无法确认该型号在中国市场的首次正式发布，故弃答。
- **Xiaomi Pad 9** `CN:mi_cn:product:25446`：conflict；2026-09 → 2023-11-29。小米于2023年11月29日在中国举行的Redmi十周年暨K70系列发布会上正式发布Xiaomi Pad 9（小米平板9），该日期为发布会当日，属首次正式发布而非开售。
- **Xiaomi 18 Pro** `CN:mi_cn:product:25524`：unverified；2026-09 → 弃答。截至我的知识截止时间，小米尚未发布 Xiaomi 18 Pro，也没有该型号在中国市场首次正式发布的独立可核实日期；无法从型号年份或前代发布时间推算，故弃答。
- **Xiaomi 18 Pro Max** `CN:mi_cn:product:25526`：unverified；2026-09 → 弃答。截至我的知识截止时间，小米尚未发布 Xiaomi 18 Pro Max，也没有该型号在中国市场首次正式发布的任何可靠信息。无法确认该产品是否存在或已发布，因此弃答，不推测日期。
- **小米活塞耳机** `CN:mi_cn:product:5059`：conflict；2013-06 → 2013-09。小米活塞耳机（第一代）于2013年9月随小米3发布会推出，并在小米官网正式开售；公开资料通常记为2013年9月上市。具体开售日无法独立确证到日，故仅给到月。

模型结果是独立知识输出，未联网；不宣称网页原文已验证或日期一定正确。尤其 Xiaomi Pad 9 Pro 的响应虽填 date，但理由自称弃答并提到其他型号，按其原始日期差判冲突、置空并列人工核查，不把替代型号日期入库。Xiaomi Book Pro 14 指向 2022 款，同名代际歧义也留空。

## 复查与验证

`PYTHONPATH=src:scripts python3 docs/release-crosschecks-20261103/make_report.py` 可重建报告；运行 prepare/run 需要新的目录，已有 sent 标记禁止重发。数据发布在统一 finalize 中重放，发布门禁含新测试；不改变商品 ID、参数、价格、图片等非 release 字段。

原始调用包：[raw-call-artifacts.tar.gz](raw-call-artifacts.tar.gz)，解包后即为上述 prompts/responses/sent/states 目录。完整商品基线可按 [baseline-manifest.json](baseline-manifest.json) 的 data commit 重取；商品日期/身份的独立基线直接保存在 [baseline-dates.json](baseline-dates.json)。 [audit.json](audit.json) 记录 151 次 HTTP 200、151 个响应哈希与提示词哈希验证，以及 token usage 总计 50,067。

## 发布与线上验收

代码提交 `c8eee496374b1b3efb32adc4d5915e411d1362ff`。本地全量测试 **387 passed**（基线 371 passed）；GitHub 离线 **379 passed / 8 deselected**；发布门禁 **94 passed**。[真实发布任务](https://github.com/null-object-0000/goodsdex/actions/runs/41597569806)：success。 [published-data.json](published-data.json) 记录 data 提交和 SHA-256，3968 条与本地预期逐值相等，非 release 字段逐值不变。 [client-verification.json](client-verification.json) 用现有客户端日期展示函数检查 30 条受影响记录，均不产生年份/月显示。

[线上完整验证](online-verification.json)：整库与真实发布集逐值相等，10 个真实详情接口 release 对象逐值相等。下列是 3 个真实 ID 的 `/api/goods/<id>` 返回摘录（只省略旁支字段）。

```json
[
  {
    "id": "CN:mi_cn:product:18520",
    "name": "米家高速吹风机 H501",
    "url": "https://spend.snewbie.site/api/goods/CN%3Ami_cn%3Aproduct%3A18520?release_check=2026-11-03T07%3A50%3A40.003316%2B00%3A00",
    "release": {
      "date": null,
      "source": "third_party",
      "corroborated": false,
      "crosscheck_status": "conflict",
      "display_allowed": false,
      "checks": [
        {
          "source": "third_party",
          "date": "2023-05",
          "delta_days": 0,
          "verdict": "original"
        },
        {
          "source": "llm",
          "date": "2023-08",
          "delta_days": 90,
          "verdict": "conflict"
        }
      ]
    }
  },
  {
    "id": "CN:mi_cn:product:21298",
    "name": "Xiaomi Civi 5 Pro",
    "url": "https://spend.snewbie.site/api/goods/CN%3Ami_cn%3Aproduct%3A21298?release_check=2026-11-03T07%3A50%3A40.003316%2B00%3A00",
    "release": {
      "date": "2025-05",
      "source": "third_party",
      "corroborated": true,
      "crosscheck_status": "corroborated",
      "display_allowed": true,
      "checks": [
        {
          "source": "third_party",
          "date": "2025-05",
          "delta_days": 0,
          "verdict": "original"
        },
        {
          "source": "llm",
          "date": "2025-05-22",
          "delta_days": 0,
          "verdict": "corroborated"
        }
      ]
    }
  },
  {
    "id": "CN:mi_cn:product:25524",
    "name": "Xiaomi 18 Pro",
    "url": "https://spend.snewbie.site/api/goods/CN%3Ami_cn%3Aproduct%3A25524?release_check=2026-11-03T07%3A50%3A40.003316%2B00%3A00",
    "release": {
      "date": "2026-09",
      "source": "third_party",
      "corroborated": false,
      "crosscheck_status": "unverified",
      "display_allowed": false,
      "checks": [
        {
          "source": "third_party",
          "date": "2026-09",
          "delta_days": 0,
          "verdict": "original"
        },
        {
          "source": "llm",
          "date": null,
          "delta_days": null,
          "verdict": "unverified"
        }
      ]
    }
  }
]
```
