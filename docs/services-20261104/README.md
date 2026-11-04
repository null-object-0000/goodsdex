# 服务排除验收

| 口径 | 修前 | 修后 |
|---|---:|---:|
| total_all | 3982 | 3982 |
| total_published | 2902 | 2856 |
| total_excluded | 1080 | 1126 |

total_published 是发布库（含历史下架），沿用原验收 2902 条口径，不将缺少 sale_status 的记录伪称为已验证在售。

| 主类目 | 发布修前 | 发布修后 | 整机修前 | 整机修后 |
|---|---:|---:|---:|---:|
| 手机 | 173 | 173 | 173 | 173 |
| 笔记本 | 196 | 196 | 196 | 196 |
| 电视 | 110 | 110 | 110 | 110 |
| 空调 | 2 | 2 | 2 | 2 |
| 中央空调Pro | 76 | 69 | 69 | 69 |
| 冰箱 | 81 | 81 | 81 | 81 |
| 波轮洗衣机 | 72 | 71 | 71 | 71 |
| 滚筒洗衣机 | 64 | 64 | 64 | 64 |
| 灯具 | 72 | 58 | 58 | 58 |
| 摄像机 | 41 | 40 | 40 | 40 |
| REDMI路由器 | 22 | 21 | 21 | 21 |
| 家庭屏 | 12 | 11 | 11 | 11 |

整机误伤 0；非服务行逐字段、多重集合完全一致。灯具按 category/categories 合集计数，服务移除不冒充整机损失。

## 全部服务明细（每行 1 条）

| ID | 名称 | 价格 ¥ | 理由 |
|---|---|---:|---|
| CN:mi_cn:product:10000270 | 吸顶灯安装服务 | 45 | service:installation |
| CN:mi_cn:product:10000286 | 空调清洁保养服务 | 99 | service:other |
| CN:mi_cn:product:10050101 | 筒射灯（不含开孔）安装服务 | 80 | service:installation |
| CN:mi_cn:product:1230800841 | REDMI Note系列屏幕换新服务 Redmi | 370 | service:other |
| CN:mi_cn:product:1230801232 | Redmi Note系列后盖换新服务 Redmi | 140 | service:other |
| CN:mi_cn:product:1230802603 | 其它系列后盖换新服务 | 210 | service:other |
| CN:mi_cn:product:1230804878 | 其它系列屏幕换新服务 | 670 | service:other |
| CN:mi_cn:product:1230804966 | 其他系列 优惠屏 屏幕换新服务 | 245 | service:other |
| CN:mi_cn:product:13099 | 卧室吸顶灯安装服务 | 45 | service:installation |
| CN:mi_cn:product:13100 | 客厅吸顶灯安装 | 70 | service:installation |
| CN:mi_cn:product:13101 | 吸顶灯一室一厅套装安装 | 95 | service:installation |
| CN:mi_cn:product:13102 | 吸顶灯两室一厅套装安装 | 125 | service:installation |
| CN:mi_cn:product:13103 | 吸顶灯三室一厅套装安装 | 160 | service:installation |
| CN:mi_cn:product:13224 | REDMI K系列屏幕换新服务 Redmi K | 450 | service:other |
| CN:mi_cn:product:13225 | REDMI Note系列屏幕换新服务 Redmi | 370 | service:other |
| CN:mi_cn:product:13226 | REDMI X系列屏幕换新服务 Redmi 10X 屏幕换新服务 | 390 | service:other |
| CN:mi_cn:product:13227 | REDMI 数字系列屏幕换新服务 Redmi | 260 | service:other |
| CN:mi_cn:product:13228 | 其它系列屏幕换新服务 | 670 | service:other |
| CN:mi_cn:product:13232 | 小米数字系列屏幕换新服务 Xiaomi 1 | 670 | service:other |
| CN:mi_cn:product:13846 | 洗衣机清洁保养服务 | 99 | service:other |
| CN:mi_cn:product:13847 | 空调挂机清洁保养服务 | 99 | service:other |
| CN:mi_cn:product:13860 | 立式空调清洁保养服务 | 159 | service:other |
| CN:mi_cn:product:15680 | 空调检测服务 | 50 | service:other |
| CN:mi_cn:product:18454 | 摄像机安装服务 摄像机安装服务 | 80 | service:installation |
| CN:mi_cn:product:18458 | 路由器安装调试 安装服务 | 75 | service:installation |
| CN:mi_cn:product:20903 | 米家面板灯安装服务 | 60 | service:installation |
| CN:mi_cn:product:20954 | 米家中央空调（多联机）上门勘测服务 | 0.01 | service:other |
| CN:mi_cn:product:21212 | 筒射灯（不含开孔）安装服务-5个及5个以下 | 80 | service:installation |
| CN:mi_cn:product:21213 | 筒射灯（不含开孔）安装服务-7个 | 96 | service:installation |
| CN:mi_cn:product:21214 | 筒射灯（不含开孔）安装服务-8个 | 104 | service:installation |
| CN:mi_cn:product:21216 | 筒射灯（不含开孔）安装服务-6个 | 88 | service:installation |
| CN:mi_cn:product:21217 | 筒射灯（不含开孔）安装服务-9个 | 112 | service:installation |
| CN:mi_cn:product:21220 | 筒射灯（不含开孔）安装服务-10个 | 120 | service:installation |
| CN:mi_cn:product:21674 | 智能家庭屏安装服务 | 80 | service:installation |
| CN:mi_cn:product:21922 | 小米数字系列 优惠屏 屏幕换新服务（15系列及以下型号） | 570 | service:other |
| CN:mi_cn:product:21923 | REDMI K系列 优惠屏 屏幕换新服务（K70系列及以下型号） Redmi K | 295 | service:other |
| CN:mi_cn:product:21924 | REDMI Note系列 优惠屏 屏幕换新服务 Redmi Note | 222 | service:other |
| CN:mi_cn:product:21929 | 其他系列 优惠屏 屏幕换新服务 | 245 | service:other |
| CN:mi_cn:product:21930 | 小米MIX系列 优惠屏 屏幕换新服务 Xiaomi MIX Fold 2 月光银 内屏 优惠换屏服务 | 2085 | service:other |
| CN:mi_cn:product:21935 | REDMI 数字系列 优惠屏 屏幕换新服务 Redmi10X/10X Pro 5G | 190 | service:other |
| CN:mi_cn:product:22187 | 小米青春系列 优惠屏 屏幕换新服务 | 245 | service:other |
| CN:mi_cn:product:22213 | 空调清洁保养套装服务 挂机 | 157.52 | service:other |
| CN:mi_cn:product:22326 | 空调外机清洁保养服务 通用 | 199 | service:other |
| CN:mi_cn:product:24569 | 家用净水器勘测服务 通用 | 0.01 | service:other |
| CN:mi_cn:product:24853 | REDMI K90 系列 优惠屏 屏幕换新服务 REDMI K90 紫色 优惠换屏服务 | 455 | service:other |
| CN:mi_cn:product:7532 | 手机上门维修 | None | service:other |

## 同类服务扫描

- 延保：0 条；
- 上门清洗：0 条；
- 以旧换新：0 条；
- 检测服务：1 条；空调检测服务 ¥50
- 拆旧费：0 条；
- 清洁保养：6 条；空调清洁保养服务 ¥99；洗衣机清洁保养服务 ¥99；空调挂机清洁保养服务 ¥99；立式空调清洁保养服务 ¥159；空调清洁保养套装服务 挂机 ¥157.52；空调外机清洁保养服务 通用 ¥199
- 换新服务：19 条；REDMI Note系列屏幕换新服务 Redmi ¥370；Redmi Note系列后盖换新服务 Redmi ¥140；其它系列后盖换新服务 ¥210；其它系列屏幕换新服务 ¥670；其他系列 优惠屏 屏幕换新服务 ¥245；REDMI K系列屏幕换新服务 Redmi K ¥450；REDMI Note系列屏幕换新服务 Redmi ¥370；REDMI X系列屏幕换新服务 Redmi 10X 屏幕换新服务 ¥390；REDMI 数字系列屏幕换新服务 Redmi ¥260；其它系列屏幕换新服务 ¥670；小米数字系列屏幕换新服务 Xiaomi 1 ¥670；小米数字系列 优惠屏 屏幕换新服务（15系列及以下型号） ¥570；REDMI K系列 优惠屏 屏幕换新服务（K70系列及以下型号） Redmi K ¥295；REDMI Note系列 优惠屏 屏幕换新服务 Redmi Note ¥222；其他系列 优惠屏 屏幕换新服务 ¥245；小米MIX系列 优惠屏 屏幕换新服务 Xiaomi MIX Fold 2 月光银 内屏 优惠换屏服务 ¥2085；REDMI 数字系列 优惠屏 屏幕换新服务 Redmi10X/10X Pro 5G ¥190；小米青春系列 优惠屏 屏幕换新服务 ¥245；REDMI K90 系列 优惠屏 屏幕换新服务 REDMI K90 紫色 优惠换屏服务 ¥455
- 勘测服务：2 条；米家中央空调（多联机）上门勘测服务 ¥0.01；家用净水器勘测服务 通用 ¥0.01
- 上门维修：1 条；手机上门维修 ¥None

拿不准或实物描述保留：[]

## 发布与线上回读

- 代码提交：`be4bc5764c81666f84990b33c6293d5269a1a2a0`；实际数据提交：`03ebb5df`，前一提交 `7fbb8f13`。
- [发布成功](https://github.com/null-object-0000/goodsdex/actions/runs/41798580189)。以上审计已针对实际发布前后两个 data 提交重跑通过。
- 全量测试：736 passed（见 tests.log）。
- [线上排除文件](https://spend-good.oss-cn-shanghai.aliyuncs.com/data/public/goods-excluded.json) 已回读；安装服务 17、其它服务 29，明细与 reasons 一致；总量 3982 = 2856 + 1126。
- revision：`cbc9df5e7c824682a998bc8cceda7588`；排除文件与 goods 文件均通过 meta SHA-256 校验，详见 online.json。
