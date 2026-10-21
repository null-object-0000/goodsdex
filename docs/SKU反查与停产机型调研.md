# SKU 反查与停产机型调研

调研日期：2026-10-21；全部时间为北京时间（UTC+8）。分支：`fix/archive-partial-missing`。

## 结论先行

- **Q1：本次未验证出铭牌 SKU → 商品的可用反查路径。** `BHR4945CN`、`BHR7504CN`、`E4501CN`、`ELA5501CN` 在商城搜索和脚本发现的搜索联想接口均未返回商品；商品名 → productId → 详情可读，但响应中的数字 `sku` 不是铭牌编码，不能称为 SKU 反查成功。
- **Q2：能取得目标历史款的官方名称、productId、铭牌型号与主要规格；不能用本次搜索枚举出全部历史商品，也不能证明该款已停产。** 官方旧页面 → 页面脚本 `P27QCA-RG` → `productId=19963` → 免登录详情已闭环；搜索按型号不返回商品，按 `G27Q` 只返回另外两项。详情实际为 `is_sale=true,is_stock=false`，只能记录当次售卖/库存字段，不能把任务中的“停产”当作已证事实。
- **如果只能用一条路，先做“官方旧产品页及其静态脚本 → productId → 已有详情采集入口”。** 对本目标已验证，不需要先找一个尚未证实存在的历史商品列表接口。

## 范围、工具与已知入口

先读 `docs/TASK-sku-lookup.md`、`src/goodsdex/sources/mi_cn.py`、`prices.py`、`probe.py`，再补读已有发布时间调研。已掌握的入口如下，仅对本任务目标作定向验证，不再探通用契约：

| 已有入口 | 代码已知能力 | 本次新增验证 |
|---|---|---|
| `api2.order.mi.com/search/index` | 关键词、分页、分类/筛选、`main_sort` | 四个 SKU、型号、名称对照；排序/下一页/空关键词 |
| `api2.order.mi.com/product/view` | product_id → 详情 | 旧款 19963 仍返回详情、数字 sku 和库存状态 |
| `m.mi.com/mtop/xiaomishop/product/info` | POST；四个业务请求头；productId/gid → 详情；已有 sku 解析 | 15061 和 19963 的匿名响应，数字 sku 的实际含义 |
| 分类页、`product/dynamicv2` | 分类发现、已知 gid 批量价格 | 不重复请求；它们不是已知的铭牌反查入口 |
| `sources/zhuanzhuan.py` | 需开放平台账号 | 不调用，不读取凭证 |

Chrome DevTools MCP 创建了独立的空白上下文；读取空白页 cookie 返回浏览器 `SecurityError`，未访问商城、未读取其他标签页。为了明确做到不带 cookie、不自动触发页面后台请求，网络实测采用临时 Python 标准库 HTTP 客户端（与 curl 同类直接请求），只下载 HTML/JS/JSON，不执行远端脚本。没有 CookieJar、Cookie、Authorization、账号或登录操作，服务器 Set-Cookie 也不回传；`DToken` 为空。重定向不自动跟随，无自动重试，无验证码处理。未使用已有采集器发网，避免其重试/间隔策略影响本次纪律。

**请求预算：直接 HTTP 33 次，另有公开网页检索 2 个查询（一次工具调用），合计 35 个可控请求/查询动作。** 搜索引擎内部抓取不在客户端可观测计数内；没有展开搜索结果中的第三方页面。两次不同主机的页面请求曾并行；同一端点重复请求均在上次完成后等待至少 2.1 秒。下面列出全部直接请求；同端点最短间隔另见计时节。

## Q1：请求和真实响应

### 可直接复现的匿名请求

以下命令不加载 curl 配置、不带 cookie、不跟随重定向、不重试；循环内每次结束等待 2.1 秒。复现会另外产生 10 次请求，不包含在本次 33 次实测内。第一组覆盖四个 SKU；第二组验证脚本发现的联想接口；最后两次展示已有 ID 的详情能力。

```bash
for q in BHR4945CN BHR7504CN E4501CN ELA5501CN; do
  curl -q -sS --max-time 22 --get \
    -A 'Mozilla/5.0' -e 'https://www.mi.com/' \
    'https://api2.order.mi.com/search/index' \
    --data-urlencode "query=$q" --data 'page_index=1&page_size=20&filter_tag=0&main_sort=0&province_id=&city_id=&sort_by=asc&callback=cb'
  sleep 2.1
done
for q in BHR4945CN BHR7504CN E4501CN ELA5501CN; do
  curl -q -sS --max-time 22 --get \
    -A 'Mozilla/5.0' -e 'https://www.mi.com/' \
    'https://api2.order.mi.com/search/query' \
    --data-urlencode "query=$q" --data 'page_index=1&jsonpcallback=xmsearch'
  sleep 2.1
done
curl -q -sS --max-time 22 -A 'Mozilla/5.0' \
  -e 'https://www.mi.com/' \
  -H 'X-User-Agent: channel/mishop platform/mishop.m' \
  -H 'mishop-client-id: 180100031051' \
  -H 'X-Mishop-App-Source: front-RNWeb' -H 'Mishop-Channel-Id: channel' \
  -H 'Content-Type: application/json' -H 'Referer: https://m.mi.com/' \
  -H 'Origin: https://m.mi.com' -H 'DToken:' \
  --data '[{}, {"productId":"19963","gid":"2230001683"}]' \
  'https://m.mi.com/mtop/xiaomishop/product/info'
sleep 2.1
curl -q -sS --max-time 22 -A 'Mozilla/5.0' -e 'https://www.mi.com/' \
  'https://api2.order.mi.com/product/view?product_id=19963&version=2'
```

### 搜索结果：四个编码均未闭环

21:37:52–21:38:00 四次 `search/index`：HTTP 200，均返回以下关键字段（从真实响应删去其他字段，未改值）：

```json
{"code":200,"msg":"success","data":{"list_v2":[],"total":45,"session":"","pc_list":[]}}
```

21:40:01–21:40:08 四次 `search/query`：HTTP 200，真实完整响应相同：

```javascript
xmsearch({"code":200,"msg":"success","data":{"list":[]}});
```

`total=45` 与空列表并存，不能当作精确命中数，亦不能推断“官方不存在该 SKU”。对照请求（21:38:07）以商品名 `米家空气净化器 4 Lite` 能拿到：

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "total": 51,
    "pc_list": [
      {
        "product_id": "15061",
        "commodity_list": [
          {
            "name": "米家空气净化器 4 Lite 白色",
            "commodity_id": 1213900027,
            "price": "599"
          }
        ]
      }
    ]
  }
}
```
这是**名称搜索成功**，不是由 BHR4945CN 返回的商品。两者映射只来自任务前提，本次官方响应尚未提供编码级佐证。BHR7504CN 与追觅全能基座的对应同样未获官方编码证据，不能写为验证成功。

### 已有详情中的 sku 并非铭牌 SKU

21:38:51 对照详情返回以下真实字段。该次误将搜索得到的 commodity_id `1213900027` 放进 gid；接口仍返回默认 goodsId `2213900003`。这提示可能有默认回退（推断），**不证明 commodity_id 可作为 gid**；不可照此扩展契约。

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "userInfo": {
      "login": false
    },
    "product": {
      "productId": 15061,
      "defaultGid": 2213900003,
      "name": "米家空气净化器 4 Lite",
      "enable": true
    },
    "goodsInfo": {
      "goodsList": [
        {
          "goodsId": 2213900003,
          "commodityId": 1213900027,
          "sku": 31961,
          "price": "599"
        }
      ]
    }
  }
}
```

21:38:53 使用旧页提供的正确 productId/gid，返回：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "userInfo": {
      "login": false
    },
    "product": {
      "productId": 19963,
      "defaultGid": 2230001683,
      "name": "Redmi 显示器 G27Q 2025款",
      "enable": true
    },
    "goodsInfo": {
      "goodsList": [
        {
          "goodsId": 2230001683,
          "commodityId": 1230802046,
          "sku": 55989,
          "price": "1299"
        }
      ]
    }
  }
}
```
两份完整响应均没有四个铭牌编码，亦没有 `AC-M17-SC` / `P27QCA-RG`。不能把 `31961`、`55989` 与 BHR/ELA 编码视为同一种标识；不能凭商品名推断二者可互换。

## Q2：能、不能、断在哪

| 问题 | 事实 | 判断（明确标注推断） |
|---|---|---|
| 旧款官方页面还能读吗 | 21:38:10 读取 [G27Q 2025 官方页](https://www.mi.com/redmi-monitors/g27q-2025)，HTTP 200，页内 product_info 含 19963、完整款名；21:39:00 购买页同样 HTTP 200 | **能**，对该目标成立，不外推全部旧款 |
| 铭牌型号能官方佐证吗 | 21:38:58 页面实际引用的产品 JS 中 `specsArray` 明示 `P27QCA-RG` | **能**，页面与其产品专用脚本连接商品名和型号 |
| 历史商品规格能拿吗 | 21:38:53 mtop code=0，规格包含 2560×1440、27英寸、180Hz、IPS | **能**，不要求登录；不是仅找到搜索引擎缓存 |
| 已经停产/停售吗 | PC code=200，`is_enable=true,is_sale=true,is_stock=false`；响应还含 `need_address_check=true` | **不能确认停产**。无地址条件下的无货字段不能推断全国无货或停售 |
| 铭牌型号能直接搜中吗 | `P27QCA-RG` 在 main_sort=0/4 均为空列表、total=45 | **本次不能**，断在搜索发现，不是详情权限 |
| 放宽名称/换排序能发现旧款吗 | `G27Q` 两种排序的首页均仅有 10050218、21067；新品排序第二页为空、total=2 | **本次不能发现 19963**；不能由搜索覆盖不足推出详情被删 |
| 有历史/全部商品列表吗 | 空 query + main_sort=4 返回 code=-30001；JS 只有综合/新品/销量/价格及筛选，未发现历史开关 | **未验证出可用入口**。main_sort=4 是“新品”排序，不能称为“含下架”开关；未穷举隐藏参数 |
| 厂商有旧款入口吗 | 本目标有可直达的官方旧产品页；其 `/specs` 返回 302 至错误页 | **有单品旧页**，本次未验证到完整“历史产品库”索引；规格实际在产品 JS 内 |

官方旧页面内真实片段：

```javascript
"product_info":{"product_id":"19963","name":"Redmi 显示器 G27Q 2025款","price":"1299","market_price":"1299","is_enable":true,"is_multi_price":false}
```

产品专用脚本真实片段（[页面引用的 JS](https://cdn.cnbj1.fds.api.mi-img.com/mi.com-assets/shop/pro/js/product/redmi-monitors/g27q-2025/index.5ab4c812.js)）：

```javascript
specsArray:[{name:"产品型号",specs:"P27QCA-RG"},{name:"电源输入",specs:"24V⎓2A"},{name:"额定功率",specs:"48W"},{name:"屏幕尺寸",specs:"27英寸"}
```

21:38:55 PC 详情关键字段（真实值，删去无关字段）：

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "need_address_check": true,
    "product_info": {
      "product_id": 19963,
      "name": "Redmi 显示器 G27Q 2025款",
      "is_enable": true
    },
    "goods_list": [
      {
        "goods_info": {
          "product_id": 19963,
          "commodity_id": 1230802046,
          "goods_id": 2230001683,
          "sku": 55989,
          "name": "Redmi 显示器 G27Q 2025款 黑色",
          "price": "1299",
          "is_sale": true,
          "is_stock": false
        }
      }
    ]
  }
}
```
这里 `1299` 是本次接口字段，不是证实可成交的价格，也不是历史发布价。页面仍有加入购物车文案，不能仅凭按钮判定有货。

## 脚本候选、robots 与错误边界

| 对象 | 事实 | 判断/处置 |
|---|---|---|
| `www.mi.com/robots.txt` | HTTP 200；Disallow 包括 `/?*`、`/search_*`、`/item/`、`/comment/`、`/accessories/`、`/cart/`、`/misc/` | 本次 `/shop/search`、旧产品页、`/shop/buy/detail` 未匹配这些前缀；不访问评论/购物车 |
| `m.mi.com/robots.txt` | 302，Location 带 `403` 错误页；未跟随 | robots 内容未能取得，不称“robots 允许”；公开商品详情 POST 实测匿名可读，不规避错误跳转 |
| `api2.order.mi.com/robots.txt` | 404，正文 `Not Found` | 无可读规则文件；不等于账号/风控豁免 |
| `api.mi.com/robots.txt` 与根路径 | 均 TLS EOF，无 HTTP 状态码 | 断在传输层，不能据此断言接口不存在、需要登录或已被风控；没有猜路由继续扫描 |
| 搜索页 JS | 真实调用 `host.orderApi + /search/index`；`getSearchTip` 调用 `/search/query`，参数 query/page_index 和 jsonpcallback=xmsearch | 后者是新增候选且已实测四个 SKU 均空；可访问不等于能反查 |
| JS 里的 `/search/droplist`、`/search/box` | 分别被 getSearchRecommend/getBoxRecommend 调用 | **仅发现、未请求**，不称可用反查/历史入口 |
| 购买页 JS 的 `/product/detail` | 有 GET 包装函数，未找到确定的本目标调用参数 | **仅发现、未验证**，不称可用；已有 view/mtop 已解决本目标规格 |
| JS 中预发/测试域名 | 配置含 pre/test 的 orderApi | 不访问；不能用来替代公开生产接口 |

本次没有 HTTP 401/429 或验证码响应；这只描述已测请求，不代表以后不会风控。`api.mi.com` 的 TLS 错误不能归因到风控。

## 基线耗时（分钟）

口径为本次单一代理按人工调研流程使用现有仓库、Chrome DevTools MCP、公开检索和直接 HTTP 工具的**墙钟耗时**，包含阅读、请求等待、负面验证与文档整理；不把 HTTP 响应时间相加冒充总耗时。不是单独计量的人类操作时长，无并行子代理。起点为首次工具记录时间，首句说明先于该记录数秒，不作不实精度外推。

| 阶段/里程碑 | 北京时间 | 自起点累计分钟 | 阶段分钟 |
|---|---|---:|---:|
| 开始、任务/代码阅读及工具检查 | 21:36:34 | 0.00 | — |
| 首个公开 HTTP 请求 | 21:37:31 | 0.95 | 0.95 |
| 旧款详情首次返回（已得名称/ID/规格，型号尚待脚本） | 21:38:53 | 2.32 | — |
| 产品脚本响应取得（后续本地检查确认型号） | 21:38:58 | 2.40 | — |
| 最后请求结束，具备本轮 Q1/Q2 有界判定证据 | 21:40:11 | 3.62 | 2.67 |
| 文档整理与校验完成、提交前冻结计时 | 21:43:37 | 7.06 | 3.43 |

**用于后续工具对比的“定位/判定”基线为 3.62 分钟；包含可审阅文档的端到端基线为 7.06 分钟。** Git 提交耗时不计入，两种口径不能混比。33 次直接请求耗时合计 0.16 分钟，仅用于解释网络占比。同端点上次响应完成至下次请求开始的最短实测间隔约 2.101 秒（日志毫秒舍入），满足 ≥2 秒；账本时间戳显示到秒，可能只显示相差 2 秒。

## 下一步最小动作

1. 在后续另行授权的实现任务中，先把 19963、2230001683、官方旧页和脚本中的 P27QCA-RG 作为一条有来源的历史商品样本，复用已有详情解析；保存 `search 未发现` 与 `is_sale/is_stock` 的独立观测，不默认写“停产”。本次不改采集器或数据。
2. 铭牌 SKU 方向仍保留“未验证”状态；下一轮只针对一款查官方说明书/标签附件是否明示 BHR/ELA 编码与型号/商品名的共同出现，形成可核验映射后再讨论本地反向索引，不凭空新增所谓 SKU API。
3. 不为未知“全部历史列表”继续盲试参数。对比其他工具时使用相同四编码、同一型号、相同匿名与频率预算，并要求同样的请求/响应证据；负面判定只限各自实际覆盖范围。

## 全量请求账本与响应摘录

公开网页检索于约 21:37:52 发起，两条查询为 `site.mi.com "G27Q 2025"`、`site.mi.com "BHR7504CN"`。结果仅作 URL 候选，旧页、ID、型号与详情均以随后直接读取的官方内容为依据。搜索结果中某个购买链接的标题与正文商品不一致，故没有采用其 ID。未把外部检索摘要当官方响应。

以下 R 编号按本地日志顺序重新编号（两条跨主机请求同秒发起）。所有响应均为实测，JSON 摘录只保留实际存在的关键字段；HTML/JS 使用原文片段。完整 URL 保留全部参数，可用 `curl -q -sS --max-time 22 -A 'Mozilla/5.0' -e 'https://www.mi.com/' 'URL'` 重放 GET；每次请求后 `sleep 2.1`，POST 则用上方相应 body/头。302 不加 `-L`。

### R01 · 21:37:31 · GET · HTTP 200 · 0.121 秒

`https://www.mi.com/robots.txt`

```text
# robots.txt for http://www.mi.com
# 2016/2/15

User-agent: *

Disallow: /?*
Disallow: /search_*
Disallow: /item/
Disallow: /comment/
Disallow: /accessories/
Disallow: /cart/
Disallow: /misc/
```

### R02 · 21:37:33 · GET · HTTP 302 · 0.139 秒

`https://m.mi.com/robots.txt`

原错误：`HTTP Error 302: Moved Temporarily`

Location：`http://err.www.mi.com/m02.html?http://fe.m.mi.com/robots.txt&403`

```text
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html>
<head><title>302 Found</title></head>
<body bgcolor="white">
<center><h1>302 Found</h1></center>
<hr/>Powered by MIWS</body>
</html>
```

### R03 · 21:37:36 · GET · HTTP 404 · 0.136 秒

`https://api2.order.mi.com/robots.txt`

原错误：`HTTP Error 404: Not Found`

```text
Not Found
```

### R04 · 21:37:38 · GET · HTTP 无 · 0.122 秒

`https://api.mi.com/robots.txt`

原错误：`URLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1082)'))`

```text
（未获得响应体）
```

### R05 · 21:37:52 · GET · HTTP 200 · 0.345 秒

`https://api2.order.mi.com/search/index?query=BHR4945CN&page_index=1&page_size=20&filter_tag=0&main_sort=0&province_id=&city_id=&sort_by=asc&callback=cb`

```text
{"code":200,"msg":"success","data":{"list_v2":[],"total":45,"pc_list":[]}}
```

### R06 · 21:37:55 · GET · HTTP 200 · 0.323 秒

`https://api2.order.mi.com/search/index?query=BHR7504CN&page_index=1&page_size=20&filter_tag=0&main_sort=0&province_id=&city_id=&sort_by=asc&callback=cb`

```text
{"code":200,"msg":"success","data":{"list_v2":[],"total":45,"pc_list":[]}}
```

### R07 · 21:37:57 · GET · HTTP 200 · 0.414 秒

`https://api2.order.mi.com/search/index?query=E4501CN&page_index=1&page_size=20&filter_tag=0&main_sort=0&province_id=&city_id=&sort_by=asc&callback=cb`

```text
{"code":200,"msg":"success","data":{"list_v2":[],"total":45,"pc_list":[]}}
```

### R08 · 21:38:00 · GET · HTTP 200 · 0.326 秒

`https://api2.order.mi.com/search/index?query=ELA5501CN&page_index=1&page_size=20&filter_tag=0&main_sort=0&province_id=&city_id=&sort_by=asc&callback=cb`

```text
{"code":200,"msg":"success","data":{"list_v2":[],"total":45,"pc_list":[]}}
```

### R09 · 21:38:02 · GET · HTTP 200 · 0.446 秒

`https://api2.order.mi.com/search/index?query=P27QCA-RG&page_index=1&page_size=20&filter_tag=0&main_sort=0&province_id=&city_id=&sort_by=asc&callback=cb`

```text
{"code":200,"msg":"success","data":{"list_v2":[],"total":45,"pc_list":[]}}
```

### R10 · 21:38:05 · GET · HTTP 200 · 0.354 秒

`https://api2.order.mi.com/search/index?query=Redmi+G27Q+2025&page_index=1&page_size=20&filter_tag=0&main_sort=0&province_id=&city_id=&sort_by=asc&callback=cb`

```text
{"code":200,"msg":"success","data":{"list_v2":[],"total":45,"pc_list":[]}}
```

### R11 · 21:38:07 · GET · HTTP 200 · 0.745 秒

`https://api2.order.mi.com/search/index?query=%E7%B1%B3%E5%AE%B6%E7%A9%BA%E6%B0%94%E5%87%80%E5%8C%96%E5%99%A8+4+Lite&page_index=1&page_size=20&filter_tag=0&main_sort=0&province_id=&city_id=&sort_by=asc&callback=cb`

```text
{
  "code": 200,
  "msg": "success",
  "data": {
    "total": 51,
    "pc_list": [
      {
        "product_id": "15061",
        "commodity_list": [
          {
            "name": "米家空气净化器 4 Lite 白色",
            "commodity_id": 1213900027,
            "price": "599"
          }
        ]
      },
      {
        "product_id": "15062",
        "commodity_list": [
          {
            "name": "米家空气净化器 4 Lite 滤芯 蓝色",
            "commodity_id": 1213900028,
            "price": "169"
          }
        ]
      },
      {
        "product_id": "4664",
        "commodity_list": [
          {
            "name": "米家空气净化器滤芯 标准版 天蓝",
            "commodity_id": 1164000002,
            "price": "149"
          }
        ]
      },
      {
        "product_id": "10178",
        "commodity_list": [
          {
            "name": "净化器滤芯 除甲醛增强版S1 绿色",
            "commodity_id": 1192600041,
            "price": "169"
          }
        ]
      },
      {
        "product_id": "12184",
        "commodity_list": [
          {
            "name": "米家空气净化器滤芯 抗菌抗病毒版 个",
            "commodity_id": 1202200011,
            "price": "169"
          }
        ]
      },
      {
        "product_id": "25602",
        "commodity_list": [
          {
            "name": "米家空气净化器 6 C 白色",
            "commodity_id": 1230809365,
            "price": "1099"
          }
        ]
      },
      {
        "product_id": "14895",
        "commodity_list": [
          {
            "name": "米家空气净化器 4Pro 滤芯 绿色",
            "commodity_id": 1213400005,
            "price": "299"
          }
        ]
      },
      {
        "product_id": "19826",
        "commodity_list": [
          {
```

### R12 · 21:38:10 · GET · HTTP 200 · 0.594 秒

`https://www.mi.com/shop/search?keyword=BHR4945CN`

```text
var $KEYWORD = "BHR4945CN";
var $REDIRECTURL = "";
```

### R13 · 21:38:10 · GET · HTTP 200 · 0.625 秒

`https://www.mi.com/redmi-monitors/g27q-2025`

```text
"product_info":{"product_id":"19963","name":"Redmi 显示器 G27Q 2025款","price":"1299","market_price":"1299","is_enable":true,"is_multi_price":false}
```

### R14 · 21:38:13 · GET · HTTP 302 · 0.233 秒

`https://www.mi.com/redmi-monitors/g27q-2025/specs`

原错误：`HTTP Error 302: Moved Temporarily`

Location：`http://err.www.mi.com/04.html`

```text
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html>
<head><title>302 Found</title></head>
<body bgcolor="white">
<center><h1>302 Found</h1></center>
<hr/>Powered by MiWeb</body>
</html>
```

### R15 · 21:38:15 · GET · HTTP 301 · 0.152 秒

`https://m.mi.com/`

原错误：`HTTP Error 301: Moved Permanently`

Location：`https://www.mi.com`

```text
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html>
<head><title>301 Moved Permanently</title></head>
<body bgcolor="white">
<center><h1>301 Moved Permanently</h1></center>
<hr/>Powered by MIWS</body>
</html>
```

### R16 · 21:38:17 · GET · HTTP 无 · 0.04 秒

`https://api.mi.com/`

原错误：`URLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1082)'))`

```text
（未获得响应体）
```

### R17 · 21:38:51 · POST · HTTP 200 · 0.214 秒

`https://m.mi.com/mtop/xiaomishop/product/info`

Body：`[{}, {"productId":"15061","gid":"1213900027"}]`

```text
{"code":0,"message":"ok","product":{"productId":15061,"name":"米家空气净化器 4 Lite","defaultGid":2213900003},"goodsList[0]":{"goodsId":2213900003,"commodityId":1213900027,"sku":31961,"price":"599"}}
```

### R18 · 21:38:53 · POST · HTTP 200 · 0.211 秒

`https://m.mi.com/mtop/xiaomishop/product/info`

Body：`[{}, {"productId":"19963","gid":"2230001683"}]`

```text
{"code":0,"message":"ok","product":{"productId":19963,"name":"Redmi 显示器 G27Q 2025款","defaultGid":2230001683},"goodsList[0]":{"goodsId":2230001683,"commodityId":1230802046,"sku":55989,"price":"1299"}}
```

### R19 · 21:38:55 · GET · HTTP 200 · 0.333 秒

`https://api2.order.mi.com/product/view?product_id=19963&version=2`

```text
{"code":200,"msg":"success","goods_list[0].goods_info":{"name":"Redmi 显示器 G27Q 2025款 黑色","sku":55989,"price":"1299","is_sale":true,"is_stock":false}}
```

### R20 · 21:38:58 · GET · HTTP 200 · 0.213 秒

`https://cdn.cnbj1.fds.api.mi-img.com/mi.com-assets/shop/pro/js/product/redmi-monitors/g27q-2025/index.5ab4c812.js`

```text
specsArray:[{name:"产品型号",specs:"P27QCA-RG"},{name:"电源输入",specs:"24V⎓2A"},{name:"额定功率",specs:"48W"},{name:"屏幕尺寸",specs:"27英寸"},{name:"点距",specs:"0.2331(H) X 0.2331(V)mm"},{name:"亮度",specs:"300nits
```

### R21 · 21:39:00 · GET · HTTP 200 · 0.623 秒

`https://www.mi.com/shop/buy/detail?product_id=19963`

```text
<title>Redmi 显示器 G27Q 2025款立即购买-小米商城</title>
```

### R22 · 21:39:03 · GET · HTTP 200 · 0.383 秒

`https://api2.order.mi.com/search/index?query=G27Q&page_index=1&page_size=20&filter_tag=0&main_sort=0&sort_by=asc&callback=cb`

```text
{"code":200,"msg":"success","data":{"total":2,"pc_list":[{"product_id":"10050218","commodity_list":[{"name":"REDMI 显示器 G系列 27 英寸","commodity_id":10050218,"price":"649"}]},{"product_id":"21067","commodity_list":[{"name":"REDMI显示器G27Q 240Hz 黑色","commodity_id":1230803658,"price":"849"}]}]}}
```

### R23 · 21:39:05 · GET · HTTP 200 · 0.214 秒

`https://api2.order.mi.com/search/index?query=G27Q&page_index=2&page_size=20&filter_tag=0&main_sort=4&sort_by=asc&callback=cb`

```text
{"code":200,"msg":"success","data":{"total":2,"pc_list":[]}}
```

### R24 · 21:39:08 · GET · HTTP 200 · 0.435 秒

`https://api2.order.mi.com/search/index?query=P27QCA-RG&page_index=1&page_size=20&filter_tag=0&main_sort=4&sort_by=asc&callback=cb`

```text
{"code":200,"msg":"success","data":{"list_v2":[],"total":45,"pc_list":[]}}
```

### R25 · 21:39:10 · GET · HTTP 200 · 0.144 秒

`https://api2.order.mi.com/search/index?query=&page_index=1&page_size=20&filter_tag=0&main_sort=4&sort_by=asc&callback=cb`

```text
cb({"code":-30001,"msg":"请求参数错误","data":null});
```

### R26 · 21:39:17 · GET · HTTP 200 · 0.48 秒

`https://www.mi.com/shop/search?keyword=BHR4945CN`

```text
var $KEYWORD = "BHR4945CN";
var $REDIRECTURL = "";
```

### R27 · 21:39:19 · GET · HTTP 200 · 0.375 秒

`https://cdn.cnbj1.fds.api.mi-img.com/mi.com-assets/shop/pro/js/buy/detail.e75c4600.js`

```text
getView:function(e,t){return e.version=2,n["a"].get("".concat(a["a"].host.orderApi,"/product/view"),{params:e},t)},getDetail:function(e,t){return n["a"].get("".concat(a["a"].host.orderApi,"/product/detail"),{params:e},t)}
```

### R28 · 21:39:36 · GET · HTTP 200 · 0.281 秒

`https://cdn.cnbj1.fds.api.mi-img.com/mi.com-assets/shop/pro/js/search.db29eda7.js`

```text
getSearchTip({query:e,page_index:1},{param:"jsonpcallback",name:"xmsearch"}).then((function(e){if(200===e.code)if(e.
orderTypeList 中实际片段：{name:"新品",value:4},{name:"销量",value:1},{name:"价格",value:2}],pageNavLogCod
```

### R29 · 21:40:01 · GET · HTTP 200 · 0.131 秒

`https://api2.order.mi.com/search/query?query=BHR4945CN&page_index=1&jsonpcallback=xmsearch`

```text
xmsearch({"code":200,"msg":"success","data":{"list":[]}});
```

### R30 · 21:40:04 · GET · HTTP 200 · 0.151 秒

`https://api2.order.mi.com/search/query?query=BHR7504CN&page_index=1&jsonpcallback=xmsearch`

```text
xmsearch({"code":200,"msg":"success","data":{"list":[]}});
```

### R31 · 21:40:06 · GET · HTTP 200 · 0.154 秒

`https://api2.order.mi.com/search/query?query=E4501CN&page_index=1&jsonpcallback=xmsearch`

```text
xmsearch({"code":200,"msg":"success","data":{"list":[]}});
```

### R32 · 21:40:08 · GET · HTTP 200 · 0.145 秒

`https://api2.order.mi.com/search/query?query=ELA5501CN&page_index=1&jsonpcallback=xmsearch`

```text
xmsearch({"code":200,"msg":"success","data":{"list":[]}});
```

### R33 · 21:40:10 · GET · HTTP 200 · 0.272 秒

`https://api2.order.mi.com/search/index?query=G27Q&page_index=1&page_size=20&filter_tag=0&main_sort=4&callback=cb`

```text
{"code":200,"msg":"success","data":{"total":2,"pc_list":[{"product_id":"10050218","commodity_list":[{"name":"REDMI 显示器 G系列 27 英寸","commodity_id":10050218,"price":"649"}]},{"product_id":"21067","commodity_list":[{"name":"REDMI显示器G27Q 240Hz 黑色","commodity_id":1230803658,"price":"849"}]}]}}
```
