# 品牌命名空间归一验收（2026-11-04）

冻结的正式基线为 data 提交 `ed43254c`。以两份完整 JSON 逐行统计，而非 grep 截断第一个冒号；同时统计 GLOBAL 命名空间。`audit-release.json` 保存各档及合计结果。

|完整前缀|goods.json|goods-excluded.json|合计|命中品牌|
|---|---:|---:|---:|---|
|CN:apple_cn:|347|2|349|Apple|
|CN:byd:|14|0|14|比亚迪|
|CN:dji:|281|502|783|大疆|
|CN:fuji:|63|0|63|富士|
|CN:hp_cn:|218|0|218|惠普|
|CN:mi_cn:|1684|569|2253|小米|
|CN:xiaomi_ev:|3|0|3|小米汽车|
|GLOBAL:apple_support:|288|7|295|Apple|
|合计|2898|1080|3978||

当前工作区 main 的 public 是 10 月 27 日旧缓存，不是正式发布数据，且没有 goods-excluded.json。完整清单另见 `audit-local.json`：CN:apple_cn: 338→Apple、CN:dji: 783→大疆、CN:fuji: 24→富士、CN:mi_cn: 4008→小米、GLOBAL:apple_support: 295→Apple，合计5448。旧缓存原未知4006→0、小米2→4008，其余品牌不变；这是本轮规则应用前后对比，不能声称4006条全是这次新修复。

本次实际读取的正式两档及旧缓存中均没有 `CN:mi:cn:`，无法从这些快照复现截图。该变体已作为明确回归输入覆盖，原始 ID 不改写。使用给定 ID `CN:mi:cn:product:10000292` 和原贴纸名称，真实 `build_excluded` 产出 brand=小米、brand_source=id_prefix、excluded_reason=accessory:sticker。

## 规则与防误归

先提取作用域及完整命名空间（以 product/reference/commodity/sku/model/lens/kit/car 等记录类型为边界；无类型旧ID使用末尾标识符作边界），再统一大小写并删除 `- _ . :` 分隔符；对归一后的完整命名空间做精确别名查询。作用域仍参与匹配。不是以 Apple/HP 等字符串开头就接受。

小米 mi_cn 与 mi:cn、mi-cn、mi.cn 均相同；Apple apple_cn、GLOBAL apple_support、大疆 dji_mall_json/ dji_cn、惠普 hp_cn、富士 fuji_cn/ fujifilm_cn、比亚迪 byd_cn 及小米汽车 mi_ev/ xiaomi_ev 使用同一机制。没有引入名称模糊规则；原名称前缀兜底与 brand_source 语义保持不变。无法确认的 namespace/source/名称/已有品牌保持 null。

单测覆盖全部审核别名、五种分隔符（含混合）、大小写、冲突 source/name/已有品牌、伪后缀、未知作用域，以及排除清单生成。对 Apple/大疆/惠普/富士/比亚迪测试故意输入小米的 source/name/brand，必须仍按 ID 正确归属。反例 mi_cn_fake、mi:cn:fake、applepie、apple_fake、hp_fake 等保持 unknown。

## 正式数据修前 / 修后

|品牌|已发布前|已发布后|排除前|排除后|
|---|---:|---:|---:|---:|
|Apple|635|635|9|9|
|小米|1684|1684|569|569|
|大疆|281|281|502|502|
|富士|63|63|0|0|
|惠普|218|218|0|0|
|比亚迪|14|14|0|0|
|小米汽车|3|3|0|0|
|未知|0|0|0|0|

全部3978条由明确命名空间命中，覆盖率100%；逐行比对跨品牌变更0、非品牌字段变更0；幂等检查通过，小米1684未减少。unknown剩余0条，样本清单为空，无法提供10条真实 unknown；不制造样本或伪造无法判断原因。负例单测中的 unknown 仅为合成测试输入，不冒充库内条目。

复现（先将冻结 data 提交的两份文件放入同一 public 目录）：

```sh
PYTHONPATH=src python3 docs/brand-namespace-20261104/audit.py --public /path/to/public --out /tmp/audit.json
PYTHONPATH=src:scripts python3 -m pytest -q -m 'not live'
```

线上真实 curl、正式流水线与提交号见 publication.md。
