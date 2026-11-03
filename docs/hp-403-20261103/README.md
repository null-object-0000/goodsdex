# Cars 解析与 HP 403 修复（2026-11-03）

## 根因与数据边界

Cars 失败 run 41631619345 在 `verify_byd_parameters` 因车型标题数量不为 1 抛异常。
此前真实响应 `code=200, success=true, configs=[]` 已保存在
`docs/actions拆分-20261030/car-source-empty-configs.json`，本次复制为无签名、无个人数据的
`tests/fixtures/cars/byd-empty-configs.json`。这不是已证实的重复列，而是空参数表也触发了同一个报错。

现在按精确 trim、列宽、列位置核对：多个标题必须对同一 SKU 指向唯一位置，不能取首列；
缺失、重复匹配、冲突或参数列数不一致均跳过并输出 `skipped_reason`。
`refresh-skipped.json` 与 `car-refresh-audit.json` 记录跳过身份及原因。
发布只更新本次可核实的配置，跳过配置必须已存在于已发布数据，且保留原字段和时间；
不将旧目录种子冒充本次采集。未审查身份、价格证据冲突等仍失败。

HP 的 403 分辨本机与 Actions 两个出口。本机 `probes.json` 记录了 9 次串行 GET：
浏览器 UA、10 秒延迟、并发 1，各 3 次，全部 200（14:35:28–14:36:10 UTC）。
响应 `Server: TencentEdgeOne`、`X-server: hpcnz`、`X-HPOLS: 0.2`，无 cf-ray。
这证明不能将线上 403 简化成全互联网不可用，最终定性以 Actions 实测为准。

采集对 HTTP 403/429/500/502/503/504 最多请求 3 次，退避 5 秒、10 秒，重试时使用浏览器 UA。
仍有连续三个独立 SKU 的最终响应都是 403 时停止全量请求：
`conclusion=degraded`、`error=blocked: 403 from hpstore.cn`，退出 0。
既有 goods、meta、HP SKU archive、成功图片审计均不写；不上传发布候选、不运行 publish。
解析错误、混合错误或已成功一部分后遇错仍按 failure 退出 1。
`collection-status.json` 和 Actions evidence 保存响应码、头和时间。

`sources-status.json` 从本次 collect 日志中的显式 outcome 识别 degraded；
向前查找真正的 success，禁止以 exit 0 的降级 run 更新 `lastSuccessAt`。
因此 GitHub 的绿色运行表示降级已妥善处理，源状态仍明确降级。
重试策略为每天北京时间 12:43（UTC 04:43）一次，不再每小时轰炸；支持手动 dispatch。
预期间隔同步为 1440 分钟；未改变 goods/meta 既有字段含义。

## 替代源实测

`alternatives.json` 是第二次独立实测，时间 14:37 UTC。

- `https://www.hp.com.cn/`：200，跳到 `hp.com/cn-zh/home.html`，是品牌首页。
- 从该首页实际发现的 `laptops-and-2-in-1s/omnibook-7-ai-pc.html`：200，跳到新版
  `laptops/home-laptops/omnibook/omnibook-7-ai-pc.html`，标题“惠普星 Book Pro AI PC”。
  是系列介绍，购买链接仍回到 hpstore.cn；没有目标 DC0F0PA 的 SKU 数据，不能替代精确配置采集。
- 将已知商城 SKU 路径移到 hp.com 的 `/cn-zh/shop/` 是探测路径（非已发现的商品链接），
  实测 503、AkamaiGHost，不能据此断言官网所有页面不可用。
- 京东 `item.jd.com/100149129016.html`：HTTP 200、35949 字节，但标题为“京东(JD.COM)-正品低价、品质保障、配送及时、轻松购物！”，
  没有目标 SKU，返回的是通用页面，不能把 HTTP 200 当作可用详情源。

结论：本次没有验证出独立且能接替现有 SKU/价格/规格采集的替代源；保留当前源并显式降级。
未使用第三方代理池。

## 验收

实现提交：`7380a1d7`。真实联网 dispatch：cars `41655448322`，HP `41655447640`。
运行结果和线上状态在完成后追加。本地基线 491 passed；修复后 498 passed，8 deselected。
