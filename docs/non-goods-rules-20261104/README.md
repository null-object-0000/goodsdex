# 非实物定金与服务排除验收

规则沿用 `services.py` 判定、`archive/services.json` 原始事实保留、共享 finalize、`goods-excluded.json` 发布机制。没有添加 ID 白名单或删除源数据。后续任意采集渠道产生的新身份都会在共享发布入口自动执行。

## 规则

- `preorder_deposit`：名称中的定金、订金、权益、预约、盲约、预售、占位、不发货。按原文顺序取首个独立语义命中词作为 `matched_text`。
- `service`：安装服务、延保、上门、以旧换新补贴、充值卡、贴膜服务，以及既有安装调试、无型号安装后缀和清洗/检测/维修等服务。`excluded_reason` 继续细分为 `service:installation` / `service:other`。
- 先移除含/赠服务与权益描述、无需预约/不收定金/非预售等否定描述、家电预约功能及定时描述、送货上门、权益保障和占位传感器等功能描述，再判定排除。延续免安装、安装尺寸、安装套件/组件等保护；仅“以旧换新手机”不判服务。
- `matched_rule` / `matched_text` 既在条目顶层，也在这些规则的 `exclusion` 内；既有 `matched` 保留。历史配件等其它规则也提供顶层证据字段。
- `meta.excluded_by_rule` 汇总所有排除规则，零值保留，`service:*` 合并为 `service`。共享校验确认汇总等于排除明细；总库 = published + excluded。

## 全库扫描与口径

[每一行命中清单](matches.md) 与 [机器审计](audit.json) 同时保留行号、ID、名称、价格、matched_rule 和 matched_text。

- 用户给出的本地 `public/goods.json` 确为 **5,448 行**旧快照。完整非实物规则命中 **78 行 / 46 个身份**：定金 1 行、沿用的服务规则 77 行。仅按本次用户列举词的字面检索为 20 行。服务重复身份逐行列出，不把重复当作新增商品。
- 当前实际发布基线（data `a73c25ed407a3e807efd6356255ccca17d9fd8ed`）为 **2,856 行**。服务已由此前发布排除，本次新增仅 **1 行**，没有为增加成果扩大范围：`CN:mi_cn:product:19045` / 耳机新品1元权益定金（不发货） / ¥1 / `preorder_deposit` / `权益`。
- 当前库没有其它含请求关键词且应保留的真实商品，因此下列反例为**合成测试商品名**，不冒充真实库记录：① 空调含安装服务；② 小米电视（赠延保服务）；③ 手机套装（含贴膜服务）。三条均不排除；另覆盖电饭煲24小时预约、智能插座预约功能、手机非预售等。

|口径|修前|修后|
|---|---:|---:|
|total_all|3982|3982|
|total_published / count|2856|2855|
|total_excluded|1126|1127|

保存修前线上 meta、发布前 goods 压缩快照及 SHA-256，避免把旧快照整理造成的变化冒充本次删除。实际线上发布及回读见 publication.json / online-meta.json。

## 验证

本地全量离线基线 771 passed / 8 deselected。新增测试覆盖全部请求词、赠品/功能/否定反例、重复 finalize、源字段保留、新采集身份自动排除和 meta 统计篡改拒绝；最终结果见 tests-final.log。首次新增测试对 archive 的全等预期未考虑已有规范化补充字段，改为逐一断言所有源字段保留，仍保留排除计数和回放断言，首次日志也保留。

复现：`python3 docs/non-goods-rules-20261104/build_audit.py`；`PYTHONPATH=src:scripts ~/.cache/goodsdex-testenv/bin/python -m pytest -q -m 'not live'`。
