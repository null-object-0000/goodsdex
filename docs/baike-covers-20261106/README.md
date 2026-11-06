# baike realIcon 封面补图审计

本轮 **1,244 条发布记录补图成功（1,241 个唯一型号）**；3 个型号返回 168×168，相关记录整组保留原图。没有使用 pdId 拼接图片，也没有重新探测该路径。

## 范围和方法

沿用上一轮冻结发布集：`56aba40cc6142c18bac20b9b7c7347a78f9c63fc:public/goods.json.gz`，4,491 条。代码从 `a2994838` 续做。以 `data/official/xiaomi-pdid-map.json` 的 1,244 个型号为候选边界，与发布集的 `miio_model` 精确匹配；已知当前图片宽高均 ≥480 的记录跳过（此次为 0 条）。未知尺寸不视为已有 480 封面。**候选 1,244 个型号 / 1,247 条记录。**

逐型号 GET `https://home.mi.com/cgi-op/api/v1/baike/v2/product?model=<model>`，只取 `data.realIcon`。全局线程池 4；每个 GET 总超时 12 秒，HTTP/传输失败最多重试 1 次。未调用 productCompact，也未构造 pdId 图地址。

本轮对返回 URL **全量实际下载并用 Pillow 完整解码**，再从新增合格型号按排序 + 固定随机种子 `20261106` 抽 40 个 URL。宽高均 ≥400 才接纳；所有失败型号的全部关联记录回退到输入原图。全量：**1,241 个 480×480、3 个 168×168**；40 条成功抽样均 480×480。记录响应 Content-Type，但验收依据实际解码尺寸：部分 CDN 返回 `text/plain`，对应正文仍可完整解码为图片，未重采样、放大或降低尺寸阈值。

来源值沿用现有 `mijia_baike_realIcon`（现有代码常量 `BAIKE_SOURCE`），未新造来源。封面重放允许已核验 ≥400×400 的百科证据按精确型号用于米家/有品等命名空间，保留独立 `image_mihome`。只改 `image` / `image_*` 及图片证据、脚本、测试和新增审计文件；params、release、supplements、发布门禁与旧缺口目录均未改。

## 补图和失败统计

|image_source|新增封面记录数|
|---|---:|
|mijia_baike_realIcon|1,244|
|mijia_pdicon|0|

|失败原因|型号数|记录数|
|---|---:|---:|
|无 realIcon|0|0|
|尺寸不足（168×168）|3|3|
|HTTP / 传输 / 解码错误|0|0|

|回退型号|实际尺寸|字节数|
|---|---|---:|
|`xiaoxun.watch.v11`|168×168|13,302|
|`xiaoxun.watch.v9`|168×168|17,529|
|`yunmi.waterpuri.lx5`|168×168|7,119|

本次所有 API 与图片最终请求均 HTTP 200。型号数与记录数不同，是因为 3 个合格型号分别关联了两条发布记录，不按 URL 重复计算型号成功数。

## 40 条新增 URL 尺寸抽样

下表链接为实际下载的 baike realIcon；字节数为下载正文长度，尺寸由 Pillow 读取。完整 HTTP 尝试、正文哈希见结构化证据。

|序号|model / realIcon URL|宽×高|字节数|
|---:|---|---|---:|
|1|[chunmi.mfcp.c3](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/f19a8698c97f5edc662384ec2f890dbe_1642150752377.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=Ar3ScEJTVR81QZg558ot2TibgmM=)|480×480|20,746|
|2|[dreame.vacuum.r2232a](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/0bf59c9ae9e40803519007436a0f28f0_1658289071263.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=2wle8zpXjIYLj05Nj2FA9HxQy0Y=)|480×480|50,611|
|3|[loock.lock.t3pmax](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/2ab4de7e91d53cacd99023cb459f1559_1704707302357.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=4Ip1IcxKgDpCRM7PAHQzYpDwepo=)|480×480|36,055|
|4|[mxiang.camera.mod11](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/ed3645d2ec2c6357baf9f72cf0eddb18_1645760922418.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=L0GwkWqfRN/lwa3hXKZmqzdX1tg=)|480×480|20,000|
|5|[chuangmi.camera.039a01](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/ccc0209e09007e21bb6b68164634eaa6_MIUI弹窗图示例.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=R86baGiUZSs+ysX3hZraLILgAmw=)|480×480|87,175|
|6|[xiaomi.aircondition.m16](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/12b6beae6fe632233cc8a76d55d05c7c_1653901927531.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=g+XfNUgyrFcJo5CwOgjflugiQA0=)|480×480|22,723|
|7|[xiaomi.hood.ym3c](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/fbb40a27e7ba4edbd956d9ff567aec48_1777453924193.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=/l9ychk6MATwXUET3A1ICJAW0ys=)|480×480|30,931|
|8|[xiaomi.airc.ar02r1](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-user-center/developer_1767164363092m12tFCWQ.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=PQzAN2mmuw/Und3xdyIfXxGWu20=)|480×480|21,359|
|9|[chuangmi.camera.065ac1](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/e2913f5f217031e371b9088ee4385a56_1696745525006.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=/4CgQLpO5fk6UQvFlRSZFVcsBCE=)|480×480|92,913|
|10|[chuangmi.cateye.i023a01](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/developer_1639119675290YOzGq3fM.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=cBaBjJ5VFp/VtJXGuBSauAMqg2g=)|480×480|61,316|
|11|[jiqid.mistudy.v2](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-user-center/developer_1679040911673od7XCAoh.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=F8IIvMXQr/3UqeHmGoueg4HAslo=)|480×480|85,201|
|12|[midjd8.washer.41](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/7dd9acde18914ab877f7eaad6292ae96_1692272557178.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=b/JmYcXcKq+lvAQ3J9mhPfNWhZ0=)|480×480|78,345|
|13|[viomi.hood.v6](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-user-center/developer_16790434539117JdWC95C.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=AXt4R+a7YM1D3G3OOVH8Y2br5d8=)|480×480|19,096|
|14|[lumi.camera.aq1](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-user-center/developer_1679040910453UXdZJqsR.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=My5RK0hEEDXLOww3iUzi3+kSO5o=)|480×480|48,081|
|15|[mibx5.washer.f83](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/a9b04e615c54798d4c8a264e6dc8daf7_1761722687905.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=MO9roaqdIyodEDFJH71YgLmhNzI=)|480×480|118,337|
|16|[xiaomi.airc.rrkh00](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/689bbff12e17eb52ce8dbceb88ddf192_1773974643663.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=MwKYQMLgJ86vfdRDRyADp/eMq64=)|480×480|15,251|
|17|[zhimi.airpurifier.sa2](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-user-center/developer_1678870694774IFDI3Fut.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=zKKZsme219opOdSHZJbLklSaAfw=)|480×480|19,535|
|18|[xiaomi.aircondition.mt2](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-user-center/developer_16790424223409GRXVLPO.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=UcGWVplphUY1VhRUqbOLOsOVDEo=)|480×480|37,843|
|19|[careli.fryer.maf07c](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/668017f7452e25899b5bf37fcfaf5177_1672209762321.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=cTB1sjUEm/L81kDAqH5guuH+42s=)|480×480|82,966|
|20|[qmdq88.dishwasher.n116](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/1dee7648cca54fd8e16eace3d36383b6_1665639606287.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=+PloYosuf3lPzDDKTapiU+5CYFc=)|480×480|69,248|
|21|[xiaomi.waterpuri.lx40](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/2dc226257bc97e17c15c9333de42c661_1715842472501.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=tVa3u0WhCJNcEKQM7S4jkd9uQeU=)|480×480|51,011|
|22|[chuangmi.camera.025b02](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/developer_1639118172626cbWkS4jr.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=0eQZhrYQNFu68zo6k1SmTSLSL50=)|480×480|82,752|
|23|[dreame.scooter.t2185](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/b816bf3768b7e9b2016d4c9ea3bbd73b_1638240620907.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=ffmkxHj7R2iP7NtYzJ1mJiGWY7o=)|480×480|79,887|
|24|[zhimi.airp.mp4a](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-user-center/developer_1679047107195GYJa94YR.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=t+gmJi0OU8ibtv7aBpFcwNjnvyM=)|480×480|89,368|
|25|[xiaomi.waterpuri.lx20](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/73a05c350c87e0c8b739899bc0d07bc7_1687859427475.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=+Cuwq+fVwa8bTilPg0z4ohBoOAY=)|480×480|19,392|
|26|[xiaomi.vacuum.d103cn](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/a15dd33db5517af7177e2ac819841652_1703042343364.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=07pgq65cSNGDKbt1+r3C1tgFoVE=)|480×480|65,878|
|27|[xiaomi.wifispeaker.l09a](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-user-center/developer_17321584974705RyTB3EA.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=LYsZzxgPBtsp7lmt6wAJjG1NmTs=)|480×480|83,234|
|28|[mmgg.feeder.inland](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/648a79694178d63d0152642eaa579075_developer_1556271530p1ywro582.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=E4T5j8xyaakkfDeG4SggVdCqtzw=)|480×480|55,834|
|29|[midjd.fridge.bs56m](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/234c0048488c4c41f51d79d0bea210ff_1791856036419.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=5psLsPshP0kFe7wCIkTCE+D1tNU=)|480×480|64,499|
|30|[dmaker.fan.p221](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/8a261e4fa11eeaea69d0b338d5593c7f_1670899153446.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=H87fYV1yFqGlpa7uL8Kc35bmO9s=)|480×480|49,697|
|31|[xiaomi.camera.091ac1](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/41415676a6cc60a126645ad2398b1a69_1783675447516.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=ZXzdf5LEQLt/GhU1M9d3BbeWnrQ=)|480×480|61,409|
|32|[xiaomi.jmprope.sr900](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/2d20d0f54c612563fb143cc70b177a94_1742279934463.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=5FDFs6t9te43jdwYuFx+0XOmx74=)|480×480|56,122|
|33|[yeelink.bhf_light.v13](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/7c3d024d4c4a9bf6a4fd7bb62dfb4300_1679278134398.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=7TKbqbR6OxLlGdy+rD1F5dyyLuU=)|480×480|26,440|
|34|[xiaomi.lock.b03](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/b7319d215c20ba43c9de3d581d1879f7_1704509776365.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=A0VnG8unGm2DH6fP+8kmXPej7ZI=)|480×480|21,605|
|35|[mibx2.washer.x20](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/fa98ba31a2a7dff1f9a445cd1b5678ed_1779069039796.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=uJNa74xV7zA/WmjgvznAf+jqV8I=)|480×480|53,555|
|36|[xiaomi.humidifier.p3](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/developer_17007203125308tI3IW24.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=Jr69rkRtBBpGlnIl08eON9+wqxk=)|480×480|56,377|
|37|[dreame.vacuum.r2246](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/7433ad57ab9bd2593156593de10ccdf1_1661496679159.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=ZP61I4Zb17Efp8ygaKwHYtStfIg=)|480×480|65,502|
|38|[yunmi.waterpuri.lx8](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-user-center/developer_16790409151160CciUqWz.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=EI4tdCNs/IW3H8aUnotBa+QJfjo=)|480×480|9,304|
|39|[xiaomi.airc.ar09r1](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/485a167f7dde1948c4b1f0a5e1f2dd5b_1776672217783.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=tRa4D/EJ1bx/VA2V3DDUm6lhR3U=)|480×480|22,857|
|40|[mibx5.washer.s111](https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/a6ad9d9080d8ef53f4b77364d5c846a5_1708932528567.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=lvPTvF7wS7+PEcMgsLnUQUz97EA=)|480×480|12,993|

## mihome:13363 最终结果

米家全能扫拖机器人 2，`xiaomi.vacuum.c102cn`：原 `image=null`，本轮选图：

- `image`: `https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/1eafc7066db11df15e91bfa15501ff49_1683351662794.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=Kce2FbwjD0f3eAdVtzfHIc3WevM=`
- `image_source`: `mijia_baike_realIcon`
- 实际图片：**480×480 / 65,878 bytes**；HTTP 200。

## 审计与复跑

[report.json](report.json) 保存候选/成功/失败计数与目标机型；[observations.json.gz](observations.json.gz) 保存每个型号的完整 API 响应、下载 HTTP、尺寸、字节数与 SHA-256；[sample-40.json](sample-40.json) 为固定抽样；[failures.json](failures.json) 为 3 个失败型号；[cover-changes.json.gz](cover-changes.json.gz) 为逐记录图片字段前后差异；[verification.json](verification.json) 保存基线与不变量核对。

全体 4,491 条记录非图片字段逐项相等；3 个失败型号记录完整等于输入；实际 `apply_covers` 重放的全部 1,247 条映射记录均与候选 image/image_source 相等；补图幂等。映射表和 `docs/pdicon-covers-20261106/` 相对 HEAD 无改动。完整候选仅写本地 `/tmp/baike-candidate.json.gz`，提交图片证据与差异，不替换发布分支产物。

```bash
git show 56aba40cc6142c18bac20b9b7c7347a78f9c63fc:public/goods.json.gz > /tmp/baike-baseline.json.gz
/tmp/goodsdex-cover-tests/bin/python scripts/backfill_xiaomi_baike_covers.py \
  --input /tmp/baike-baseline.json.gz --output /tmp/baike-candidate.json.gz --reuse
PYTHONPATH=src /tmp/goodsdex-cover-tests/bin/python -m pytest tests -k "image or publish or supplement" -q
```

不带 `--reuse` 则重新获取；复跑只读网络与本地图片证据，不发布、不部署、不触发 workflow。

定向测试：**110 passed / 1034 deselected / 4 subtests passed**，见 [tests.log](tests.log)；封面专项检查 **18 passed**，见 [tests-covers.log](tests-covers.log)。
