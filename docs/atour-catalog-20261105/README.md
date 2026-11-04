# 亚朵星球官方 SKU 目录接入与验收

本轮完整匿名读取官方 H5 商城48 SPU，精确按“亚朵星球 ”品牌前缀纳入38 SPU / 267 SKU；另10条萨和、亚朵村茶与公益商品均不入库。38 SPU含5个标题明确为组合装的SPU。SKU面板另有多只装、搭配购和四件套，总计113条标记 `bundle=true`，商品组件数与清单单列，赠礼袋不混入商品件数。

`price`逐SKU取官方面板 `salesPrice`；`promo_price`单独取 `activityPrice`，包含与销售价相等的活动值，不用SPU起价、券后价、国补价或会员结算价覆盖。267个官方规格选项中258条 `spuStatus=1`、9条 `spuStatus=2`，后者保留价格原值并标 `price_status/sale_status=unavailable_option`。这是完整SKU选项库存，不宣称267条均可购买。

名称按“官方SPU原文 / 官方SKU原文”组成；两个原文也分别保存在 `official_name` / `sku_name`。不截断型号、颜色、只数、组合与预售时效后缀。尺寸/高度只从明确文字提取；填充等未结构化字段保留null，`specs_missing`逐项说明。分类来自官方分类接口的实际SPU归属；两条巾类不在官方导航中，按官方商品名归类，并明确记录依据。

所有主图URL来自亚朵自有CDN。官方轮播图包含大量人物/海报，完整SKU规格图也带文案和表格，均不直接当主图。使用官方CDN对对应SKU原图进行矩形裁剪，只显示白底/近白底商品区域；原URL、裁剪坐标、原图与CDN返回图SHA-256逐SKU留档。没有生成、补绘、换色或借用其它型号图。18条长袖睡衣采用上衣主体局部，`image_scope=sku_primary_garment`，规格名仍完整保留长袖长裤套装；组合/多只装的图示与件数以官方来源为准，图示单个成员不改变整包价格。裁剪接口语法见[七牛官方文档](https://developer.qiniu.com/dora/8256/tailoring)。

采集全新匿名浏览器上下文，只允许官方公开读取端点；全程≥2.1秒。记录中无Cookie、token、Authorization、unionid、localStorage或登录状态。没有访问微信小程序或任何第三方商城。采集中的业务对象与时间见[evidence/capture.json](evidence/capture.json)，本轮最小接口间隔实测2.100秒。

自动化：[refresh-atour](../../.github/workflows/refresh-atour.yml)每天北京时间05:17运行。完整分页、SPU/面板覆盖、唯一SKU、价格、图片审校任一验证失败即停止，不生成发布候选，不据此下架。成功后走共享`publish-release`锁、候选合并、既有门禁、finalize、data分支与OSS镜像；其它品牌重建会保留亚朵记录。

通用留档：完整成功快照与上一轮比较，消失SKU保留原记录、历史价、规格与图片，新增`status=retired`、首次`retired_at`及证据；再次出现会保留退档历史后恢复。本轮创建`public/archive/atour.json`，发布器也把下架行写入通用`archive/retired.json`。失败/部分采集不会制造缺席事件。相关测试覆盖删除一个SKU、重新出现、其它采集器保留亚朵，以及共享archive缺席事件。

原图与裁剪图的六张逐SKU审校联系表位于 `evidence/images/review-*.jpg`、`evidence/crops/sheet-*.jpg`；精确审校清单为[data/official/atour-images.json](../../data/official/atour-images.json)。完整图片可按官方URL和SHA复现：

```bash
python3 scripts/audit_atour_images.py --out /tmp/atour-image-audit
python3 scripts/verify_atour_release.py --capture docs/atour-catalog-20261105/evidence/capture.json --h5-samples docs/atour-catalog-20261105/evidence/h5-samples.json --online --out docs/atour-catalog-20261105/online-verification.json
```

渲染页面的10条独立对照证据见[evidence/h5-samples.json](evidence/h5-samples.json)，并非拿同一接口对象与自身比较。完整发布结果、线上total、3条真实记录、5条随机枕芯及10条逐字对照见下方发布验收。
