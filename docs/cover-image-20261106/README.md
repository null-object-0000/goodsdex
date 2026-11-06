# 商品封面审计与修复（2026-11-06）

后续已按产品要求调整为 **米家 realIcon → 商城主图 → 原图**。本页保留 `2c1097b7` 的历史审计；当前规则、五条抽样与最终 URL 见 [realIcon 优先审计](realicon/README.md)。

本次仅在本地修改并提交，未 push、部署或触发 workflow。公开线上数据未改动。基线来自已存在的 `origin/data` 快照 `9d7971f5505c3325f5d616199491ed8342cd7f69`，原始 goods.json SHA-256 为 `e4124c656849aeff2563c715a993cd8e8e3e98f8fc80d66c987b80667ab9877c`。

## 判据与分布

“营销图”仅是疑似指标：图片非 1:1，或与同 id 的 mtop `goodsList[0].imgUrl` 不同，取并集；不是 OCR/视觉确认。另统计 jpg 且 `max(w,h)/min(w,h)>1.05`，它是非 1:1 的子集。计数按商品行，不按唯一 URL；小米 1,550 行包含 1,545 个唯一 product id。尺寸失败、无图不会算成正常图片。

| 指标 | 全库改前 | 本地候选改后 | 小米改前 | 小米改后 |
|---|---:|---:|---:|---:|
| 商品行数 | 4491 | 4491 | 1550 | 1550 |
| 正方形 | 2067 | 2083 | 1163 | 1179 |
| 非正方形 | 915 | 902 | 97 | 84 |
| jpg 比例 >1.05 | 326 | 313 | 71 | 58 |
| mtop 同 id 主图不同 | 37 | 0 | 37 | 0 |
| 疑似营销图并集 | **939** | **902** | **121** | **84** |
| 无图 | 1221 | 1221 | 165 | 165 |
| 图片尺寸未验证 | 288 | 285 | 125 | 122 |

1,545 个唯一小米 id：1,262 个返回主图；278 个返回已下架；5 个请求异常，**未验证**。没有主图的均标 `image_status: official_unavailable`，已有图仅作为回退保存。剩余 84 条小米非方图不借其他型号替换，不能断言其全是营销海报。非小米记录完全不变；所有非 `image*` 字段逐条相等，包括价格、release 和门禁证据。

## 两件商品

- 20833（米家智能宠物饮水机 2）：https://cdn.cnbj1.fds.api.mi-img.com/nr-pub/202412131023_424a80fba7a3ba0d83e866e8f0008bd3.png
- 21630（小米无线键鼠套装 舒适版）：https://cdn.cnbj1.fds.api.mi-img.com/nr-pub/202507221658_b76557cd46bf30d480870a4ced4d5d61.png

两张均已实际下载、解码并查看，800×800，无场景与营销文案。原始文件为 `20833.png` / `21630.png`；浏览器截图见 [official-main-images.png](official-main-images.png)，截图以原图字节在白底页面显示。未做 CDN → OSS 替换。

## 证据与重放

- `report.json`：前后分布与不变性校验。
- `dimensions-before.json` / `dimensions-after.json`：逐 URL 尺寸/失败原因。
- `mtop-images.json`：逐完整商品 id 的接口结果、时间与错误。
- `cover-changes.json.gz`：所有变更的 image 字段前后对照。
- `data/official/xiaomi-cover-images.json`：用于旧记录发布时重放的同 id 官方主图证据，不改 supplements。
- 本地完整候选为忽略目录 `public/goods.json`，未发布；可按以下命令重建。

```sh
git show 9d7971f5505c3325f5d616199491ed8342cd7f69:public/goods.json.gz > /tmp/cover-input.json.gz
python scripts/audit_xiaomi_covers.py --input /tmp/cover-input.json.gz --out docs/cover-image-20261106 --reuse --baseline-revision 9d7971f5505c3325f5d616199491ed8342cd7f69 --output public/goods.json
```

审计脚本使用 Pillow 解码尺寸（采集/发布运行时代码仍只用标准库）。去掉 `--reuse` 可重新网络审计。写入官方重放证据需显式指定 `--write-evidence data/official/xiaomi-cover-images.json`。脚本只写本地文件，不发布。

采集新增独立 mtop 主图请求并保存请求/响应证据，发布优先新采集断言、其次已保存的同 id 官方证据、最后原 `view.values.img_url`。普通 finalizer 重放图片证据；专门的其他来源限定发布模式保持原有范围。

## 验证

Python 全量回归 1,126 项通过。包括真实 finalizer 的首次执行与重复执行、既有 release/series/date 断言、分片输出，以及新增封面选择/失败回退/非小米不变测试。release 期望只增加独立封面重放步骤，未删除或放宽原有逐字段比较与日期断言。客户端另有 22 项相关测试通过，并实际运行 Chrome H5 列表刷新、详情离线保留封面场景。线上联调与微信真机：未验证。
