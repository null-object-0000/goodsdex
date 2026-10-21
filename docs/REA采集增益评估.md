# REA 对现有采集的增益评估

实测日期：2026-10-21，北京时间（UTC+8）。分支：`fix/archive-partial-missing`。任务依据：[TASK-rea-collection-eval.md](TASK-rea-collection-eval.md)。

## 结论与执行偏差

**这两个样本没有测出 REA 的增量字段、增量入口或定位提速，不建议据此长期注册到日常采集环境。** 小米的详细规格仍需视觉或其他来源；Apple 的目标字段已在原始 HTML，直接解析更合适。复杂 JS 的跨模块追踪可作为以后单独评估的场景，本次未验证其收益。

本次严格先做完 A/B 基线，再备份、安装、复测，最后回滚。但安装阶段有两项必须披露的偏差，**不能把这次执行描述为全部符合纪律**：

- 首轮默认 `npx` 自动安装可选依赖 Frida 17.23.2。发现其安装动作后停止该路径，但事后检查发现 `build/frida_binding.node` 已下载完成，Frida 目录文件合计 117,526,662 字节。没有调用 Frida 功能，最终删除整个本次 npx 安装目录。Hopper/Ghidra 未安装；setup 也未强制要求安装它们。不能将“未装 Hopper”扩写成“未引入重型依赖”。
- 小米/Apple 实测 **12 次**外部 HTTP 请求，另取 REA 官方安装文档 **1 次**。npm 日志另有 **238 条 HTTP fetch 记录**（含下载、缓存更新和重新校验），Frida 安装脚本的额外下载未完整计数。因此全外网口径超过“几十次以内”，且 npm 内部同端点间隔没有受本次限速器约束。仅目标站点请求满足频率纪律，不能用 13 次冒充总网络请求数。

配置已恢复到安装前原始字节；本次 REA MCP 进程、分析子进程、临时快照服务均已结束。本次没有修改采集器、定时任务或 data 分支，没有 push；仓库只新增本报告。

## 范围与计时方法

先读现有小米实现、视觉链路、上一轮调研，不重新枚举商品或探测搜索契约。固定目标如下：

- A：档案中已有的“巨省电 1.5匹新一级能效 小米空调”，`productId=13143`、`gid=1204700007`，规格 tab 长图的字段是否还有结构化来源。
- B：公开的 [AirPods 5 规格页](https://www.apple.com.cn/airpods-5/specs/)和 [iMac 规格页](https://www.apple.com.cn/imac/specs/)，关注续航条件、耳机/充电盒区别，以及不同端口机型的内存、存储和按单配置。

**任务书与当前检出内容有差异：本分支 `src/goodsdex/` 没有 Apple 适配器。** `git ls-files` 和文件检索只找到旧的 [Apple 侦察文档](苹果官网采集侦察-2026-10-16.md)，没有 Apple 解析实现。因此可以定位字段所在层，不能给出不存在于当前检出中的解析器的具体漏采代码行；后者记为“未验证”。没有切换分支寻找它。

每项起止时间写入临时文件，包含该项目标选择、工具适配、阅读输出、失败尝试和真实请求复核的墙钟时间，不只是 HTTP 耗时。共同的仓库阅读、安装、MCP 连通性核验、回滚及报告写作不计入单项目标时间。安装准备另计：22:13:10 备份至 22:15:09 setup 结果落盘，约 1.97 分钟。

| 缺口 | 现有工具起止 | 基线分钟 | REA 起止 | REA 分钟 | 缩短分钟（基线－REA） |
|---|---|---:|---|---:|---:|
| A | 22:11:20.958–22:12:15.886 | 0.915 | 22:15:22–22:16:46 | 1.400 | −0.485，约慢 53% |
| B | 22:12:15.886–22:13:00 | 0.735 | 22:16:46–22:18:00 | 1.233 | −0.498，约慢 68% |

这是各一次的顺序实验，不能归因出工具的普遍性能。第二轮已经知道答案，并复用了第一轮下载的 JS/HTML，存在学习和缓存优势；不是盲测，也不是两次独立发现实验。REA 耗时含初次熟悉命令和为流量纪律搭建离线页面的开销。未单独测纯引擎耗时、熟练使用耗时或统计方差。

## 第一步：不安装 REA 的基线

工具：Python 标准库直接 HTTP、源码字符串定位、已配置的 Chrome DevTools MCP。HTTP 客户端不使用 CookieJar，不带 Cookie、Authorization 或账号，`DToken` 为空；不执行下载的 JS，不自动跟随重定向，不自动重试。重复端点按“主机＋路径、忽略查询参数”计算，距上一响应结束至少等待 2.15 秒。

### A：部分重叠参数有结构化来源，详细长图字段未找到替代源

1. `GET https://api2.order.mi.com/product/view?product_id=13143&version=2` 返回 HTTP 200、业务 `code=200`。`$.data.extend_info.desc_tabs_view[1]` 为“规格参数”，三个 `tab_content` 均为 `view_type=plain_view`，只有图片地址、宽高及空标题等布局字段。
2. `POST https://m.mi.com/mtop/xiaomishop/product/info` 返回 HTTP 200、`code=0`、`$.data.userInfo.login=false`。`$.data.goodsInfo.goodsList[0].classParameters.list` **实际有 12 项**，包括 APF 值 `5.27`、制冷量 `3500（150-5100）`、制热量 `5000(150-6610)W`。这些与长图有重叠；不能沿用历史文档中“空调结构化参数全为 0”的概括。
3. 第一张规格图为 [cc43efbbe5b01cd5380d5a2312bb86ec.jpg](https://cdn.cnbj1.fds.api.mi-img.com/mi-mall/cc43efbbe5b01cd5380d5a2312bb86ec.jpg)，1226×2564。视觉检查可见内机 840×311×200 mm、外机 860×551×331 mm、额定制冷功率 860（75–1950）W 等。上述详细尺寸/功率的成组参数没有在本次下载的接口和页面脚本文本中找到结构化对应。
4. 型号 `KFR-35GW/N1A1` 其实出现在 PC JSON 的 `$.data.product_info.seo_keywords` 中。这是逗号分隔的 SEO 文本，不能直接当作已验证的规范型号字段。当前 `_parse_pc` 没解析该字段；这是基线人工看到的线索，**不是 REA 的新发现**。
5. 商品购买页引用 [detail.e75c4600.js](https://cdn.cnbj1.fds.api.mi-img.com/mi.com-assets/shop/pro/js/buy/detail.e75c4600.js)。该文件第 1 行的 UTF-16 零起始列 83712 为 `getView:function`，83827 为 `getDetail:function`，159929 为 `desc_tabs_view`，173250 为 `"plain_view"===i.view_type`。可复现的关键逻辑：

```javascript
getView:function(e,t){return e.version=2,n["a"].get("".concat(a["a"].host.orderApi,"/product/view"),{params:e},t)}
getDetail:function(e,t){return n["a"].get("".concat(a["a"].host.orderApi,"/product/detail"),{params:e},t)}
```

`descTabsView` 从 `commodityData.extend_info.desc_tabs_view` 赋值，`plain_view` 分支使用 `plain_view.img` 渲染。直接请求 `product/detail?product_id=13143` 返回 **404，正文 `Not Found`**。这里只验证了这个 GET 参数组合，不能推断该路径所有调用方式均不可用。

结论：**本样本的部分长图信息确有结构化重叠来源，但未找到完整细规格的结构化替代源。** 已检查的规格 tab 本身确实只提供图片布局；“全官网只在图里”仍未验证。未扩大到其他商品、App 插件或购买流程。

现有采集为何缺：`sources/mi_cn.py` 的移动解析已遍历 `classParameters.list`；PC `_parse_pc` 对规格 tab 只提取图片及宽高，随后交给视觉链路。详细尺寸字段没有藏在本次响应的 tab 文本字段中。不能说这些字段只是当前解析器忘了解析。

### B：就在原始 HTML，无需先逆向 JS

两个匿名 GET 均为 HTTP 200。以下分组和值在原始响应中已存在，不依赖执行 JS：

| 页面 | 可复现 CSS 定位 | 本次看到的字段与条件 |
|---|---|---|
| AirPods 5 | `.section-chip [aria-labelledby="chip-headline"]` | H2 耳机芯片 |
| AirPods 5 | `.section-battery`，结合各个 `h4`/列表的 `aria-labelledby` | 普通充电盒款单次启用降噪 4 小时、关闭噪声控制 6 小时；无线充电盒款分别 5/7 小时；搭配充电盒且启用降噪分别 20/22 小时 |
| AirPods 5 | `.section-dimensions .caption-headline` / `.caption-values` | 每只耳机 4.3 g；普通/无线充电盒分别 32.3/34.7 g，需保留对象区别 |
| iMac | `.section-memory .grid-item-2-port` | 标配 16GB、可选配 24GB |
| iMac | `.section-memory .grid-item-4-port-1`、`-2`、`-3` | 前两组标配 16GB、可选 24/32GB；第三组标配 24GB、可选 32GB |
| iMac | `.section-storage` 同名机型列 | 两端口标配 256GB、可选 512GB/1TB；四端口第一组标配 256GB、可选 512GB/1TB/2TB，其余两组标配 512GB、可选 1TB/2TB |
| iMac | `.section-configure .grid-item-2-port` / `.grid-item-4-port-1` | 两端口列列有千兆以太网选配；四端口列列有纳米纹理玻璃面板等按单配置 |

Chrome DevTools 的空白隔离页用 `DOMParser.parseFromString` 解析两份完整 HTML，再用这些选择器读取文本及机型 class，未加载远程资源。首次用 MCP `sourcePath=/tmp/...` 被工作区路径限制拒绝；随后把同一脚本内容以内联参数送入 MCP，成功。一次尝试本地 BeautifulSoup 发现未安装，未加装；这些失败开销均留在基线时间中。

可确定的采集建议：不要照搬旧 iPhone 对比页的 `.compare-row/.compare-column` 规则；这两页使用 `techspecs-*` 或 section/grid。保留 AirPods 子型号与降噪条件、iMac 机型列，不能把“最高 32GB”赋给所有型号。**旧规则造成当前 Apple 适配器漏采这一因果关系未验证**，因为当前检出没有该适配器。

## 第二步：安装、注册与同目标复测

### 版本、配置和依赖

安装前 22:13:10.707 使用文件复制备份：

```text
原文件：/home/nichangen/.codex/config.toml
备份：/home/nichangen/.codex/config.toml.before-rea-20261021-221310.bak
SHA-256：26144a0657b95523f71ed1b118f21396724a60a433449911f988b2c3a8b5e843
```

REA：npm `rea-agents@6.7.0`；Node.js `v24.20.0`、npm `11.19.0`；浏览器观测报告 Chrome `155.0.8059.84`。版本来自实际 npm 元数据、包内 `package.json` 及 MCP initialize 返回值，不是猜测。

先下载 npm 包检查 `package.json` 和安装器，发现 Hopper 为可选项，但漏看了单独的 `optionalDependencies.frida`，导致首轮 `npx --yes rea-agents@6.7.0 setup --help` 触发其原生依赖下载。停止后改用以下命令检查计划并注册，计划只有 Codex 配置，没有 Hopper 安装动作：

```bash
npm_config_omit=optional npm_config_ignore_scripts=true \
  npx --yes rea-agents@6.7.0 setup --client codex --skill=false --dry-run --json
npm_config_omit=optional npm_config_ignore_scripts=true \
  npx --yes rea-agents@6.7.0 setup --client codex --skill=false --yes --json
```

setup 实际返回 `status=ready`、`appliedActions=["configured_codex"]`。没有手动注册，没有技能文件安装，没有安装 Hopper、Ghidra、额外浏览器或系统服务。`--yes` 可非交互通过。注意这些省略可选依赖的环境变量没有删除首轮已经安装的 Frida，不能把第二条命令的成功当作“Frida 从未安装”。

唯一修改的配置文件是 `~/.codex/config.toml`，追加：

```toml
[mcp_servers.rea]
command = "npx"
args = [ "-y", "rea-agents@6.7.0", "mcp" ]
startup_timeout_sec = 30
tool_timeout_sec = 450
```

setup 另生成 `~/.codex/config.toml.rea.backup`。npx 安装路径是 `/home/nichangen/.npm/_npx/a1722018f28f9df2`，约 250 MiB，另有共享 npm 下载缓存和日志。没有生成仓库内配置、依赖清单或锁文件。安装前后 TOML 语义比较确认仅增加 `mcp_servers.rea`。

本次会话没有热加载新 MCP 工具；目标分析通过已安装 REA 的 CLI 调用完成。为区分“写入配置”与“服务可启动”，另起一次 stdio MCP 实际发送 initialize、tools/list、binary_session：返回服务 `rea/6.7.0`，目录 207 项，`binary_session` 调用无错误，关闭 stdin 后退出码 0。此核验不代表 Codex 重启后的完整集成已验证，也不代表目录中的 207 项都已实测。

后续分析使用已安装包的 `node .../scripts/rea.mjs` 入口，避免重复 npx 的注册表校验。官方安装参考：[installation.md](https://github.com/morluto/rea/blob/main/docs/installation.md)，本次下载在 22:13:39，具体包行为以 6.7.0 实际输出为准。官方说明中的其他能力没有用作本报告的实测结果。

### A：静态结果没有新增可用入口，且存在明确截断

输入为基线完整下载的 `detail.e75c4600.js`，字节不改写，仅从 `.txt` 复制为 `.js`：

```bash
node /home/nichangen/.npm/_npx/a1722018f28f9df2/node_modules/rea-agents/scripts/rea.mjs \
  analyze-javascript-application /tmp/goodsdex-rea-eval/mi-input \
  --analysis-timeout-ms 45000 --json
```

实际得到证据 `ev_76b2075730d744e5309512ab1cd27eabd4bd524245cb80231d1a04c52f4ef418`，JSON 为 40,536,147 字节。1 个 JS、378,796 输入字节、107,380 个访问过的 AST 节点、0 解析失败；应用图 14 节点、22 边。语义图保留 20,000 节点、12,318 关系及 20,000 unknown，`coverage.status=partial`、`truncated=true`，命中每文件默认上限。

在保留的应用图及语义节点 JSON 中检索 `/product/view`、`/product/detail`、`desc_tabs_view`、`plain_view`，未得到对应节点；不能把这理解为源码中没有这些字符串——基线已经给出了确切位置。没有提高上限重新跑大图，未验证扩大预算后的效果。摘要还把网页普通 `preload` 属性标成 Electron preload 线索，存在面向本目标的噪声，不能照单全收为应用架构。

随后真实重请求 `product/view` 得到与基线相同 SHA-256 的响应，规格仍为三张图片；同样的 `product/detail` 请求仍 404。**REA 本次没有补出尺寸、功率或新的可用接口。** 细规格是否存在于未检查的其他位置仍未验证，不能从截断结果给出不存在证明。

### B：可读到已有漏采字段，没有自动生成机型参数映射

先对两份原始 HTML 运行相同的 `analyze-javascript-application`：实际读入 376,824 字节，0 个已解析 JS、19 个 findings、应用图 7 节点。该静态输出没有直接给出本目标的完整规格表。

再使用 `inspect-web-page`，输入是**同两份 HTML 的本地只读回放**：临时服务器仅绑定 `127.0.0.1:18763`，响应加入 `Content-Security-Policy: default-src 'none'` 等限制，禁用脚本、图片、样式、连接和框架；新的隔离浏览器上下文加载 `/airpods`、`/imac`。服务器实际只收到这两次本地 GET。没有在公网打开完整 Apple 页面或执行其脚本，不触碰现有登录上下文。

```bash
node /home/nichangen/.npm/_npx/a1722018f28f9df2/node_modules/rea-agents/scripts/rea.mjs \
  inspect-web-page http://127.0.0.1:9333 TARGET_ID \
  --allowed-origins http://127.0.0.1:18763 --include-accessibility-text --json
```

这是离线 DOM/可访问性观察，**不是线上 Apple 运行时或网络入口发现测试**。CSP 改变加载行为、没有原站样式，可能影响可访问性树中的重复、隐藏和分组表现。REA 的 `completeness` 为 `policy_filtered`，明确有 attach 前网络活动不可见等限制。

实际证据及部分机器定位：

- AirPods：`ev_dd4ca02c2744e9913aa1f2d5dadb8e56385d113ea5e61e517d996f04743aee8d`；`$.normalized_result.accessibility.nodes[676].name` 为 H2 耳机芯片，`[777].name` 为启用主动降噪下单次 4 小时的续航描述。其他节点也保留充电盒区别，但存在重复文本，需要人工选择节点和对应条件。
- iMac：`ev_a6ec4313f015e9bace0e8f01f86ddbc906af281025a7dc7d0928e1ac369d99e0`；`$.normalized_result.accessibility.nodes[953].name` 包含 24GB 或 32GB，`[1774].name` 为可选配千兆以太网端口。不能脱离 DOM 机型列把该值赋给所有 iMac。

最终两个公网规格页再次匿名 GET，均为 200，响应 SHA-256 分别与基线完全一致。**REA 部分完成“看到漏采字段”，但没有比直接 HTML 多看到字段，也没有解释缺失的 Apple 适配器内部原因。** 本次没有验证它能自动归并为正确的带条件断言。

## 对照与采集建议

| 问题 | A：小米长图 | B：Apple 规格 |
|---|---|---|
| REA 能否发现现有采集漏掉的字段/入口 | **不能：本次未发现增量**；有限静态图不能排除其他入口 | **部分**：能在可访问性树中显示目标字段；相对基线新增为 0，漏采代码原因未验证 |
| 两种方式结论是否一致 | 均未找到完整细规格的结构化替代源；REA 自身不足以证明“只在图里” | 字段都在原始 HTML；REA 离线观察与真实响应一致 |
| REA 额外价值 | 产出带哈希、位置和覆盖限制的静态分析证据；未转化为这次的字段增益 | 输出可定位的 DOM/可访问性证据，便于复核；未带来新入口 |
| REA 漏看/未完成 | 保留节点未覆盖已知的接口/渲染关键位置，图被截断；未重建细规格来源 | 未自动给出完整的机型×选配×条件映射；线上 JS/接口未验证 |
| 定位时间是否缩短 | 没有，增加 0.485 分钟 | 没有，增加 0.498 分钟 |

**真实请求复核仍需要。** 源码明明声明 `getDetail`，相同 GET 请求却实际 404，说明静态位置不是可用接口契约；也可能是参数或调用条件不足，本次没有扩探。REA 静态图的截断不能用来宣布接口不存在。Apple 的本地可访问性树只是已下载内容的派生视图，最终用真实匿名 GET 和响应哈希确认它对应当前公开页面。不能把本次经验推成“REA 所有输出都错误”或“所有结论必须重复下载”；有原始响应证据的静态字段可直接回指该证据。

建议维持已有工具链：小米优先读真实 JSON、按字段保留证据，详细长图继续视觉提取并标明来源；Apple 优先做分组 HTML 解析。每小时批量刷价、已知接口的稳定字段解析不应引入 REA 进程。复杂压缩 JS、跨模块调用或动态路径让现有 HTTP/CDP 方法遇阻时，可以按需、在独立依赖目录中另做有限实验；长期接入的价值、本次未出现的复杂场景收益、线上动态观察收益均为**未验证**。

## 回滚、卸载与副作用核验

本次实际采用精确手动回滚，避免 `rea uninstall` 扫描其他客户端。先用 TOML 比较确认删除新增 `mcp_servers.rea` 后其余内容等于备份，才执行等价于以下的操作：

```bash
cp -p /home/nichangen/.codex/config.toml.before-rea-20261021-221310.bak \
  /home/nichangen/.codex/config.toml
# 仅在确认它与上述原始备份逐字节相同时删除 setup 自动备份：
cmp -s /home/nichangen/.codex/config.toml.rea.backup \
  /home/nichangen/.codex/config.toml.before-rea-20261021-221310.bak && \
  rm /home/nichangen/.codex/config.toml.rea.backup
rm -rf /home/nichangen/.npm/_npx/a1722018f28f9df2
sha256sum /home/nichangen/.codex/config.toml \
  /home/nichangen/.codex/config.toml.before-rea-20261021-221310.bak
```

这些是本次确切路径，不应在有其他配置编辑后盲目整文件覆盖。未来有并发改动时，应只移除 REA 配置段并保留其他改动。官方通用命令为 `rea uninstall`，加 `--purge-data` 还处理 `~/.rea` 缓存/状态；本次未执行这个跨客户端卸载命令，其清理效果未验证。

实测清理结果：

- `~/.codex/config.toml` 与人工备份逐字节相同，SHA-256 均为 `26144a0657b95523f71ed1b118f21396724a60a433449911f988b2c3a8b5e843`，没有残留 REA 注册。
- 删除本次整个 npx 安装目录，包含 Frida 原生文件；保留人工配置备份。共享 `~/.npm/_cacache` 中可能仍有安装下载缓存，npm 调试日志仍在；未清空用户的共享 npm 缓存，故不是“磁盘无痕”。
- 没有 `~/.rea` 目录。未装服务，进程列表未发现本次 REA、Frida、Hopper、Ghidra或快照服务器进程；MCP 关闭退出码 0，快照端口 18763 连接被拒绝；关闭本次创建的三个浏览器标签，保留原有标签。
- 原始公开响应、计时、安装日志摘要和 REA 输出留在 `/tmp/goodsdex-rea-eval/` 供本机审计，未提交大体积文件或个人配置。目录包含下载的 npm 包副本，没有运行中的进程；可在审阅后用 `rm -rf /tmp/goodsdex-rea-eval` 删除。npm 缓存/日志保留不是采集进程。
- 没有运行日常全量采集，没有写入 data、价格文件或修改计划任务；因此没有引入持久运行副作用。对未来长期运行的性能、稳定性和未知副作用未验证。

## 请求账本与复现

目标站点仅下载公开页面、静态脚本、图片及免登录接口，无购买、登录、验证码或第三方私有数据操作。目标站点与安装文档的全部直接 HTTP 请求如下；请求失败也计数：

| 序号 | 时间 | 阶段/标记 | 请求 | 状态 |
|---:|---|---|---|---:|
| 1 | 22:11:48 | 基线 A-pc | GET `api2.order.mi.com/product/view?product_id=13143&version=2` | 200 |
| 2 | 22:11:48 | 基线 A-mobile | POST `m.mi.com/mtop/xiaomishop/product/info`，见下方 body/headers | 200 |
| 3 | 22:11:54 | 基线 A-page | GET `www.mi.com/shop/buy/detail?product_id=13143`，仅静态下载 | 200 |
| 4 | 22:12:02 | 基线 A-js | GET 上述 CDN `detail.e75c4600.js` | 200 |
| 5 | 22:12:02 | 基线 A-detail | GET `api2.order.mi.com/product/detail?product_id=13143` | 404 |
| 6 | 22:12:07 | 基线 A-image | GET 上述 `cc43efbbe5b01cd5380d5a2312bb86ec.jpg` | 200 |
| 7 | 22:12:15 | 基线 B-airpods | GET `www.apple.com.cn/airpods-5/specs/` | 200 |
| 8 | 22:12:16 | 基线 B-imac | GET `www.apple.com.cn/imac/specs/` | 200 |
| 9 | 22:13:39 | 安装文档 | GET `raw.githubusercontent.com/morluto/rea/main/docs/installation.md` | 200 |
| 10 | 22:16:46 | REA A-pc 复核 | 同 1 | 200 |
| 11 | 22:16:46 | REA A-detail 复核 | 同 5 | 404 |
| 12 | 22:18:00 | REA B-airpods 复核 | 同 7 | 200 |
| 13 | 22:18:00 | REA B-imac 复核 | 同 8 | 200 |

按端点忽略查询、从上次响应完成到下一次开始，四个重复端点间隔分别 298.027、283.827、343.826、343.723 秒，最小 283.827 秒。上述预算不包含回环 CDP、两次本地快照 GET，以及前文已披露的 npm/Frida 安装网络活动。

可复现核心请求如下，执行会增加新的请求；顺序执行且每次结束等待 2.1 秒，不开启自动重试或重定向：

```bash
curl -q -sS --max-time 25 -A 'Mozilla/5.0' -e 'https://www.mi.com/' \
  'https://api2.order.mi.com/product/view?product_id=13143&version=2'
sleep 2.1
curl -q -sS --max-time 25 -A 'Mozilla/5.0' \
  -H 'X-User-Agent: channel/mishop platform/mishop.m' \
  -H 'mishop-client-id: 180100031051' \
  -H 'X-Mishop-App-Source: front-RNWeb' -H 'Mishop-Channel-Id: channel' \
  -H 'Content-Type: application/json' -H 'Referer: https://m.mi.com/' \
  -H 'Origin: https://m.mi.com' -H 'DToken:' \
  --data '[{}, {"productId":"13143","gid":"1204700007"}]' \
  'https://m.mi.com/mtop/xiaomishop/product/info'
sleep 2.1
curl -q -sS --max-time 25 -A 'Mozilla/5.0' \
  'https://www.apple.com.cn/airpods-5/specs/'
sleep 2.1
curl -q -sS --max-time 25 -A 'Mozilla/5.0' \
  'https://www.apple.com.cn/imac/specs/'
```

本次部分原响应 SHA-256（JSON/HTML 原始字节，未格式化）：

```text
A-pc / REA A-pc   6734b87409e19d82c0a4823bc82bffcb2bfbd88320d1826a619f641d13db3f3f
A-mobile          e9ced7360b250260bb18a03106784c9f2c02dddd81660455f9a930c7bc0a99ad
A-js              7dfade863c230a3ec33234f8c1be56c06274278aa3fbc51e86e64abf1722274d
A-image           dbca5406c7b8e0490f3666b5d466da52a3bc54d73c90aef38886f2a52a7072e8
B-airpods / REA B 78aaf41f05234629adcfaa90da33822448bae2a4873cfdde0e493fd69e811cef
B-imac / REA B    2bbebbcb06572cf35aec96156c2ab0be96d7feb5e8027d5bfdeed29ef8147644
```
