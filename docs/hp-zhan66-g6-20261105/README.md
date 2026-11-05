# 战66六代检索：官方配置补充与候选验收

本轮完成官方货号和配置补证、候选筛选及发布；**没有宣称完成战66六代全部营销SKU的确认**。HP公开支持站/零件库只明示ProBook平台与G10代际，未取得这些货号与“战66六代”的SKU级官方映射，亦未明示120Hz。不能把ProBook G10批量改名成战66六代。

## 实际数据变更

HP 790 → 791；新增货号 **7Z8L4PC**。目标 **7P2D5PC** 原已存在，名称为HP支持站原文，不另造重复SKU。本轮为112条官方ProBook G10配置补齐零件库明示的屏幕和存储；111条原SKU + 1条新SKU。系列级14英寸记录完整保留，不改名、不改尺寸。新增记录与112条完整记录见new-records.json / configurations.json。

新增记录：
```json
[
 {
  "part_number": "7Z8L4PC",
  "name": "HP PB450G10 i5-1335U 15 32GB/1T PC (7Z8L4PC)",
  "series": "ProBook",
  "generation": "G10",
  "status": "retired",
  "source_url": "https://support.hp.com/cn-zh/product/troubleshooting/hp-probook-450-15.6-inch-g10-notebook-pc/model/2101593796?sku=7Z8L4PC",
  "params": {
   "产品编号": "7Z8L4PC",
   "型号": "HP ProBook 450 15.6 英寸 G10 笔记本电脑",
   "官方配置标识": "32GB/1T",
   "source_specs": {
    "productName": "HP PB450G10 i5-1335U 15 32GB/1T PC (7Z8L4PC)",
    "productSeriesName": "HP ProBook 450 15.6 英寸 G10 笔记本电脑",
    "productPlatform": "Roc15",
    "productType": "Laptops and Hybrids"
   },
   "CPU型号": "i5-1335U",
   "运行内存": "32GB",
   "屏幕尺寸": "15.6英寸",
   "variant_attrs": {
    "dimensionEdition": {
     "value": "7Z8L4PC",
     "label": "7Z8L4PC"
    }
   },
   "屏幕规格": "QHD",
   "存储容量": "1TB"
  }
 }
]
```

所有配置沿用支持站productNumber/productName、source_url、series=ProBook、generation=G10。状态均retired：它们不在已完整核验的3份官方商城sitemap现售目录中；retired_at为首次观察缺席时间，非停产日期。零件清单不提供销售状态，不用零件库在场推翻商城退出留档。

## 官方证据与边界

- HP支持接口逐号验证productNumber与productName；旧570个响应见../hp-history-20261105/support-evidence.json.gz，新货号见support/7Z8L4PC.json。
- PartSurfer公开网页 https://partsurfer.hp.com/?searchtext=7P2D5PC&searchby=product 。112个原响应在parts-evidence.json.gz，每个带请求URL、采集时间、HTTP状态和SHA256；每一条Body.ProductNumber必须与支持站货号一致。
- 精确SKU零件清单中7P2D5PC的N44345-001为`SPS-RAW PANEL 15.6 QHD AG UWVA 300`，支持站名称明示i7-1360P、32GB/1T；硬盘清单也明示1TB。QHD保留官方缩写，不凭第三方补2560×1440或120Hz。
- 9T0Q0PC同为i7-1360P/32GB/1T，但N43570-001是`SPS-RAW PANEL 15.6FHD AG UWVA250`，必须排除。摄像头边框文字中的FHD不算屏幕规格。
- 官方商城文章 https://www.hpstore.cn/blog/post/高原雨雪冰雹没难住惠普战66，甘南苦旅变成开心交友 确认“15英寸惠普战66六代酷睿版2.5K屏版”；原文留在../hp-history-20261105/responses/blog-1.html.gz。它只证明有该系列版本，未给唯一货号。
- **不能写“官方无15.6寸六代”**：已取得官方15英寸六代2.5K版本描述。16英寸六代没有取得官方货号；这不是官方宣告不存在。48个请求配置组合逐项缺号原因见coverage-and-missing.json，缺号组合不造商品记录。
- 中国商城旧详情地址跳转首页；公开搜索没有提供该货号商品详情；REST为401、GraphQL为403。见store-probes.json及压缩原文。没有将这些访问限制说成官方不存在，也没有使用惠普社区用户发言作为厂家规格或营销映射。
- 京东标题仅作为查询输入；京东货号、价格6799、屏幕参数都未进入官方字段。

## 按尺寸/配置统计

以下是已核验官方平台的112条配置，**不是已确认的战66六代SKU总数**。请求中的营销身份与平台对应仍有缺口。14英寸67条、15.6英寸45条、16英寸0条；FHD88、QHD20、HD4。i3/锐龙等实际存在的配置也如实列出，不用它们冒充i5/i7组合。

|尺寸|CPU|内存|存储|屏幕|货号条数|
|---|---|---|---|---|---:|
|14英寸|R5-7530U|16GB|1TB|FHD|1|
|14英寸|R5-7530U|16GB|512GB|FHD|5|
|14英寸|R5-7530U|32GB|1TB|FHD|1|
|14英寸|R5-7530U|32GB|512GB|FHD|2|
|14英寸|R7-7730U|16GB|1TB|FHD|1|
|14英寸|R7-7730U|16GB|512GB|FHD|3|
|14英寸|R7-7730U|32GB|1TB|FHD|1|
|14英寸|R7-7730U|32GB|512GB|FHD|1|
|14英寸|i3-1315U|8GB|256GB|FHD|2|
|14英寸|i5-1334U|16GB|512GB|FHD|1|
|14英寸|i5-1334U|16GB|未明示|FHD|1|
|14英寸|i5-1335U|16GB|1TB|FHD|2|
|14英寸|i5-1335U|16GB|1TB|HD|1|
|14英寸|i5-1335U|16GB|256GB|FHD|1|
|14英寸|i5-1335U|16GB|512GB|FHD|5|
|14英寸|i5-1335U|32GB|1TB|FHD|1|
|14英寸|i5-1335U|32GB|512GB|FHD|1|
|14英寸|i5-1335U|8GB|512GB|HD|1|
|14英寸|i5-1340P|16GB|1TB|FHD|5|
|14英寸|i5-1340P|16GB|512GB|FHD|6|
|14英寸|i5-1340P|32GB|1TB|FHD|2|
|14英寸|i5-1340P|32GB|512GB|FHD|1|
|14英寸|i5-1345U|16GB|512GB|FHD|3|
|14英寸|i5-1345U|16GB|512GB|HD|1|
|14英寸|i5-1345U|8GB|512GB|FHD|1|
|14英寸|i7-1355U|16GB|1TB|FHD|3|
|14英寸|i7-1355U|16GB|512GB|FHD|3|
|14英寸|i7-1355U|16GB|未明示|FHD|1|
|14英寸|i7-1355U|32GB|1TB|FHD|1|
|14英寸|i7-1355U|32GB|512GB|FHD|1|
|14英寸|i7-1355U|32GB|512GB|HD|1|
|14英寸|i7-1360P|16GB|1TB|FHD|1|
|14英寸|i7-1360P|16GB|512GB|FHD|1|
|14英寸|i7-1360P|32GB|1TB|FHD|1|
|14英寸|i7-1360P|32GB|512GB|FHD|1|
|14英寸|未明示|未明示|512GB|FHD|3|
|15.6英寸|R5-7530U|16GB|1TB|FHD|1|
|15.6英寸|R5-7530U|16GB|512GB|FHD|2|
|15.6英寸|R5-7530U|32GB|1TB|FHD|1|
|15.6英寸|R5-7530U|32GB|512GB|FHD|1|
|15.6英寸|R7-7730U|16GB|1TB|FHD|1|
|15.6英寸|R7-7730U|16GB|512GB|FHD|3|
|15.6英寸|R7-7730U|32GB|1TB|FHD|1|
|15.6英寸|i5-1335U|16GB|1TB|FHD|1|
|15.6英寸|i5-1335U|16GB|1TB|QHD|1|
|15.6英寸|i5-1335U|16GB|512GB|FHD|1|
|15.6英寸|i5-1335U|16GB|512GB|QHD|1|
|15.6英寸|i5-1335U|32GB|1TB|FHD|1|
|15.6英寸|i5-1335U|32GB|1TB|QHD|2|
|15.6英寸|i5-1335U|32GB|512GB|QHD|1|
|15.6英寸|i5-1340P|16GB|1TB|FHD|2|
|15.6英寸|i5-1340P|16GB|1TB|QHD|2|
|15.6英寸|i5-1340P|16GB|512GB|FHD|2|
|15.6英寸|i5-1340P|16GB|512GB|QHD|1|
|15.6英寸|i5-1340P|16GB|未明示|FHD|1|
|15.6英寸|i5-1340P|16GB|未明示|QHD|1|
|15.6英寸|i5-1340P|32GB|1TB|FHD|1|
|15.6英寸|i5-1340P|32GB|1TB|QHD|2|
|15.6英寸|i5-1340P|32GB|未明示|FHD|1|
|15.6英寸|i5-1340P|32GB|未明示|QHD|1|
|15.6英寸|i5-1340P|8GB|512GB|FHD|1|
|15.6英寸|i7-1355U|16GB|1TB|QHD|1|
|15.6英寸|i7-1355U|16GB|512GB|FHD|1|
|15.6英寸|i7-1355U|16GB|512GB|QHD|1|
|15.6英寸|i7-1355U|32GB|1TB|FHD|1|
|15.6英寸|i7-1355U|32GB|1TB|QHD|1|
|15.6英寸|i7-1355U|32GB|512GB|QHD|1|
|15.6英寸|i7-1360P|16GB|1TB|QHD|1|
|15.6英寸|i7-1360P|16GB|512GB|FHD|1|
|15.6英寸|i7-1360P|16GB|512GB|QHD|1|
|15.6英寸|i7-1360P|32GB|1TB|FHD|1|
|15.6英寸|i7-1360P|32GB|1TB|QHD|1|
|15.6英寸|i7-1360P|32GB|512GB|QHD|1|

## 原文标题的真实匹配入口

原文：`惠普（HP）战66 六代酷睿 15.6 英寸 i7-13代 32G 1T 2.5K 120Hz`。服务已有入口是GET /api/goods/match（并未提供POST）；按请求许可使用后台既有匹配入口。修前是正式服务原始响应，修后本地实际HTTP请求使用完整3682条候选库；发布后另留match-after-online.json。

修前（完整JSON）：
```json
{
 "ok": true,
 "match": null,
 "candidates": [
  {
   "product_id": "CN:mi_cn:product:7438",
   "display_name": "13.3\"笔记本 八代四核i7 深空灰",
   "price_from": null,
   "image": null,
   "score": 0.72
  },
  {
   "product_id": "CN:mi_cn:product:7866",
   "display_name": "13.3\"笔记本 四核i7 8G 256G MX150",
   "price_from": null,
   "image": null,
   "score": 0.72
  },
  {
   "product_id": "CN:mi_cn:product:8648",
   "display_name": "15.6\"游戏本 8代i7 16G 1060",
   "price_from": null,
   "image": null,
   "score": 0.72
  }
 ],
 "matchReason": "没有唯一且身份一致的库内商品"
}
```

修后（完整JSON，含规则输出）：
```json
{
 "ok": true,
 "match": null,
 "candidates": [
  {
   "product_id": "CN:hp_cn:sku:7P211PC",
   "sku_id": "CN:hp_cn:sku:7P211PC",
   "part_number": "7P211PC",
   "display_name": "HP PB450G10 i7-1355U 15 32GB/1T PC (7P211PC)",
   "price_from": null,
   "image": null,
   "score": 0.9,
   "rules": [
    {
     "field": "part_number",
     "value": "7P211PC",
     "source": "HP Support productNumber",
     "exact": false
    },
    {
     "field": "size",
     "value": 15.6,
     "source": "HP Support productSeriesName"
    },
    {
     "field": "cpu",
     "value": "i7-1355U",
     "source": "HP Support productName"
    },
    {
     "field": "memory_gb",
     "value": 32,
     "source": "HP Support productName"
    },
    {
     "field": "storage_gb",
     "value": 1024,
     "source": "HP PartSurfer exact ProductNumber"
    },
    {
     "field": "display",
     "value": "QHD",
     "source": "HP PartSurfer exact ProductNumber"
    }
   ],
   "unresolved": [
    "战66六代营销名称与该货号的官方映射未取得",
    "120Hz未在官方SKU配置或零件清单中明示"
   ],
   "source_url": "https://support.hp.com/cn-zh/product/troubleshooting/hp-probook-450-15.6-inch-g10-notebook-pc/model/2101593797?sku=7P211PC",
   "evidence": {
    "support_url": "https://support.hp.com/wcc-services/profile/devices/warranty/specs?cache=true",
    "support_sha256": "4393a05fc537c9ba814bb18eb71f9b29e8fa2271434127258c61f8eef244ad40",
    "parts_url": "https://partsurfer.hpcloud.hp.com/bff/proxy/get?input=/Product/GetProduct/7P211PC/country/US/usertype/EXT",
    "parts_sha256": "7a54425c9e4f87d588ce3c67f483b5984f3d124b4f2d84ffb060c77f9c77d579"
   }
  },
  {
   "product_id": "CN:hp_cn:sku:7P2D5PC",
   "sku_id": "CN:hp_cn:sku:7P2D5PC",
   "part_number": "7P2D5PC",
   "display_name": "HP PB450G10 i7-1360P 15 32GB/1T PC (7P2D5PC)",
   "price_from": null,
   "image": null,
   "score": 0.9,
   "rules": [
    {
     "field": "part_number",
     "value": "7P2D5PC",
     "source": "HP Support productNumber",
     "exact": false
    },
    {
     "field": "size",
     "value": 15.6,
     "source": "HP Support productSeriesName"
    },
    {
     "field": "cpu",
     "value": "i7-1360P",
     "source": "HP Support productName"
    },
    {
     "field": "memory_gb",
     "value": 32,
     "source": "HP Support productName"
    },
    {
     "field": "storage_gb",
     "value": 1024,
     "source": "HP PartSurfer exact ProductNumber"
    },
    {
     "field": "display",
     "value": "QHD",
     "source": "HP PartSurfer exact ProductNumber"
    }
   ],
   "unresolved": [
    "战66六代营销名称与该货号的官方映射未取得",
    "120Hz未在官方SKU配置或零件清单中明示"
   ],
   "source_url": "https://support.hp.com/cn-zh/product/troubleshooting/hp-probook-450-15.6-inch-g10-notebook-pc/model/2101593804?sku=7P2D5PC",
   "evidence": {
    "support_url": "https://support.hp.com/wcc-services/profile/devices/warranty/specs?cache=true",
    "support_sha256": "47236ff9848b92337acbc2ae691bbc0fbdb969bef6a7fe029c9ff497340480cb",
    "parts_url": "https://partsurfer.hpcloud.hp.com/bff/proxy/get?input=/Product/GetProduct/7P2D5PC/country/US/usertype/EXT",
    "parts_sha256": "76848a3c760f220fcddfc20c7df01a2a0ef86c98d255c4bdbc6a5726f41ec864"
   }
  }
 ],
 "candidateCount": 2,
 "candidatesTruncated": false,
 "matchReason": "官方平台配置候选；缺少战66六代货号映射，不能唯一确认，请按机身货号选择"
}
```

两候选：7P211PC是i7-1355U，零件清单主板含RTX2050；7P2D5PC是i7-1360P、UMA主板。原文仅i7-13代，不能从这一点排除任一。两条均32GB、1TB、15.6英寸、QHD；用户应核对机身货号选择。

分数是规则得分，不是概率：官方品牌/货号记录基础0.10 + 尺寸0.20 + CPU级别/代际0.20 + 内存0.15 + 存储0.15 + 屏幕0.10 = **0.90**。输入未给货号，所以货号exact=false；只用货号验证候选来源，未假称货号命中。营销映射及120Hz缺证独立阻止自动命中，即使配置筛到一条也保留match=null。全程不修改身份一致阈值。

## 验证与发布

测试、提交号、构建/发布run和线上读回见publication.md。原工作区与独立发布工作树均验证；原有live/集成跳过保持不变。

```bash
python3 scripts/build_hp_configurations.py --captures docs/hp-zhan66-g6-20261105/parts-evidence.json.gz
PYTHONPATH=src python3 -m pytest -q -m "not live"
node docs/hp-zhan66-g6-20261105/match-local.mjs /path/to/spend-good/services/api /path/to/goods.json
```
