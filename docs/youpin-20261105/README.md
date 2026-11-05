# 有品 firstTime 与小米商城跨库映射审计

结论：接口可用，但 firstTime 不是通用产品发布日期。仅作为有品渠道上架日和 release_upper_bound。本轮 50 条固定随机样本命中 16 条（32%），低于 50% 门槛；旧款机型样本 0/11，不能声称解决 223 条旧款分类或 1,150 条日期缺口。名称搜索只能识别搜索结果覆盖的商品，不能据此宣布未命中的商品不存在。

## 真实请求复现

Chrome 157 无登录新 context 打开 `https://www.xiaomiyoupin.com/detail?gid=156975`，捕获 POST `https://www.xiaomiyoupin.com/api/gateway/detail`。原请求和完整返回见 raw/browser-156975.json；curl 完整返回见 raw/curl-156975.json，29,568 字节，两者 name、firstTime 一致。

```bash
curl -sS -X POST 'https://www.xiaomiyoupin.com/api/gateway/detail' \
 -H 'content-type: application/json' \
 -H 'X-Yp-App-Source: front-PC' \
 -H 'X-User-Agent: channel/youpin platform/youpin.pc' \
 -d '{"groupName":"details","groupParams":[["156975"]],"pid":"","methods":[],"version":"1.0.0","debug":false,"channel":"","vipMode":false,"system":"3"}'
```

关键返回：`data.goods.goodsInfo.name=米家负离子吹风机 H301`，`firstTime=1667268001`（Asia/Shanghai **2022-11-01 10:00:01**），`ctime=1667209064`（2022-10-31 17:37:44），`scheduleOnSaleTime=1667268000`。三个分类为家用电器/个护健康/电吹风，brandName=小米自营产品，pids=402089/402090，img800 有官方图。

cookie：浏览器自行生成匿名统计/session cookie；curl 与 Python 均不发送 cookie，不使用账户。DToken 在浏览器中为空；脚本不发送它也成功。请求 URL/body 不含签名，不需要登录。brand.jumpURL 里的 sign 是另一个落地链接参数，不是 detail 请求的签名。

限流：229 个缓存下来的匿名搜索/详情请求均 HTTP 200、业务 code=0；每请求后暂停 0.7 秒，搜索/语义两组进程曾并发。未做高频压力测试，**未观察到限流不代表没有频率限制**；真实阈值未知。HTTP/业务错误不得降格为“无商品”。

浏览器复现：`YOUPIN_PLAYWRIGHT_MODULE=/path/to/playwright-core node scripts/capture_youpin.cjs capture.json`。运行时依赖仅用于可选取证，不改变标准库采集约定。

## firstTime：20 条官方证据

完整对照：[20 条证据表](semantics-table.md)，包括 firstTime CST、官方发布日、差值、与 scheduleOnSaleTime/ctime 的差。逐项新闻稿原句、定位、原有官方抓取文件和 SHA-256 在 semantics-reviewed.json。均为中国发布事件的小米官方新闻稿/投资者材料；没有把媒体报道当官方新闻稿。

19/20 与发布会同日，但 Xiaomi Sound 音箱（gid=161384）为 2023-09-14，比官方 2021-08-10 晚 **765 天**。该样本证明跨渠道重建商品/晚入驻时不能由 firstTime 还原产品首发。它不是 ctime：20 条的 firstTime 均晚于 ctime，差值从小时到十余天。scheduleOnSaleTime 部分缺失；Xiaomi 17 Ultra 的 schedule 晚于 firstTime 约277天，说明该计划字段也不是稳定首发时间。

语义结论是基于字段关系与反例的推断，未取得有品字段契约来证明“不可重置的首次开售”。故不向所有映射记录泛化 19/20 的同日关系。逐条通过对照的19条符合用户14天容差，但已有更直接官方发布证据，无需用上架日替换。20条样本按可取得的官方材料和精确型号选择，偏重发布会产品，不能外推长尾准确率。Pad 8 依据官方稿明确列出的系列成员，另外4条仅接受无版本差异的品类后缀（音箱/手表/平板电脑），不将容量、颜色、Pro等变体随意归并。

## product_id → gid

- 小米商城 product_id 与有品 gid 不是同一命名空间。H301 为 product_id=16725、商城 gid=2221501323、有品 gid=156975、pid=402089/402090、skuId=43906/43904。原 gid 完整保留，新字段叫 youpin_gid。
- H301 detail 没有 productId/miProductId 直接桥接字段；小米商城 product/view 与购买页也未得到可用的反向有品链接（保存 raw/mi-view-16725.json、raw/mi-page-16725.html）。这是本次实测范围的未取得，非所有页面绝不提供。
- 浏览器捕获的匿名搜索 POST `/mtop/market/search/v2/doSearch` 用 `[{}, {query:[{queryName:型号,queryType:0,rule:[]}], ...}]`。完整请求/响应见 raw/browser-search.json 及逐查询压缩证据。
- 固定种子 156975，从 data 956252e1 快照1583条小米 product 行（按id排序）简单随机抽50条，保留容量/型号/套餐/年份；只做 NFKC、casefold、去空白的精确名称匹配。仅首20条搜索结果中的唯一gid才进入详情核验；详情品牌须明确小米自营/小米/米家。同名多gid（如米家工具箱）拒绝自动选。
- [50 条映射表](mapping-table.md)与 mapping-50.json 给出所有命中和未命中，16/50=32%，无请求错误；旧款样本0/11。它是此保守映射方法的实际产出率，不是网站潜在可映射率。不能把匹配名和搜索返回当外部ID的直接关联字段。
- 当前仅纳入17个核验过的小米自营商品（16样本+用户H301对照），不把第三方品牌并入小米。用户允许的生态链扩充须另有官方关系证据，不能仅因在有品售卖就认定生态链。

## 落地与覆盖率

`data/official/youpin-crosswalk.json` → `goodsdex.youpin.apply_youpin` → 共享finalizer重放。17条保存 youpin_gid、三级分类、官方图、SKU属性、渠道价格与上架时间/上界，不造重复商品、不改原商城gid。旧桶可按映射三级分类修复，缺图可补；本次17条均已有非旧桶分类和主图，实际修正/补图均为0。

SKU价格按分转元。H301 `productInfo.price=19900`（接口基础标价199元），`priceInfo.singlePrice=12500`且promotionType=PriceReduce，因此渠道offer记125元、price_kind=promotion，基础标价单独保留。SKU onSale=false 时保留 not_on_sale，不伪装成可购买报价。不覆盖商城原价或促销语义，不把 marketPrice 叫常规成交价。

实际增量见 impact.json：上架日及日期上界17，新增 release **0**、分类修正 **0**、主图补齐 **0**。上界不计发布日期覆盖率。按题述相同口径，这条线的影响是 **43.97% → 43.97%（+0个百分点）**。32%低于用户指定50%估算门槛，不以1150×32%推算补日期数；发布日期可新增量当前证据支持为0。

注意版本：本次抓取 data c1c2abde 的 meta.release_scope 是旧统计（3605发布行/3114整机，小米1368整机缺1001），与题述1150和43.97%不相同；baseline-meta.json/current-meta.json 原样保存以免混用。最终发布验收会另存最新revision与正式服务统计，任何其他已合并代码带来的变化不算本轮收益。

证据存储：raw/*.json.gz 包含完整JSON返回和请求体；sha256为当时HTTP响应字节摘要，response_json_sha256为保留JSON的可复验规范化摘要，二者不混淆。正式数据清单使用后者校验；首个curl原始字节另原样保留。

验证：独立工作树基于 origin/main 8d6c6aba，离线全量 **1026 passed / 8 deselected / 0 failed**；8项为原有live标记，不增加跳过。原共享工作区初始941项通过；整合后快照预期需显式加入新的重放步骤，且新证据测试修正了真实响应 singlePrice=null 的空值处理，最终最新主线全量通过。正式发布回执另见 publication.json。
