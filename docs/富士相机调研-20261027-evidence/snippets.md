# 关键摘录（脱敏，不含整页 HTML）

### fujifilm.com.cn robots：禁止站内搜索/登录，给出 sitemap
- URL: https://www.fujifilm.com.cn/robots.txt
- HTTP: 200
- 摘录: `Disallow: /cn/search/ ... Sitemap: https://www.fujifilm.com.cn/cn/sitemap.xml`
- 说明: 全站产品页未被 Disallow；不要碰 /cn/search/ 和登录路径。

### fujifilm-x.com robots：AI/搜索 bot 允许，部分 bot Crawl-delay 1–60
- URL: https://www.fujifilm-x.com/robots.txt
- HTTP: 200
- 摘录: `User-agent: * / Disallow: /wp-admin/ ... Crawl-delay: 1（部分搜索 bot）… Crawl-delay: 60（Scrapy 等）`
- 说明: 产品/规格页不在 Disallow 内。

### fujifilm.com.cn sitemap：1222 条 URL，含数码相机系列页
- URL: https://www.fujifilm.com.cn/cn/sitemap.xml
- HTTP: 200
- 摘录: `url 数=1222；示例 lastmod：X 系列页 2026-09-04T16:20:02+08:00`
- 说明: 可作为改版监测信号。

### X 系列页：可换镜 10 款 + 固定镜头 3 款（含旧款）
- URL: https://www.fujifilm.com.cn/cn/zh-hans/consumer/digitalcameras/X
- HTTP: 200
- 摘录: `FUJIFILM X-T5 | FUJIFILM X-H2 | FUJIFILM X-H2S | FUJIFILM X-T50 | FUJIFILM X-E5 | FUJIFILM X-M5 | FUJIFILM X-T30 III | FUJIFILM X-Pro3 | FUJIFILM X-S20 | FUJIFILM X-E4 | FUJIFILM X100VI | FUJIFILM X-HF1 | FUJIFILM X100V`
- 说明: 卡片文字；其中 X-E4、X100V 不在当前规格页导航里，按旧款处理。

### 规格页导航的“当前 X 线”：9 可换镜 + 2 固定镜头
- URL: http://www.fujifilm-x.com/zh-cn/products/cameras/x-e5/specifications/
- HTTP: 200
- 摘录: `x-h2s | x-h2 | x-pro3 | x-t5 | x-s20 | x-t50 | x-t30-iii | x-e5 | x-m5 | x100vi | x-hf1`（GFX 4 款另列）
- 说明: X-E4、X100V 不在此导航里，故按“官网在列旧款”单列；X-HF1 的官方商品名是 X half。

### X-T5 产品页 JSON-LD：USD 1,699 起，明确“价格因地区而异”
- URL: http://www.fujifilm-x.com/zh-cn/products/cameras/x-t5/
- HTTP: 200
- 摘录: `"@type":"Product","name":"X-T5","url":"https://www.fujifilm-x.com/zh-cn/products/cameras/x-t5/","description":"\u5bcc\u58ebX\u7cfb\u5217 FUJIFILM X-T5 \u5b98\u65b9\u4ea7\u54c1\u9875","image":{"@type":"ImageObject","url":"https://fujifilm-x.b-cdn.net/wp-content/uploads/2022/10/koes_x-t5_thum.jpg?width=480&amp;height=480"},"releaseDate":"2022-11-02","offers":{"@type":"https://schema.org/AggregateOffer","lowPrice":"1699","priceCurrency":"USD","availability":"https://schema.org/InStock","description":"Starting from US$1,699 (excluding VAT). Prices may vary by region.","priceSpecification":{"@type"`
- 说明: 中国频道页面仍输出 USD；页面无 CNY/RMB/人民币/¥。

### X-T5 规格页：TablePress HTML 表格，可直接解析
- URL: http://www.fujifilm-x.com/zh-cn/products/cameras/x-t5/specifications/
- HTTP: 200
- 摘录: `<table id="tablepress-x-t5_spec_zh-cn" class="tablepress ..."> <tr class="row-1"><td colspan="2" class="column-1">机型</td><td class="column-3">FUJIFILM X-T5</td></tr> ...`
- 说明: 47 个顶层规格条目；传感器/像素/卡口/连拍/视频/重量/电池均有。

### X-E5 规格页：改为 div + h6 结构，不是 table
- URL: http://www.fujifilm-x.com/zh-cn/products/cameras/x-e5/specifications/
- HTTP: 200
- 摘录: `<div class="camera-specifications__block ..."><h6>Model Name</h6></div><div class="col-span-full xs:col-span-6">FUJIFILM X-E5</div> ...`
- 说明: 46 个顶层条目；标签仍为英文（zh-cn 页面未本地化），且无顶层“连拍”字段。

### 天猫官方旗舰店：302 到登录页，匿名不可读
- URL: https://fujifilm.tmall.com/
- HTTP: 302
- 摘录: `location: https://login.taobao.com/jump?group=tao&target=https%3A%2F%2Ffujifilm.tmall.com%2Fshop%2Fview_shop.htm%3Ftbpm%3D1`
- 说明: 未跟随登录；官方授权网络店列表里“富士官方旗舰店 天猫”指向此域名。

### 京东自营 X-T5 套机 SKU：页面 200，但价格为“登录查看价格”
- URL: https://item.m.jd.com/product/100104023155.html
- HTTP: 200
- 摘录: `"priceFloor":{"priceLoginText":"登录查看价格"`
- 说明: 同页真实 price 被掩码（如 "1??90"）；未登录拿不到数值。

### 京东搜索：302 到 risk_handler（风控）
- URL: https://so.m.jd.com/ware/search.action?keyword=%E5%AF%8C%E5%A3%ABX-T5%E5%A5%97%E6%9C%BA
- HTTP: 302
- 摘录: `location: https://cfe.m.jd.com/privatedomain/risk_handler/03101900/?returnurl=...`
- 说明: 本轮唯一一次搜索请求即触发；未继续尝试。

### 京东套机 SKU 直链：302 到 risk_handler
- URL: https://item.m.jd.com/product/100038651631.html（另两个：100046206061 / 10170879177339，同样结果）
- HTTP: 302
- 摘录: `location: https://cfe.m.jd.com/privatedomain/risk_handler/03101900/?evApi=color-mesh_A_SC_mview_show&...`
- 说明: 连续 3 个套机 SKU 直链即触发；套机版本应读父商品页的 `newColorSize`，不要逐个 SKU 抓。

### 官方主图 CDN：匿名 GET 200，image/jpeg，ACAO *
- URL: https://fujifilm-x.b-cdn.net/wp-content/uploads/2022/10/koes_x-t5_thum.jpg?width=480&height=480
- HTTP: 200
- 摘录: `content-type: image/jpeg; content-length: 20886; access-control-allow-origin: *; cache-control: public, max-age=2592000`
- 说明: 480×480 缩略图；无 Referer 也可取。

### X100V 产品页：明确标记 Discontinued；规格页 301 回产品页
- URL: http://www.fujifilm-x.com/zh-cn/products/cameras/x100v/
- HTTP: 200
- 摘录: `<h1 class="support-header__name">X100V</h1><h4>Discontinued</h4> ... status-discontinued ... data-discontinued-source="child_specifications_post"`
- 说明: 产品页内嵌 tablepress-x100v_spec（45 条，英文）；/specifications/ 301 到该页。

### X100V 规格页 HTTPS 变体：Cloudflare 403 “Just a moment...”
- URL: https://www.fujifilm-x.com/zh-cn/products/cameras/x100v/specifications/
- HTTP: 403
- 摘录: `<title>Just a moment...</title>`
- 说明: 同一路径 http 返回 301→产品页；说明旧页在 CDN/WAF 侧行为不一致。

### 官方“网上商城”页：只是京东/天猫/苏宁入口，不标价
- URL: https://www.fujifilm.com.cn/cn/zh-hans/consumer/digitalcameras/e-Shop
- HTTP: 200
- 摘录: `富士数码相机网上商城，京东旗舰店、天猫旗舰店、网络经销商查证、苏宁易购旗舰店、次新品官方授权店`
- 说明: 页面是导流入口，没有商品价格；`.../digitalcameras/shop` 同样只是购买方式说明。

### 官方“授权网络店”列表：给出天猫/京东/苏宁旗舰店入口
- URL: https://sp.fujifilm.com.cn/shops/ecshop
- HTTP: 200
- 摘录: `富士京东自营旗舰店 京东商城 https://shop.m.jd.com/?shopId=1000000858 / 富士官方旗舰店 天猫商城 https://fujifilm.tmall.com/ / 富士影像旗舰店 京东商城 https://mall.jd.com/index-871329.html`
- 说明: 这是“官方旗舰店”的官方定义来源；价格仍受平台登录限制。

### 京东 X-T5 页面内嵌版本矩阵：单机身/1680/23F2/35F2/1650 套机
- URL: https://item.m.jd.com/product/100104023155.html
- HTTP: 200
- 摘录: `"salePropSeq":{"1":["银色","黑色"],"2":["X-T5 单机身","X-T5 1680套机","X-T5 23F2套机","X-T5 35F2套机","X-T5 1650套机"]}`
- 说明: 套机名只写“1680/1650”等缩写；含镜头需另做别名表。

### 页面版本/缓存信号：WordPress Last-Modified + X-Post-Shield + 7 天缓存
- URL: http://www.fujifilm-x.com/zh-cn/products/cameras/x-e5/
- HTTP: 200
- 摘录: `Last-Modified: Mon, 16 Jun 2025 03:36:40 GMT; X-Post-Shield: allowed-known-slug; Cache-Control: max-age=604800, must-revalidate; cf-cache-status: HIT`
- 说明: 无构建号；可用 Last-Modified / sitemap lastmod / 静态资源 ?ver= 监测改版。
