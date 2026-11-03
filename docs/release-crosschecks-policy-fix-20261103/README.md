# 交叉核验证据规则修正

本次对原先冻结的 39 条 third_party 独立模型回答重放新规则，没有重新请求模型。保留日期、身份、提示词、原始响应和 SHA-256，避免随机换一轮回答掩盖规则问题。全部 39 条对比见 [comparison-39.json](comparison-39.json)，5 条完整原证据、原文、LLM 回答与最终处置见 [conflicts-5.json](conflicts-5.json)。旧报告作为历史保留。

## 规则

- `checks[].verdict` 只记录数值差异，不能直接当裁决；`effective_verdict` 是按证据规则计算的有效判定。
- LLM 的 `reason` 不算引用；必须有独立 `evidence.url` 或 `evidence.quote` 才有资格提出异议。无引用的不同答案保留审计，但有效判定为 `unverified`，不降低置信度，不否决已有独立一致结果。
- 有原文、链接、采集哈希及时间的当月报道优先于未经核实的模型记忆/引文。报道日期取 `evidence.published_at` 或原文中的明确日期，不取抓取日期。
- 可回指的冲突一般保留原日期，`internal_only=true, display_allowed=false`。只有双方都有采集证据，且模型一方已由人工核对其型号、市场、事件和日期（`evidence.verified=true`），才置空并 `manual_review_required=true`。组装器只接收模型的 URL/quote，绝不接受模型自封 `verified`。
- 未获得独立佐证的第三方日期继续使用既有的内部参考门禁；弃答和无依据异议的待遇一致。没有把无依据异议用作隐藏日期的额外理由。`usage=disabled, display=null` 用于阻止现有客户端回退展示年份。
- 保留全部第三方候选和证据。旧的无依据冲突检查保留，但用新规则重算决策；已经置空的旧数据从原始断言恢复。经核实的硬冲突不会被后续一句一致回答抹掉。

## 39 条统计

|口径|corroborated|disagreement|conflict|弃答/未核实|置空|
|---|---:|---:|---:|---:|---:|
|旧规则|14|0|5|20|5|
|本次原始回答数值比较|14|0|5|20（真实弃答）|—|
|本次有效判定|14|0|0|25（20 弃答 + 5 无依据异议）|0|

不将 5 条无依据异议冒充模型弃答，也不将其计为已核实一致。14 条 corroborated 的品牌分布仍是 Apple 1、大疆 2、富士 3、小米 8。5 条冲突均恢复为原日期并仅内部保留，没有新增硬证据冲突。

## 5 条逐项处置

|商品 / ID 尾号|原依据原文及报道日期|LLM 日期及依据|新判定|最终处置|
|---|---|---|---|---|
|米家高速吹风机 H501 / 18520|[IT之家](https://www.ithome.com/0/695/691.htm)，2023/5/27：「米家高速吹风机 H501 今年 5 月上市」|2023-08；URL、quote 均 null|无依据异议忽略，unverified|恢复 2023-05，internal_only，display_allowed=false，无需硬冲突人工复核|
|Xiaomi Book Pro 14 / 23472|[IT之家](https://www.ithome.com/0/930/804.htm)，2026/3/19：「小米 2026 春季新品发布会今晚（3 月 19 日晚）如期举行」「小米笔记本 Pro 14 和小米手表 S5 两款新品亦相继登台」；正文明确第三代酷睿 Ultra X7 358H|2022-07；URL、quote 均 null；理由描述的是 2022 款、12 代酷睿|无依据异议忽略，unverified；理由与当期产品代际不符|恢复 2026-03，internal_only，display_allowed=false，无需硬冲突人工复核|
|Xiaomi Pad 9 Pro / 25445|[IT之家](https://www.ithome.com/1/006/476.htm)，2026/9/23：「就在今天（9 月 23 日）19:00，小米秋季新品发布会如期举行」「小米平板 9 Pro 则采用 12.5 英寸大屏」|2024-02-22；evidence=null；理由明确说的是 Pad 6S Pro 12.4，且“无法确认…故弃答”|无依据异议忽略，unverified；不把别的型号日期视为反证|恢复 2026-09，internal_only，display_allowed=false，无需硬冲突人工复核|
|Xiaomi Pad 9 / 25446|[同篇 IT之家](https://www.ithome.com/1/006/476.htm)，2026/9/23：「紧接着登场的是小米平板 9 系列」「小米平板 9 配备 11.2 英寸的屏幕」|2023-11-29；URL、quote 均 null|无依据异议忽略，unverified|恢复 2026-09，internal_only，display_allowed=false，无需硬冲突人工复核|
|小米活塞耳机 / 5059|[IT之家](https://www.ithome.com/0/047/461.htm)，2013/6/24：「6月24日晚间消息，小米活塞耳机价格正式公布：99元。将于6月28日开放首轮购买。」|2013-09；URL、quote 均 null|无依据异议忽略，unverified；当月开售原文优先|恢复 2013-06，internal_only，display_allowed=false，无需硬冲突人工复核|

H501 的原日期、medium 置信度、third_party 来源、原文、链接、哈希及采集时间全部保留。5 月当期稿件的明确上市陈述优先于没有引用的“8 月发布会”模型记忆。`display_allowed=false` 是这次要求的内部保留处置，不能解释为模型证实原日期有错。

## 复现与验证

```bash
python3 docs/release-crosschecks-policy-fix-20261103/replay.py --catalog /path/to/goods-before.json
PYTHONPATH=src:scripts python3 -m pytest -q
```

最新数据分支的 3968 条本地重建：全部非 release 字段逐值不变，39 条原证据逐值不变，重建幂等。基线全量 395 passed；修改后全量 401 passed。离线 393 passed / 8 deselected。保留原有第三方证据和原始响应存档；仅补齐组装时丢弃的 evidence 字段。

线上发布结果与真实接口摘录在发布完成后记录于本目录。
