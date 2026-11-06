# 米家目录独立源与展示优先级

修复 `836a2f64` 的覆盖式写入。330 条确定身份保留两个来源；不把米家名字、图标或分类存入商城原字段。`miio_model` 原有值保留，缺失时补确定映射；`mihome_model/mihome_pd_id` 保持兼容。

- `name/name_mihome`：商城销售名优先。空名或有精确容量证明/明确省略号前缀证明的截断名才在派生 `catalog_display.name` 使用米家名。仅空白、大小写、全半角差异永远不算截断。`name_source` 保留已有商城标题证据；无来源时注明 xiaomi_store；选米家时注明 mihome_directory。
- `image/image_mihome`：原图不改；已验证的米家图标保留 URL、sha256、width/height=168、size=168x168、source=mihome_directory、scope=device_icon。仅官方缺图时用于展示。后台明确显示“设备图标 · 168×168 · 非商品主图”。
- `category/category_mihome`：原类别和 categories 不改。原分类属于已审核宽泛桶（家电、其他、智能家居、智能家庭、旧款机型）或为空时选米家细类；两者已是细类时保留商城分类。不用字符串长度猜类别细度。
- 派生 `catalog_display` 携带各字段来源；轻索引与详情都保留双源字段。后台详情并列展示商城原值、米家值、当前展示值与来源；列表图片和品类也使用同一优先级。

## 逐条判定

[90 条逐项清单](review-90.md)、[结构化决策](review-90.json)。记录级真修正 **32**（有效图标/品类证据）、格式回滚 **58**、待定 **0**。若一条同时有名称格式回滚和有效补图/细类，记录级归回滚，字段决策仍各自保留。

字段级：**名称语义修正 0、格式回滚 58、图标有效 18、细分类有效 28**。所有有效内容移入独立字段；所有原商城字段恢复，不能将此事描述为“58 个名称修正”。

旧覆盖恢复仅针对相同 id、model、pdId、旧来源标记与旧写入值；原字段是否存在以及原始证据从冻结快照留存于每条映射的 `legacy_original_fields`。后续其他源更新不会按 ID 无条件回滚。新增容量截断测试保证真正的完整名称仍可在展示层使用，原 name 不被覆盖。

## 三条真实记录

详见 [完整字段对照](examples.json)。

|ID|商城 name / image / category|米家独立字段|展示|
|---|---|---|---|
|12136|米家智能除菌加湿器 S；原图；加湿器|name_mihome=`米家智能除菌加湿器  S`|保留商城单空格名称、原主图|
|10330|米家智能微波炉 20L；原图；家电|category_mihome=微波炉|展示微波炉，category 仍是家电|
|3488|米家压力IH电饭煲；image=null；原分类|image_mihome 为 168×168 设备图标|缺主图时用图标，明确角色标签|

## 来源与界面验收

[10 条来源抽查](sample-10-sources.json)：2026-11-06 重新读取商城商品页，`name` 与 HTML title 去精确商城后缀后逐字一致 **10/10**；原文 gzip 与 SHA-256 在 source-pages。米家值与本轮目录原响应逐字一致 **10/10**；响应文件/URL/sha256 在原批次 evidence.tar.gz 与清单内，330 条映射另经 audit_evidence.py 全量验证。

后台验收截图使用真实审核记录、真实 API 和隔离 SQLite；环境、10 条名称与 5 条图标结果见 ui-verification.json。截图覆盖 1440 桌面与 390 手机，图标在概览和双源区都明确标注。发布后另用不可变 OSS 整库、详情与索引读回核验，不把本地截图冒充生产截图。

## 日期与测试

原批次冻结快照：**1,580/3,572=44.23% → 1,580/3,572=44.23%**。本轮开始时最新数据预演：**1,646/3,572=46.08% → 1,646/3,572=46.08%**。其它任务此前增加的日期不计作本轮增益。所有 release* 与 page_first_archived 字段逐条不变。真实发布父版本数字以 online-verification.json 为准。

数据测试：基线 **1050 passed / 8 deselected**，修改后 **1054 passed / 8 deselected**，仅既有 pytest 插件弃用警告；含旧写入 90 条恢复、全库日期不变、幂等、后续来源保护与截断展示门禁。后台、API 与构建日志见本目录。直接 tsc 既有 Umi 类型导出配置错误在相同依赖环境前后都是 32 条，忽略位置后错误集合相同，未新增。

发布沿用共享发布锁和 mihome_catalog_only。门禁要求整库精确等于 apply_catalog(真实父版本)，防止价格、日期及其它任务变更混入本次迁移。发布回执与线上验证在 publication.json、online-verification.json。

18 张图标的无签名地址全部重新匿名请求，HTTP 200 且 SHA-256 与原归档字节完全一致，见 [unsigned-icons.json](unsigned-icons.json)。image_mihome.url 使用已核验无签名地址，source_url 保留目录原链接，避免后台安全脱敏把签名图片链接隐藏。未放松凭据脱敏。


## 后台上线证据

后台提交 `7d95619e32e903fc8d2a110848cf2703daed1f09`；[构建与 API CI 42134065192](https://github.com/null-object-0000/spend-good/actions/runs/42134065192) success。ECS 部署已完成，三次公网 health 都返回同一提交，见 admin-deploy。实际线上双源展示 JS 的 SHA-256 与该 CI artifact 一致，见 admin-live-assets.json。后台 13 测试通过；API 371 通过、4 跳过，无失败。

[桌面双源与图标截图](admin-3488-1440.png)、[手机截图](admin-device-icon-390.png)、[格式名并列截图](admin-12136-1440.png)、[品类并列截图](admin-10330-1440.png)来自真实 API + 隔离 SQLite 的实际审核记录，图标使用原始已验证字节；不是生产登录会话截图。5 张图标均检查自然宽度 168 和可见角色标签，手机无横向溢出，浏览器运行错误 0。

首次迁移 [42133960169](https://github.com/null-object-0000/goodsdex/actions/runs/42133960169) 已成功，真实父子版本全库精确比较见 first-migration-verification.json：名称恢复 58、原图片字段恢复 18、原分类恢复 28；独立名称 330；日期 1646 → 1646。后续最终发布仅完善已验证公开图标地址及缺名展示门禁，最终 OSS/后台核验见 publication.json。


## 最终发布与线上核验完成

代码提交 `2e630213d7ff0de314799d02f8f6a93cf072610e`；[最终发布 42134849232](https://github.com/null-object-0000/goodsdex/actions/runs/42134849232) **success**，发布门禁 **662 passed**；[CI 42134849594](https://github.com/null-object-0000/goodsdex/actions/runs/42134849594) **success，1054 passed / 8 deselected**。

数据提交 `308fc9bda99a9aa1303b1cd0a1aeaa7c44780cc9`；真实父版本 `c878130c59c25404b4e33076ad92890d1175df51`；OSS revision `be87a47ca5d64261a994611bd5e899f2`。整库、10 条详情和 5 条图标详情、全部小米轻索引双源字段均经不可变 blob SHA-256 读回核验。3572 行逐字段精确等于 apply_catalog(真实父版本)，日期相关字段逐条不变：**1646/3572 = 46.08% → 1646/3572 = 46.08%，+0.00 个百分点**。最终发布的原 name/image/category 增量都是 0，因为首次迁移已完成对应原值恢复；两轮结果分别留证。

后台已显式同步最终数据；[真实生产后台 15 条接口结果](live-admin.json)包含 **10 条商城/米家名称逐字一致、5 条官方缺图记录的可公开访问无签名图标 URL 与 device_icon/168×168 标记**。未放松鉴权或凭据脱敏；同期部署的实际线上 JS 与 CI artifact 哈希相同。完整回执见 [publication.json](publication.json)，机器验证见 [online-verification.json](online-verification.json)。
