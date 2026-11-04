# 小米名称保真与配件混入修复（2026-11-04～05）

冻结线上 `/api/goods`：2855行，小米1637行/1632唯一ID。不是按“1600”估算分母。本轮请求257个不同ID，其中固定随机200条、定点追加57条；234页取得有效商品title，23页HTTP200但无商品title。原文、状态、最终URL、请求时间、SHA256全部留档。最小请求起始间隔2.14996秒，满足≥2.1秒。

## 根因与22105链路

修前代码基于 `4540c215815466dd5eff15c0056a26a62863167c`：

- `src/goodsdex/identity.py:83–93`：`_is_color_token` 将2–6个汉字中含任意颜色字视为颜色，“金属面板”因“金”命中；`:108–109` 用while循环逐段剥除，不是只剥最后一段。
- 同文件`:188–191`：多变体名称还可能取字符级公共前缀，甚至截在型号中间，并非严格“截到型号”。
- `src/goodsdex/pipeline.py:103–112`：虽然采到完整官方name，但`if not prod.name`令已有短名无法被覆盖；subject/view保留全名，product保留短名。
- `src/goodsdex/publish.py:48`：发布取`p.get("name")`，没有取完整view名。归一化另有删除末尾“系列”的规则；官方title来源现在阻止它清洗真名。
- `src/goodsdex/kind.py:20–24`缺少金属面板词；发布配件规则的整机优先分支以已丢后缀的`Xiaomi Sound`判成整机，错误压过“配件”分类。

22105实际字符串：`Xiaomi Sound 2 Max 金属面板 金属面板` → 第一次剥尾 `Xiaomi Sound 2 Max 金属面板` → 第二次剥尾 `Xiaomi Sound 2 Max` → identity/pipeline/product不变 → publish `Xiaomi Sound 2 Max`。同时移动API断言和view中一直是`Xiaomi Sound 2 Max 金属面板`。合并没有制造截断，而是延续了上游错名。

[逐步对照](22105-trace.md)、[机器记录](22105-trace.json)、[含原始响应的采集记录](22105-source.json)。

## 随机抽样结果与全量门槛

|分类|数量|占200条|
|---|---:|---:|
|与官网完整名逐字一致|160|80%|
|库里多字|11|5.5%|
|仅空格差异|2|1%|
|库里少通用“系列”|4|2%|
|少区别性词（面板/数量/套装/Pro/Max等）|0|0%|
|页面明确与商品无关|0|0%|
|页面未提供商品title，无法核实|23|11.5%|

随机种子20261104，按唯一ID排序后无放回随机抽样。有效title177条中也未发现区别性词缺失；23条未核实没有计成一致。缺任意字4/200恰好2%，区别性词缺失0/200，均未达到“>2%”全量条件，因此没有冒称已对1632个ID全量抓取。这个结果不证明未采页没有问题。

定点补查另外找到5条区别性词缺失：22105/22107/22544（配件）、19703/21957（不同蓝牙音箱型号）；这些偏置样本不混入随机比例。全部13条少字（含通用系列/颜色）均逐条列在[少字完整清单](missing-words.md)。[200条逐行比对](sample-200.md)、[统计JSON](sample-statistics.json)、[原始请求记录](titles.jsonl)、[全257条结构化记录](title-observations.json)。

## 离线补充诊断

将当前发布ID对应的已保存采集view完整名与线上name比较，筛查“支架/面板/连接器/底座/挂架/保护套/贴膜/线缆”出现在前者而从后者消失的情形，只发现22105、22107、22544三个ID，均已用实时title核实并修复。明细见[离线名称差异](offline-accessory-name-drift.json)。这是历史采集数据的辅助诊断，不能发现官方采集源本身就少字的情况，也不能替代未请求页面的官网标题核实。

## 修复规则与范围

`mi_names.page_name`只剥精确商城后缀`立即购买-小米商城`，保留型号、颜色、系列、数量及配件后缀。新增官方HTML标题Capture/Assertion；采集将完整名称无条件写回product，发布优先官方title，缓存回放也可从完整view恢复。公共前缀不再用作name；没有新增短名，也没有用short_name掩盖缺失。

234条本轮取得有效title的官方名称存入`data/official/mi-page-names.json`，共享finalizer在每次发布中重放，防止旧采集缓存重新覆盖。逐ID校验状态、官方URL、完整title和原文SHA；更晚的新官方采集优先。其余未逐页核实记录不伪造官方名称或通过状态。已有series批次10050180名称恢复“系列”后，只为同ID同model同params补一个有title佐证的精确指纹，原日期和成员不变。

配件按完整title判断，新增明确面板/连接器/挂架/线缆词，`is_accessory=true`与kind=accessory，沿用现有排除、档案和5%门禁。整机加配件、双支整机、显示器多功能支架版、集成支架充电宝及面板灯保留；独立智能家庭控制屏也保留。所有保留的本轮已核标题商品明确`is_accessory=false`。索引和详情都带标记。

正式发布及线上核验新增排除13条：22105/22107/22544及10条独立空调/新风面板。2855→2842；新增排除率13/2833=0.459%，门禁绿，无放行参数。13条被排除记录仍在`archive/accessories.json`和`goods-excluded.json`，完整官方名、原价格、图片、来源均保留。[原22条逐条处置](accessory-22-decisions.md)：10排除、12保留（其中去掉非官方附加词的同时改名）。未修改任何价格；其它品牌、汽车和既有受保护冲突不变，见[预演不变量](preview-invariants.json)。

## Sound四条

|ID|官网title去商城后缀后的完整名|库内价格|实时HTML价格|is_accessory|结论|
|---|---|---:|---|---|---|
|22104|Xiaomi Sound 2 Max|1649|1649|false|整机，保留|
|22105|Xiaomi Sound 2 Max 金属面板|299|未提供|true|独立配件，排除|
|22547|Xiaomi Sound 2 Max+2 Pro+无线连接器套装|5696|未提供|false|整机套装，保留|
|23722|Xiaomi Sound 2 Max双支装|3198|未提供|false|双支整机，保留|

页面title原文均为表内名称直接加`立即购买-小米商城`。22547线上数据库本来就存有完整名称，`…`属于列表展示的现象，本次没有把它当成入库截断案例。299/5696/3198是已采官方报价的库内值，本轮HTML没有提供价格，没有将导航里的别的商品价格充作当前报价。22107金属落地支架的库内价399，单独排除，不与22105混为一个配件。[四条完整结果](sound-four.json)。

## 同名价格交叉校验

对全库正价且至少2个不同ID的同名组计算中位数（包含全部成员），判断`price>=median*2 OR price<=median/3`。修前61个同名组中仅2组达标：Sound 2 Max（median974，299命中）与Sound 2 Pro（median774，249命中），原因均是金属面板配件冒充整机。修后严格命中0组，不存在20个达标组可如实列出。最高价/最低价≥2是另一个口径，修前有9组，未拿它偷换中位数阈值。

[交叉校验报告](price-group-review.md)完整覆盖全部20个小米同名组及全库61组索引，[JSON](price-group-review.json)保留各ID、完整名、价格、gid、attrs、标题和去留。其余差异包含容量、颜色、不同型号/版本和多ID同价；投影仪Lite价差已有资料只证明颜色不同，未说明价差原因，未断言已证实错价或擅改价格。其它品牌解释沿用仓库现有官方变体证据，不冒称本轮重新抓价。严格异常前后清单见[strict-price-anomalies.json](strict-price-anomalies.json)。

## 验证与发布

修前801 passed / 8 deselected；修后828 passed / 8 deselected。8项live测试沿用既有排除范围；没有删除测试或放松日期证据断言。两项历史快照集成测试增加本轮冻结的精确排除ID集合，并保留逐字段相等、日期不变和二次finalize幂等断言；首次预期变化失败日志也保留。

复现：

```sh
python3 scripts/audit_mi_names.py
python3 scripts/audit_mi_names.py --targeted
python3 docs/name-fidelity-20261104/build_manifest.py
python3 docs/name-fidelity-20261104/build_report.py /path/to/public/goods.json
PYTHONPATH=src:scripts ~/.cache/goodsdex-testenv/bin/python -m pytest -q -m 'not live'
```

默认API已确认2842条与当前OSS和数据提交完全一致，234个官方标题、配件排除及套装保留全部通过。正式提交、发布run与线上API验收见[publication.md](publication.md)。
