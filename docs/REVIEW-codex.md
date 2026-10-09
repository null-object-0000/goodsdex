# GoodsDex 整体设计评审（第 2 轮）

评审日期：2026-10-09。阅读基线为 `8e67524`；评审中途工作区新增 `317eb32`，本报告已复核该提交并区分已修代码与历史数据。下文未特别标注版本的行号取阅读基线；标“当前”的位置取 `317eb32`。未修改采集代码或数据文件。

最终复核：gid成功响应已保存、新子记录继承captures、tier2新增正向特征、单视觉不再被默认重复标成接口，这些原始缺陷不再作为当前未修代码问题。历史数据仍有46,195条移动端孤儿断言；56份快照仍不可解析。多片 observations 虽已增加到返回结果，却未进入写回链路。后续全量视觉的阻塞问题仍成立。

## 结论与四个问题的直接回答

1. **选图仍有系统性缺陷，现在不宜花百元铺全量并写回。** 新提交已将tier2改为正向特征，但名称仍不能证明图内容是规格；图像预筛没有语义验证，配额也不能保证型号覆盖。基线候选曾有 `选购指南` 35 张、`温馨提示` 3 张、`型号对比` 3 张，最终复核已不再选中它们；剩余候选的真实精度/召回尚未标注。见下文 Q1 和复现 A。
2. **数据可信度的首要风险是证据链与来源标签，而不只是模型读错。** gid快照未保存的代码已修，但历史46,195条移动端断言仍在各自记录中找不到capture；视觉断言的locator仍指向不存在于其capture中的结构。单视觉伪双源已修，来源未知仍默认接口、视觉多候选仍会丢失。见 Q2、复现 A/B。
3. **手工表可以保留，但必须变成有品类、条件、单位、版本和测试样例的规则资产。** 现在全局别名与附件关键词删除已经制造语义丢失，例如 `电池容量` 被归入附件、不同工况的噪声被合并并只留长值。规模扩大之前，先统一规则入口和保留原始断言。见 Q3、复现 B。
4. **下一步先修证据链和失败语义，再做小规模分层视觉试点。** 暂缓全量视觉写回，砍掉“盈亏平衡”决策输出和未经验证的 OCR 自动放行；保留净支出情景计算、接口采集、可追溯的视觉补缺。见 Q4。

`Capture → Assertion → View` 的分层方向值得保留，但当前执行路径没有兑现“完整证据、原始断言不丢、视图可重建”的契约。这个判断来自下面的代码与离线复现，不来自字段数量或测试通过率。

## 验证范围与事实基线

- 执行请求中的测试命令：`PYTHONPATH=src:scripts bash -c 'for t in tests/test_*.py; do python3 "$t"; done'`。初次执行为 **8 个测试文件、84 个测试函数，全部通过**。最终提交新增测试后重跑为 **9个文件、90个函数，全部打印通过**（其中一个联网测试可能在无断言时直接返回，不能仅凭打印证明采集成功）。可用 `rg -n '^def test_' tests` 复核。
- 遍历 `data/categories/*.json`：86 个文件、2,236 条记录，其中 45 条 `is_model_child`；扣除子记录后是 2,191 条。不同文件之间按 `product_id` 去重只有 1,468 个 ID（包含子记录 ID）。因此“2,191 款独立商品”不成立，这是分类内记录数；分类重叠本身可以接受，但预算与质量分母要去重。
- `kind=machine` 有 998 条（含子记录和跨分类重复），初次候选为tier1 1,641张、tier2 4,815张；最终复核为tier1 1,641张、tier2 2,412张，共4,053张。详见复现 A。
- 本次运行离线mock、数据审计和测试，未重新调用OCR/视觉模型。最终重跑新增的 `test_live_fetch_provenance_is_complete` 时，测试自行尝试了一次移动端采集；其无断言也可返回通过，因此不把它作为成功实采依据。当前 `python3` 环境没有 Pillow（`import PIL` 报 `ModuleNotFoundError`），不能把既有 bench 时间当成本次实测时间。
- 查阅了小米官方条款原页以校验经济模型，见 Q4 的链接。没有重新全量抓取商城，所以分类解析与分页的反例是离线契约反例，不是声称线上当日页面一定采用了那些形式。

## Q1：选图还有什么系统性缺陷？

### 1. tier2 已收紧，但仍没有证明“具体型号/真实规格”（P0，需验收后全量）

基线位置：`scripts/vision_params.py:30–42,74–87`；当前位置：同文件`45–55,87–100`。

基线条件是 `nm and not GENERIC_TAB.search(nm)`，任何未命中排除词的非空tab都进入tier2。`317eb32` 已换成 MODEL_TAB 正向特征，最终审计不再选择“选购指南/温馨提示/型号对比”；不能继续把这三个tab误选描述为当前缺陷。

**仍存在的边界：** MODEL_TAB 子串含`Pro|Max|Plus|Ultra`，合成 `Pro全新升级` 仍可进入tier2；普通显示器型号/分辨率tab则被全部排除，但没有人工证据证明这些tab不含真规格表。SPEC_TAB与NON_SPEC_TAB依然先排除“说明”再认参数，`规格参数说明`仍被误杀；英文匹配未忽略大小写。tier标签也没有决定排序或预算优先级。

原来的数量回归测试只检查总量小于12,000，不验证图片内容。新测试 `tests/test_spec_image.py:66–86` 把“显示器规格描述不应是型号”作为预期，但**选图的目标是找规格内容，不是只找型号字符串**：排除规格描述tab不能据此证明其中图片不值得提取。这是当前白名单可能过窄的重要验收缺口。`multi_model.is_model_tab`仍是另一套规则（`src/goodsdex/multi_model.py:29–45`），选图与拆分定义没有统一。

**建议：** tab名只提供先验。参数tab提高优先级，型号tab带实体候选，规格描述tab允许独立验证，未知tab标未知；不能凭tier2入事实库。保留候选与拒绝原因，分别测误选和漏选率。

### 2. 预筛只是外观排序，却实际决定了数据是否存在（P1）

位置：`scripts/img_preselect.py:74–78, 104–150`；调用位置 `scripts/vision_params.py:130–139`。

- 白底、低彩、高长宽比阈值由空调样本校准；白底售后文案也能满足，彩色、横向参数表可能不满足。每 tab 的 `spec` 候选按原顺序取前两张，其他按长宽比取前两张，并没有检查是否真含参数。
- 六个 tab 各两张、`max_keep=10` 时，全局 `keep[:max_keep]` 删除第六个 tab 的全部图片。离线复现返回 tab `[0,1,2,3,4]`，虽然 stats 报 `tabs=6`。注释承诺的“按 tab 配额”被全局截断破坏。
- URL 去重发生在 tab 分组之前，同一图被多个 tab 引用时仅保留第一个上下文。应缓存一次图片字节，但保留多条“图属于哪个 tab”的关联，不能把内容去重等同于实体归属去重。
- `download` 以 URL basename 作为缓存文件名（81–90），不同路径下同名图片会复用错误文件；没有检查 curl 返回码/HTTP 状态。至少要按完整 URL 或内容哈希缓存，校验成功状态和图片解码。

这不是主张完全取消预筛。应该测它筛掉的真规格图比例，并明确“本次只抽查这些图片”，不能把未保留的内容记为官方未提供。

### 3. 图选对仍会错：切片、主体、条件没有完整保留（P0/P1）

位置：`src/goodsdex/vision_extract.py:36–37, 69–92, 153–171`。

- 1700px 无重叠切片可能从一行或跨行值中间切开。`MAX_SLICES=12` 意味着超过 20,400px 的尾部直接不读，没有截断状态；这是代码推导，本次因缺 Pillow 未执行切图实验。
- Prompt 一开始就断言它是“规格参数”长图，对未知或营销图没有“这不是规格图/无法确定主体”的输出分支。数字化营销承诺并不会因为“只提取真实可见文字”就自动成为规格事实。
- JSON 以属性名为字典键；同图多个型号、同属性不同工况不能完整表达。当前跨切片已额外返回不同值的 `observations`，但params仍保留第一值，`vision_params.py`写回仍只传params和aliases，observations未持久化（当前`vision_extract.py:146–184`、`vision_params.py:157–166`）；后续归一化再按字符串长度择一（Q3）。错误在到达断言层前就发生了，接口优先无法补救接口本来没有的字段。
- 写入只凭 `all_asserts` 非空（`scripts/vision_params.py:159–173`），有切片 errors 也会标 `vision_extracted=True`。这不是已验证或完整提取的证据。
- `count_real_params` 统计的是 view 所有非元数据值，并不限定接口来源（`scripts/vision_params_lib.py:18–26`）。一次部分视觉结果超过 8 项，下一次就可能以“接口已有参数”为由跳过；对多型号父记录，一份接口参数超过 8 项也会阻止其他型号补缺。
- 不预筛分支把图片 URL 直接传给 `slice_image`，后者调用 `Image.open(path)`，没有下载 URL 的逻辑（`vision_params.py:144–146`、`vision_extract.py:145`）。请求中列出的“图片 URL”用法也没有完整实现。

**更可靠的流程：** 图内容缓存 → 区域/表格候选识别 → 提取原始条目列表（属性、值、单位、条件、型号、片段/bbox）→ 验证 → 暂存候选断言 → 按策略发布视图。分类、区域检测、LLM 判断都可出错，要允许拒答。先人工标注分层小样本，评估图选择精度/召回、主体归属准确率、字段值准确率，再决定扩大哪一个品类。

真实参数可能存在于“商品详情”中；当前完全排除它会漏。**本次没有标注被排除图，无法给出漏图率。** 应抽取被拒候选作为负样本复核，发现真规格区域后只提取该区域，避免重新对所有详情长图进行无差别提取。

## Q2：还有哪些“自欺式”数据来源？

### 1. gid成功快照代码已修，历史溯源断裂仍待修复（P0数据修复）

位置：`src/goodsdex/sources/mi_cn.py:247–262, 269–273`。

基线首次请求cap0被append，gid成功后仅替换局部变量，未append，断言引用了未保存的新capture。`317eb32` 已在当前 `mi_cn.py:259–261` append新快照，并增加引用自检；最终复现B返回2个capture且引用全部存在。**失败降级仍没有独立保存第二次失败请求/响应，也未保存POST请求体。**

当前库按每条记录检查：46,195 条 `mi_cn_mobile` 断言 capture 引用缺失。例：`data/categories/REDMI K系列.json` 的 `Redmi Note 13 Pro`，断言引用 `b5d9fa9d6eca`，记录内只有 `9be516c622bc`、`7b863177ba9d`。这是记录级计数，包含跨分类重复，不是 46,195 个独立错误事实。基线离线mock返回1个capture且断言全部悬空，当前相同mock已通过。

**修复：** 每次尝试保存独立 Capture，并把实际使用的那个 ID 绑定到断言；保存 POST body 的 pid/gid。修完代码不能修复已经丢失的第二次快照，需要重新采集，或明确把旧断言降级成证据缺失。

### 2. 原响应被截断；capture ID 也不保证唯一（P0/P1）

位置：`src/goodsdex/pipeline.py:30–45, 71–73`；`src/goodsdex/facts.py:90–95`。

- 原响应超 300,000 字符时被截去中间，然后保留原完整响应计算的 hash。当前库有 **56 个 hash 与存储内容不符的 capture，56 个不可 JSON 解析的非空快照**。例如 `REDMI K系列.json` 的 Redmi K70 PC capture 长度 300,022，含省略标记。依赖 JSON 的选图、拆分直接捕获异常后跳过，于是损坏证据会表现成“没有图”。完整字节应外置到内容寻址文件，记录引用，不能破坏原快照。
- `capture_id` 只含 source、URL、秒级时间，不含请求体、响应内容或随机唯一量。同一秒两次同 URL 不同响应可得到相同 ID（复现 B）；移动端所有 pid 的初次 URL 又都相同。当前单记录未发现重复 ID，但并发/合库时不能依赖碰巧跨秒。
- 适配器断言 `subject_id=pid`，产品/视图是 `CN:mi_cn:product:<pid>`（`mi_cn.py:270,396` 与 `pipeline.py:57,86`）；没有规范化实体引用。断言 ID 是 `cid:attr`，同 capture 重复属性仍可能撞 ID，即使列表保住了条目，`selected_from` 也无法唯一定位。

### 3. 视觉 Capture 保存的是答案，不是其声称定位的证据（P0）

位置：`src/goodsdex/vision_extract.py:209–230`。

`response_raw` 只有 `json.dumps(params)`，locator 却是 `$.data.extend_info.desc_tabs_view[...]...img`。该路径不可能在这份 JSON 中解析。没有 parent PC capture ID、原图内容哈希/持久化引用、切片坐标、模型响应、实际模型配置、prompt 版本、原始别名映射和附件条目。`parser_version=vision-v1` 不能代替这些。

实际返回的 `raw_params/aliases/accessories/parts/errors`（166–171）大多未传给持久化层。即使 URL 可打开，也不能证明图片没有变化，更不能证明该数值在哪个区域出现。

基线子记录直接复用父断言且captures为空；当前`multi_model.py:119–123`已继承父captures，解决新拆记录的引用存在性。历史仍有76条子记录视觉断言在本记录内缺capture；可迁移父证据/显式父引用，性质不同于移动端快照彻底未保存。继承captures也不解决视觉JSONPath指向答案capture的问题。子断言 `subject_id` 仍是父 ID，要显式记录派生归属依据，不能靠 view 换个 subject 就宣称身份已校验。

### 4. 单视觉伪双源已修，但未知来源与多候选问题仍在（P1）

基线位置：`scripts/compare_all.py:31–53`；当前位置：同文件`43–82`。

基线把view所有参数标成接口，再遍历视觉断言，于是同一视觉值产生“接口/视觉一致”。`317eb32` 已按 selected_from 查断言来源；最终复现B仅视觉输入只返回视觉。这一修复有效。

当前残留：查不到 selected_from/断言时仍默认“接口”（72–73），应标unknown并报告证据异常；`vision_values[canon]=value`（45–51）只保留最后一个视觉值，视图也最多补回选中的一个值，离线构造容量0L/1L/2L三条视觉断言，collect只返回0L和2L，丢了1L。新修复不能替代从完整断言列表构建候选。

`count_real_params`仍不限定接口来源（`scripts/vision_params_lib.py:18–26`），所以覆盖统计/补缺条件仍会把视觉值说成接口已有。模型读取官方图片是对官方证据的派生观察，不是接口直接声明或独立来源佐证。

### 5. “没抓到”和“源未提供”并未贯穿到下游（P0）

位置：`src/goodsdex/resolve.py:421–429`；`scripts/audit_usability.py:26–55`；`scripts/crawl_all.py:68–79`。

- `build_view` 不接收 captures；没有 `_params_empty` 就把缺口标 `absent`。`build_view([], category='earphone')` 全部缺口为 absent，即使真实背景是所有请求失败。失败状态在 captures 中存在，不代表下游知道它。
- 移动解析 `g={}` 时，缺失 `goodsList` 与明确返回空参数都通过 `or []` 变成 `_params_empty`（`mi_cn.py:266–267,327–340`）。协议缺字段应为解析/契约异常，不能推断源明确返回空。
- 审计把“没有任何 view 参数”的补集全部打印为“官方接口参数为空”，虽然它读取了 `params_empty` 却没用来判定。视觉 view 值也会被算成结构化接口参数。
- `crawl_all` 只要 `run_category` 不抛异常就记录 `status=ok`，包括搜索异常返回空列表、部分枚举、所有 PC 请求被熔断等；`--resume` 会跳过这些分类。零记录时 discovery 没有商品可承载，也没有分类级文件保存发现失败证据。失败采集还可能原子覆盖掉旧的有效分类文件（`pipeline.py:178–184`）：原子性不等于历史保留。

**修复：** 分类级保存发现任务与状态；View 结合源成功范围/解析契约计算缺口；缺乏足够证据时给 `not_collected/unknown`。`source_empty` 只表示指定接口/指定位置这次明确空，不表示整个官方网站没有。进度状态区分 complete、partial、failed、confirmed_empty，并支持按源补采。

### 6. 比较路径会掩盖冲突或条件（P1）

位置：`resolve.py:299–320,368–407`；`compare.py:110–147`；`scripts/compare_vision.py:39–48`。

- `build_view` 所谓“官方优先”实际是 `picked=items[0]`。当前主脚本的顺序偶然使接口在前；调换输入顺序即可选中视觉值（复现 B 的补充命令/代码位置）。空接口值也不会主动让位给提供值。
- 关系判断没有使用 `Assertion.qualifiers`，只从文本提取 anc；View 也不按 `subject + attr + qualifiers` 分组。型号/工况信息可能被合并。
- `compare` 不消费 view.relations，存在明确 conflict 的格子仍是 `ok`。条件对比只把非空 qualifiers 加入集合，一方条件已知、一方未知也不会提醒。`compare_vision` 则按“属性 + 商品名”直接取最后一条，完全绕过冲突层。
- 数量解析从自由文本拿第一个数字、后续最大数字当 range_max（`resolve.py:267–287`）；文本渲染又只展示第一个数（`compare.py:170–177`），例如 `3500 (150-5100)` 显示成 `3500W`。应明确区分额定值、上下限、尺寸向量和条件，而非统一提取数字。
- 变体价格仍是产品级：`mi_cn.py:267–290,403–410` 取 goodsList 第一项价格挂 pid；`pipeline.py:89–97` 的 market_prices 只有身份，没有价格或观察时间，枚举的 variant price 被丢掉。不要把容量/套装不同的默认 SKU 价格用于换机比较。

这些属于“数据本身有证据，但导出时制造了更强含义”的风险，应和模型读错分开统计。

## Q3：手工映射表方向对吗，会不会失控？

**手工确认语义是合理的；全局猜测、多个入口各自清洗不可持续。** `resolve.py:9` 说映射按 source + category + raw_attribute 定义，实际 `CATEGORY_RULES` 只按品类，取值代码也没按 source 区分（148–155、382–389）。`vision_normalize.py` 的 ALIASES/FRIDGE_ALIASES 是全局表，`compare_all` 对接口/视觉再跑一次，`apply_split` 又自己筛字段重建视图。这些入口没有共同的规则版本和不变量。

### 已经存在的语义损失（P0）

位置：`src/goodsdex/vision_normalize.py:47–55,60–93,114–135,164–178`。

- `ACCESSORY_PAT` 用包含匹配，“电池容量/电池类型”会被当附件删除；“包装尺寸”也被删。手机或电池产品上的真实参数不能用空调清单词表判定。复现 B：`电池容量:5000mAh` 不在参数里，只剩 accessories；持久化时 accessories 又没有保存。
- `室内机噪音(dB(A))(高风-强力)` 与未写工况的噪音都变成“室内机噪音”；APF 带测试标准/条件的名字也被去掉条件。不同条件不能靠 alias 证明相等。
- 同 canonical 的不同值只保留**字符串较长**的那个：`噪音=35dB` 与 `噪声(声功率级)=40dB` 只剩 35dB。后者还涉及声功率/声压等测量含义，不能全局映射后作为同一标量比较。aliases 只记录名字，不保留被丢的值，无法重建冲突。
- NFKC/lower 和目标名混用导致不幂等：`APF` 先变 `能效APF`，再 canonical 会变 `能效apf`；循环风量的 `m³` 会经 NFKC 变为 `m3`，但别名键仍写 `m³`（37、63、75、106）。没有一套“规则键也规范化”的机制。

### 建议的控制范围

1. **原始观察不可变。** 保存条目列表而不是字典择一；raw_attribute/raw_value/原图定位永远保留。归一化只生成派生字段，不替换原始字段。合并同义字段不等于删除相互冲突的原观察。
2. **统一规则注册表。** key 至少是 `(source_schema, category, raw_name)`，结果是稳定 attr_id + 单位 + qualifiers + 适用实体层级；展示名独立。全半角、空格作为可测试的字符层，语义规则必须带依据样例/反例、版本、负责人或变更来源。
3. **未知保持未知。** 动态 generic 属性适合展示原文，不等于可计算 schema。当前 generic `attrs=[]`（`resolve.py:155`），`compare` 无显式 attrs 时不生成参数行（`compare.py:83–99`），`coverage_report` 关键属性分母也为 0（`coverage.py:34`）。需要为实际服务的几个品类定义小型决策 schema，不能用“出现了多少字段”证明可比。
4. **每条规则有反例测试。** 电池参数 vs 随附干电池、带工况 vs 未知工况、不同能效标准、同属性不同单位、同名不同值、重复归一化、规则升级后重建。用未映射字段频次发现候选别名，模型可以建议，未经确认不自动跨语义合并。
5. **把分类/型号规则合到一处，但保留 unknown。** 当前分类过滤、选图、拆分是三套 regex；名称形态不能成为型号证明。`identity.py:207` 有 commodity 就标 verified，子记录又继承父 verified（`multi_model.py:109`），应分别表示“源销售组确认”和“实物型号归属确认”。

## 对第 1、2、5、6 点的专项补充

### 分类解析：当前可用，但结构变化会静默漏分类（P1）

位置：`mi_cn.py:99–125`。

正则精确要求 `<dd>` 没属性、href 双引号、span 恰为 `class="text"`，不能容忍 `dd class=...`、单引号、多 class、内部文本标签等常见合法 HTML。URL 用 `split('keyword=')[-1]`，会把 `&amp;page=2` 一并当关键词。离线 fixture 只解析出 `{'耳机':'耳机&amp;page=2'}`，手机/电视漏掉（复现 B）。

改用 HTMLParser 或成熟 HTML parser 收集分类容器里的链接文本，HTML 实体解码后 `urlsplit/parse_qs`。保存页面快照与解析版本，建立真实页面 fixture；遇到大类消失、分类数量骤降、重复同名不同查询要报告异常，不返回成功的短字典。更换 parser 只能修语法脆弱性，还需要限定分类区避免吸入非分类链接。

### 分页与熔断：区分状态的方向正确，语义与实现还没闭环（P0/P1）

位置：`mi_cn.py:128–215,346–373`。

- `_jsonp` 不匹配时返回 `{}`，枚举不检查业务 code 或 data/pc_list 的类型。业务错误 `{code:500,data:{total:57}}` 直接标 `no_sellable_items`（复现 B），破坏“失败不装成官方没有”的核心承诺。需要保存发现响应 Capture 并校验业务成功与 schema。
- 不只首页空列表触发 no_sellable：**已发现若干商品后的两个空页也会触发**，此时 completeness 仍是 `no_sellable_items`。这个名字错误地描述整个结果集。首页成功空 pc_list 最多证明“本次查询未返回可售列表”，还需确认地域/库存/接口契约才能断言在售范围。
- `total` 曾被确认是全局匹配数，但仍以 `len(rows)>=total` 作为 complete 的依据（184–199）。需要明确 total 的计数单位/过滤口径，并与返回可售产品数分开。
- 已见 pid 就整个跳过（165–181），后页同产品出现新 commodity 会丢变体；复现第二页新增 SKU b，最终只有 a。`new==0` 不能证明枚举完成。稳定枚举需要独立合并 product 和 commodity；搜索排序变化、重复页应标 partial，不能猜完整。
- `pages_fetched=page` 包括异常请求和超过上限的循环页号，例如正常跑满 max_pages 会得到 max_pages+1。用尝试数、成功页数分开记录；total 变化和重复页要有日志。
- breaker 的 fails 在成功后**从未清零**：实际是累计失败五次，不是连续五次。429 后成功一次仍是 fails=1（离线已复现）。每次 `_get` 还可尝试 4 次，因此熔断可能发生在约 20 次 HTTP 尝试后。
- 熔断只有 fetch_pc 使用，搜索和分类也访问 PC 接口却不受保护；没有冷却/半开恢复、Retry-After 或线程同步（pipeline 使用线程池）。一次长跑开路后，余下全库都不会尝试恢复，而且进度可能仍是 ok。

原型可保持简单：按 host 管理退避与状态，成功清零，冷却后单次探测，记录“未尝试/开路”与真实收到的 429；再配合可恢复进度。没有必要先引入复杂分布式熔断组件。

### 三个实测结论：能指导试点，不能证明全库安全

依据：`data/_bench_modes.json`、`data/_bench_route.json`、`data/_bench_ocr_vision.json`；采样/评分代码 `scripts/bench_modes.py:90–117`、`bench_route.py:43–89`、`bench_ocr_vision.py:60–80,121–139`、`bench_common.py:55–102`。

| 结论 | 当前证据 | 评审判断 |
|---|---|---|
| 混合无增益 | 3 张 spec 图：视觉 16/20/8 项，混合 16/17/6 项；合计 44 vs 39，67.6s vs 161.2s | **这些样本上没有项数增益且更慢**成立；不支持所有品类无增益或正确率无增益。逐项原字符串也非完全相同，部分是全半角/空格差异。 |
| 几何特征不足 | 能效图反例，以及配对污染输出 | 足以否定“几何像表格就可用”；不能证明“污染率低就正确”。换错行但值不含键，也可污染率 0。 |
| 规整表格 OCR 快，混排不可用 | spec_0 的 0.6s vs 21.2s；route 9 张里仅 1 张放行 OCR；接口基准 bench 仅 3 条记录 | 可作为这几张图和当前配对算法的观察，不是 OCR 技术在所有混排上的能力界限。当前测的是百度 OCR + 自写配对器。 |

具体设计缺陷：

- `route` 算出 layout 却不使用它，8 对且污染率<5% 就选 OCR（`layout_detect.py:127–133`）。复现 B 中任意八个错配纯数字值、布局非表格，仍返回 OCR。污染率是拒绝信号，不是正确性证明。
- bench 优先选择已经有 ≥8 项参数的商品，还挑前几张/前几个商品；全量目标恰是没有接口参数的商品（`vision_params.py:123` vs `bench_route.py:76`）。存在明显选择偏差，分类重叠和多个图来自同一产品也不能算独立样本。
- 用视觉输出作为 route 真值，并只比值前 6 个字符（`bench_route.py:55`）会自证视觉更好；模式一致也可能同源同错。
- `similar('5g','5kg')` 返回 True；子串还能把 `1级` 与 `11级` 当近似正确（`bench_common.py:62–67`）。键包含匹配也不校验一对一和条件。
- precision 注释说 extras 不算错，但分母用了全部 got（`bench_common.py:93–102`）；未知增量被隐式扣分，仍不知道哪些是真增量、哪些是幻觉。接口缺失的参数尤其无法用接口当完整真值。
- `PROMPT_HYBRID` 预先声明 OCR 文字准确（`vision_extract.py:98`），与已有识别错误观察冲突。bench 没记录 errors/OCR 是否真实成功参与、模型配置或重复试验，不能排除混合失败降级和随机波动。

建议建立人工复核的**图区域级真值**，同时保留接口作为辅助一致性检查。按品类、tier、被预筛拒绝、布局、单/多型号分层；训练/调阈值样本与验收样本分开。指标是图精度/召回、字段和值准确率、型号归属、条件保留和失败率，延迟/费用另报。人工标注不是原罪，标注可核验与独立复核比“没有人工真值”更可靠。

### 经济模型：净现金支出公式可用，当前权益处理与“盈亏平衡”不成立（P0）

位置：`src/goodsdex/economics.py:66–117,133–180,199–220`。

本次核验的[小米官方服务条款](https://www.mi.com/article/detail/637b5886162f.html)明确区分保值回收与未达标准的保底补贴分支，且权益期间从服务生效日起算。当前实现有以下问题：

1. `official_trade_in` 无成色/保值标准输入，一律先取 guarantee 与 detected 的最大值；`advise` 随后**另减 subsidy**。保值额和未达标准补贴是两条不同分支，不应叠加。已有测试把 `5999-2650-338=3011` 当正确答案（`tests/test_economics.py:87–116`），实际把错误规则固化了。对于满足保值标准、原价5299且质检2600的情景，应按保值额度计算，不再额外抵扣338；未达标准情景则不能保证拿到2650。
2. 窗口在计算之后只是文字标签。`purchase_date='2020-01-01'`、当前残值1000的 Xiaomi 15 Pro 仍得到 recover2650、subsidy338、net3011，同时 window=expired（复现 B）。应先判权益有效性；缺服务生效日、缺成色时分别展示条件情景，不能当成当前可用金额。
3. 购机日不等于服务生效日，尤其补购；购入价也不一定等于条款认定的商城原设备零售价。未知机型还会被默认套用50%，补贴名用子串匹配（78–89），都需要身份/适用条款验证。该判断依据官方页面的零售价判定与服务生效规则。
4. `ResidualQuote.kind=market` 的中位行情被当作个人设备实际质检额（171–173），两者身份、成色、渠道和费用不同。区间只取中点，却继承单个输入 confidence，未来残值和权益不确定性未传递（167、192）。
5. “继续用折旧/天”与“净掏钱/新机计划使用天数”不是同口径成本。旧机是机会成本资产，新机也有期末残值；必须在**同一 horizon**比较期末净资产、使用费用和维修等情景。简化情况下，继续用成本 `R0-Rold(H)+Oold(H)`，换新成本 `R0+P-T-B-Rnew(H)+Onew(H)`（T为实际回收额，B为独立额外补贴）。若按当前残值卖出，即T=R0，后者化为 `P-B-Rnew(H)+Onew(H)`；初始旧机资产R0在两种方案中一致，卖旧机的现金流是资金来源，不应把它从新机折旧中再次扣掉。
6. `net/keep_daily` 只是“净支出相当于多少天的假设旧机折旧”，不是策略盈亏平衡。它把当前 horizon 内的旧机折旧线性外推多年，未计算新机折旧，也忽略旧机残值降到零之后不能继续贬值。现有例子1375天，已超365天预测区间；净支出3011甚至超过当前残值2600，旧机不可能单凭折旧累计损失3011。应删除该决策标签，或仅作为明确假设下的算术比值；真正平衡需要求同时间点两种完整成本路径交点，可能根本没有交点。

上面经济成本公式是用于审查代码口径的简化推导，并非对某台设备未来收益的预测。可以先只输出可复算的净掏钱与有条件权益情景；没有新机期末残值/共同使用期限时，不输出哪条策略更划算。官方窗口是合同使用期限，不能推导为经济最优换机日。

CLI 还有输入问题：`scripts/should_i_upgrade.py:93–100` 用 truthiness 判断 residual_later，显式传0会退回30%假设；改变 `--horizon` 不会改变“年化30%”计算。`economics.py:136,179` 零/负使用期没有明确拒绝。需要校验边界并记录假设的期限。

## Q4：下一步优先级，以及建议砍什么

### P0：先兑现证据契约和失败契约

1. 已修gid成功快照保存，继续保存失败尝试与请求体；原快照外置且不可变；生成唯一 capture/assertion ID；统一 subject 引用。对现有孤儿断言和损坏快照做审计并明确降级，不能默默声称已恢复。验收依据是 Q2 的 46,195 条孤儿与56份损坏快照，复现 A/B 必须转为回归测试。
2. 视觉结果保存原图哈希/引用、parent capture、切片范围、原始模型输出、模型/prompt/规则版本；不在入库前按键丢值。未知图片、主体/条件不清的条目进入暂存区。验收：每个 view 值能走到唯一断言，再走到实际存在的证据与图区域；修改归一化规则不需重新调用模型就能重建。
3. 单视觉重复误标已修，继续处理未知来源与丢失的多候选、采集失败被当absent、进度假成功；将选值/对比统一走含条件与冲突的策略。验收：仅视觉输入不得产生接口佐证；所有源失败必须显示 not_collected；partial/failed 分类 resume 可恢复。
4. 如果继续暴露换机输出，立刻修复权益分支与窗口前置，撤掉“盈亏平衡”的当前解释。依据 Q4 专项与已有测试错误预期。

### P1：小规模验证价值，再扩张成本

- 先选空调、冰箱等已有真实使用案例的两三个品类，修复 tier2 未知放行与配额、建立分层图真值；抽查被排除图，测漏图。以缺失的决策关键属性/型号为补缺目标，替代8项总数阈值（Q1）。
- 修复分类 parser、分页状态、breakers、SKU 价格挂载和分类级 discovery；预算按唯一商品/唯一图片内容计算，保留多处关联（专项与Q2）。
- 做到拆分幂等：`scripts/apply_split.py:66–81` 每次都对已拆父记录再生成 kids；当前冰箱已有45个子记录，再跑会再追加45个同ID子记录。保存 parent 与唯一 children 集合，重建/upsert，而非 append（离线已验证）。
- 把真实分类排除状态落实到所有消费端：`vision_params.py:112`、`compare_all.py:70–71`、`audit_usability.py:37–46` 均只看kind，不排除 excluded、已拆parent或重复ID。这些计数/对比入口应共享有效实体集合。
- 对首个试点设明确验收目标：关键字段逐项复核、主体与条件归属无错配、失败/截断不报完成、所有字段证据可解引用；精度/召回分层报告而非一个全库平均数。达到后逐品类扩展，不能从三张图推算全库安全。

### 暂缓/砍掉

- **暂缓全库视觉 `--write`。** 未解决Q1/Q2前，扩张只会增加需要重新复核的数据。
- **砍掉默认 OCR 自动入事实库。** 当前污染率低不是质量证据；保留 OCR 为检索/候选/人工核验辅助，只有经独立样本验证的模板才自动放行（`layout_detect.route` 反例）。
- **砍掉当前“盈亏平衡天数”决策标签。** 保留净现金支出，未来有共同期限、期末残值与情景数据时再建立成本路径。
- **不要继续复制规则和对比脚本。** 收敛 `compare_all`、`compare_vision`、包内 compare 的字段与来源策略；旧 `normalize.py/model.py` 兼容路径应标边界，新增功能进入统一证据/视图流程，而不是再造一份清洗表。
- **暂缓自动残值决策集成。** `sources/zhuanzhuan.py:99–129` 目前是成交行情转 quote；即使回收方同属转转，也不能推导成交价等于个人设备回收额。先完成SKU/成色/渠道匹配和权益分支，保留手动、明确来源的残值情景即可。

## 可直接运行的离线复现

以下从仓库根目录执行，不联网、不读取密钥、不修改数据。A 是对本次快照的审计，数据更新后数字允许变化；B包含已修问题的回归核验和仍未修的确定性契约反例。

### A. 当前数据审计

```bash
PYTHONPATH=src:scripts python3 - <<'PY'
import json, hashlib
from pathlib import Path
from collections import Counter
from vision_params import find_spec_images
files = sorted(Path('data/categories').glob('*.json'))
rows, orphan, tier, suspect = [], Counter(), Counter(), Counter()
hash_bad = invalid_json = 0
for f in files:
    for r in json.loads(f.read_text()):
        rows.append(r)
        ids = {c['capture_id'] for c in r.get('captures', [])}
        for a in r.get('assertions', []):
            if a['capture_id'] not in ids:
                orphan[a['source']] += 1
        for c in r.get('captures', []):
            raw = c.get('response_raw', '')
            if not raw:
                continue
            hash_bad += c.get('response_hash') != hashlib.sha256(raw.encode()).hexdigest()[:16]
            try:
                json.loads(raw)
            except Exception:
                invalid_json += 1
        if r['product'].get('kind') == 'machine':
            for im in find_spec_images(r):
                tier[im['tier']] += 1
                if im['tab_name'] in ('选购指南', '温馨提示', '型号对比'):
                    suspect[im['tab_name']] += 1
print('分类/记录/唯一ID:', len(files), len(rows), len({r['product']['product_id'] for r in rows}))
print('子记录:', sum(bool(r['product'].get('is_model_child')) for r in rows))
print('孤儿断言:', dict(orphan), 'hash不符:', hash_bad, '无效JSON:', invalid_json)
print('候选分层:', dict(tier), '需复核tab:', dict(suspect))
PY
```

最终复核输出：`86 / 2236 / 1468`；子记录45；孤儿 `mi_cn_mobile=46195, mi_cn_pc_vision=76`；hash不符56、无效JSON56；tier1=1641、tier2=2412；需复核tab计数为空。后者说明已去除这三个误选tab，不能证明剩余4053张全部是规格图。

### B. 采集、语义与路由反例

```bash
PYTHONPATH=src:scripts python3 - <<'PY'
import json
from unittest.mock import patch
from goodsdex.sources import mi_cn as m
from goodsdex.facts import Capture
from goodsdex.resolve import build_view
from goodsdex.vision_extract import to_assertions
from goodsdex.vision_normalize import canonicalize_params
from goodsdex.economics import OwnedDevice, ResidualQuote, advise
from compare_all import collect
from bench_common import similar
from layout_detect import contamination, route
import img_preselect as ip

responses = [
    ({'code':0,'data':{'product':{'defaultGid':'g'}}}, '{"first":true}', 200, ''),
    ({'code':0,'data':{'product':{'name':'测试'}}}, '{"second":true}', 200, '')]
with patch.object(m, '_mtop_call', side_effect=responses):
    caps, aa = m.fetch_mobile('p')
    print('移动响应数/所有引用存在:', len(caps), all(a.capture_id in {c.capture_id for c in caps} for a in aa))
with patch.object(m, '_get', return_value='cb({"code":500,"data":{"total":57}})'):
    print('搜索业务错误:', m.enumerate_products('x', pause=0)['discovery']['completeness'])
print('无断言缺口:', {g['reason'] for g in build_view([], category='earphone').gaps})
with patch('goodsdex.facts.now_iso', return_value='2026-10-09T10:00:00+08:00'):
    print('不同响应ID相同:', Capture.make('s','u','a').capture_id == Capture.make('s','u','b').capture_id)
print('归一化:', canonicalize_params({'电池容量':'5000mAh','噪音':'35dB','噪声(声功率级)':'40dB'}))
caps, aa = to_assertions('u', 0, 0, {'容量':'1L'}, 'p')
print('视觉证据:', caps[0].response_raw, aa[0].locator)
r = {'view':build_view(aa, category='generic').to_dict(), 'assertions':[a.to_dict() for a in aa]}
print('单视觉来源(已修):', collect(r))
print('5g等于5kg:', similar('5g','5kg'))
pairs = {f'字段{i}':str(99-i) for i in range(8)}
c = contamination(pairs)
print('无表格布局仍走OCR:', route({'n':8,'multi_row_ratio':0,'height_cv':1}, pairs, c['rate']))
imgs = [{'url':f'u{t}-{p}','tab_index':t,'part_index':p} for t in range(6) for p in range(2)]
with patch.object(ip, 'download', return_value='fake'), patch.object(ip, 'profile_image', return_value=ip.ImgProfile('fake',100,200,.9,0)):
    keep, stats = ip.preselect(imgs, '/tmp/unused', max_keep=10, per_tab=2)
    print('六tab保留:', sorted({x['tab_index'] for x in keep}), stats)
html = '<dd><a href="/search?keyword=耳机&amp;page=2">耳机</a></dd><dd class="nav"><a href="/search?keyword=手机">手机</a></dd><a href="/search?keyword=电视"><span class="text active">电视</span></a>'
with patch.object(m, '_get', return_value=html):
    print('HTML解析:', m.list_categories())
dev = OwnedDevice('Xiaomi 15 Pro',5299,'2020-01-01',ResidualQuote(1000),True)
a = advise(dev,5999,500)
print('过期仍享权益:', a['window']['status'], a['upgrade'])
PY
```

最终关键输出：移动响应2个且引用True（代码已修）；搜索错误报no_sellable_items；失败缺口absent；ID碰撞True；电池容量进入accessories且两个噪音值只剩35dB；单视觉仅出现视觉一份（代码已修）；5g/5kg相等True；错配样例走ocr；第六tab丢失；HTML只得耳机且关键词混入`&amp;page=2`；过期仍recover2650/subsidy338/net3011。

已有测试为何没挡住：`test_assertion_locator_points_to_raw` 只检查构造字符串前缀（`tests/test_evidence.py:167–173`），没有解析真实 capture；`test_capture_status_distinguishes_failure` 只比较手造枚举；`test_subsidy_cap` 只检查 estimated_amount，没有检查 advise 额外补贴（`test_economics.py:72–77`）。测试主入口捕获异常后打印、没有非零退出，也不适合作为CI唯一门禁。应增加少量真实适配器输出的离线契约测试，验证引用、定位、状态传递、幂等与经济分支，而不是只验证数据类能承载这些字段。

最终新增审计的边界：`scripts/audit_provenance.py:25–38` 只检查capture ID存在，不能证明hash一致、locator可解引用或图内容可核验；应扩展为多级证据完整性指标。`tests/test_provenance.py:22–46` 发现历史孤儿后仅pass，联网测试在无断言时返回；这些测试的“通过”不代表历史数据已修复。

### C. 最新提交仍丢中间视觉观测，并且正向特征不等于语义验证

```bash
PYTHONPATH=src:scripts python3 - <<'PY'
import json
from vision_params import find_spec_images
from goodsdex.facts import Assertion
from goodsdex.resolve import build_view
from compare_all import collect
raw = json.dumps({'data':{'extend_info':{'desc_tabs_view':[
    {'name':'Pro全新升级','tab_content':[{'plain_view':{'img':'u'}}]}]}}})
print(find_spec_images({'captures':[{'source':'mi_cn_pc','response_raw':raw}]}))
aa = [Assertion(str(i),'p','c','mi_cn_pc_vision','容量',str(i)+'L') for i in range(3)]
r = {'view':build_view(aa,category='generic').to_dict(), 'assertions':[a.to_dict() for a in aa]}
print(collect(r))
PY
```

输出：Pro全新升级仍为tier2；三个容量候选只返回 `0L/2L`。这是合成契约反例，不是声称现有库已经有该营销tab或这些容量值。
