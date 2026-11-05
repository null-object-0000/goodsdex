# 正式发布与线上验收

实现提交：[d381d6ad](https://github.com/null-object-0000/goodsdex/commit/d381d6ad153e2e1c25ffe94851c4dfc58eb02611)。正式数据发布 run：[42033245603](https://github.com/null-object-0000/goodsdex/actions/runs/42033245603)，collect / publish 均 success，发布门禁 **644 passed**，OSS immutable blobs 与最终 manifest 完成哈希读回。数据提交：[c1c2abd](https://github.com/null-object-0000/goodsdex/commit/c1c2abde257d3176b3326ff81d39ac12a4c0f9d5)。未排除、未合并任何一个目标 ID。

前序 Apple 发布曾在原15分钟预算内未完成镜像，故另补作业预算提交 [de98cc6c](https://github.com/null-object-0000/goodsdex/commit/de98cc6cbce7e29720c835611cb56a6e256c6332)，只延长至45分钟，不放宽门禁。原本轮 run 随后成功，后补重复 run 42037198546 已取消；不把它作为成功依据。

后台提交：[b3f1600](https://github.com/null-object-0000/spend-good/commit/b3f16000af88832b1ef38989708b1c98179a9d4e)。构建 / API 测试 run：[42033251496](https://github.com/null-object-0000/spend-good/actions/runs/42033251496)，最终均 success。ECS 已实际运行该完整 gitCommit，服务器与外部各3次 HTTP200 版本读回通过；见 admin-deploy-final.log / final-version-readback.json。不是仅构建成功。

首次部署在短预热后健康检查502，自动回滚保住原服务；一次重试与诊断共用远程会话而超时，未切换服务。最终顺序执行同一已验证产物的部署，把预热等待延至60秒，保留原生依赖检查、3次精确版本读回和失败自动回滚。没有改线上业务模块或跳过验证；完整操作脚本为 deploy-warmup.sh，原失败与最终日志均保留。首轮API云端浏览器测试启动超时，原样重跑后367 passed / 4 skipped / 0 failed，未放宽断言。

## 线上数据

同步返回 `{"ok":true,"count":3605,"succeeded":10,"errors":[]}`。全库最终扫描3605行，12个目标逐项核验 name / status / is_historical / price / price_missing / historical_price；现价始终 null，发布日期未编造。最终正则剩余命中0，其他品牌同类命中0。见 [online-verification.json](online-verification.json) 与 online-verification-final.log，完整真实响应在 online-goods.json.gz。

真实请求：`GET https://spend.snewbie.site/api/goods?q=小米笔记本%20Air`。返回8条，包含本轮6条Air。完整响应：[online-air-response.json](online-air-response.json)，六条字段节选：[online-air-excerpt.json](online-air-excerpt.json)。后台部署完成后再次以正式域名请求，6个修复ID全部匹配，均 retired / is_historical=true / price=null / price_missing=true。

返回节选（原响应 items 中的实际字段）：

```json
{
  "id": "CN:mi_cn:product:7866",
  "name": "小米笔记本 Air 13.3\" 四核i7 8G 256G MX150 银色",
  "status": "retired",
  "is_historical": true,
  "price": null,
  "price_missing": true,
  "historical_price": 5999
}
```

## 截图边界

[1440×1100上半页](admin-1440-top.png) / [1440×1100下半页](admin-1440-bottom.png) / [全部12条长图](admin-local-1440.png)。截图为**本地真实后台组件加载正式线上12条原始记录**，使用同一b3f1600前端实现；不是绘图或替换DOM文案。12个名称、旧款/已下架标签、“旧款·无现价”及独立历史标价全部实际渲染。ui-verification.json记录视口与数据来源；长图宽1425是全页截取排除15px滚动条，上下两图实际宽1440。

线上飞书扫码登录尚未完成，**未取得已登录的线上后台截图**，不将本地截图冒充线上截图。已经打开线上登录页并请求用户完成登录；不绕过线上认证。

## 测试

- 数据最新独立工作树：1022 passed / 8 deselected / 0 failed；同实现云端 [42033236848](https://github.com/null-object-0000/goodsdex/actions/runs/42033236848) 同数通过；仅预算更改后的 [42037194340](https://github.com/null-object-0000/goodsdex/actions/runs/42037194340) 亦success。
- 正式发布门禁：644 passed；没有增加skip或降低既有断言。历史快照集成测试显式加入本轮同一证据重放，仍完整逐字段比较。
- API云端全量：367 passed / 4 skipped / 0 failed；4项为原有跳过。没有改API业务代码。
- 后台单测：10 passed / 0 failed，类型检查及正式构建通过。初建独立工作树缺生成的Umi类型，经正常prepare补齐后类型检查通过。
