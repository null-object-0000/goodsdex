# 被排除商品发布契约

后台默认读 `goods.json`；复核被排除记录读同一发布的 `goods-excluded.json`。
排除条目不回填 `goods.json`、轻索引或详情分片。

## 文件与口径

- `goods-excluded.json`：`generatedAt`、`revision`、`total`、`reasons`、`items`。每条提供原商品字段、`excluded_reason`、`excluded_at` 和 `exclusion` 判定证据。
- `meta.json`：`total_all`、`total_published`、`total_excluded`，以及 `files["goods-excluded.json"]` 的 sha256/count/bytes。计数按行，与既有 `count` 一致；安全去重移除的额外行列为 `duplicate`，冲突行继续保留。
- 过滤前全集由本次输入，加上源档案中已排除且本次输入未出现的身份组成。历史配件首次快照、审核删除的源记录是事实输入；上次生成的 `goods-excluded.json` 从不作输入。`total_all` 从输入行数和新增历史身份数独立计算，再校验等于发布行数与排除行数之和。
- 共享 finalize 每次重新执行判定并分配 revision；排除文件与 meta 使用相同 revision/时间，每条 `excluded_at` 指本次判定时间，首次事实快照仍保留在 archive。分片生成与 OSS 上传前均校验发布一致性。
- OSS 通过 meta 描述符上传不可变 blob 和公开别名，所有文件回读 SHA-256 成功后最后上传 meta。data 分支整批提交。
- 原类目 `category/categories` 原样保留。`category_l1` 没有来源时为 null，`category_l2` 优先原同名字段，否则沿用原 `category`，不根据配件规则伪造两级分类。price/image/source_url 没采到则为 null。
- 既有审核删除十个身份的完整记录从同一 data revision 的 `data/categories` 恢复，并保存在 `archive/non-goods.json`；新增未审核空壳仍阻止发布。现有 `is_container` 标记本身不构成新删除规则；本任务不扩大过滤范围。

## 固定理由枚举

每行仅一个主理由；按审核身份、明确服务名称、配件具体词、配件类别/名称规则的次序选取。安全去重的额外行独立记录为 duplicate。
新增理由必须同时更新此文件、README 和 `src/goodsdex/exclusions.py`，未知枚举拒绝发布。

| 枚举 | 含义 |
|---|---|
| `accessory:sticker` | 贴纸 |
| `accessory:screen_film` | 保护膜、类纸膜、高透膜等 |
| `accessory:cleaning_consumable` | 清洁剂耗材 |
| `accessory:category` | 配件类目命中，原始类目见 exclusion.matched |
| `accessory:name` | 配件名称词命中，原始词见 exclusion.matched |
| `service:installation` | 安装/上门服务 |
| `service:other` | 名称确认的延保、清洗、检测、拆旧、勘测、维修、换屏换盖服务 |
| `container` | 系列容器（保留枚举，当前未启用新增过滤） |
| `duplicate` | 无冲突安全合并的额外输入行，原字段完整保存 |
| `invalid` | 已审核的六条空壳身份 |
| `manual` | 已审核的四条非商品软件页面 |

`accessory` 旧档案值不作为新文件枚举，必须按本轮规则重新判定。reasons 包含全部枚举（无命中为 0），总和必须等于 total。

## 验收

实际运行、测试、分布与线上回读结果见本目录的 `acceptance.json`、`publication.md` 和日志。
原始类目属于手机、笔记本、家电的配件仍必须如实出现，不能为了表面满足“类目不出现”而改类目。
误伤复核按原始类目列出所有命中行，再按商品主体与判定证据核查是否为整机。

服务档案 `archive/services.json` 独立保存源事实；每次生成重新判定，服务理由不使用配件理由。名称含安装服务/安装调试/上门安装，或无型号词且以安装结尾时排除。免安装、安装尺寸、安装组件、安装套件、含/赠安装保留。
