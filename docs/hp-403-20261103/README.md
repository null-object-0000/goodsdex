# 两条采集线修复与实测验收（2026-11-03）

## 最终结果

| 采集线 | 真实联网 workflow | 新观测数 | 最终结论 |
| --- | --- | ---: | --- |
| cars | [41658518208](https://github.com/null-object-0000/goodsdex/actions/runs/41658518208)（verified_only=false） | 40 | success，另有 3 条明确跳过并保留旧记录 |
| HP | [41655447640](https://github.com/null-object-0000/goodsdex/actions/runs/41655447640) | 209 | success，209 条有图、有价，errors=[] |

`cars-final-run.log` / `hp-run.log` 是 `gh run view <run> --log` 的完整结果；仅清理行尾空白。
`cars-final-audit.json`、`cars-final-skipped.json`、`hp-final-audit.json` 保存采集审计。
本轮 HP 没有复现持续的商品站点级封锁，线上目标状态为 `conclusion=success, error=null`。
独立状态刷新 [41659618688](https://github.com/null-object-0000/goodsdex/actions/runs/41659618688)
在两条最终 workflow 完成后执行。最终回读与断言见 `verification.json`。

## Cars 根因与处理

原失败 run 41631619345 在 `verify_byd_parameters` 因车型标题数量不为 1 抛异常。
真实响应 `code=200, success=true, configs=[]` 已在此前取证中保存；
本次复制为 `tests/fixtures/cars/byd-empty-configs.json`，保留公开响应，没有签名、cookie 或个人数据。
源文件和来源说明见 fixture 目录 README。这是空参数表也被报成了“列歧义”，并非已证实的重复列。

现在按精确 trim、列宽、列位置核对。多个标题对同一 SKU 必须指向唯一位置，禁止取首列；
缺失、重复匹配、冲突或参数列数不一致均跳过，并输出 `skipped_reason`。
参数 API 明确失败、身份/价格证据冲突仍报错。没有用 try/except 吞掉解析错误。
发布只更新本次可核实配置；跳过配置必须已存在于发布集，保留原值与时间戳。
两个 CLI 入口均支持同一保留行为。

最终联网运行又遇到 goodsId=10030 缺少车型列，以下 3 条被明确跳过，其他 40 条成功：

- `CN:byd:car:goods-10030:unknown:attr-1542`
- `CN:byd:car:goods-10030:unknown:attr-1543`
- `CN:byd:car:goods-10030:unknown:attr-1506`

三条原因均为 `missing_trim_columns`。`verify.py --previous-goods ...` 还比较线上记录与本轮前的旧值。
回归覆盖真实空参数表、重复同名列、同一位置的合法标题别名、冲突列位置、列数不一致，
以及跳过 SKU 的发布保留和没有旧数据时拒绝发布。

首轮 41655448322 已越过参数解析，但 SU7 图片来源页约 5 分钟无响应，图片门禁阻止发布。
现在图片不可核实也跳过整个 SKU、保留旧记录，不发布空图、不审核通过新 CDN 对象。
真实响应离线回放得到 40 条可核实配置、3 条跳过（`cars-first-replay.json`），后续另有完整联网验收。
中间 41656893995 被主动取消，未计作成功。

41657125381 采得 43 条，但 publish 被 `Car refresh changed non-car objects` 门禁拒绝。
最新发布集为 2909 条，共享发布又从补充库加入 51 条非汽车商品（含后续归档阶段处理的旧配件）。
修复 `publish(..., car_refresh=True)`：仅允许汽车补充项或原发布集中已有的补充项，
最终 verifier 使用同一范围，并在写文件前严格比较所有非汽车对象。
普通发布的补充逻辑不变；没有删除或放松原门禁。
`publication-replay.json` 记录用真实候选与 OSS 基线在临时目录回放整个发布/finalize：
2909 → 2909，finalize 后非汽车对象仍完全一致。

## HP：本机和 Actions 两个出口的实测

`probes.json` 是本机探测：浏览器 UA、10 秒延迟、并发 1，各 3 次，全部 200。
`actions-probes.json` 保存 Actions 出口的同一组实验和响应头，同一个商品 URL：

| 实验（串行） | UTC 请求开始时间 | 状态码 |
| --- | --- | --- |
| 浏览器 UA | 14:37:49 / 14:37:53 / 14:37:55 | 200 / 200 / 200 |
| 原 UA，每次额外延迟 10 秒 | 14:38:08 / 14:38:21 / 14:38:34 | 200 / 200 / 200 |
| 原 UA，并发 1、间隔至少 2.1 秒 | 14:38:39 / 14:38:43 / 14:38:46 | 200 / 200 / 200 |

9 次响应均有 `Server: TencentEdgeOne`、`X-server: hpcnz`、`X-HPOLS: 0.2`，无 cf-ray。
此前 14:15 的失败与当天 13:18 的成功交替出现，本轮则采得 209 条：
可确认访问不稳定，不能据此认定永久站点级封锁，也不足以确定具体限频/风控规则。
不将本次恢复完全归因于 UA。

`actions-collection-status.json` 保存实际采集全部 225 次请求，其中 219 次 HTTP 200，
6 次 HTTP 403 来自两张图片 CDN 地址（每张重试三次仍拒绝），并非本轮商品页面。
这些 403 的 `Server: AmazonS3`、`X-Cache: Error from cloudfront`、`X-Amz-Cf-Pop: BJS9-E1`，
头和时间见 `actions-image-403.json`。同 URL 没恢复，因此 recovered_at 为 null；
现有图库回退找到并校验了其他图片，最终 209 条商品均有图。
9 条之前已确认下架的 SKU 归档仍保留，没有删除 HP 数据。

## 重试、降级与状态语义

- 对 HTTP 403/429/500/502/503/504 最多请求 3 次，退避 5 秒、10 秒；重试时用浏览器 UA。
- 连续三个独立 SKU 经重试后最终仍全是 403，停止整批采集：`conclusion=degraded`，
  `error=blocked: 403 from hpstore.cn`，job 退出 0。
- 降级时不改 goods、meta、SKU archive、成功图片审计，不产生发布候选，不运行 publish。
  解析错误、混合错误或部分成功后遇错仍返回 failure；不是把 403 当正常采集成功。
- `collection-status.json` 和 Actions evidence 保存响应码、头、时间。
  `sources-status.json` 从对应 run 的显式 collector outcome 读取 degraded，
  向前寻找真正成功的 run；退出 0 的降级不得推进 `lastSuccessAt`。
- 每天北京时间 **12:43**（UTC 04:43）再试一次，预期间隔同步为 1440 分钟；支持手动 dispatch。
  本轮实际 success；降级分支由保留性和重试边界回归验证。

未修改 goods/meta 既有字段语义，未使用第三方代理池。

## 替代源实测

`alternatives.json` 是 14:37 UTC 的独立复测；Actions 也执行了替代 URL 探测。

- `hp.com.cn`：200，跳到 `hp.com/cn-zh/home.html`，为品牌首页。
- 从首页实际发现的 `laptops-and-2-in-1s/omnibook-7-ai-pc.html`：200，跳到新版路径，
  标题“惠普星 Book Pro AI PC”，为系列介绍；购买链接回到 hpstore.cn，不能替代精确 SKU/价格采集。
- 将商城 SKU 路径移到 hp.com 的 `/cn-zh/shop/` 是试探路径（非发现的商品链接）：503、AkamaiGHost。
  这个负结果不能用于声称官网所有页面不可用。
- 京东 `item.jd.com/100149129016.html`：200、35949 字节，但标题为京东通用首页标题，
  没有目标 SKU，不能把 HTTP 200 当可用商品详情。

本次没有验证出独立、能接替既有 SKU/价格/规格采集的替代源。

## 测试、提交与线上核对

基线 491 passed；最终本地 **500 passed, 8 deselected**，见 `tests.log`。
汽车工作流回归 **40 passed**；共享发布回归 **200 passed**，见最终 cars 日志。
线上全量 [41658484070](https://github.com/null-object-0000/goodsdex/actions/runs/41658484070)
也是 **500 passed, 8 deselected**（`cloud-tests.log`）。

实现提交为 `7380a1d7`、`e8ce732b`、`ae1dc885`、`81698694`，均已推送。
`verify.py` 核对两条最终 workflow 全部成功、data 分支与 OSS 状态原文一致、
meta 中 sources-status 的 sha256/bytes、refresh-hp 的实际 conclusion/error，
并可用旧 goods 比较所有非汽车对象及本轮跳过的三个 SKU。
产出为 `verification.json`、`sources-status.json`、`oss-sources-status.json` 和两条 run JSON。
