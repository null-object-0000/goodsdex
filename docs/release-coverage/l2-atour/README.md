# L2 亚朵星球：SPU详情与官方首发查证

2026-11-05 本轮匿名重新读取官方商城。38 SPU 详情均返回成功，映射线上267 SKU。当前 **0 / 267** 取得月级以上的发布证据，均记 `no_release_field` / `not_collected`，不是“官方无此信息”。

其中枕芯30、抱枕4、床垫18，共52 SKU；若“床品”作为大类，还包括床品98、被芯24、盖毯3。所有38 SPU均探测，所以父级runner可按优先品类筛选统计而不漏候选。38/38详情存在 createTime，却没有带发布/上市语义的字段。不能把商城记录创建时间当作发布日期；尤其Pro1.0详情 createTime=2024-08-08，而官方年报说明其2023年已经推出，这直接反证该字段等同发布日的假设。

## 实测与复现

```bash
ATOUR_PLAYWRIGHT_MODULE=/absolute/path/to/playwright-core python3 scripts/release_lane_atour.py --goods /path/to/online-goods.json
# 离线重放本轮实际匿名响应
python3 scripts/release_lane_atour.py --goods /path/to/online-goods.json --no-refresh --capture docs/release-coverage/l2-atour/live-capture.json
```

`run(rows, output_dir=None, refresh=True, capture_path=None)` 返回 `{lane: 'L2', candidates: [], outcomes: [...], summary: {...}}`。每条 outcome 包含商品ID、SPU ID、URL、原响应哈希、采集时刻、观察到的字段名和拒绝createTime的原因。刷新失败记transport_error，不用旧快照伪称本轮成功。依赖node、Playwright、Chromium；环境变量 `ATOUR_PLAYWRIGHT_MODULE`、`ATOUR_CHROMIUM_PATH` 可指定部署位置。默认Chromium路径 `/opt/google/chrome/chrome`。

官方匿名H5前端负责既有接口封装/解包；没有登录或保存用户账号。脚本执行官方SPA公开读取函数，逐页读取完整目录、逐SPU读取详情。`live-capture.json` 是本轮解包后的完整官方业务响应（含网络状态、时间与完整原文字段），不是捏造的测试fixture。`result.json` 与 `data/official/atour-release-evidence.json` 保存逐SKU归因；这里的“无字段”只限定这次所查详情接口，不推断所有官方渠道。

## 首发信息查证与拒绝错误继承

已查集团官方投资者关系材料：

- [2025年度20-F](https://ir.yaduo.com/static-files/ca1c5509-cfdf-4f4d-a592-1599d1417212)，第55页，原文“launched Deep Sleep Memory Foam Pillow Pro 1.0 in 2023.” 只有年份，无法填月份。该文另明示 Pro3.0 在August 2025推出，但当前目录Pro4.0不能继承第三代日期；Pro1.0亦不能继承。
- [2026 Q1官方业绩发言](https://ir.yaduo.com/static-files/60788498-9e69-4b63-9410-326db8934206)，明确2026年3月底发布夏季Pro3.0被。但当前目录是冬季/四季Pro3.0，不可把夏季版发布月填给冬季/四季版。
- [2023 Q1官方业绩发言](https://ir.yaduo.com/static-files/8a2cebd7-9703-479a-ad86-0dc6e8f13493)，提到2023年3月发布R90 2.0。该名称与当前Pro1.0缺少官方精确身份映射，不能靠推测套用。

后续缺口：精确版本的官方历史首发新闻/微信官方推文原文或厂家明示的上市字段。未检索到不能写成厂家从未公布。未采集的图片文字也不能推断为“官方没有”。
