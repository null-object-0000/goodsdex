# 亚朵星球官方 SKU 目录接入与验收

本轮完整匿名读取官方 H5 商城48 SPU，精确按“亚朵星球 ”品牌前缀纳入38 SPU / 267 SKU；另10条萨和、亚朵村茶与公益商品均不入库。38 SPU含5个标题明确为组合装的SPU。SKU面板另有多只装、搭配购和四件套，总计113条标记 `bundle=true`，商品组件数与清单单列，赠礼袋不混入商品件数。

`price`逐SKU取官方面板 `salesPrice`；`promo_price`单独取 `activityPrice`，包含与销售价相等的活动值，不用SPU起价、券后价、国补价或会员结算价覆盖。267个官方规格选项中258条 `spuStatus=1`、9条 `spuStatus=2`，后者保留价格原值并标 `price_status/sale_status=unavailable_option`。这是完整SKU选项库存，不宣称267条均可购买。

名称按“官方SPU原文 / 官方SKU原文”组成；两个原文也分别保存在 `official_name` / `sku_name`。不截断型号、颜色、只数、组合与预售时效后缀。尺寸/高度只从明确文字提取；填充等未结构化字段保留null，`specs_missing`逐项说明。分类来自官方分类接口的实际SPU归属；两条巾类不在官方导航中，按官方商品名归类，并明确记录依据。

所有主图URL来自亚朵自有CDN。官方轮播图包含大量人物/海报，完整SKU规格图也带文案和表格，均不直接当主图。使用官方CDN对对应SKU原图进行矩形裁剪，只显示白底/近白底商品区域；原URL、裁剪坐标、原图与CDN返回图SHA-256逐SKU留档。没有生成、补绘、换色或借用其它型号图。18条长袖睡衣采用上衣主体局部，`image_scope=sku_primary_garment`，规格名仍完整保留长袖长裤套装；组合/多只装的图示与件数以官方来源为准，图示单个成员不改变整包价格。裁剪接口语法见[七牛官方文档](https://developer.qiniu.com/dora/8256/tailoring)。

采集全新匿名浏览器上下文，只允许官方公开读取端点；业务API请求串行且相邻启动时间≥2.1秒；图片审校下载另行串行限速≥2.1秒。记录中无Cookie、token、Authorization、unionid、localStorage或登录状态。没有访问微信小程序或任何第三方商城。采集中的业务对象与时间见[evidence/capture.json](evidence/capture.json)，本轮最小接口间隔实测2.100秒。

自动化：[refresh-atour](../../.github/workflows/refresh-atour.yml)每天北京时间05:17运行。完整分页、SPU/面板覆盖、唯一SKU、价格、图片审校任一验证失败即停止，不生成发布候选，不据此下架。成功后走共享`publish-release`锁、候选合并、既有门禁、finalize、data分支与OSS镜像；其它品牌重建会保留亚朵记录。

通用留档：完整成功快照与上一轮比较，消失SKU保留原记录、历史价、规格与图片，新增`status=retired`、首次`retired_at`及证据；再次出现会保留退档历史后恢复。本轮创建`public/archive/atour.json`，发布器也把下架行写入通用`archive/retired.json`。失败/部分采集不会制造缺席事件。相关测试覆盖删除一个SKU、重新出现、其它采集器保留亚朵，以及共享archive缺席事件。

原图与裁剪图的六张逐SKU审校联系表位于 `evidence/images/review-*.jpg`、`evidence/crops/sheet-*.jpg`；精确审校清单为[data/official/atour-images.json](../../data/official/atour-images.json)。完整图片可按官方URL和SHA复现：

```bash
python3 scripts/audit_atour_images.py --out /tmp/atour-image-audit
python3 scripts/verify_atour_release.py --capture docs/atour-catalog-20261105/evidence/capture.json --h5-samples docs/atour-catalog-20261105/evidence/h5-samples.json --online --out docs/atour-catalog-20261105/online-verification.json
```

渲染页面的10条独立对照证据见[evidence/h5-samples.json](evidence/h5-samples.json)，并非拿同一接口对象与自身比较。完整发布结果、线上total、3条真实记录、5条随机枕芯及10条逐字对照见下方发布验收。

## 发布验收

发布 run：[41900226785](https://github.com/null-object-0000/goodsdex/actions/runs/41900226785)。代码已推main；共享发布作业已推data并完成OSS镜像。本轮使用verified_snapshot=true导入同日国内匿名已审校快照，全部走正常collector与共享发布门禁。首轮41898936180因runner升级至26.04与固定Playwright不兼容，在安装浏览器时失败；已固定24.04。随后41899314683及只读探测41901313408仍在H5初始导航超时，均未发布。

线上查询：[亚朵星球](https://spend.snewbie.site/api/goods?q=%E4%BA%9A%E6%9C%B5%E6%98%9F%E7%90%83)，`total=267`；OSS `meta.sources.atour.spu_count=38`、`sku_count=267`、`meta.brands.亚朵星球=267`，与官方本轮38/267完全一致，无差1。发布revision：`561a11960b45452bb4702d47572eff7d`。

云端实时采集限制：[41901313408](https://github.com/null-object-0000/goodsdex/actions/runs/41901313408)在等待H5初始页面domcontentloaded时60秒超时，尚未取得HTTP业务响应，不能声称已验证GitHub出口的自动实时刷新。每天05:17的live采集仍失败即停止并保留旧库存；可访问官网的采集端生成新完整快照后，可再走verified_snapshot正常发布、对比退档。本机修正模块等待与定时余量后另重读38/267成功，全部200、最小2.105秒，名称/价/规格/图片及包装与本轮快照无差异，见[独立复核](readiness-recheck.json)。

校验：共享发布门禁573项通过；data提交`0075b8cf532604ffb0fff662adbab16706df17cf`，3414→3681，新增267；旧ID零丢失，其它品牌全对象多重集合相等，见[发布校验](publication.json)。

### 3条真实线上记录

```json
[
  {
    "id": "CN:atour:spu:2099:sku:010020101010411-001",
    "name": "亚朵星球 深睡枕 Pro4.0（深睡稳压枕） / 单只装(枕芯*1+岩溪蓝 外枕套*1)",
    "brand": "亚朵星球",
    "category": "枕芯",
    "price": 435,
    "promo_price": 435,
    "image": "https://xbu-qiniu.yaduo.com/QN/chain/67da8787-5853-42a7-8884-290e3b47927d.jpg?imageMogr2/crop/!720x280a40a250/format/webp",
    "source_url": "https://h5mall.yaduo.com/subpacks/mall/goodsDetail/goodsDetail?id=2099",
    "sku_no": "010020101010411-001",
    "spu_id": 2099,
    "specs": {
      "official_text": "单只装(枕芯*1+岩溪蓝 外枕套*1)",
      "dimensions": null,
      "height": null,
      "filling": null
    },
    "specs_missing": [
      "dimensions",
      "height",
      "filling"
    ],
    "bundle": true,
    "package_quantity": 2,
    "bundle_contents": [
      {
        "name": "深睡枕 Pro4.0 枕芯",
        "quantity": 1
      },
      {
        "name": "岩溪蓝 外枕套",
        "quantity": 1
      }
    ],
    "captured_at": "2026-11-04T19:12:57.176Z"
  },
  {
    "id": "CN:atour:spu:1987:sku:010210005724052",
    "name": "亚朵星球 慢回弹记忆绵枕 / 单只装70*42*6cm",
    "brand": "亚朵星球",
    "category": "枕芯",
    "price": 139,
    "promo_price": null,
    "image": "https://xbu-qiniu.yaduo.com/QN/chain/1668ee76-845e-43e5-8e33-d4b4d030347b.jpg?imageMogr2/crop/!720x285a40a230/format/webp",
    "source_url": "https://h5mall.yaduo.com/subpacks/mall/goodsDetail/goodsDetail?id=1987",
    "sku_no": "010210005724052",
    "spu_id": 1987,
    "specs": {
      "official_text": "单只装70*42*6cm",
      "dimensions": "70*42*6cm",
      "height": "6cm",
      "filling": null
    },
    "specs_missing": [
      "filling"
    ],
    "bundle": false,
    "package_quantity": 1,
    "bundle_contents": null,
    "captured_at": "2026-11-04T19:13:18.161Z"
  },
  {
    "id": "CN:atour:spu:2006:sku:0102000038-l",
    "name": "亚朵星球 90鹅绒复合枕 / 单只装中枕",
    "brand": "亚朵星球",
    "category": "枕芯",
    "price": 299,
    "promo_price": null,
    "image": "https://xbu-qiniu.yaduo.com/QN/chain/b9adfb33-9839-4ee2-becd-7a17ae9bf30c.jpg?imageMogr2/crop/!720x280a40a245/format/webp",
    "source_url": "https://h5mall.yaduo.com/subpacks/mall/goodsDetail/goodsDetail?id=2006",
    "sku_no": "0102000038-l",
    "spu_id": 2006,
    "specs": {
      "official_text": "单只装中枕",
      "dimensions": null,
      "height": null,
      "filling": null
    },
    "specs_missing": [
      "dimensions",
      "height",
      "filling"
    ],
    "bundle": false,
    "package_quantity": 1,
    "bundle_contents": null,
    "captured_at": "2026-11-04T19:14:50.733Z"
  }
]
```

### 枕芯随机5条（固定种子20261105，可复现）

|名称（库中完整原文）|销售价 CNY|规格原文|主图 URL|官方详情页 URL|
|---|---:|---|---|---|
|亚朵星球 深睡枕 Pro4.0（深睡稳压枕） / 单只装(枕芯*1+岩溪蓝 外枕套*1)+深睡枕套 Pro4.0(夜云紫)*1|534|单只装(枕芯*1+岩溪蓝 外枕套*1)+深睡枕套 Pro4.0(夜云紫)*1|[官方白底商品图](https://xbu-qiniu.yaduo.com/QN/chain/aa214ab9-759d-4ed0-8911-769d1c59f846.jpg?imageMogr2/crop/!720x215a40a250/format/webp)|[SPU 2099](https://h5mall.yaduo.com/subpacks/mall/goodsDetail/goodsDetail?id=2099)|
|亚朵星球 深睡枕 Pro1.0 / 70*42*10cm（两只装）|600|70*42*10cm（两只装）|[官方白底商品图](https://xbu-qiniu.yaduo.com/QN/chain/23715661-e5f5-4d4f-9a80-40b1f77f0c9d.jpg?imageMogr2/crop/!720x215a40a250/format/webp)|[SPU 1977](https://h5mall.yaduo.com/subpacks/mall/goodsDetail/goodsDetail?id=1977)|
|亚朵星球 深睡儿童枕 / 星砂蓝两只装(立减10元)|568|星砂蓝两只装(立减10元)|[官方白底商品图](https://xbu-qiniu.yaduo.com/QN/chain/d33f51be-8593-419c-906a-80195888fa1a.jpg?imageMogr2/crop/!720x215a40a250/format/webp)|[SPU 2048](https://h5mall.yaduo.com/subpacks/mall/goodsDetail/goodsDetail?id=2048)|
|亚朵星球 90鹅绒复合枕 / 单只装中枕|299|单只装中枕|[官方白底商品图](https://xbu-qiniu.yaduo.com/QN/chain/b9adfb33-9839-4ee2-becd-7a17ae9bf30c.jpg?imageMogr2/crop/!720x280a40a245/format/webp)|[SPU 2006](https://h5mall.yaduo.com/subpacks/mall/goodsDetail/goodsDetail?id=2006)|
|亚朵星球 深睡随行枕 / 深睡随行枕+深睡眼罩2.0 青空灰|258|深睡随行枕+深睡眼罩2.0 青空灰|[官方白底商品图](https://xbu-qiniu.yaduo.com/QN/chain/9246a33d-2f4f-4cc5-9185-4d800d9be878.jpg?imageMogr2/crop/!720x215a40a250/format/webp)|[SPU 2044](https://h5mall.yaduo.com/subpacks/mall/goodsDetail/goodsDetail?id=2044)|

尺寸/高度/填充等字段与null缺口见[线上机器验收](online-verification.json)，其中不会把多只装价格当单只价。

### 10条H5渲染页面与库逐字对照

页面名、库中`official_name`逐字相同；页面已选规格、库中`sku_name`逐字相同。库中`name`是两者按` / `连接，避免仅存SPU名或仅存颜色。表中两侧名称/规格写在各自列，价格为页面“活动价”显示值与该SKU销售价；本10条两者数值恰好相等，不外推其它规格的优惠口径。

|H5页面商品名|库商品原名|H5已选规格|库SKU原文|H5价格|库销售价|结果|
|---|---|---|---|---:|---:|---|
|[亚朵星球 慢回弹记忆绵枕](https://h5mall.yaduo.com/subpacks/mall/goodsDetail/goodsDetail?id=1987)|亚朵星球 慢回弹记忆绵枕|单只装70*42*6cm|单只装70*42*6cm|139|139|逐字/数值一致|
|[亚朵星球 深睡随行枕](https://h5mall.yaduo.com/subpacks/mall/goodsDetail/goodsDetail?id=2044)|亚朵星球 深睡随行枕|50*30*10cm（单只装）|50*30*10cm（单只装）|169|169|逐字/数值一致|
|[亚朵星球 深睡儿童枕](https://h5mall.yaduo.com/subpacks/mall/goodsDetail/goodsDetail?id=2048)|亚朵星球 深睡儿童枕|绮光粉单只装|绮光粉单只装|289|289|逐字/数值一致|
|[亚朵星球 深睡枕 Pro1.0](https://h5mall.yaduo.com/subpacks/mall/goodsDetail/goodsDetail?id=1977)|亚朵星球 深睡枕 Pro1.0|70*42*10cm（单只装）|70*42*10cm（单只装）|300|300|逐字/数值一致|
|[亚朵星球 90鹅绒复合枕](https://h5mall.yaduo.com/subpacks/mall/goodsDetail/goodsDetail?id=2006)|亚朵星球 90鹅绒复合枕|单只装中枕|单只装中枕|299|299|逐字/数值一致|
|[亚朵星球 深睡枕 Pro4.0（深睡稳压枕）](https://h5mall.yaduo.com/subpacks/mall/goodsDetail/goodsDetail?id=2099)|亚朵星球 深睡枕 Pro4.0（深睡稳压枕）|单只装(枕芯*1+岩溪蓝 外枕套*1)|单只装(枕芯*1+岩溪蓝 外枕套*1)|435|435|逐字/数值一致|
|[亚朵星球 深睡枕套 Pro4.0](https://h5mall.yaduo.com/subpacks/mall/goodsDetail/goodsDetail?id=2113)|亚朵星球 深睡枕套 Pro4.0|深睡蓝|深睡蓝|99|99|逐字/数值一致|
|[亚朵星球 深睡双感眼罩2.0](https://h5mall.yaduo.com/subpacks/mall/goodsDetail/goodsDetail?id=2034)|亚朵星球 深睡双感眼罩2.0|深睡蓝|深睡蓝|89|89|逐字/数值一致|
|[亚朵星球 深睡抱枕](https://h5mall.yaduo.com/subpacks/mall/goodsDetail/goodsDetail?id=1965)|亚朵星球 深睡抱枕|浅灰蓝-105*30cm|浅灰蓝-105*30cm|219|219|逐字/数值一致|
|[亚朵星球 深睡儿童枕套](https://h5mall.yaduo.com/subpacks/mall/goodsDetail/goodsDetail?id=2049)|亚朵星球 深睡儿童枕套|星砂蓝|星砂蓝|79|79|逐字/数值一致|

原始渲染正文与采集时间见[evidence/h5-samples.json](evidence/h5-samples.json)；完整线上响应见[api-atour.json](api-atour.json)。接口返回前20条，`total=267`；三条完整详情又逐条与OSS整库做了全对象相等校验。
