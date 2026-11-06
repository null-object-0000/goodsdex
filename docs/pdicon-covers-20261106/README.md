# pdId 封面与米家目录缺口审计

**本轮有效补图 0 条，原图全部保留。** 不是映射缺失：1,244 个发布型号已全部解析 pdId。实际图片均未通过要求的 HTTP 200 + image/* + ≥400×400 验收，不能把 168×168 设备图标作为合格封面计数。

## 改动与边界

新增 `xiaomi-pdid-map.json`、`pdicon-audit.json` 和可复跑的 `scripts/backfill_xiaomi_pdicons.py`。封面入口按所有非空 `miio_model` 精确匹配，不限定 ID 前缀；现有百科 realIcon 优先。只有 `usable=true` 的映射才选择构造 URL，选图时清除旧图尺寸及来源元数据，保留独立 `image_mihome`。本轮所有映射 `usable=false`，因而没有封面替换。

冻结发布输入：`origin/data` 的 `56aba40cc6142c18bac20b9b7c7347a78f9c63fc`，路径 `public/goods.json.gz`，4,491 条；1,247 条带型号，去重后 1,244 个型号。输入与只读外部 APK 表的 SHA-256 见 [baseline.json](baseline.json)。候选整库逐字段等于该输入，`cover-changes.json.gz` 是空列表。代码基线与 data 快照分别记录，产品集只从冻结发布输入读取。

没有改 params、release、supplements 或门禁实现，没有补采商品。仅提交当前代码分支；本轮不产生线上发布。

## 映射规模与补图统计

- 映射文件：**1,244 条 / 208,831 bytes**；本地表 1,227、productCompact 17。离线表作为优先身份源，未复制或修改外部仓库。
- productCompact 调用共 63 批，每批 ≤20（17 个离线未命中型号全部成功返回）；为检查旧图风险，对离线命中的全部 1,227 个发布型号也做了比较。原响应与请求型号保存在 [product-compact-responses.json](product-compact-responses.json)。
- 审计文件：1,247 条，按发布记录而非唯一型号计数。`image` 是被测试的候选 URL，HTTP/尺寸对应这个 URL；`selected_image` 是保留的原图。

|image_source|本轮补图条数|
|---|---:|
|mijia_pdicon|0|
|mijia_baike_realIcon|0|
|其他来源|0|

带型号记录的来源计数前后相同：未标记 1,114、有品 120、live_official_page 13。所有旧图及原 image_source 保留。

## 图片实测与 30 条抽样

curl 实际下载响应正文与 Content-Type，再用 Pillow 完整解码；未重采样或放大。1,244 个唯一 URL 全量验证结果：**993 个 HTTP 200 / image/png / 168×168；251 个 HTTP 404 / 无可解码尺寸**。对应 1,247 条发布记录：995 条尺寸不足、252 条 404，均回退原图。所有失败逐记录列于 [failures.json](failures.json)，所有 URL 的正文 SHA-256、HTTP、类型、尺寸列于 [url-checks.json](url-checks.json)。

任务给出的 `13363.png` 本次实测也是 HTTP 200、image/png、**168×168**（SHA-256 见 url-checks），因此不符合 ≥400×400。接口可匿名访问与图片尺寸是否合格是两个独立事实。

固定种子 `20261106`，从按 ID 排序的候选记录随机抽 30 条；不因失败替换样本。**25 条 HTTP 200 但 168×168，5 条 404，合格 0/30**。本轮没有最终新增 URL，下表是补图候选抽样及其回退结果，未冒充成功补图抽样。结构化明细见 [sample-30.json](sample-30.json)。

|ID / model|pdId|HTTP|Content-Type|实际像素|处理|
|---|---:|---:|---|---|---|
|CN:mi_cn:product:20105 / `xiaomi.health_pot.p1v2`|[24873](https://cnbj1.fds.api.xiaomi.com/iotweb-product-center/24873.png)|200|image/png|168×168|保留原图|
|CN:mi_cn:product:21562 / `xiaomi.projector.rm34k`|[81811](https://cnbj1.fds.api.xiaomi.com/iotweb-product-center/81811.png)|200|image/png|168×168|保留原图|
|CN:mi_cn:product:24811 / `xiaomi.ysj.ymmax`|[23012](https://cnbj1.fds.api.xiaomi.com/iotweb-product-center/23012.png)|404|application/octet-stream|—|保留原图|
|mihome:1520 / `zhimi.lock.da1`|[1520](https://cnbj1.fds.api.xiaomi.com/iotweb-product-center/1520.png)|200|image/png|168×168|保留原图|
|CN:mi_cn:product:15069 / `xiaomi.heater.ma4b`|[36640](https://cnbj1.fds.api.xiaomi.com/iotweb-product-center/36640.png)|404|application/octet-stream|—|保留原图|
|mihome:2806 / `xiaomi.aircondition.mt5`|[2806](https://cnbj1.fds.api.xiaomi.com/iotweb-product-center/2806.png)|200|image/png|168×168|保留原图|
|mihome:4816 / `yeelink.bhf_light.v8`|[4816](https://cnbj1.fds.api.xiaomi.com/iotweb-product-center/4816.png)|200|image/png|168×168|保留原图|
|mihome:20867 / `mibx2.washer.x11`|[20867](https://cnbj1.fds.api.xiaomi.com/iotweb-product-center/20867.png)|200|image/png|168×168|保留原图|
|CN:mi_cn:product:16311 / `xiaomi.wifispeaker.x6a`|[8608](https://cnbj1.fds.api.xiaomi.com/iotweb-product-center/8608.png)|200|image/png|168×168|保留原图|
|CN:mi_cn:product:18649 / `xiaomi.vacuum.c103`|[13403](https://cnbj1.fds.api.xiaomi.com/iotweb-product-center/13403.png)|200|image/png|168×168|保留原图|
|CN:mi_cn:product:23408 / `miwear.watch.p62`|[27469](https://cnbj1.fds.api.xiaomi.com/iotweb-product-center/27469.png)|404|application/octet-stream|—|保留原图|
|mihome:13260 / `xiaomi.aircondition.c36`|[13260](https://cnbj1.fds.api.xiaomi.com/iotweb-product-center/13260.png)|200|image/png|168×168|保留原图|
|mihome:1974 / `xiaomi.wifispeaker.l05b`|[1974](https://cnbj1.fds.api.xiaomi.com/iotweb-product-center/1974.png)|200|image/png|168×168|保留原图|
|CN:mi_cn:product:25053 / `xiaomi.teabar.mtb02`|[29621](https://cnbj1.fds.api.xiaomi.com/iotweb-product-center/29621.png)|404|application/octet-stream|—|保留原图|
|CN:mi_cn:product:9726 / `lumi.acpartner.mcn02`|[66078](https://cnbj1.fds.api.xiaomi.com/iotweb-product-center/66078.png)|200|image/png|168×168|保留原图|
|mihome:2477 / `chunmi.juicer.a1`|[2477](https://cnbj1.fds.api.xiaomi.com/iotweb-product-center/2477.png)|200|image/png|168×168|保留原图|
|youpin:169576 / `xiaomi.bhf_light.na1`|[19355](https://cnbj1.fds.api.xiaomi.com/iotweb-product-center/19355.png)|200|image/png|168×168|保留原图|
|mihome:3025 / `hannto.printer.honey1s`|[3025](https://cnbj1.fds.api.xiaomi.com/iotweb-product-center/3025.png)|200|image/png|168×168|保留原图|
|CN:mi_cn:product:12136 / `deerma.humidifier.jsqs`|[72559](https://cnbj1.fds.api.xiaomi.com/iotweb-product-center/72559.png)|200|image/png|168×168|保留原图|
|mihome:16055 / `midjd7.fridge.520b`|[16055](https://cnbj1.fds.api.xiaomi.com/iotweb-product-center/16055.png)|200|image/png|168×168|保留原图|
|mihome:76733 / `roborock.vacuum.a76`|[76733](https://cnbj1.fds.api.xiaomi.com/iotweb-product-center/76733.png)|200|image/png|168×168|保留原图|
|CN:mi_cn:product:13857 / `k0918.toothbrush.t700`|[2054](https://cnbj1.fds.api.xiaomi.com/iotweb-product-center/2054.png)|200|image/png|168×168|保留原图|
|CN:mi_cn:product:21258 / `mibx5.washer.s111`|[29560](https://cnbj1.fds.api.xiaomi.com/iotweb-product-center/29560.png)|404|application/octet-stream|—|保留原图|
|youpin:166327 / `chuangmi.camera.066a01`|[78521](https://cnbj1.fds.api.xiaomi.com/iotweb-product-center/78521.png)|200|image/png|168×168|保留原图|
|mihome:75802 / `xiaoxun.watch.sw770`|[75802](https://cnbj1.fds.api.xiaomi.com/iotweb-product-center/75802.png)|200|image/png|168×168|保留原图|
|mihome:71735 / `dreame.vacuum.p2157`|[71735](https://cnbj1.fds.api.xiaomi.com/iotweb-product-center/71735.png)|200|image/png|168×168|保留原图|
|mihome:79572 / `chuangmi.camera.46e01`|[79572](https://cnbj1.fds.api.xiaomi.com/iotweb-product-center/79572.png)|200|image/png|168×168|保留原图|
|mihome:14746 / `xiaomi.pet_waterer.002`|[14746](https://cnbj1.fds.api.xiaomi.com/iotweb-product-center/14746.png)|200|image/png|168×168|保留原图|
|mihome:12191 / `xiaomi.waterpuri.800f4`|[12191](https://cnbj1.fds.api.xiaomi.com/iotweb-product-center/12191.png)|200|image/png|168×168|保留原图|
|CN:mi_cn:product:21103 / `xiaomi.hood.ymv9`|[24357](https://cnbj1.fds.api.xiaomi.com/iotweb-product-center/24357.png)|200|image/png|168×168|保留原图|

## 内置 icon_real 与 productCompact 比较

对 1,227 个本地命中的发布型号逐一比较，移除 URL 查询签名和 fragment 后，**不一致 0 条**，没有可提供的真实不一致样本；不把“拆包提示可能过时”写成已发现差异。[icon-comparison.json](icon-comparison.json) 保存比较数量和空差异列表；原响应可逐一复核。此结论限本次发布型号及当前返回地址，不证明 APK 全部 11,990 条图标均无历史变化，也未声称比较了历史图片字节。构造的 `<pdId>.png` 与接口 realIcon 地址可能不同，二者并不等价；本轮按任务规定只尝试构造 URL，失败保留原图。

## 目录缺口

表内唯一 model：11,990；发布集与表交集：1,227，覆盖率 **10.23%**；缺口 **10,763**。另有 17 个发布型号由 productCompact 解析，不属于表内分母。按 cate_name 分组，未按 brand_id/status 过滤。完整型号 + name + pd_id 清单及八类家电专项见 [mihome-gap.md](mihome-gap.md)；这些是目录缺口，并非参数缺口统计或自动采集队列。

|cate_name|已有型号|表内型号|覆盖率|缺口|
|---|---:|---:|---:|---:|
|个护与起居|16|1187|1.35%|1171|
|传感器|4|213|1.88%|209|
|其他|0|53|0.00%|53|
|出行车载|13|53|24.53%|40|
|办公学习|14|42|33.33%|28|
|卫浴|63|508|12.40%|445|
|厨房电器|289|1064|27.16%|775|
|安防|155|489|31.70%|334|
|宠物与植物|11|62|17.74%|51|
|影音娱乐|72|294|24.49%|222|
|插座开关|8|3138|0.25%|3130|
|清洁电器|192|725|26.48%|533|
|照明|19|2308|0.82%|2289|
|环境电器|280|1260|22.22%|980|
|路由网关|17|143|11.89%|126|
|运动健康|74|451|16.41%|377|

## 复跑与测试

```bash
git show 56aba40cc6142c18bac20b9b7c7347a78f9c63fc:public/goods.json.gz > /tmp/pdicon-baseline.json.gz
python scripts/backfill_xiaomi_pdicons.py \
  --input /tmp/pdicon-baseline.json.gz \
  --table /home/nichangen/代码/self-code/spend-good-competitors/evidence/mihome/plugin_config_cn-zh_cn.json.gz \
  --output /tmp/pdicon-candidate.json --reuse
PYTHONPATH=src /tmp/goodsdex-cover-tests/bin/python -m pytest tests -k "image or publish or supplement" -q
```

`--reuse` 重放已有响应与实测证据；首次运行不带该选项。离线优先解析 pdId；额外在线调用用于本任务要求的图标比较。映射只缓存成功身份结果，验证失败不丢失身份映射。

定向测试：**103 passed / 1034 deselected / 4 subtests passed**，见 [tests.log](tests.log)。新增与既有封面单元测试合计 **11 passed**（[tests-covers.log](tests-covers.log)），验证跨命名空间匹配、百科优先、失败保留、幂等与非图片字段不变。全套回归：**1,137 passed / 4 subtests passed**，见 [tests-full.log](tests-full.log)。
