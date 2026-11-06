# 小米耳机 CN 目录入库验收（2026-11-06）

本轮收录23条型号（17主线、6联名/限定），不因缺价格或日期排除。ID直接使用CN目录model；primary_source与discovered_by均为earbuds_directory，每行唯一primary。保留完整sources、observations与display，商城/有品为secondary。全部price=null、price_missing=no_channel_price、price_comparable=false，display.price也保留missing原因。常规采集通过goods-supplements保留这23条，不依赖下次重新访问App接口。

目录证据直接复用DSH的CN生产响应（39条），未重做APK、鉴权、区域探测。仅复制无密钥的CN响应及必要对照表；不复制APK、Cookie或DE/SG数据。DSH原始报告只记录抓取日，未保留精确HTTP时间，captured_at按2026-11-06 UTC日界规范化，evidence明确captured_at_precision=day及归一依据；不冒充秒级抓取时间。source_url为CN接口完整查询，鉴权仅注明需要App内置静态Cookie。

## 23条与10条抽样

完整入库结果：[all-23.json](all-23.json)；10条完整来源/图片/空价标记：[sample-10.json](sample-10.json)。所有样本来源均为earbuds_directory，price_missing均为no_channel_price。

| 型号 | 目录model | 官方图 |
|---|---|---|
| Redmi Buds 4 Pro | `miwear.headphone.l76c` | [图片](https://cdn.cnbj1.fds.api.mi-img.com/static-files/tws_icon/e688c1ee0aa9a288b4d13d2bb1946bab-black.png) |
| Redmi Buds 4 | `miwear.headphone.l77c` | [图片](https://cdn.cnbj1.fds.api.mi-img.com/static-files/tws_icon/aa70a3d4c52f673e029f8150815c1601-white.png) |
| Xiaomi Buds 4 Pro | `miwear.headphone.l71c` | [图片](https://cdn.cnbj1.fds.api.mi-img.com/static-files/tws_icon/4468e86d4d72e00ab4f18a7f2ad78d43-tarnish.png) |
| Xiaomi Buds 3 Star Wars | `miwear.headphone.k75sc` | [图片](https://cdn.cnbj1.fds.api.mi-img.com/static-files/tws_icon/765774863db308b19b896ebb8fbd95c7.png) |
| Redmi Buds 4 哈利·波特版 | `miwear.headphone.l77sc` | [图片](https://cdn.cnbj1.fds.api.mi-img.com/static-files/tws_icon/8dfaca97e875bc97beae05ef0abcc675.png) |
| Xiaomi 真无线降噪耳机 3 迪士尼100周年限定版 | `miwear.headphone.k75mcn` | [图片](https://cdn.cnbj1.fds.api.mi-img.com/static-files/tws_icon/66914a9721779195ef46d077f2443b62.png) |
| Xiaomi Buds 5 | `miwear.headphone.n75c` | [图片](https://cdn.cnbj1.fds.api.mi-img.com/static-files/tws_icon/N75_0611_国内白.png) |
| REDMI Buds 6 Pro | `miwear.headphone.o76cn` | [图片](https://cdn.cnbj1.fds.api.mi-img.com/static-files/tws_icon/O76cn_白色.png) |
| Xiaomi Buds 5 Pro Wi-Fi | `miwear.headphone.o71c` | [图片](https://cdn.cnbj1.fds.api.mi-img.com/static-files/tws_icon/O71c_首页设备图__黑色.png) |
| REDMI Clip Neo | `miwear.headphone.q74cc` | [图片](https://cdn.cnbj1.fds.api.mi-img.com/hlth-operate/article/user/resource/%E5%8D%95%E5%B8%A7860x580_167658097999885.png) |

## 第二源与价格

全23条均搜索小米商城及有品，接口错误0。保守核验产品名/详情；Wi-Fi版另按DSH已核SKU关系确认，拒绝把Pro、基础款、限定版和模糊搜索推荐互相替代。搜索未命中只说明本轮检索未获得对应商品，不说明从未上市。

总命中2/23=8.70%；商城2/23、有品1/23（Clip Neo重叠）。固定10条覆盖样本命中2/10=20%，该样本故意包含两条已知渠道候选，不是随机命中率估计；总体实际命中率以全23条为准。逐查询、候选、错误和完整压缩响应见[channel-searches.json](channel-searches.json)、[channel-summary.json](channel-summary.json)及raw/。

| 目录型号 | secondary渠道 | 官方名 | product_id | gid | 渠道标价 |
|---|---|---|---|---|---|
| Xiaomi Buds 5 Pro Wi-Fi | mi_store | Xiaomi Buds 5 Pro Wi-Fi版 幻影黑 | 20978 | 2230003554 | ¥879 |
| REDMI Clip Neo | mi_store | REDMI Clip Neo | 25802 | 2230016745 | ¥399 |
| REDMI Clip Neo | youpin | REDMI Clip Neo | — | 185253 | ¥399 |

上述价均标price_kind=list，表示本轮渠道展示标价，不是上市首发价、历史价或券后最低价。写入secondary.fields.channel_price及channel_links；顶层price继续为空，符合本轮23条无价型号收录要求，不把同一商城商品重复计为可比报价。来源中的官方名也保留，目录显示名仍来自目录。

Wi-Fi版关联已存在的商城product 20978、gid 2230003554，作为独立目录型号存在，record_level=model_reference，不新建商城product记录。Clip Neo保留目录ID，关联商城25802与有品185253，不再额外创建同一商城商品行。

## 同品牌、同名称、同价格重复扫描（不删除）

按字段原值严格分组（不做模糊归并，null单列分组）：125组，涉及392行，按每组留1计算的候选冗余267行；有价114组、无价11组；同ID2组、跨来源0组，全部字段相等0组。删除/合并0条。

完整清单含全部ID、来源、差异字段、料号/颜色：[duplicates.json](duplicates.json)；前20组机器清单：[duplicates-first-20.json](duplicates-first-20.json)。以下列前20组；“候选冗余”不等于确认可以删除。

| # | 品牌 | 名称 | 价格 | 行数 | 不同ID数 | 来源 |
|---|---|---|---|---|---|---|
| 1 | Apple | iMac | 12499 | 8 | 8 | apple_cn |
| 2 | Apple | iMac | 13999 | 8 | 8 | apple_cn |
| 3 | Apple | iPad Air | 8199 | 8 | 8 | apple_cn |
| 4 | Apple | iPad Air | 9499 | 8 | 8 | apple_cn |
| 5 | Apple | AirPods Max 2 | 3999 | 5 | 5 | apple_cn |
| 6 | Apple | HomePod mini 2 | 1099 | 5 | 5 | apple_cn |
| 7 | Apple | iPhone 16 | 5999 | 5 | 5 | apple_cn |
| 8 | Apple | iPhone 17 | 6799 | 5 | 5 | apple_cn |
| 9 | Apple | iPhone 17 | 8799 | 5 | 5 | apple_cn |
| 10 | Apple | Apple Watch Series 12 | 2999 | 4 | 4 | apple_cn |
| 11 | Apple | Apple Watch Series 12 | 3399 | 4 | 4 | apple_cn |
| 12 | Apple | Apple Watch Series 12 | 3799 | 4 | 4 | apple_cn |
| 13 | Apple | Apple Watch Series 12 | 4199 | 4 | 4 | apple_cn |
| 14 | Apple | MacBook Air | 11999 | 4 | 4 | apple_cn |
| 15 | Apple | MacBook Air | 9999 | 4 | 4 | apple_cn |
| 16 | Apple | MacBook Neo | 5499 | 4 | 4 | apple_cn |
| 17 | Apple | MacBook Neo | 6299 | 4 | 4 | apple_cn |
| 18 | Apple | MacBook Pro (Liquid 视网膜 XDR 显示屏) | 24999 | 4 | 4 | apple_cn |
| 19 | Apple | MacBook Pro (Liquid 视网膜 XDR 显示屏) | 35999 | 4 | 4 | apple_cn |
| 20 | Apple | iPad | 3799 | 4 | 4 | apple_cn |

AirPods Max 2的¥3999五行ID分别以MHWK4CH/A、MHWL4CH/A、MHWM4CH/A、MHWN4CH/A、MHWP4CH/A结尾，来源全为apple_cn，分别为午夜、星光、蓝、橙、紫，attrs/variant_attrs/料号/图片均存在差异。因此它们满足本轮三字段重复条件，但不属于整个记录完全相同，不能直接按名称/价格删除。另有GLOBAL:apple_support:model:126620无价支持站参考行，与有价五行不在同价格组。

同ID的2组是REDMI K90与米家洗衣机超净洗滚筒系列，各3行，存在分类、参数、gid/来源观察差异，也不做自动合并。其余组以不同SKU ID为主，不能因为同品牌同名同价就将容量/颜色/规格抹去。

建议后续规则：同ID先逐字段核对，互补观察可合并进sources.observations，冲突需保留且复核；不同ID先确认相同型号、容量、颜色、套餐与地区，才能将渠道ID绑定到共同产品身份，仍保留各SKU/offer。三字段键只产生复核队列，不触发删除。

## 日期覆盖率

本轮真实基线为1646/4468=36.84%，新增后为1646/4491=36.65%（下降0.19个百分点）；无日期2822→2845，分子不变。

题述46.08%来自历史1646/3572；若仅在该历史基线上加23条，则1646/3595=45.79%。最新线上已增加其他任务商品，不能将历史46.08%直接当成本轮发布前数字。两套口径见[coverage.json](coverage.json)。

## 测试与发布

支持空价、目录主源、海外域名拒绝、日期拒绝、错误型号拒绝、来源保留、逐行重放与CN原始证据对账；共享发布锁内执行Earbuds专用追加模式，并断言after==apply_intake(before)，已有行（包括所有重复候选）完全不变。保留原排除决定和归档，更新发布元数据/分片。发布回执与最终线上读回结果将在完成后补入publication.json。

真实快照完整finalizer重放通过：[replay-acceptance.json](replay-acceptance.json)，4468→4491、旧4468行逐字段相等、23条来源与详情分片核验通过、76个发布文件哈希核验通过，价格历史新增0。第一轮全量离线1108 passed/8 deselected；补充CN原始响应对账后定向46 passed。最终完整测试日志另见tests-final.log。
