# MySQL 商品发布

在线商品库唯一来源是现有 ECS API 连接的私网 MySQL。Actions 完成原有证据、身份、日期和无丢失门禁后，通过 HTTPS 专用导入接口发送 gzip 增量。公开 MySQL 端口不开放，不增加 Redis、ES 或实例。

Secrets：`CATALOG_API_URL`（API HTTPS 域名）、`CATALOG_IMPORT_TOKEN`（独立高强度令牌，与后台/支付令牌隔离）。禁止将凭据放入仓库、日志或候选 artifact。

`node scripts/publish_mysql.mjs _data/public --dry-run` 只读取轻量哈希及身份基线并校验已发布详情分片。去掉 `--dry-run` 才导入差异；无变化时不上传商品内容。每批最多 50 条，压缩前后均有限额，使用内容哈希幂等键和乐观版本。服务端事务保留人工修订，拒绝未经审核的名称/产品身份改变。缺失来源记录不物理删除；下架来自经过门禁的排除记录。

OSS 保留图片、原始证据和冷备份。在线 JSON 镜像已退役，状态心跳不再访问或重写 OSS 商品整包。Git data 分支暂保留采集上下文及回滚记录，不作为 C 端出口。

迁移期间所有定时采集工作流保持手动禁用。重新启用采集需要先处理已有全量候选中的跨产品标题污染，确认身份门禁通过，并更新数据库的 collection-policy；不能靠关闭门禁恢复发布。
