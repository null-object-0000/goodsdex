# 米家说明书参数补采（2026-11-06）

2026-11-07 rebase 更新：发布入口现在只将 `params` 写回商品记录，参数来源、缺失原因和冲突证据写入独立的 `public/parameter-audit.json`；以下采集统计与样本仍是原始冻结验收结果。最新兼容性与全套测试见 [rebase 验收](../manual-params-rebase-20261107/README.md)。

已完成独立采集器、保守解析器、finalizer 重放和证据留存。**四类覆盖目标未达到；洗衣机达到 60%。** 本轮仅本地提交，不 push、不部署、不触发 workflow。

|品类|07ca1970 基线|本轮实际写入后|本轮目标|结果|
|---|---:|---:|---:|---|
|微波炉|3/5|3/5（60.00%）|5/5|未达到，两个既有日期身份暂缓|
|扫地机器人|57/92|57/92（61.96%）|≥85/92|未达到|
|冰箱|89/147|89/147（60.54%）|≥120/147|未达到|
|空调|52/146|52/146（35.62%）|≥90/146|未达到|
|洗衣机|59/76|63/76（82.89%）|≥60%|达到|

覆盖按记录是否有非空 `params` 计算。前四类沿用上一轮固定 ID 母体；洗衣机按同一 4,491 行快照中品牌为小米/米家/小米公司、主分类为洗衣机/波轮洗衣机/滚筒洗衣机的 76 条记录计算，包含容器与无 model 记录，没有缩小分母。原始数据来自上一轮已冻结 data 提交 `44a45f00bfa2eee8bef68158aa6278597354aec7`。当前分支先合并 `07ca1970`，保留已有封面修复，再开展本轮改动。

实际新增 **321 个字段，涉及 63 条记录**，其中 4 条洗衣机从空参数变为有参数；其余为已有参数记录补字段。候选清单有 74 条记录、502 个字段，候选不等于写入；身份门禁、已有同键值、容器以及多容量变体范围会阻止写入。没有用候选条数代替覆盖率。

## 采集与成功率

实际采集五类家电中 **330 个可确认 model**；无 model 的记录仍在覆盖分母中。默认脚本支持所有小米 model，本次使用 `--appliances-only` 固定本轮范围。已成功下载/运行 `pdftotext -layout` 的 PDF 为 **240 份**，其中 **74 份解析出至少一项参数，成功率 30.83%（74/240）**。有检测到规格标题文本的 127 份中，成功 74 份（58.27%）；标题检测可能包含目录，此分母只作诊断。

|型号级结果|数量|含义|
|---|---:|---|
|parsed|74|至少一个符合封闭规则的完整标签值单元格|
|no_pdf|85|成功取得 introduction，但响应未提供 PDF URL|
|no_text|22|pdftotext 输出仅为空白，不推断 PDF 是否含参数|
|table_not_found|91|提取文字未命中规格区块，不推断 PDF 是否含参数|
|parse_failed|53|检测到标题，但单元格或多型号范围无法安全解析|
|download_error|5|下载失败，未验证内容；不是没有参数|

5 个失败均为下载错误，详情、异常原文与 URL 在 [collection.json](collection.json)。[record-outcomes.json](record-outcomes.json) 列出每条验收记录的采集状态、阻止写入原因及新增字段；[acceptance.json](acceptance.json) 给出完整覆盖和剩余原因。

复用上一轮 byte-exact introduction/PDF 缓存，同时为所有 330 个型号冻结 introduction 原响应及哈希；本轮补采新增洗衣机等缺失证据。失败下载已重试一次仍失败。PDF 与原始文本只作为证据，未使用 OCR 或 LLM 推断。

## 解析与写入约束

- 独立入口：`scripts/collect_manual_params.py`；解析与应用：`src/goodsdex/manual_params.py`；不进入图片刷新链路。
- PDF 和 pdftotext 缓存在 `data/manual-pdf/<model>.pdf`、`.txt`，已 gitignore。`introductions/` 与 `texts/` 留存压缩后的原响应/原文，附 SHA-256。三份测试用 PDF 单独保留原始二进制。
- 只接受规格标题后、同一物理页同一行的标签值。标签用封闭白名单，值需完整匹配该物理量的单位/形态。保留原单位、标点和内部空格；例如 `Φ350×97mm`、双容量限定词、`3.67kg` 均不换算。
- 主机与基座并列表只在明确并列表头存在时截取主机列。拒绝多型号列、矛盾重复值、单位不符、无单位数字、跨行数值与无法确定的残留文字；多容量商品档案不承接单一变体说明书。
- 每项保留 `source: manual_pdf`、`source_type: official`、`model`、`pdf_url`、物理 `page`、原行 `quote`、PDF 与文本 SHA-256。240 份本地 PDF 的字节哈希逐份校验结果见 [pdf-byte-verification.json](pdf-byte-verification.json)。
- `homeappliance-params.json` 的现有官方文字先重放，PDF 只补缺失同键；保留全部既有非空参数。manifest 按精确 ID、商品名及 model 匹配，无当前 model 时必须命中上一轮冻结的审定桥接。
- 普通 finalizer 与 crawler 出口重放新清单；既有专用发布模式仍保持原来的跳过规则。没有修改任何门禁实现、release、商品名或 supplements。

既有 L7 日期和系列日期成员身份哈希包含 `params`。测试暴露一条系列成员在第二次 finalizer 回放时会身份漂移；因此对两类已冻结日期身份均保留候选但暂缓写入，不重签哈希、不放宽检查。微波炉 P1（`xiaomi.microwave.cm20l`）确实有 PDF，物理第 13 页解析出额定容积、输入功率、输出功率等；12548、20545 仍受上一轮日期身份暂缓限制，故不能报告 5/5。

## 抽样、测试与复现

[十条原文逐行对照](sample-10.md) / [结构化样本](sample-10.json)：每类两条，均为实际新增字段，按类别和 ID 排序固定选择。每条给出原文行、解析值、model、PDF 链接与物理页。

三份真实 PDF 为 `xiaomi.vacuum.c102cn`（第 14 页）、`xiaomi.microwave.cm20l`（第 13 页）、`midjd.fridge.bs60s`（第 18 页）；已渲染并视觉核对参数表。见 `tests/fixtures/manual_params/` 的原 PDF 与 `sources.json`。解析器测试覆盖这三份原始 PDF、缺表、多列错位、重复冲突、错误单位、跨行值、无单位数字、旁列边界、官方优先、身份匹配、幂等、日期门禁和多容量范围。

离线全量测试 **1156 passed，8 deselected**；解析器专项 **12 passed**。完整测试结果见 [tests-final.log](tests-final.log)，解析器专项见 [parser-tests.log](parser-tests.log)。[verification.log](verification.log) 的离线校验逐项验证 introduction 字节哈希、PDF URL、文本字节哈希、页内 quote、解析器确定性回放，并检查所有非参数字段、全部既有参数值不变以及重复应用幂等。

```bash
# 在线采集：Python 标准库 + 系统 Poppler（pdftotext）
python scripts/collect_manual_params.py --goods <goods.json.gz> --appliances-only

# 可选：复用上一轮原始证据（路径需含 captures.json/raw/manuals）
python scripts/collect_manual_params.py --goods <goods.json.gz> --appliances-only --seed <preceding-evidence-directory>

# 完全离线重放冻结文本，不请求网络，也不执行 OCR
python scripts/collect_manual_params.py --goods docs/manual-params-20261106/baseline.json.gz --reparse-only
python scripts/verify_manual_params.py --goods docs/manual-params-20261106/baseline.json.gz
PYTHONPATH=src python -m pytest -q -m 'not live'
```

`baseline.json.gz` 冻结验收范围的原始记录，可独立复算覆盖。使用完整 4,491 行原始输入的验收文件保留其输入哈希；用此范围子集复现时输入哈希会不同，但覆盖与抽样应相同。live 测试未运行。
