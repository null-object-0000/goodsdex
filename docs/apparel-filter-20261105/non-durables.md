# 非耐用品候选（仅列出，不新增排除）

按名称主体审计，排除咖啡机/胶囊耳机等设备误命中；多组重叠不重复计身份。候选词见 report.py，未命中不代表已证明耐用。完整 JSON 同时列出已被既有规则排除的历史记录。

|status|食品/饮料|消耗品|虚拟服务|一次性用品|
|---|---|---|---|---|
|published|2|6|1|0|
|already_excluded|0|230|46|1|

发布中候选前 20 条（不足 20 条全部列出）：

|id|name|category|groups|status|
|---|---|---|---|---|
|CN:mi_cn:product:10050169|日常元素抑菌洗手液 阳光清柚香/地中海无花果|洗手机|['消耗品']|published|
|CN:mi_cn:product:10050170|日常元素泡沫洗手液（3瓶装）|洗手机|['消耗品']|published|
|CN:mi_cn:product:10679|小卫质品泡沫抑菌洗手液三瓶装（青柠香型） 黄色|洗手机|['消耗品']|published|
|CN:mi_cn:product:10779|喷墨打印机墨水|打印机|['消耗品']|published|
|CN:mi_cn:product:1171700022|小米儿童会员年卡|旧款机型|['虚拟服务']|published|
|CN:mi_cn:product:19488|日常元素泡沫洗手液（3瓶装）|洗手机|['消耗品']|published|
|CN:mi_cn:product:19489|日常元素抑菌洗手液 地中海无花果香 2瓶装|洗手机|['消耗品']|published|
|CN:mi_cn:product:20996|Cafe Royal胶囊咖啡 经典系列 60粒|家电|['食品/饮料']|published|
|CN:mi_cn:product:22262|Café Royal胶囊咖啡 30粒|家电|['食品/饮料']|published|

既有排除记录前 20 条（不是本次新增排除）：

|id|name|category|groups|existing_reason|
|---|---|---|---|---|
|CN:dji:sku:191481|ROMO 去污清洁液|扫地机器人配件|['消耗品']|accessory:category|
|CN:dji:sku:191541|ROMO 拖布|扫地机器人配件|['消耗品']|accessory:category|
|CN:dji:sku:191571|ROMO 基站集尘袋|扫地机器人配件|['消耗品']|accessory:category|
|CN:dji:sku:191691|ROMO 尘盒滤网|扫地机器人配件|['消耗品']|accessory:category|
|CN:dji:sku:192321|ROMO 除菌清洁液（适用于 DJI ROMO P）|扫地机器人配件|['消耗品']|accessory:category|
|CN:dji:sku:239511|ROMO 2 系列尘盒滤网|扫地机器人配件|['消耗品']|accessory:category|
|CN:dji:sku:239841|ROMO 基站集尘袋（超薄基站）|扫地机器人配件|['消耗品']|accessory:category|
|CN:dji:sku:239871|ROMO 去污清洁液（超薄基站）|扫地机器人配件|['消耗品']|accessory:category|
|CN:dji:sku:239901|ROMO 除菌清洁液（超薄基站）|扫地机器人配件|['消耗品']|accessory:category|
|CN:dji:sku:239931|ROMO 去污清洁液（白色外壳）|扫地机器人配件|['消耗品']|accessory:category|
|CN:dji:sku:239961|ROMO 除菌清洁液（白色外壳）|扫地机器人配件|['消耗品']|accessory:category|
|CN:mi_cn:product:10000270|吸顶灯安装服务|灯具|['虚拟服务']|service:installation|
|CN:mi_cn:product:10000275|米家净水器800G、小米净水器H800G/H800G Pro滤芯|净水器|['消耗品']|accessory:name|
|CN:mi_cn:product:10000286|空调清洁保养服务|中央空调Pro|['虚拟服务']|service:other|
|CN:mi_cn:product:10010007|小米净水器400G(厨下式)/小米净水器400G厨上增强版滤芯|净水器|['消耗品']|accessory:name|
|CN:mi_cn:product:10010008|小米台式净饮机，米家台式净饮机智享版/冷热版/凉白开版滤芯|净水器|['消耗品']|accessory:name|
|CN:mi_cn:product:10010029|小米净水器1A （厨下式） 滤芯|净水器|['消耗品']|accessory:name|
|CN:mi_cn:product:10010030|小米净水器500G滤芯|净水器|['消耗品']|accessory:name|
|CN:mi_cn:product:10010031|小米净水器600G滤芯|净水器|['消耗品']|accessory:name|
|CN:mi_cn:product:10010032|小米净水器400G增强版滤芯|净水器|['消耗品']|accessory:name|
