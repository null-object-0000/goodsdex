# 证据目录：富士相机公开页调研（2026-10-27）

## 口径

- 只访问公开页面/公开接口；不登录、不绕验证码、不逆向 App、不伪造签名。
- 正式取证阶段同一 host 串行、并发 1；脚本强制相邻请求间隔 ≥2.15 秒（日志时间戳为秒级，显示 2 秒是截断）。
- 总请求 **约 113 次**（≤200）：日志记录 96 次 + 建立日志前的首轮侦察 14 次 + 补充核验 3 次；日志窗口 2026-10-27 19:52:52–20:07:23（CST）。首轮侦察未套用限速脚本（首页/robots 曾连续 2 次），发现后立即改为脚本限速；补充核验 3 次按 2.2 秒间隔执行。
- 只保留状态码、字节数、content-type、最终 URL 与短摘录；**不在本目录放整页 HTML，也不放图片本体**。
- 请求日志不含 Cookie、Authorization、UA 全文；URL 里的 keyword 为公开搜索词。

## 状态分布（仅日志内 96 次）

| HTTP | 次数 | 说明 |
|---|---:|---|
| 200 | 70 | 官网系列页/规格页/产品页、京东商品页、图片 CDN |
| 302 | 20 | 天猫登录跳转、京东 risk_handler（搜索 1 次 + 套机 SKU 直链 3 次）、京东部分失效 SKU、站点跳转 |
| 301 | 4 | `fujifilm-x.com` 顶点域 → `http://www...`；X100V 规格页 → 产品页 |
| 403 | 1 | X100V 规格页的 HTTPS 变体触发 Cloudflare `Just a moment...` |
| 28 (curl) | 1 | `p.3.cn` 价格接口超时；未重试 |

未出现 429 / 412；没有触发验证码，也没有尝试绕过。

## 失败与限制（必须连同结论一起看）

1. **天猫官方旗舰店**：`https://fujifilm.tmall.com/` → 302 到 `login.taobao.com`，匿名不可读；未跟随登录。
2. **京东价格**：商品页 200，但页面内 `priceLoginText` 为“登录查看价格”，价格字段被掩码（如 `1??90`）；未登录拿不到数值。
3. **京东搜索**：一次搜索即 302 到 `cfe.m.jd.com/.../risk_handler/`，判定为风控；立即停止，未再试。
4. **京东套机 SKU 直链**：对 `100038651631` / `100046206061` / `10170879177339` 三个套机 SKU 直链连续请求，均 302 到 `risk_handler`（`evApi=color-mesh_A_SC_mview_show`）；套机信息应读父商品页的版本矩阵。
5. **京东 PC 商品页**：返回 SPA 空壳（35KB，正文无商品数据）；移动页 `item.m.jd.com` 才有服务端渲染内容。
6. **X100V**：规格页 301 回产品页；产品页标记 `Discontinued`，规格表内嵌在产品页（英文，45 条）。
7. **`p.3.cn` 价格接口**：30 秒超时（curl 28），未重试；不作为价格证据。
8. **ZOL 搜索**：返回 GBK 页面且结果与关键词不匹配，未采用其价格。
9. **HTTPS 顶点域**：`https://fujifilm-x.com/...` 301 到 `http://www.fujifilm-x.com/...`（协议降级），不是正常 canonical 行为。

## 文件

| 文件 | 内容 |
|---|---|
| `requests.tsv` | 日志建立后的 96 次请求（首轮 14 次 + 补充 3 次未入表，见上）（时间/标签/URL/状态/字节/content-type/最终 URL/错误） |
| `snippets.md` | 19 条关键摘录：robots、sitemap、系列页、JSON-LD、两种规格结构、天猫/京东价格门、风控、图片头、X100V 停产、版本头 |
| `samples.csv` | 抽样 18 行：9 机身 + 6 套机 + 3 固定镜头，含参数条数、字段命中、价格来源、URL |
| `kits.csv` | 实测 13 种套机版本（5 条机身线），含镜头归一与示例 SKU |
| `spec-fields.csv` | 12 个型号的规格条目数、HTML 形态、8 个关键字段命中/缺失、关键值 |
| `official-models.csv` | 官网 13 个在列型号、当前/旧款状态、releaseDate、USD 参考价 |

## 复跑提示

- 官网系列页：`https://www.fujifilm.com.cn/cn/zh-hans/consumer/digitalcameras/X`
- 规格页：`http://www.fujifilm-x.com/zh-cn/products/cameras/<slug>/specifications/`（必须 `http://www`，不要用 HTTPS 顶点域）
- 官方授权网络店：`https://sp.fujifilm.com.cn/shops/ecshop`
- 京东自营店：`https://mall.jd.com/index-1000000858.html`；商品页用 `https://item.m.jd.com/product/<sku>.html`，套机读父页 `newColorSize`，**不要逐个套机 SKU 直链**
- 按本目录 `requests.tsv` 的时序复跑；不要并发，不要碰搜索/登录。
