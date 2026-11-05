# 米家匿名设备目录：名称、图标、品类与 model 映射

2026-11-06。仅匿名 GET，未登录、未调用需鉴权接口、未修改发布日期。

**公开目录实得 1,928 个唯一 model / 1,928 个唯一 pdId，15 个有效品牌；100 条随机样本匹配 22%。** 不能声称拿到了全平台所有品牌：品牌来自既有匿名产品响应和有限邻近探测，没有品牌全量枚举 API 的证据。已发现品牌按分类及真实游标抓到空页；服务端声明总量与可见条目仍有差额。

## 数字与边界

|项目|结果|
|---|---:|
|现网小米母体|1,550 行 / 1,545 唯一商城商品 ID|
|确定映射|330（21.36%）|
|固定随机抽样|22/100 = 22%|
|名称修正|58，全部为官方空白/大小写格式统一|
|截断名称恢复|**0**；未将型号代际、颜色、Pro/Max 或规格容器猜成单设备|
|缺图补齐|18，全部 **168×168 设备图标**|
|品类细化|28，只从家电/智能家居/智能家庭等宽泛桶细化|
|旧款机型桶修正|0；采集前现网小米该桶已为 0|
|新增 mihome_model / mihome_pd_id|330 / 330|
|发布日期新增|**0；覆盖率无变化**|

输入为本轮匿名读取 `data` 分支 `public/goods.json` 的 3,572 行完整快照，见 `goods-before.json.gz`。用户提到的 1,583 不是本次现网分母；不以已命中条目作抽样分母。样本用排序后的唯一 `CN:mi_cn:product:*` ID 和 `random.Random(20261106).sample(...,100)` 固定抽取，保留未匹配条目，详见 `sample-100.json`。规格/系列容器不强行绑定某个 device，具体按 `is_container` 排除。

## 分页、分类和品牌

从官方品牌页 `https://home.mi.com/webapp/product/brand/index.html?id=1520` 的 JS `product/brand.b343e1bddb.js` 发现实际调用：

```http
GET /cgi-op/api/v1/brand/h5/list?brandId=1520&classifyId=0&limit=100
GET /cgi-op/api/v1/brand/h5/list?brandId=1520&classifyId=0&limit=100&changeTime=<上一批末条changeTime>&lastPdId=<上一批末条pdId>
```

两个游标必须一起携带；循环到返回空数组，不能因返回少于 limit 就结束（limit=100 首批只有 97 条）。去重 model/pdId、检测游标停滞。`pageIndex=2`、`offset=100`、`pageSize=5&pageIndex=2`、`cursor=100`、`page=2`、`start=100` 都与基准返回相同。`limit=10/50/500/2000` 分别返回 9/47/495/1274；大 limit 可以补充交叉验证，但仍以分类游标并集作为清单。详见 `pagination-probes.json`、`requests.json` 和压缩的原始响应。

分类 ID 直接来自 `brand/h5/detail?id=1520` 的 classifyList，不猜连续数字。品牌候选来自既有匿名 product 响应中观察到的 brandId，之后逐个 detail 验证；脚本串行保证详情请求间隔 ≥2.15 秒，无大范围数字扫描。2/3/4/6 的 detail 都返回 id=1520；limit=2000 的五个别名列表集合一致。初次小分页缓存/可见性有轻微差异，因此最终以显式 1520 为主，并保留全部探测响应。有限邻近探测仅 0/1519/1521：前二者 code=60008，1521=界古、声明 0 条，未作为有设备品牌。

75 个“库内完整同名、APK 中存在、目录未见”的 model 又做了匿名 product 核验，74 个有效，但未发现新的 brandId；这只是面向本库的发现闭环，不证明全球品牌已穷尽。`discovery.json` 保留结果。

|规范品牌 ID|品牌|声明总数|公开分类并集唯一 model|
|---:|---|---:|---:|
|1520|小米公司|1307|1275|
|31|小白|62|62|
|32|知吾煮|6|6|
|33|TOKIT|18|18|
|41|德尔玛|2|2|
|47|追觅|36|36|
|94|Aqara|85|84|
|116|飞利浦|144|144|
|122|石头|19|19|
|123|小瓦|2|2|
|157|Yeelight|231|231|
|163|智米|45|45|
|288|星月|1|1|
|558|纯米|2|2|
|2037|imilab|1|1|

小米详情声明 1,307，公开分类并集 1,275，相差 **32**；Aqara 声明 85、公开 84，相差 **1**。其它已发现品牌与声明一致。声明数不是额外设备记录；没有为了对齐数字虚构 model。小米“全部”大 limit 是 1,274，分类并集另补 1 条。

## 分类分布

|classifyId|官方分类|唯一 model 数|
|---:|---|---:|
|5|安防|160|
|12|照明|329|
|11|插座开关|191|
|13|传感器|40|
|4|影音娱乐|78|
|7|环境电器|303|
|16|路由网关|60|
|3|厨房电器|301|
|21|卫浴|69|
|20|清洁电器|202|
|19|宠物与植物|11|
|8|运动健康|83|
|23|个护与起居|57|
|1|出行车载|21|
|22|办公学习|17|
|9|其他|3|
|—|接口未返回细分类|3|

16 类合计 1,925，另有 3 条仅在“全部”可见，合计 **1,928**。更细的 `categoryName` 分布见 `summary.json` 的 leaf_categories；入库使用细分类而非整个“环境电器”大类。

## 编号桥接与匹配

三套编号不直接比较：商城 product_id、有品 gid、米家 pdId 各自独立。对已有匿名 baike product 证据复核，找到 **287** 个设备的官方商城购买链接，其中 **218** 个 product_id 当前库中存在；另有 **79** 个有品购买链接，与库内现有 gid **0** 个相等。`id-bridges.json` 逐项保留 URL、pdId、model 和原响应哈希。桥接证明的是购买页关联，可能覆盖多规格，因此不单凭购买链接或数字碰撞绑定设备。

本批 330 条均为 NFKC、大小写和空白规范化后完整名称唯一匹配；不删除容量、括号、版本或 Pro/Max。核心段加洗涤容量门禁有实现，但本批通过 0 条；最接近的超净洗洗烘页是 is_container，仍不绑定。既有说明书机型编号证据未产生新的精确身份，未重复下载全量 PDF。异名、多 model 同名、系列容器均保留原样，见 unmatched.json。

`mihome_catalog_evidence` 保留匹配方法、官方接口 URL、响应哈希、分类。显示名修改保留 `name_raw`；分类保留 `category_raw/categories_raw`。日期验证重放使用本批已审核的原身份，所有日期证据校验结束后再应用显示修正，不放宽日期证据规则。

## 五条已落地对照

|商城 product_id|修改前|修改后|内容|
|---|---|---|---|
|12136|米家智能除菌加湿器 S|米家智能除菌加湿器  S|name；deerma.humidifier.jsqs / pdId=72559|
|15858|Xiaomi智能家庭屏 10|Xiaomi 智能家庭屏 10|name；xiaomi.wifispeaker.x10a / pdId=3240|
|3488|缺图|mihome_icon，168×168 设备图标|image；chunmi.cooker.press1 / pdId=66|
|10330|家电|微波炉|category；chunmi.microwave.cmwb3 / pdId=14931|
|18523|家电|蒸烤箱|category；xiaomi.oven.cmtsx8 / pdId=36114|

完整逐项对照见 `changes.json`。已有主图不覆盖；图标没有被标成商城高清商品图。18 张已下载原始字节、Pillow 解码校验和 SHA-256 归档，所有入库行明确 `image_source=mihome_icon`、`image_scope=device_icon`、image_width/image_height 及说明。

## 日期、测试与发布

**这套接口不提供发布日期。** 原响应 createTime/updateTime/changeTime/ts 为记录或接口时间，productOnlineTime 非空无新增发现；没有写入 release。逐条核对所有 release* 和 page_first_archived 字段完全不变。当前严格有效日期 **1,580/3,572 = 44.23% → 44.23%，无变化，+0.00 个百分点**。本次 100 条抽样不是日期覆盖抽样。

基线全量 **1,041 passed、8 deselected**；修后全量 **1,048 passed、8 deselected**，无新增失败，均只有既有 pytest 插件弃用警告。日志见 tests-final.log，发布结果见 publication.json。最初 sparse checkout 缺少既有报告夹导致的测试失败不作为有效基线；补齐后重新跑得上述基线。本轮曾暴露日期重放身份和旧测试冻结图数假设，修复后重跑，不以首轮失败充作最终验收。发布使用 `mihome_catalog_only=true`：持共享发布锁读取最新快照，并断言最终商品列表逐字段等于 `apply_catalog(最新快照)`，阻止其它日期、图片、分类补丁混入本次发布。试跑 3,572 行逐字段通过，见 dry-run-summary.json。

```sh
PYTHONPATH=src python scripts/collect_mihome_catalog.py --output docs/mihome-catalog-20261106 --seed-brands docs/mihome-catalog-20261106/seed-brands-expanded.json
PYTHONPATH=src python scripts/build_mihome_catalog.py --output docs/mihome-catalog-20261106
python docs/mihome-catalog-20261106/audit_evidence.py
PYTHONPATH=src python -m pytest -q -m "not live"
```

原始匿名响应与图标字节在 evidence.tar.gz；requests.json 记录游标请求原 URL 与原始字节 SHA-256。离线核验会验证 330 条映射的名称/model/pdId 确实同时出现在相应官方响应，并校验原始响应与图标哈希。复跑采集应使用新目录，以免复用当前固定快照缓存；品牌种子路径仅作发现证据，不承诺存在全平台品牌范围。
