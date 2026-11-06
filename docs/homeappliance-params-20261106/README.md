# 家电规格补采（2026-11-06）

本轮本地补采、预演与提交，不发布。**空调目标未达到；微波炉有两条因现有日期身份校验暂缓写入。** 不用空参数标记、系列参数或图片识别值充覆盖率。

## 实测验收

|品类|改前|实际写入后|比例|验收|
|---|---:|---:|---:|---|
|微波炉|0/5|3/5|60.00%|待两条日期身份补审|
|空调|1/146|52/146|35.62%|未达到 60%|
|扫地机器人|10/92|57/92|61.96%|达到 60%|
|冰箱|70/147|89/147|60.54%|达到 60%|

净增 **120 条**有参数记录：104 条官方来源、16 条明确标为第三方。扫地机器人本轮新增 31 条官方、16 条第三方；冰箱新增 19 条全部官方。所有已有非空参数保持原值。完整逐条缺失原因在 [coverage.json](coverage.json) 和发布输入清单。

验收母体固定为 data 提交 `44a45f00bfa2eee8bef68158aa6278597354aec7` 的 4,491 行，原始 JSON SHA-256 `3fd96f1e1a731ffef78126aef56844fb1aa0599a77c07f4da71e381785d31d38`。空调/扫地机/冰箱按该快照主分类计数，恰为题述的 1/146、10/92、70/147。

微波炉按原五条库内 ID 固定验收：10330、12548、20545、21480、mihome:66347。该快照中前四条已归入其他主分类；没有修改分类或改变验收分母。**21312 是额外指定的探测对象，不在这五条库内记录中，不能与 21480 混同。** [targets.json](targets.json) 保存全部 390 个目标及身份。

## 入口实测

|入口|实测结果|处理|
|---|---|---|
|PC `api2.order.mi.com/product/view?product_id=…&version=2`|20545、21312 均业务成功；`extend_info.desc_tabs_view` 只有图片列表，`product_info.product_desc` 是简介|PC 图片规格不作为参数值|
|`api.mi.com/product/detail`、`shop.mi.com/product/detail`|前者 DNS 失败，后者 HTTP 404|前者未验证；不据此断言所有 PC 接口都无数据|
|移动 `product/info`，含已关联商品的默认 gid 请求|48 个百科明确关联的商城 product ID；核对商品自指与独立型号|仅接收自己 productId 的 `classParameters.list`|
|百科 `product` / `attribute`|部分空调、冰箱有 `attributeMap` / `data.list`；大量旧扫地机为空|沿用已存在的中文字段名和完整原值|
|百科 `introduction` / 官方 PDF|300 个待补 model 全部尝试，含 5 个最终下载超时；原生文本能提取部分规格|只读原生文字单元格，不 OCR|
|石头厂家产品中心及纯米厂家说明书|设备 model、完整手册名和标准版/Pro/上下水版分别核对|厂家文字参数标官方来源|
|京东 P1、天猫 20L 商品页|匿名响应未取得可用同款参数表|未验证；没有拿促销页内容当官方规格|
|中关村在线独立型号参数表|22 页捕获，16 页通过完整品牌/型号核对；T8 不能给 T8 Plus，物理型号未确认的页面不采用|所有字段明确 `source_type: third_party`，原网页原值保留|

PC 探测见 [candidate-probes.json](candidate-probes.json)；第三方访问见 [third-party-probes.json](third-party-probes.json)，逐型号取舍见 [third-party-review.json](third-party-review.json)。商城/百科 JSON 的 URL、POST 请求体、时间、业务状态与内容哈希见 captures / shop-captures 清单。没有请求登录接口，也没有把代理用于内网。

## 20545 与 21312 的结论

**20545 米家智能微波炉 P1：能拿到官方文字参数。** 商城移动接口参数数为 0，PC 详情为长图；百科 product 的 attributeMap 与 attribute 列表也为空，但 introduction 提供了文字 PDF。
- [官方说明书](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/b3180755ff4b7db4b9b7ca893c5be7f5_1777528674238.pdf?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=uDPQdZFncNQv52mH7dw0vZVWWCA=)，PDF 第 13 页、印刷第 11 页。
- 原文：`额定容积 20 L`、`额定输入功率 1250 W`、`微波输出功率 800 W`、`产品型号 MWB04M`。
- 本库沿用「容量」「额定功率」「产品尺寸」「能效等级」等已有字段；「额定功率」保留原始来源字段「额定输入功率」，不会把 800 W 输出功率混成输入功率。
- [原说明书](p1.pdf)、[文字](p1.txt)、[规格页渲染](p1-spec.png) 已留存。PC 长图仅作入口证据；参数来自 PDF 文字。

**21312 米家微波炉20L 节能版：本轮实测入口确实未取得可落库的结构化参数。** [PC 响应](21312-pc.json)业务成功，简介原文为 `700W速热微波+2级能耗 | 双旋钮操作 | 360°旋转加热+专业解冻`；移动端 `classParameters.list` 仍为空，PC 参数为图片。没有从图片转写参数；独立文字说明书未验证。
- [官方 PC 接口](https://api2.order.mi.com/product/view?product_id=21312&version=2)。[原图 URL](detail-image-urls.json) 与 [图像样本](21312-detail-spec-candidate.jpg) 仅作线索。
- 21480 对应 `xiaomi.microwave.cm20l2`，名称是「米家**智能**微波炉 20L 节能版」；说明书不能套到 21312。
- 这不是对全互联网“绝对不存在参数”的断言；结论限定于本次实际探测的入口。详见 [diagnostic-products.json](diagnostic-products.json)。

## 身份与日期校验冲突

现有 `release_l7.fingerprint` 把 `params` 纳入身份。12548 与 20545 已有 `llm_verified` 日期证据；新增规格会使下一次 finalizer 的原身份匹配失败。[首轮完整测试](tests-initial.log.gz)暴露了该问题；原 HEAD 的两条相关回归单独跑均通过，见 [baseline-failures.log](baseline-failures.log)。

按“不动 release 口径、门禁”的硬约束，这两条设置 `deferred_reason: release_identity_review_required`：保留已核对的规格候选，但 `params` 继续为空。**五条微波炉都能取得可核参数，不等于五条已写入。** 没有修改日期、日期证据、身份指纹算法、release_policy 或门禁。是否允许仅补审两条身份指纹的选择尚待用户答复，本提交不预先执行该动作。

## 接入与来源边界

- 中性发布输入：[`data/enrichment/homeappliance-params.json`](../../data/enrichment/homeappliance-params.json)，没有把第三方证据放入官方清单冒充官方。
- `publish.to_public` 在普通 `crawl_all` 导出路径应用已审的精确商品 ID 参数；finalizer 在源策略解析后再次重放，保证日常重建不丢。专用其他任务的 metadata-only 发布模式不串入本轮数据。
- `params_sources` 逐字段保留来源类型、URL、原值/原字段、定位符、内容哈希；`params_source_type` 标记 official / third_party。缺失原因保持在参数字典之外。
- 不覆盖已有非空值；遇到差异保留候选冲突。名称、ID、model 变化或容器范围未确认时拒绝套用。
- 521L/523L 共用设备不能接收只有 521L 的手册参数；606L/600L 表格只接收两列明确相同的能效、冷冻容积等，拒绝把 606L 的总容积给 600L。空调多列也仅选各列明确完全相同的单元格。此边界有专项回归。
- 不从品名凑参数覆盖率，不把“米家互联”一类目录标志塞成规格，不用同系列相近型号补空。

## 抽样、验证与未验证项

[十条逐字段原文对照](sample-10.md) / [机器可核对样本](sample-10.json)：固定随机种子 20261106，3 微波炉、3 空调、2 扫地机（官方/第三方各一）、2 冰箱，包含每个写入字段的值、URL、原文与定位符。[PDF 规格页](sample-pages/) 已渲染并目视核对；P1 另见上节。

全部 826 个候选字段（731 官方、95 第三方，含两条暂缓商品的 11 个字段）均与原始 JSON 单元、HTML span 或 PDF 原文/页码逐条核对，不仅核查十条样本。见 [verification.json](verification.json)。在固定 4491 行上，本模块重放前后所有非规格字段逐条相同、顺序/ID/行数相同，再次重放幂等。

最终离线全量测试 **1136 passed，8 deselected**，见 [tests-final.log](tests-final.log)；本机使用 `/tmp/goodsdex-carry-forward-venv/bin/python`（pytest 9.2.0），采集代码无新增运行时依赖。8 项 live 测试未运行，标为**未验证**。现有日期回归保留全部断言，只在其独立预期流水线加入新参数重放阶段；不删除或放宽任何日期检查。

5 个说明书最终下载超时：

- `xiaomi.airc.1r04r1`：[请求 URL](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/7414043884aa99df714842583edc35c2_1776912727481.pdf?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=f0c3aMsT9CcMSvpL+spm4uST5zY=)；`response exceeded wall time limit`，**未验证**。
- `xiaomi.airc.ar07r1`：[请求 URL](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/4d37b4338145aa792f254809d51128eb_1776861631465.pdf?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=067A8KwPZip9eqG2yZPXSL32EtA=)；`response exceeded wall time limit`，**未验证**。
- `xiaomi.airc.arf2r2`：[请求 URL](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/6054f66cd3664f38190cb912fc1c0a2a_1783926440280.pdf?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=CM/MHDDzwhPbmTsGnJmh/bGS+BU=)；`response exceeded wall time limit`，**未验证**。
- `xiaomi.airc.f53h00`：[请求 URL](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/1d92546fe4087a08dabc22b69f5a035f_1782387482329.pdf?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=LQVDgG9U+slmtrAANwBftYm7NMw=)；`response exceeded wall time limit`，**未验证**。
- `xiaomi.airc.h53h00`：[请求 URL](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/85282fa98041bfd28b4ea28bc49c8904_1782387063584.pdf?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=APLTzHd/vMOq/woj7Q6xPBoDvok=)；`response exceeded wall time limit`，**未验证**。

其余空白的 `image_only_spec` 表示无可直接提取的规格文字，`no_unambiguous_text_spec` 表示有文字但不能唯一选值（含缺失字体映射），`identity_unverified` / `container_scope_unverified` 表示身份或规格范围不足；不是把所有解析不到的页面都说成“页面没有参数”。

## 证据与复跑

[evidence.tar.gz](evidence.tar.gz) 包含 1165 份原始 API JSON、225 份原生 PDF 提取文字、22 份第三方 HTML，全部按原始字节保留；哈希清单见 [evidence-manifest.json](evidence-manifest.json)。完整说明书缓存约 2.4 GB，位于被忽略的 manuals/，不全部提交；原始 URL、PDF 哈希及文字哈希在 manuals.json / manufacturer-manuals.json 中。P1 PDF 单独保留供复核。

```bash
export HTTPS_PROXY=http://127.0.0.1:7890
export PYTHONPATH=src:scripts
audit=docs/homeappliance-params-20261106
# 不切分支，不写主仓；从已经存在的数据提交恢复固定验收输入
git show 44a45f00bfa2eee8bef68158aa6278597354aec7:public/goods.json.gz > "$audit/goods-4491.json.gz"
tar -xzf "$audit/evidence.tar.gz" -C "$audit"
# 离线重建与核对
python3 scripts/build_homeappliance_params.py --goods "$audit/goods-4491.json.gz"
python3 scripts/verify_homeappliance_params.py --goods "$audit/goods-4491.json.gz"
# 采集入口（不发布；复用成功缓存、重试失败项）
python3 scripts/collect_homeappliance_params.py --goods "$audit/goods-4491.json.gz"
python3 scripts/collect_homeappliance_manuals.py
python3 scripts/collect_homeappliance_shop_links.py
python3 scripts/collect_homeappliance_manufacturers.py
python3 scripts/collect_homeappliance_third_party.py
# 重建后运行原离线测试命令
PYTHONPATH=src python3 -m pytest -q -m "not live"
```

第三方新链接、不同产品名称或发生内容漂移的旧手册须重新审查；不能仅凭新的搜索结果或 source_empty 状态自动授权写入。没有 push、部署或触发 workflow；`data/supplements/goods-supplements.json` 与 release 生产代码保持不变。
