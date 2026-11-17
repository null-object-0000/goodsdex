# 三路采集恢复（2026-11-17）

惠普、汽车、亚朵均已完成采集、发布和 MySQL 入库；监控状态均为 success，连续失败次数 0、无过期告警。生产 API 为 `3707e568b0ed93056e34c9d4a2849c314b181b65`，已发布 4531 条、来源行 5783 条、重复 0、同步门禁 ok。线上核验见 [online-verification.json](online-verification.json)。

- 惠普：[44023131361，发布重试第 2 次成功](https://github.com/null-object-0000/goodsdex/actions/runs/44023131361)，完成于北京时间 13:58。
- 汽车：[44018658096](https://github.com/null-object-0000/goodsdex/actions/runs/44018658096)，完成于北京时间 12:56。
- 亚朵：[44018661824](https://github.com/null-object-0000/goodsdex/actions/runs/44018661824)，完成于北京时间 13:08。
- 采集端完整离线测试：[44022748319](https://github.com/null-object-0000/goodsdex/actions/runs/44022748319)，代码 `291925fbc5973acac100d0c530c7d6647d9770f7`。
- API 全量测试：[44025938906 的 api-tests 作业](https://github.com/null-object-0000/spend-good/actions/runs/44025938906)。

## 惠普

海外 Actions 出口访问官网返回 403，原任务只能降级保留历史；旧发布端还存在 baseline 请求失败。现由已有上海 API 读取数据库中既有惠普官方 SKU 原始链接及绑定已知 SKU 编号的规范地址，保留 TLS、导入令牌鉴权、2.105 秒串行限速、35 秒超时、4 MiB 上限、重定向范围与原文 SHA256 校验，不透传认证或 Cookie。其它配置的跳转不能覆盖原 SKU；目录跳转下架保留原规格和历史价格。采集降级会明确失败、不生成候选。

最后一轮复用失败实时捕获 44019080257 的已验证原文，只重新读取缺页；不是历史静态快照。每页保留真实采集时间，定时任务默认全部实时读取。结果：200 个配置、核心参数完整 200、有效官网价格 200、已验证图片 200、错误 0；4 个新下架页面，低于 10% 门禁。见 [hp-capture-validation.json](hp-capture-validation.json)。

D71MWPC 的 CPU 描述有真实官方更正。采集端保留原文摘要、商品上下文 SKU、规格表 SKU 与核心配置；发布器和 API 都要求相同 SKU、系列身份和原始链接，以及更新的观察时间，再根据规格独立推导标题。无证据更名仍拒绝。baseline 的旧采集时间从 goods 源标量读取，修复轻量索引不含 fetched_at 导致的误拒绝；生产已确认该更正被接受并展示 Ultra 7。

## 亚朵

官网 11 月 10 日升级三个匿名读取端点为 `pageByParam/v1`、`getNewDetail/v1`、`getGoodsSkuPanel/v1`；同步统计脚本还会阻塞页面初始化。已更新公开读取白名单并跳过无关统计和图像资源，保留匿名请求、凭据移除、2.1 秒间隔、完整分页、SKU 唯一性及图片审校门禁。

38 SPU / 255 当前 SKU 验证通过。名称调整必须绑定同一 SPU/SKU ID 和编号，目录、详情、规格三份原文一致且观察更新；缺失、过期或串到其它商品的证据都拒绝。完整原文见 [atour-live-capture.json.gz](atour-live-capture.json.gz)，摘要和全部 82 次 HTTP 200 校验见 [atour-capture-validation.json](atour-capture-validation.json)。线上已展示新的“预售7天”文案和当天采集时间。

## 汽车与共用发布

汽车采集成功后，被无关小米配件的旧名称拦住：排除档案保留首次快照，但同 ID、同 gid 的较新官方观察已存在。排除投影现在使用已绑定身份的最新观察，原始档案不改写，避免不同采集任务反复回放旧名称。16030 真实回归、跨 SKU 拒绝、重复重放和发布原子性均通过。

来源预期间隔改为读取现行注册表，修复旧状态文件仍按每天判断、实际任务已每周运行的不一致。另修复 API 部署回滚 pin 继承 Compose 服务标签导致的容器名冲突；API 侧部署与验证记录见 spend-good 的 `docs/source-recovery-20261117/README.md`。
