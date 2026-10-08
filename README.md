# GoodsDex

> 商品数据索引：从多源采集商品信息，字段级溯源，可验证、可对账。

给一个商品分类，枚举出全部商品，从多个数据源采集，合并成**每条数据都能追溯来源**的结构化数据集。

## 为什么需要它

做「这东西该不该换/该不该买」这类判断，需要三类数据：

1. **参数** —— 官方最准，但常以图片形式存在，且新品滞后
2. **时间** —— 官方参数页往往只给到月，精确到日要另找源
3. **口碑/热度** —— 官方页面里有（评价数、买家秀、问答），但埋在接口深处

现有做法各有毛病：爬虫只取一个源、解析器写死页面结构、数据没有溯源、冲突被静默覆盖。
GoodsDex 的核心主张是：**数据必须可溯源、冲突必须留痕、宁可缺不可错**。

## 核心原则

**① 三路并查** —— 抓任何页面前，先看三层：

| 层 | 手段 | 能看到什么 |
|---|---|---|
| raw HTML | curl/urllib | 服务端渲染的部分，或 SPA 空壳 |
| 渲染后 DOM | CDP `Runtime.evaluate` | JS 注入的内容 |
| 网络请求 | CDP `Network.*` | **隐藏的数据接口**（最高价值，最容易漏） |

实战教训：小米商城 PC 商品页的 raw HTML 是空壳，真正的数据在
`api2.order.mi.com/product/view` —— 只有看网络请求才发现。若只看 HTML，会误判"没有数据"。

**② 字段级溯源** —— 每条值记录来源：

```json
{
  "value": "369",
  "site": "m.mi.com",
  "page": "移动端商品详情页价格区",
  "api": "POST /mtop/xiaomishop/product/info",
  "json_path": "data.goodsInfo.goodsList[0].price",
  "fetched_at": "2026-10-08T20:25:54+08:00"
}
```

**③ 严格匹配，宁缺勿错** —— 第三方源按名称查找时，词条名必须与商品名**完全一致**（归一化后）。
0.77 相似度的模糊匹配曾把「REDMI Buds 8 青春版」匹配到「REDMI Buds 8 Pro」——
这种错误比没有数据更危险。

**④ 冲突留痕** —— 多源冲突不静默覆盖，全部保留并分类：

- `表述差异`：同一事实的不同说法（`约5.3g` vs `5.3±0.1g`、`冰川藍` vs `Glacier Blue`）
- `数据矛盾`：真正对不上的值（需人工核查）

## 架构

```
src/goodsdex/
  model.py        数据模型（Record / Field / Provenance）
  normalize.py    字段归一化 + 冲突判定
  pipeline.py     采集主流程（枚举 -> 多源 -> 归一化 -> 输出）
  sources/
    mi_cn.py      小米商城官方（PC + 移动端）
    baike.py      百度百科（精确发布时间、代际定位）
    zol.py        ZOL 中关村在线（第三方参数）
  parse/
    html.py       HTML 标签配对解析 + JS 注入噪声清洗
    text.py       可见文本解析
tools/
  probe.py        CDP 三路并查探测器（独立可用）
docs/
  methodology.md 抓取方法论与实战案例
```

## 用法

```bash
# 列出可采集的分类
python3 -m goodsdex.pipeline --list-categories

# 采集一个分类
python3 -m goodsdex.pipeline --category 吹风机

# 只采集官方源（快）
python3 -m goodsdex.pipeline --category 耳机 --sources mi_cn

# 独立探测任意页面（三路并查）
python3 tools/probe.py <url>
```

## 数据源优先级

```
小米官方-移动端 mtop   ← 主力：参数/价格/销量/口碑/问答
小米官方-PC 详情       ← 补充：图文详情、购买选项
百度百科              ← 精确发布时间、代际定位（覆盖低，严格匹配）
ZOL                   ← 第三方参数、上市日期
```

**已排除**：小米国际站/香港站 —— 区域版本，型号体系与国行不同（港版 `M2535E1`），
配色命名也不一致，混入会污染型号主键。

## 状态

早期开发中。已完成：小米官方双源采集、字段归一化、CDP 探测器、百科/ZOL 适配。
