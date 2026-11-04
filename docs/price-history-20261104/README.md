# 逐商品价格观测

四条采集线（prices、Apple、HP、cars）将本轮结果写入候选 `data/price-observations/*.jsonl`；共享发布锁内合并最新 data、一次性回填基线 goods、去重并写入本次 `meta.revision`。待发布队列只在成功产出后清理，不进入 goods.json。

公开产物是 data 分支的 `public/price-history/<YYYY-MM>.jsonl.gz`，OSS 为 `data/public/price-history/`。商品主键使用规范命名空间 ID（例如 CN:mi_cn:product:10000292），原来 goods.gid 的小米数字值仍仅用于调用小米批量接口。汽车观测按采集配置 ID 保存，未把车型起价冒充配置价。价格类型固定 price，原始报价语义仍在 goods.price_kind。

`index.json.files` 是默认热读集合；`archived_files` 是冷档案清单，消费者不得默认扫描。文件末次观测早于 90 天截止时间后退出热集合；跨截止日的月文件仍保留，读取者按 `detail_cutoff` 过滤明细。服务端先以其已有 price_history_daily 保留日聚合，再清理 90 天前明细；生产端不删除月档案。单个 gzip 超过 200 MiB 后按上海时区 1–15 日 / 16–月末切成 -a/-b，已经拆分的月份不再合并。SHA-256 校验的是 gzip 原始字节，count 是解压后 JSONL 行数，start/end 为实际观测时间范围。每月内旧观测内容与 revision 永远不改，同一 gid 的等价 UTC 时间只留一条，冲突拒绝发布。

回填只读取本次采集前 goods 的实际 fetched_at，不插值、不将当前价复制到任意过去时间。回填包括显式缺价，标 backfilled:true；累计条数见 index.backfilled_count 和 meta.price_history。离线重放、汽车 verified-only/historical-only 不构造新的当前观测。Apple stale 与 HP 下架/本轮确认封锁记 unavailable/null；HTTP 成功但无报价记 no_price/null；有效正价格记 ok，零值不会变成观测价格。

线上核查发现现有 syncHistory 实际仍只读 prices/<月>.jsonl，未实现新 index 读取。为了让现有服务端立即导入，发布器在旧月快照后追加真实逐商品观测的兼容投影，并将旧价格月文件纳入 meta.price_history.files 的 SHA 清单与 OSS 镜像。兼容投影不改已有快照，不改 goods/meta 既有字段含义。服务端旧 parser 将状态映射为 observed/price_missing；新 gzip 中保留完整 ok/no_price/unavailable。新 index 的 revision 自动新鲜度与严格热读需服务端后续消费此契约；生产端已提供文件与截止时间。

OSS 发布顺序：全部文件与不可变 blob 上传并 GET 验证 → history/index 别名 → meta，任一内容校验失败不写最终 meta。

验证基线：728 passed / 8 deselected。结果、真实观测样本、data/OSS SHA 比对及在线 API 摘要见本目录后续验收文件。

首次同步验证发现旧服务端对 meta.files 有严格的商品路径白名单。已把价格历史全部描述符隔离到新增的 meta.price_history.files，保留原 meta.files 的商品清单语义，OSS 镜像读取两份描述符。用现有服务端 validDescriptor 对修复后的全部商品描述符验证通过；增补分离清单、共享 raw gid 的多个规范 ID 和 OSS index 发布顺序回归。最终本地 747 passed / 8 deselected。
