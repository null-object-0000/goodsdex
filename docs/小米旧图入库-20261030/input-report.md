# 小米停售款商品图补齐（169 条）

- 生成时间：2026-10-30T21:17:37+08:00
- 范围：`public/goods.json` 中小米 `model_reference` 且 `image=null` 的 169 条（170 条小米历史参考中 169 条缺图，1 条已有图）
- 结果：**命中 126 / 169 = 74.6%**；缺失 43 条
- 口径：全量 169 条逐一尝试，不是抽样；每张入选图都在本轮真实 GET 验证。

## 方法

1. 用 `data/archive-history/<pid>.json` 的 `official_specs_url` 还原官方商品页 slug（如 `redmi4`、`mix2s`），再用页面标题与目标名做身份核对。
2. 抓官方商品页、图集页、参数页的产品专属 CSS/HTML 图 URL；只取路径属于该产品目录的图，排除全站导航/图标/占位图。
3. 对能在 Wayback 找到的 `api.order.mi.com/product/get?product_id=...` JSONP 响应，解析 `goods.image/images`，优先使用 800×800 白底图。
4. 每张候选图 GET 校验：HTTP 200、`content-type: image/*`、字节数 >30KB、宽度 ≥600px；并采样边框判断白底/透明/浅底/场景。
5. 人工目检 165 张候选缩略图，剔除“只有场景/人物/屏幕内容/文字表”的 39 条，不拿别的型号或非商品图充数。

## 命中与尺寸

- 命中 **126** 条，缺失 **43** 条，命中率 **74.6%**（全量口径）。
- 宽度分布：600–799 13，800–1023 17，1024–1599 36，1600+ 60
- 字节分布：30–50KB 8，50–100KB 24，100–300KB 65，300KB+ 29
- 最小宽度 602px；最小字节 30759B。

## 白底 / 透明 / 场景

| 类型 | 数量 | 说明 |
|---|---:|---|
| 白底 | 34 | 边框近白、白色占比 ≥0.35，可直接用于列表 |
| 透明底 | 33 | PNG 带 alpha，列表用建议压到白底 |
| 浅底 | 17 | 边框浅色但不是纯白 |
| 场景/深色底 | 42 | 商品可见，但需要裁切或换背景才适合列表 |

> 二次处理建议：34 张白底可直接用；33 张透明底需 flatten 到白底；59 张浅底/场景图建议人工确认后再做抠图或裁切。

## 图源与主机

| 来源 | 数量 |
|---|---:|
| `live_official_page` | 122 |
| `wayback_api_product_get` | 4 |

| 主机 | 数量 |
|---|---:|
| `c1.mifile.cn` | 100 |
| `i1.mifile.cn` | 22 |
| `i8.mifile.cn` | 4 |

## 一图多 pid（必须注意）

共 6 组图被多个 pid 复用，已在 `candidates.json` 的 `shared_with` 标出：

| 图片 | pid |
|---|---|
| `https://i1.mifile.cn/f/i/2018/mipad4p/index_battery.jpg` | 10000108, 8385, 8387, 8388 |
| `https://c1.mifile.cn/f/i/16/chain/max2/max2-03-phone.png?v1` | 10000057, 5780, 5781 |
| `https://c1.mifile.cn/f/i/16/chain/plateshoes/mj-plateshoes-03-1.jpg` | 10000067, 6518 |
| `https://i1.mifile.cn/f/i/17/mix2/index-gallery-01.jpg` | 10000070, 7154 |
| `https://i1.mifile.cn/f/i/18/mibookair/13/index_fun_list3.jpg` | 10000082, 7440 |
| `https://c1.mifile.cn/f/i/16/chain/mivr-1o/mivr-1o-07.jpg` | 10000101, 8202 |

这些多为同系列/同型号不同容量或配色（如小米平板4 容量版、红米5/5 Plus、MIX 2 皓月白），**不能当成单品独占图**。

## 缺失原因

| 原因 | 数量 | 说明 |
|---|---:|---|
| `no_official_product_page` | 4 | 官方商品页/规格页不存在，未找到可归属的商品页 |
| `only_scene_or_people` | 15 | 官方页只有场景图/人物图，图中商品不可辨识或无完整商品 |
| `only_screen_content` | 15 | 官方页只有屏幕内容/壁纸，未出现电视机身或完整产品 |
| `only_diagram_or_text` | 6 | 官方页只有示意图/文字表/图标，非商品图 |
| `partial_product_only` | 2 | 仅有局部特写（边缘/表带），不能作为列表商品图 |
| `packaging_only` | 1 | 只有包装盒图，未出现商品本体 |

缺失 pid 详见 `missing.json`。其中 4 条没有官方商品页；其余是官方页只有场景/人物/屏幕内容/示意图，按“拿不到写拿不到”处理，没有用别的型号图片顶替。

## 合规说明

- 只读：未写 `public/`，未下载图片进仓库，未提交/推送分支；图片仅保留 URL、字节数与尺寸校验结果。
- 限速：对同一 host 的请求间隔 ≥2.1 秒；Wayback 请求间隔 ≥2.3 秒，本轮未触发 429。
- 身份：所有命中项都来自该 pid 对应的官方商品页/参数页或该 pid 的归档 `product/get` JSON；页面标题与目标名做过核对。
- 复用：同一 URL 被多个 pid 使用时已在 `shared_with` 标出，不视为独立单品图。

## 文件

- `candidates.json`：126 条命中，含 pid、URL、host、HTTP 状态、字节、宽高、来源、归档时间戳、背景类型、复用标记。
- `missing.json`：43 条未命中及原因。
- `report.md`：本文件。
