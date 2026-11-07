# refresh-images / refresh-atour 诊断（2026-11-07）

## 图片：复现来源与真实分布

- 历史 run：https://github.com/null-object-0000/goodsdex/actions/runs/42228655779
- 代码提交：`710b7782e92c5bda5518e496499cc00b99d20cee`。
- collect-base 实际读取的数据提交：`56aba40cc6142c18bac20b9b7c7347a78f9c63fc`。
- 历史步骤日志见 `images-run-excerpts.log`：13:52:41Z 输出 `No official image verified; see image-refresh-report.json`，随后 exit 1。该 run 没打印逐条 reason，失败后也没有上传报告，因此无法还原当时的 HTTP 原因分布。
- 本地解压上述精确数据提交的 `public/goods.json.gz`，按原脚本条件筛选，符合条件共 **165** 条；默认 `limit=100`，本轮实际处理前 **100** 条。把这 100 条完整原始行写入忽略目录 `_data/public/goods.json`，不改正式商品数据。
- 首次运行被本地 requests 缺少 SOCKS 支持阻断（100 条均为 `Missing dependencies for SOCKS support.`）。仅在 `/tmp/img-atour-python` 安装 PySocks 后重新运行原脚本，退出码仍为 **1**，这才是下面的在线复现结果。

| 分类 | 本地在线复现数量 |
| --- | ---: |
| added | 0 |
| no_official_image | 0 |
| network_error | 100（58 个 HTTP 406，42 个 HTTP 429） |

所有 **100 条 id + reason 原文**均保存在 `image-refresh-reproduction.json`，不是合成错误，也不是历史 run 的原始响应。三条抽样：

```text
CN:mi_cn:product:10000024
406 Client Error: Not Acceptable for url: https://api2.order.mi.com/product/view?product_id=10000024&version=2
CN:mi_cn:product:10000057
406 Client Error: Not Acceptable for url: https://api2.order.mi.com/product/view?product_id=10000057&version=2
CN:mi_cn:product:5781
429 Client Error: Too Many Requests for url: https://api2.order.mi.com/product/view?product_id=5781&version=2
```

不能据此宣称这些商品上游无图：请求在身份和图片验证前就被 HTTP 拒绝。406 和 429 均归网络/HTTP 失败。没有反复重试限流接口；改动后通过回放这 100 条实际 HTTP 错误验证 CLI：

```text
本轮 100 个候选：补上 0、上游无图 0、网络失败 100
Recorded-response replay exit: 1
```

## 图片：退出码与测试

报告仍为逐条列表，`status` 从笼统的 `pending` 改为 `no_official_image` / `network_error`，保留 `added`，异常的 `reason` 原文不变。stdout 始终输出本轮计数。

- requests / urllib HTTP 404 → no_official_image。
- 名称无匹配、图片身份不唯一、无图、非 HTTPS、小图或无法验证的图 → no_official_image；现有图片身份和尺寸校验不变。
- timeout、URLError、连接/TLS/requests 错误、除 404 以外的 HTTP 拒绝（含 403/406/429/5xx）→ network_error。不能把访问受阻当作上游不存在。
- 只有 `候选数 > 0 && network_error > 0 && added == 0` 返回 1。全无图、零候选、已有成功均返回 0。
- 未识别的编程异常重新抛出，避免当作上游无图吞掉。

新增 `tests/test_refresh_missing_images.py`：异常分类参数化；使用 runpy 执行真实 `__main__`，断言 SystemExit 码、报告、stdout 及失败时原始行保持一致。覆盖全网络失败、全 404、零候选、名称无匹配、API 无图、无图混合网络失败（exit 1）、成功混合网络失败（exit 0，真实验证 PNG 并 materialize）。原 source-registry 测试改为断言明确分类。

## 亚朵：历史失败与当前可复现问题

历史 run：https://github.com/null-object-0000/goodsdex/actions/runs/42144359599

`atour-run-excerpts.log` 记录：

```text
2026-11-06T01:33:27.8261146Z page.goto: Timeout 60000ms exceeded.
  - navigating to "https://h5mall.yaduo.com/", waiting until "domcontentloaded"
    at .../scripts/capture_atour.cjs:41:14
No files were found ... No artifacts will be uploaded.
```

结论：该次失败是首页导航未在 60 秒内完成，发生在 waitForFunction 和 API 调用之前。日志没有响应码或 HTML；不能硬判为 HTTP 403/429，也不能归因选择器。没有证据证明改超时即可自动修复该次云端连通性问题，需原执行环境再次观测，当前任务不触发 workflow。

本地进一步读取官网：

- 首页 HTTP **200**（约 0.22 秒）；公钥接口 HTTP **200**，业务 `code: 0`。
- 当前 HTML 关键片段：

```html
<title>亚朵星球</title>
<script defer="defer" src="https://ack-frontend-oss.yaduo.com/static-all/atour-planet-h5/prod/20261105191210/js/6995.5453ed17.js"></script>
<script defer="defer" src="https://ack-frontend-oss.yaduo.com/static-all/atour-planet-h5/prod/20261105191210/js/app.5453ed17.js"></script>
<body><div id="app"></div></body>
```

- 浏览器实际加载首页和上述 JS 均 HTTP **200**；webpackJsonp、模块 5251 及 pg/JV/Ec 均仍存在，模块选择器没有失效。
- 原脚本随后可复现 `page.evaluate: TypeError: Failed to fetch`。只增加 URL 路径/响应码诊断的临时副本发现：

```text
BLOCKED POST https://api-shoppingmall.yaduo.com/goods/spu/pageByParam
FAILED https://api-shoppingmall.yaduo.com/goods/spu/pageByParam net::ERR_FAILED
```

这是采集器自身白名单主动 abort，尚未获得 HTTP 响应，并非官网返回 403/429。当前官方 JS 中的只读调用为：

```javascript
x.Z.post("/goods/spu/pageByParam", {"data":a})
x.Z.get("/goods/spu/getNewDetailById", {"data":a,"codePass":!0})
x.Z.get("/goods/sku/getGoodsSkuPanelBySpuId", {"data":a})
```

原白名单是 `/goods/spu/pageByParam/v1`、`/goods/spu/getNewDetail/v1`、`/goods/sku/getGoodsSkuPanel/v1`。已用一行改为官网实际的三个只读路径；仍拒绝广告、购物车等非许可请求，保持匿名、凭证过滤、串行、至少 2.1 秒限速及所有快照/图片校验。路径修正后列表、SKU 面板和详情均 HTTP 200 / code 0。该改动能修复当前路径不匹配，不代表已解决历史云端首页导航超时。

验证只在本地内存/临时文件进行，不导入商品、不修改图片清单，不 push、不发布、不触发 workflow。

## 最终验证

- 路径修正后的临时诊断副本已完整采集 **3 页、48 个全站 SPU，其中亚朵星球 38 个 SPU / 267 个 SKU**。临时副本仅加 URL 路径、响应状态/业务码日志及首个调用的诊断超时；采集、匿名过滤、限速和业务对象保存逻辑与修正后的脚本一致。
- 原 `validate_capture` 和使用原图片/类目清单的 `build_rows` 均通过；全程没有调用落库/发布入口。响应码、全部许可请求时间戳、最小间隔和临时快照 SHA-256 见 `atour-live-validation.json`，原白名单阻断证据见 `atour-browser-before.log`。不把临时完整业务快照或任何商品图片改动入库。
- `PYTHONPATH=/tmp/img-atour-python:src:scripts python3 -m pytest -q -m 'not live'`：**1173 passed，8 deselected，4 subtests passed**。已有环境 anyio 插件有一条 pytest 弃用警告，无失败。
- 在亚朵一行修改后，单独重跑 image / publish / atour 相关测试：**106 passed，4 subtests passed**。
- `node --check scripts/capture_atour.cjs`、`git diff --check` 均通过。
