# L3 全量收尾（2026-11-05）

已处理全部 **1,624 行／1,619 唯一 ID**。命中 **44 行：33 day、11 month**，未命中 1,580 行：1,552 行未取得精确型号月份声明，28 行有提及但市场/事件/代际/变体不满足条件；28 行另有人工复核记录。命中包含已有日期复核，单独 L3 净新增覆盖 1 行，不能把 44 写成净新增。

完整官方新闻目录 249 篇正文全部抓取成功；加上目录、历程、IR、官方文章页面，共 304 个唯一 URL（294 HTTP 200、10 IR HTTP 403）。日期断言来自 151 条已审核的官方声明，每份归档原文哈希及引文均校验成功；被拦的新请求与历史有效原文分开记录。请求起点间隔实测不低于 2.1 秒，含重定向。型号年份、文档元数据、第三方唯一来源不产生日期。

- 全量逐行结果：[full/result.json](full/result.json)
- 网络响应与间隔：[full/captures/2026-11-05/requests.jsonl](full/captures/2026-11-05/requests.jsonl)
- 28 行排除复核：[full/reviewed-mentions.json](full/reviewed-mentions.json)
- 日期、品牌矩阵和十条抽查：[日报](../2026-11-05.md)
- 已配置本机 cron，每日北京时间 03:17；首次下一次 2026-11-06 03:17。

下方保留首轮 102 条优先品类研究记录，仅作历史，不代表本轮全量范围或结论。

---

# L3 小米官方路径实测（2026-11-05）

范围按线上 goods.json（3,682 行）筛选：所有小米笔记本/游戏本（包括“旧款机型”中的电脑）、显示器、鼠标/键鼠套装、宠物用品候选。排除独立滤芯/贴纸/屏幕服务。不是只检查用户购买的三条。

本轮范围 **102 条**；新增可发布的精确型号发布日期 **0**。这意味着“本轮没有拿到满足要求的证据”，绝不等于“官方没有此信息”。每条保留 `missing_reason=not_obtained` 和 URL 请求记录；HTML 200、页面备案日期、文件测试日期、新闻入库时间、存档日期和型号年份均不能填入发布日期。

已探测：官方中国商品页；官方新闻底层 JSON；官方发展历程；官网产品专题；历史官方 blog 路径；官方新闻链接的 press kit。复用了上一轮官方新闻目录 249 条的研究背景（既有工作已实测过该新闻接口，因此不能把此路径宣传成从未尝试）。本轮重新联网抓取，不把旧缓存伪装为新请求。

找到一个有效的官方日级证据，但未写入任何商品：

- URL：<https://go.buy.mi.com/global/discovery/land?from=pc&id=1668>
- 定位：`data.content` 的 `RedmiBook Pro` 段。
- 原句：`Official sales start from March 4th, 2021 via all Xiaomi official channels in Mainland China.`
- 为什么能判 day：正文明确日期是 2021-03-04，事件为中国大陆正式销售，并非新闻 `add_time`。
- 为什么不能补给现有笔记本：同段限定 `11th Gen Intel Core H35`、14/15 英寸，现库的 Redmi Book Pro 候选是 Ultra 2024/2025/2026 代，不能跨代继承。旧小米笔记本也不能冒充这代 RedmiBook。
- 官方 press kit：<https://drive.google.com/drive/folders/16J9lT8YIxiLrb2ySSX30JPAvG1miZuf-?usp=sharing>；这是 2021 代产品图片素材，不作为其他代际的日期。

用户设备关键边界：Redmi G27Q 2025 的版本年份不是发布日期；标准底座、多功能底座、节能版、240Hz 不能互相继承。米家饮水机 2、除菌版、饮水机+喂食器套装不能互相继承。小米无线键鼠舒适版公开报道存在不同“上市/开售”日期，未取得合格官方原文时不强填。

复现：

```sh
python3 scripts/release_lane_xiaomi.py --goods /path/to/online-goods.json
# 仅重放已抓原响应，不伪称联网成功：
python3 scripts/release_lane_xiaomi.py --goods /path/to/online-goods.json --reuse-captures
```

集成接口：`run(rows, output_dir=None, refresh=True)` 返回 `lane/total/candidates/records/captures/discoveries`。`candidates` 只收可发布断言，本轮为空；`discoveries` 是不能直接发布的研究结果。每次抓取均写响应体、SHA-256、时间、HTTP 状态和最终 URL。全量原结果见 `result.json` 与 `data/official/xiaomi-priority-release-evidence.json`。

实测统计：83 个唯一 URL 请求（82 个 HTTP 200，1 个历史 blog TLS 连接失败）。102 个商品均未获得精确型号的月级或日级合格新断言；无一标记为“官方无此信息”。源码边界测试 3 passed，日志见 `tests.log`。
