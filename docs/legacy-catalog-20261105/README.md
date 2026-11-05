# 旧来源桶 223 条修复验收

223 个 ID 全部保留：主列表 182 + 排除档案 41；待人工 0。

|真实品类|条数|
|---|---:|
|VR设备|3|
|乐器|1|
|健康测量|4|
|儿童定位设备|1|
|充电宝|4|
|净水器|2|
|出行|5|
|学习机|1|
|家纺家具|12|
|对讲机|1|
|手机|36|
|手环|1|
|手表|2|
|投影仪|1|
|摄像机|5|
|料理机|1|
|无人机|2|
|智能家居|16|
|服务|1|
|服饰|7|
|玩具|7|
|生活用品|8|
|电动牙刷|1|
|电磁炉|1|
|电视|8|
|电视盒子|3|
|电饭煲|3|
|相机|6|
|眼镜|6|
|空气净化器|2|
|笔记本|13|
|箱包|14|
|耳机|4|
|路由器|6|
|车载设备|5|
|配件|20|
|音箱|3|
|风扇|1|
|首饰|2|
|鼠标|4|

价格：`page_no_price` 223。主图：`page_no_image` 173；有型号主图 50。139 条保留原 Wayback 存档时间，实际采集时间未知；84 条沿用原记录 fetched_at。

冻结时线上已有 8 条被服饰规则排除，主列表剩 215 条。当前 source_url 为 128 个 Wayback + 95 个商城页：其中11条历史笔记本后续已由官方名称修复替换为商城来源，原139条 Wayback证据另存 archived_source_url。2条板鞋在旧排除清单中的source_url为空，本轮从同ID已存在的archive/apparel.json恢复（见source-url-recovery.json），其余链接保持原值。没有伪造source_url。

原图片补充清单60张，其中2张板鞋的排除档案没有主图且旧补图证据仅为 series，未补回；本次冻结非空58张，其中8张 series 也降为 reference_image，保留原图URL与证据，不冒充型号主图。故验收为50/173，不沿用原60/163。

系列展示以品牌+系列作为父组；series_key 保留品牌+系列+尺寸/代际子键，尺寸、CPU、内存、存储、颜色等名称明确写出的配置进 attrs。红米5父组7条；小米笔记本Air父组8条（本次6条+原已正确分类的12.5/13.3四核增强2条，仅补聚合标记）。组价均null，显示“旧款 · 无现价”，历史标价只在其原配置记录独立展示。

## 排除前清单（每品类前20条）

分类后由既有 apparel / accessory 规则自动命中；41条中8条此前已排除，本次新增33条。没有删除源记录。

### 服饰：7 条

|ID|名称|主排除理由|
|---|---|---|
|CN:mi_cn:product:10000067|Free Tie 真皮板鞋|apparel|
|CN:mi_cn:product:10000102|米家运动鞋2|apparel|
|CN:mi_cn:product:6518|Free Tie 真皮板鞋 男款|apparel|
|CN:mi_cn:product:8263|米家运动鞋2 男款|apparel|
|CN:mi_cn:product:8264|米家运动鞋2 女款|apparel|
|CN:mi_cn:product:8605|8周年纪念款T恤|apparel|
|CN:mi_cn:product:8806|90分轻薄无缝一体织鹅绒羽绒服|apparel|

### 配件：20 条

|ID|名称|主排除理由|
|---|---|---|
|CN:mi_cn:product:10000066|电力猫套装|accessory:category|
|CN:mi_cn:product:10000081|小米米家插线板|accessory:category|
|CN:mi_cn:product:10000105|米家二位转换器|accessory:category|
|CN:mi_cn:product:1182700039|小米红外遥控器|accessory:category|
|CN:mi_cn:product:4814|米家扫地机器人主刷|accessory:category|
|CN:mi_cn:product:4815|米家扫地机器人边刷|accessory:category|
|CN:mi_cn:product:4817|米家扫地机器人主刷罩|accessory:category|
|CN:mi_cn:product:4888|米家插线板6位基础版|accessory:category|
|CN:mi_cn:product:5481|积木机器人传感器|accessory:category|
|CN:mi_cn:product:5501|电力猫套装|accessory:category|
|CN:mi_cn:product:5678|米家智能插线板|accessory:category|
|CN:mi_cn:product:5857|小米插线板 5孔位|accessory:category|
|CN:mi_cn:product:6009|米粉卡日租卡|accessory:category|
|CN:mi_cn:product:7209|青米智能插线板|accessory:category|
|CN:mi_cn:product:7309|九号平衡车Plus 载物筐|accessory:category|
|CN:mi_cn:product:7591|米家四位四控插线板|accessory:category|
|CN:mi_cn:product:7627|米家车载逆变器|accessory:category|
|CN:mi_cn:product:7805|小米插线板（含3口USB 2A快充）|accessory:category|
|CN:mi_cn:product:8311|米家手持手机云台|accessory:category|
|CN:mi_cn:product:8581|小米蓝牙语音遥控器|accessory:category|

### 箱包：14 条

|ID|名称|主排除理由|
|---|---|---|
|CN:mi_cn:product:2839|小米极简都市双肩包|apparel|
|CN:mi_cn:product:3452|小米经典商务双肩包|apparel|
|CN:mi_cn:product:3460|小米多功能都市休闲胸包|apparel|
|CN:mi_cn:product:3938|90分轻户外旅行洗漱包|apparel|
|CN:mi_cn:product:6621|90分金属登机箱|apparel|
|CN:mi_cn:product:7132|90分户外休闲双肩包|apparel|
|CN:mi_cn:product:7140|90分轻商务登机箱 米家定制|apparel|
|CN:mi_cn:product:7688|90分全天候机能背包|apparel|
|CN:mi_cn:product:7841|90分简约头层小牛皮手包|apparel|
|CN:mi_cn:product:7899|小米极客双肩包|apparel|
|CN:mi_cn:product:8621|小米小背包|apparel|
|CN:mi_cn:product:8655|90分旅行箱 1A 20英寸|apparel|
|CN:mi_cn:product:8656|90分旅行箱 1A 26英寸|apparel|
|CN:mi_cn:product:8878|米兔拉杆箱|apparel|

“米家内衣物洗烘一体机”保留在主列表：CN:mi_cn:product:18431。

完整逐项记录见 after-223.json；待人工清单见 manual-review.json（空）；完整排除计划见 exclusion-plan.json。截图、测试、提交和发布记录见 [publication.md](publication.md)。
