# 品牌回填与配件补漏验收

本次以 data 提交 b07660b0 的 2909 行真实发布数据为基线，与线上 `/api/goods` 的 ID 顺序、品牌字段和条数一致；两端存在正常采集代差（Apple 价格时间戳、6 行现价及少量汽车/惠普采集字段），不将其伪报为字节一致。原始基线含 1552 行空品牌（53.35%），与提单时的 1547 有 5 行差异；按本轮实测统计。原 `/api/meta.brands` 已通过 ID 临时把空品牌算作小米，但 index/mi_cn.json 仅 143 行、index/other.json 1552 行。品牌原字段与统计口径不一致，不能把原 meta 的小米 1695 当作 brand 已回填。

品牌规则位于 `src/goodsdex/brands.py`：大小写不敏感的 ID 命名空间优先，精确 source/同义词其次，明确的名称前缀再次，最后是审核覆盖/既有明确品牌；不使用 LLM。既有明确品牌归为 manual。无法判定时 brand/brand_source 均为 null（没有证据就不伪造来源），完整 ID/名称/source/原因写入 data 分支 `public/archive/brand-review.json`。本次全部由 ID 前缀判定，brand_source=id_prefix；人工表为空。每次共享 finalize 都执行，采集器覆盖旧记录后也会恢复；轻索引、详情、完整导出均携带 brand_source。

|品牌|实际 brand 回填前|只回填后|过滤后发布|
|---|---:|---:|---:|
|Apple|635|635|635|
|大疆|281|281|281|
|富士|63|63|63|
|惠普|218|218|218|
|小米|143|1695|1684|
|比亚迪|14|14|14|
|小米汽车|3|3|3|
|未知|1552|0|0|
|合计|2909|2909|2898|
|未知比例|53.35%|0%|0%|

剩余 unknown 前缀 Top 10：空，剩余 0 行，无无法判断的前缀。没有用猜测品牌填充；当前全部已知品牌的稳定 ID 命名空间均有规则覆盖。后续遇到无法识别的前缀、来源、名称、既有品牌，将保持空并进入人工清单。

## 配件根因与范围

`CN:mi_cn:product:10000292` 的名称为「新秀无畏」系列笔记本定制贴纸，价格 99 元，原分类笔记本。共享 finalize 已执行现有过滤；不是只在某个采集器执行。旧关键词缺少“贴纸”，而 DEVICE 命中“笔记本”，PARTS 没有覆盖普通定制贴纸（只有保护贴纸），因此以 whole_device 放行。

补充本次实测命中的“贴纸、类纸膜、高透膜、钢化玻璃膜、清洁剂”。清洁剂是现有清洁液耗材规则的补漏，不使用宽泛的“清洁”词；清洁保养服务、整机赠/含贴纸或膜均保留。提单列出的保护膜已在原表并生效；键盘膜、内胆包、鼠标垫、耳机套、贴膜工具、清洁套装、定制壳在本次发布集未发现，未凭空加词。电饭煲内胆未在本轮扩排。

新增排除 **11** 行（5 贴纸、3 膜、3 清洁剂），已有档案 1059 行保持原对象逐值不变，排除档案共 **1070** 行。新排除记录带 accessory:sticker / accessory:screen_film / accessory:cleaning_consumable，以及 exclusion 判定明细；首次快照不覆盖，源档案、价格历史不修改。新增排除门禁 11/2887=0.381%，正常绿灯，无人工放行参数。

相机 41→41、相机镜头 39→39，合计相机与镜头 80→80；笔记本 201→196，减少的 5 行全部是上述贴纸，没有移除笔记本整机。电脑 210→210、无人机 51→51、运动相机 94→94、洗地机 34→34、净水器 50→50、电视 100→100、空调 2→2。以下按原主 category 统计，不改变既有 category/categories 语义；完整所有主类目见 comparison.json。

|主品类|前|排除|后|
|---|---:|---:|---:|
|笔记本|201|5|196|
|平板|213|1|212|
|旧款机型|226|2|224|
|家电|78|2|76|
|扫地机器人|12|1|11|

扫地机器人少的 1 行是“日常元素地面清洁剂（自动添加版）”，不是机器人。逐行校验：保留行除 brand/brand_source 外的所有字段、顺序、冲突 ID 各行均完全相同，排除档案原 1059 行完整保留。汽车新增 brand_source 是可复验的发布派生字段，重复迁移时核对其规则来源；不修改嵌套 source_record。

## 20 条真实排除样本

以下包含本次全部 11 条新增，以及既有档案 9 条；不能为凑 20 条扩大排除。完整 ID/批次/原因见 comparison.json 的 excluded_samples20。

|批次|ID|名称|excluded_reason|
|---|---|---|---|
|new|CN:mi_cn:product:10000292|「新秀无畏」系列笔记本定制贴纸|accessory:sticker|
|new|CN:mi_cn:product:13929|【定制】小米笔记本Pro 15 OLED 机车女孩款贴纸|accessory:sticker|
|new|CN:mi_cn:product:13930|小米笔记本Pro 15 OLED 宇航员款贴纸|accessory:sticker|
|new|CN:mi_cn:product:13931|【定制】RedmiBook Pro 15 机车女孩款贴纸|accessory:sticker|
|new|CN:mi_cn:product:13932|【定制】RedmiBook Pro 15 宇航员款贴纸|accessory:sticker|
|new|CN:mi_cn:product:16422|日常元素地面清洁剂 1L|accessory:cleaning_consumable|
|new|CN:mi_cn:product:18012|日常元素地面清洁剂 200ml|accessory:cleaning_consumable|
|new|CN:mi_cn:product:18029|日常元素地面清洁剂（自动添加版）|accessory:cleaning_consumable|
|new|CN:mi_cn:product:20218|Redmi Pad Pro 类纸膜 透明色|accessory:screen_film|
|new|CN:mi_cn:product:7790|小米MIX 2S 标准高透膜|accessory:screen_film|
|new|CN:mi_cn:product:8136|小米8 标准钢化玻璃膜|accessory:screen_film|
|historical|CN:mi_cn:product:19186|Redmi Pad SE 钢化保护膜 透明|accessory|
|historical|CN:dji:sku:109971|DJI 65W 车载充电器|accessory|
|historical|CN:mi_cn:product:11859|小米Type-C转Lightning数据线 1m|accessory|
|historical|CN:dji:sku:101241|御 Mavic 2 行业版智能飞行电池|accessory|
|historical|CN:dji:sku:117771|DJI Pocket 2 保护壳|accessory|
|historical|CN:mi_cn:product:10000275|米家净水器800G、小米净水器H800G/H800G Pro滤芯|accessory|
|historical|CN:dji:sku:191541|ROMO 拖布|accessory|
|historical|CN:dji:sku:128241|DJI Mini 3 系列全向桨叶保护罩|accessory|
|historical|CN:dji:sku:117801|DJI RS 2 便携收纳包|accessory|

## 复现

```bash
PYTHONPATH=src python3 docs/brand-accessory-20261103/report.py \
  --before docs/brand-accessory-20261103/baseline-goods.json.gz \
  --old-archive docs/brand-accessory-20261103/baseline-archive.json.gz \
  --after /path/to/data/public/goods.json \
  --archive /path/to/data/public/archive/accessories.json \
  --out /tmp/brand-accessory-comparison.json
PYTHONPATH=src:scripts python3 -m pytest -q
```

正式发布、线上 curl 返回与提交号见 publication.md。
