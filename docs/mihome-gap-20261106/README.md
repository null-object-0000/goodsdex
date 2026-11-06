# 米家目录反哺：先判定，再寻找销售证据

## 只读缺口审计

目录 1,928 个唯一 model，映射文件 330 行但仅覆盖 **328 个唯一 model**，真实缺口 **1,600**。
重复映射为 `xiaomi.projector.yslite`（19767、20278）与 `xiaomi.cooker.cmby4`（21852、22321）。
1,598 是将商品映射行数误当设备去重数的差值，不能为凑数丢掉两个设备。

首次只读清单：**A 944、B 377、C 279**，总数 1,600。其中 27 个设备有库内规范化同名记录；缺少映射不等于缺少商品。

- [全量缺口 JSON](gaps.json)：model、pd_id、官方名、分类、官方目录品牌、jumpUrl、同名商品 ID、A/B/C 与理由。
- [A 类整机 CSV](A.csv) / [JSON](A.json)
- [B 类不收录 CSV](B.csv) / [JSON](B.json)
- [C 类待用户决定 CSV](C.csv) / [JSON](C.json)
- [品牌 × 叶分类 × A/B/C 统计](brand-category-counts.json)
- [母体、映射去重与输入哈希](inventory-summary.json)

品牌保持官方目录的 brandId 归属，例如“小米公司”目录包含生态链产品，不凭 model 前缀擅自改成制造商品牌。
A 使用耐用整机白名单；B 先于 A 判定，剔除传感器、开关、网关、灯泡、灯带、安装照明组件、窗帘电机、遥控器、散热背夹、控制面板及演示设备。
官方把空气管理面板归为“空调”、把热水器遥控归为“热水器”，因此不能只信分类。
灯具整机、路由器、插座与其他边界设备保留 C，未获决定前不收录。

同名匹配只做 NFKC、大小写和空白规范化，保留代际、容量、颜色、Pro/Max、标点及尺寸；同名仅是复核线索。

首个清单提交 `4e76d2e8` 未改商品数据；最终质检另外把两条同名桌搭改判 B、摄像机配套室内端改判 C，以下采用最终口径。固定抽样为排序后 A 类 model，以 `random.Random(20261106)` 不放回抽取 50 条，见 [sample-50-input.json](sample-50-input.json)。


## 渠道验证与全量决策

最终 A 类 944 条固定随机抽样 50 条，**7/50 = 14%** 查得渠道详情且官方完整名称精确一致，商城 **0**、有品 **7**、未获已核渠道 **43**。7 条中 3 条存在多个同名 gid，仅 4 条能唯一选择渠道 ID；“能搜到”不等于可直接建唯一商品。样本接口错误 **0**。[逐条证据](sample-50.json)。最终母体重抽前的首轮试验 9/50（18%），不作为定稿验收分母。

低于 30% 后仍选择**只对明确的 A 类进行有限精确查询**，未扩大到 B/C，也未做无限模糊搜索：用户允许为耐用品建立无价设备档案，低命中率影响可比商品比例，不能成为少收录的理由。全量 944 条均核验百科 model + pdId；161 条有渠道详情命中，783 条未获精确渠道身份，业务/传输错误 0。部分同名有多个 gid，故 161 不是新增商品数。[全量渠道结果](channels-all.json)。

商城使用 `api2.order.mi.com/search/index` 的名称搜索及 `product/view` 详情；有品使用匿名搜索与详情接口，金额 `priceMin` 分转元。百科读取真实 `buyUrl.channelUrl`，只接受有渠道详情佐证且完整名精确一致的商品；pdId 不当商城 product_id，搜索中的 commodity_id 不当产品 ID。搜索仅首 40 结果，不把推荐结果、相似代际、颜色差异或共享购买链接当身份确认。

未命中的可证原因是：目录设备名与渠道销售名的前缀、容量、颜色、规格或系列粒度不一致；搜索推荐中没有完整同名项；百科未提供有效桥接购买链接。例如“空调 巨省电 大1匹新一级能效”与渠道“小米空调 巨省电 大1匹 新一级能效”没有自动合并；“REDMI 投影仪 3 Lite 版/3C”不能猜成其中一个销售型号。老设备已停产、线下销售、生态链自有渠道均是**待验证解释**，不能仅凭搜索未命中就判定。这里“仅设备档案”意为“本轮无已核销售渠道”，不声称市场上绝对买不到。

## 入库结果与字段约束

- A 类 944 = **896 新增 + 19 原库同名/身份项 + 29 本批重复名/身份待核项**。
- 新增 **120 条有品报价商品**、**776 条米家设备档案**；商城新增 0。48 条未新建的逐项决策见 [intake-decisions.json](intake-decisions.json)，没有把多个设备版本冒充多个可比商品。
- 有价 120，其中 **84 可比、36 渠道标记不可售**；后者保留渠道展示报价，`price_status=stale`、`price_comparable=false`，不进最低价。报价为抓取时的渠道商品起价，非所有 SKU 的成交价保证。
- 无价 776：`price=null`、`price_missing="no_channel_price"`、`price_kind="unknown"`、`price_comparable=false`。`image=null`，图标只存 `image_mihome`，明确 `scope=device_icon`。未伪造商品主图。
- 新 ID 使用 `youpin:<gid>` 或 `mihome:<pdId>`；保留 `miio_model`、`mihome_pd_id`、`source_channels[]` 与 `*_mihome`。新商品的名称、主图、分类优先使用已核渠道值。
- **原库 3,572 行逐个对象完全不变**，包含原有冲突 ID 的重复行；name/image/category 及所有日期字段均未覆盖。新模块仅追加，不向既有对象写任何字段。
- 普通发布通过默认补充入口重放审核清单；本次使用共享发布锁和专用 `mihome_intake_only` 范围，强制结果严格等于“最新 previous + 审核新增”。未绕过测试、价格资格、排除清单或 OSS 摘要验证。
- 补充了 8 个完整整机名称 × 分类的精确配件例外，避免“电池版”或“适用于智能空气管理面板”被旧词匹配误删；散装电池仍是配件，有回归测试。

审核输入见 [mihome-intake.json](../../data/official/mihome-intake.json)，统计见 [intake-summary.json](intake-summary.json)。

## 日期覆盖率影响（发布前测算）

|情形|日期分子|商品行数分母|覆盖率|
|---|---:|---:|---:|
|新增前|1,646|3,572|46.08%|
|新增 896 条均无日期（本轮实际）|1,646|4,468|**36.84%**|
|新增中 X=20% 有合规日期（理论情形）|1,646 + 896×20%|4,468|**40.85%**|

通式 `(1646 + 896 × X) / 4468`；若取整数 179 条新增有日期，则 `1825 / 4468 = 40.85%`。全量分母采用发布行口径，与 46.08% 一致，不改为“有价格商品”或去重 ID 分母。日期覆盖下降约 **9.24 个百分点**。firstTime、createTime、changeTime、文档时间没有当发布日期使用。[测算与真实 finalize 对账](dry-run-summary.json)。

## 十条新收录样本

分层选取 7 条有报价商品与 3 条无价档案，逐条原始字段见 [sample-10-new.json](sample-10-new.json)，渠道主图 HTTP/尺寸/摘要见 [sample-10-verification.json](sample-10-verification.json)。7 张主图均成功读取且为 800×800；3 条档案主图为空。

|名称|价格（元）|主图|来源|
|---|---:|---|---|
|米家智能空气炸锅 4L|349.0|[渠道主图](https://img.youpin.mi-img.com/youpin_gms/514e8238_5f19_42e5_8de6_409954992734.png?w=800&h=800)|[详情](https://www.xiaomiyoupin.com/detail?gid=155838)|
|米家智能空气炸锅6.5L嫩烤版|449.0|[渠道主图](https://img.youpin.mi-img.com/youpin_gms/28e42326_2ad8_4588_9eb2_81a72de92f6b.png?w=800&h=800)|[详情](https://www.xiaomiyoupin.com/detail?gid=161613)|
|小米智能摄像机 云台版2K|179.0|[渠道主图](https://img.youpin.mi-img.com/youpin_gms/3b416aa5_b2cd_4066_ab7f_d2a11cd8153a.png?w=800&h=800)|[详情](https://www.xiaomiyoupin.com/detail?gid=121914)|
|小米智能摄像机2 云台版|169.0|[渠道主图](https://img.youpin.mi-img.com/youpin_gms/8b7d9f31_61e8_476a_b386_539dd68fcb7a.png?w=800&h=800)|[详情](https://www.xiaomiyoupin.com/detail?gid=149429)|
|小米智能摄像机母婴看护版|599.0|[渠道主图](https://img.youpin.mi-img.com/youpin_gms/0aa22a5e_8c1c_45d1_be8f_9bdf16a9f063.png?w=800&h=800)|[详情](https://www.xiaomiyoupin.com/detail?gid=166327)|
|小米智能摄像机C700|299.0|[渠道主图](https://img.youpin.mi-img.com/youpin_gms/f5ebc622_1edd_4e1f_8f54_1eb8e9ac4e76.png?w=800&h=800)|[详情](https://www.xiaomiyoupin.com/detail?gid=166747)|
|米家透明蒸汽电饭煲|699.0|[渠道主图](https://img.youpin.mi-img.com/youpin_gms/cd2cac63_95d0_4f08_93da_995d70a897c5.png?w=800&h=800)|[详情](https://www.xiaomiyoupin.com/detail?gid=156507)|
|4K云台摄像头|null|无，仅 image_mihome|[详情](https://home.mi.com/webapp/content/baike/product/index.html?model=careco.camera.650#/)|
|米家智能空气炸锅3.5L|null|无，仅 image_mihome|[详情](https://home.mi.com/webapp/content/baike/product/index.html?model=careli.fryer.maf03#/)|
|米家智能空气炸锅Pro 4L|null|无，仅 image_mihome|[详情](https://home.mi.com/webapp/content/baike/product/index.html?model=careli.fryer.maf04#/)|


## 验证与复现

基线 1,054 通过、8 个 live 排除；最终离线 **1,068 通过、8 个 live 排除**，原有警告 1，没有新红。[最终日志](tests-final.log)。验证覆盖既有对象不变、幂等重放、B/C 混入拒绝、无价不参与比较、图标不能当主图，以及新整机不会被旧配件规则误排除。

- [输入完整快照](goods-before.json.gz) / [输入 meta](meta-before.json)
- [3,087 个请求索引](requests.json) / [原始响应压缩证据](evidence.tar.gz)（每份原始响应 SHA-256 已复核）
- [本地真实 finalize 日志](dry-run.log)

```bash
python3 scripts/discover_mihome_gaps.py --goods <解压后的 goods-before.json>
python3 scripts/probe_mihome_channels.py
python3 scripts/probe_mihome_channels.py --input docs/mihome-gap-20261106/A.json --output docs/mihome-gap-20261106/channels-all.json
python3 scripts/build_mihome_intake.py --goods <解压后的 goods-before.json>
PYTHONPATH=src:scripts python3 -m pytest -q -m 'not live'
```

先将 evidence.tar.gz 解压到本目录可复用缓存，避免重复网络请求。本次仅 A 类收录；B/C CSV 提供完整逐项列表，C 类未收到决定前保留待定。
