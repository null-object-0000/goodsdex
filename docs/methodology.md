# 抓取方法论

从实战中总结。核心是**三路并查**：抓任何页面前，不要只看一层。

## 三路并查

| 层 | 手段 | 能看到什么 | 容易漏掉什么 |
|---|---|---|---|
| ① raw HTML | curl / urllib | 服务端渲染的部分 | SPA 空壳、JS 动态注入的内容 |
| ② 渲染后 DOM | CDP `Runtime.evaluate` | JS 执行后的完整 DOM | — |
| ③ 网络请求 | CDP `Network.*` | **隐藏的数据接口** | ← 最容易忽略，价值最高 |

工具：`python3 -m goodsdex.probe <url>`

输出：raw/rendered 字节数对比、全部请求（按类型分类）、可能含数据的请求及其响应体。

## 实战案例

### 小米商城 PC 商品页

- **raw HTML**：约 200KB，但正文是空的，只有导航和页脚
- **渲染后 DOM**：仍是空壳（正文由接口异步填充）
- **网络请求**：发现 `GET api2.order.mi.com/product/view?product_id=X&version=2`
  → `product_info` + `goods_list` + `extend_info.desc_tabs_view`（图文详情）

**教训**：只看 HTML/DOM 会得出「这个页面没有数据」的错误结论。
真正的数据在接口里，只有看网络请求才发现。

### 小米移动端 mtop

```
POST https://m.mi.com/mtop/xiaomishop/product/info
X-User-Agent: channel/mishop platform/mishop.m
mishop-client-id: 180100031051
X-Mishop-App-Source: front-RNWeb
Mishop-Channel-Id: channel
Content-Type: application/json

[{},{"productId":23966,"gid":2230009359}]
```

三个坑（缺一不可）：
1. 必须 **POST**（GET 一律返回「jsonp没有传入callback」或「参数错误」）
2. 4 个自定义头缺一不可
3. body 是 **mtop 数组格式 `[{}, {...}]`**，且带 `gid` 才返回完整数据
   （不带 gid 只有 20KB，带了 42KB）

返回字段最全：21 项关键参数（含**发布日期**）、销量、口碑标签、买家秀、问答、图文详情。

### ZOL 参数页

- **raw HTML**：参数**在里面**（14 项）
- **渲染后 DOM**：163KB（比 raw 多 50KB，JS 注入了广告和按钮）
- **问题**：JS 注入的「纠错」「问豆包」按钮污染了 `th/td` 结构
  → 解析出 `产品型号 = 问豆包`

**教训**：解析优先级是 **HTML 标签配对 + 噪声清洗**，不是裸可见文本。
见 `parse/html.py` 的 `strip_noise()`。

### 百度百科

- curl 直连 → **403 Forbidden**
- 无头浏览器 → 正常（375KB）

内容价值：精确到日的**发布时间**（官方只给到月）、代际定位描述。

**严格匹配原则**：词条名必须与商品名完全一致（归一化后）。
模糊匹配（0.77 相似度）曾把「REDMI Buds 8 青春版」匹配到「REDMI Buds 8 Pro」。
**宁可返回"无数据"，也不返回错数据。**

### GSMArena / 京东

- GSMArena：Cloudflare Turnstile 挑战墙，脚本无法通过
- 京东：搜索页是空壳（2.6KB），需登录

## 数据可信度原则

**① 信源分级**

```
1 级  官方（小米商城 PC/移动端）
3 级  第三方（百科、ZOL、52audio）
```

**② 字段级溯源**，不是记录级。同一记录的 `价格` 和 `发布日期` 可能来自不同源。

**③ 冲突留痕**，不静默覆盖：

- `表述差异`：同一事实的不同说法（`约5.3g` vs `5.3±0.1g`）
- `数据矛盾`：真正对不上（需人工核查）

**④ 字段名歧义要警惕**

实例：移动端字段「产品净重（含充电盒）= 34.5g」，而 PC 参数页明确写
「充电盒重量 34.5g / 整机重量 43.4g」—— 移动端把充电盒重量标成了「含充电盒」。
**跨源对照才发现，单源会一直错下去。**

## 解析优先级

```
HTML 标签配对 + 噪声清洗   ← 最优（结构清晰）
> 内嵌 JSON（__NEXT_DATA__ 等）
> 网络接口 JSON
> 裸可见文本               ← 噪声最多
```

## 性能

- 无头浏览器冷启动约 40s，**复用实例后每页约 3s**
- 别每页启一个浏览器进程（`probe.Probe` 类支持复用）
- 小米官方纯接口请求：单商品 3 个请求约 1s，11 款商品并发不到 10s
