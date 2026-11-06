# 米家 realIcon 优先（2026-11-06）

在 `2c1097b7` 上只调整小米 `CN:mi_cn:product:<数字>` 的图片选择。顺序为：记录有 `miio_model` 且同型号百科 `data.realIcon` 可用 → 原有同 productId 商城 mtop 主图 → 保留原图。没有 miio_model 不通过名称猜型号，不用其他型号图片。

`image_source` 新增来源值 `mijia_baike_realIcon`；商城继续为 `mi_cn_mtop_cover`，保留原图时保留其来源。同步写 `image_source_url`、`image_captured_at`、`image_checked_at`、`image_width/height` 和 `image_note`（`$.data.realIcon` 与精确 miio_model）。原图回退仍有 `image_status` / `image_fallback`。百科 brief、购买链接等只存在原始响应审计中，不改商品名称、价格、日期、参数或门禁。

普通 finalizer 先解析现有米家目录身份再选图，随后重建目录展示图片，保证首次与重复执行得到相同结果。其他来源限定发布模式保持原有范围。

## 本地审计

沿用前一提交的 4,491 行本地候选及原 mtop 证据，无需重新探接口、重采商城主图。候选 SHA-256：`ab3510fa138fee3be553219161a65eaac40b2329dcc333153646ccd101bf9e6f`。小米 1,550 行，其中 351 行有 miio_model（348 个唯一型号）；348 个型号均实取 realIcon 并完整下载解码成功，351 行改用 realIcon。其余继续原商城/原图回退。非小米逐条相等，所有非 `image*` 字段逐条相等。选图重放幂等。详见 [report.json](report.json)。

- `data/official/xiaomi-realicon-images.json`：逐 miio_model URL、实测尺寸、时间、响应与图片 SHA-256；发布时离线重放。
- [baike-responses.json.gz](baike-responses.json.gz)：348 份完整原始接口响应，包含 realIcon、brief、buyUrl。两个中文路径 URL 下载时做百分号编码，不改保存的原始 URL。
- [cover-changes.json.gz](cover-changes.json.gz)：逐记录 image 字段前后对比，含来源字段和 miio_model。
- [samples.json](samples.json)：五组 realIcon / 商城图完整 URL、实际尺寸、原始背景（透明/白色）和视觉描述；原图同目录留存。
- [five-samples.png](five-samples.png)：五组并排对比图，已经逐组查看。

## 五条抽样

| ID / 商品 | realIcon | 商城 mtop 主图 | 结果 |
|---|---|---|---|
| 20833 米家智能宠物饮水机 2 | 480×480，透明底/白底展示，正面 | 800×800，透明底/白底展示，斜视 | realIcon 可用，已选 |
| 10330 米家智能微波炉 20L | 480×480，透明底/白底展示，正面 | 800×800，透明底/白底展示，正面 | realIcon 可用，已选 |
| 10722 小米口袋照片打印机 | 480×480，透明底/白底展示，俯视 | 800×800，白底，斜视 | realIcon 可用，已选 |
| 12010 米家落地扇 | 480×480，透明底/白底展示，扇头特写 | 800×800，透明底/白底展示，整机 | realIcon 可用，按指定顺序已选 |
| 12548 米家智能微烤一体机 | 480×480，透明底/白底展示，正面 | 800×800，白底，正面 | realIcon 可用，已选 |

全部实际下载、完整解码与目视核验；另读取 RGBA 四角像素确认透明背景。五张 realIcon 均为透明底；商城 20833/10330/12010 也为透明底，10722/12548 为纯白底。对比图在白底上合成展示，未修改最终图片 URL 或原图。未将“480×480”直接当作白底判据。realIcon 不保证每条都是整机全貌，落地扇例子明确留存。

## 两条最终结果

20833 的 miio_model 是 `xiaomi.pet_waterer.70m2`，`image_source=mijia_baike_realIcon`，480×480：

```text
https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/33d2334960da7c5a6682ca24144f2010_1720607831847.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=jDx3nO9KeTRu7FJabTINHKhY3gc=
```

21630 无 miio_model，`image_source=mi_cn_mtop_cover`，800×800：

```text
https://cdn.cnbj1.fds.api.mi-img.com/nr-pub/202507221658_b76557cd46bf30d480870a4ced4d5d61.png
```

## 重放

先以先前审计的冻结基线和商城证据重建上一提交候选（显式禁用 realIcon），再执行此次审计；全程本地，无网络请求：

```sh
git show 9d7971f5505c3325f5d616199491ed8342cd7f69:public/goods.json.gz > /tmp/cover-input.json.gz
PYTHONPATH=src python - <<'PY'
import gzip, json
from pathlib import Path
from goodsdex.xiaomi_covers import apply_covers
rows = json.loads(gzip.decompress(Path('/tmp/cover-input.json.gz').read_bytes()))
mtop = json.loads(Path('data/official/xiaomi-cover-images.json').read_text())
Path('/tmp/cover-realicon-before.json').write_text(json.dumps(apply_covers(rows, mtop, {}), ensure_ascii=False, indent=1)+'\n')
PY
python scripts/audit_xiaomi_realicons.py --input /tmp/cover-realicon-before.json --out docs/cover-image-20261106/realicon --write-evidence data/official/xiaomi-realicon-images.json --output public/goods.json --reuse
```

去掉 `--reuse` 才会请求已知百科接口与图片；运行时选图仅用标准库读取冻结证据。脚本不发布。

## 验证结果

- `PYTHONPATH=src python -m pytest -q -m 'not live'`：**1,121 passed，8 deselected**，包含首次/重复 finalizer、既有 release/series/date、历史原图和分片检查，以及新增三项 realIcon 顺序、失败回退和其他来源不变检查。[完整日志](tests.log)
- 客户端沿用原来的四组相关测试（item-cover-refresh、item-hero、item-thumbnails、items）：**22/22 通过**，未修改客户端代码。[日志](client-tests.log)
- 审计重放幂等；非小米记录与所有非图片字段逐条相等；348 份冻结响应的 SHA-256 和 realIcon URL 一致；`git diff --check` 通过。

仅在当前分支提交；未 push、未部署。
