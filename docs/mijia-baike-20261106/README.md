# 米家 baike：名称、型号、说明书与品类线索

2026-11-06。匿名采集；未登录、未请求需鉴权接口、未请求有品接口。**本轮交付是补充证据；实际改名、改品类、补图均为 0，发布日期覆盖率变化为 0 个百分点。**

## 验收

|项目|结果|
|---|---|
|小米抽样母体|1545 个唯一商城商品 ID（公开快照小米 1550 行含 5 个重复 ID）；完整快照 3572 行|
|固定随机抽样 50 条|唯一确认 model **9/50 = 18%**；2 条多 model；39 条未确定|
|全量候选映射|429 条，其中 373 条候选唯一；11 条系列容器不自动写入设备元数据|
|入发布清单|362 条详情证据；314 条完整名称唯一匹配确认 `miio_model`（20.32%）；48 条仅保留商城购买链接关联线索|
|成功 model 抓取|481 个；1 个源返回无有效主体，见 rejected-models.json|
|说明书|481 个入口：374 份 PDF（均经 pdfinfo 验证，提取第一页）、107 份 HTML；下载失败 0，损坏 PDF 0|
|物理机型编号|31 个 model 的第一页有可提取编号；其余封面无明确编号，不用功率/认证号补空|
|参数|130 个 model 非空，共 1375 条去重参数；其余按 source_empty/source_error/not_collected 分别记录|
|名称修正|**0**。不能提供 5 条“已修正”实例；下表仅是待核差异|
|品类修正|**0**；分布为空；机型编号与库内名称精确匹配 **0** 条；保留品类线索，不动旧款桶结构|
|主图|新增 **0**；映射并写入元数据的条目仍缺 **16**；小米全母体仍缺 **165**；481 个 model 中 materialPictures 为空 **450** 个|
|发布日期|所有 release/release_date/release_upper_bound 与输入逐条比较不变；覆盖率变化 **0**|
|测试|独立最新 main 基线全量 1041 通过；新增 8 测试后离线 **1041 通过、8 个 live 跳过**，与 CI 命令相同。原有 pytest 插件弃用警告未新增|

抽样使用排序后的唯一商城 ID 与 `random.Random(20261106).sample(..., 50)`；完整清单见 [sample-50.json](sample-50.json)。输入快照 SHA-256：`099e37eb9a58d7b6d61b70201d15327f24cfe890a4014a0e518b664108e5f024`，见 [goods-before.json.gz](goods-before.json.gz)。不以旧目录或已命中的设备作抽样分母。

## 为什么没有直接改名

官方 baike 购买链接可能指向含多规格的商城页。商品 ID 一致，不能证明某个颜色、尺寸或新版本就是库内整组商品。完整名称匹配只做 NFKC、大小写、空白规范化，**不删除括号、容量、颜色、版本或 Pro/Max**。不以 pd_id 数字碰撞匹配商城 product_id。

五条待核差异（均未覆盖原名）：

|库内名|baike 官方名|保留原因|
|---|---|---|
|米家风扇灯|米家风扇灯 36英寸|购买链接不足以确认尺寸|
|米家体重秤S200|米家体重秤 S200 蓝色|不能用单色款覆盖全商品|
|米家智能直流变频落地扇1X 升级版|米家智能直流变频落地扇1X|不能丢失“升级版”|
|米家三区洗衣机 滚筒14kg 冰晶白|米家三区洗衣机Pro 滚筒14kg|Pro、颜色身份需进一步核验|
|小米儿童手表|米兔儿童手表U2|不能只凭购买链接决定代际|

自动显示名修正还须现有 `产品型号/设备型号/型号` 与说明书物理编号精确一致，且新名只是原名的完整扩展。本批没有通过此门禁的记录。物理编号与全库小米名称逐条做字母数字边界匹配，命中为空，见 [hardware-name-matches.json](hardware-name-matches.json)。未将“线索可用”报成“分类已经修好”。

## 证据与字段

逐个成功 model 的 `productName / hardware_models / manual_url / parameter_count / materialPictures / category_clue / 状态` 见 [collected-models.tsv](collected-models.tsv) 和 [collected-models.json](collected-models.json)。HTML 说明书链接使用官方说明书页面；原始 introductionHtml 正文在响应证据中。

示例 `mibx5.washer.x15`：官方名“米家三区洗衣机Pro 滚筒10kg”；参数 0 条；materialPictures 为空。下载的[真实 PDF](x15-sample.pdf)第一页为 `XQG105MJ101、XQG105MJ102`，已对照[封面渲染](x15-cover.png)。未把接口的 createTime/updateTime/ts、目录 verified_time/change_time 或文档日期写成发布日；本批原始产品响应 productOnlineTime 非空数为 0。

发布清单位于 `data/official/mijia-baike.json`，由共享 finalizer 重放；`mijia_baike` 是详情证据字段，`image_missing` 在其中表示 baike 的 materialPictures 缺失，并不覆盖既有主图。参数保存在该字段中，不跨型号覆盖原 params。现有 name/category/categories/release 保持本批原值。无法映射和有歧义的记录保留原样。

[证据压缩包](evidence.tar.gz)保留所有匿名产品/说明书/参数响应、MIoT model 目录、APK 目录投影和所有 PDF 第一页文本。产品响应可用 UTF-8、ensure_ascii=False、separators=(',', ':') 重建原始字节，本批逐条核对 SHA-256；说明书和参数原响应按原字节保留。完整 PDF 已下载至采集工作区 `docs/mijia-baike-20261106/manuals/`，约 2 GB，不全部提交；逐文件 URL 与哈希保存在成功清单中。7 份初次超时/损坏文件重试后均有效，见 [manual-retries.log](manual-retries.log)。

APK 源为[小米应用商店](https://app.mi.com/details?id=com.xiaomi.smarthome)，版本 11.8.707，APK SHA-256 `60faf083a7f1874423b77d034d2fbd11ff7f97aafeb656f35333dbd5e498ac28`，设备 asset SHA-256 `00285ee38ecad7df66d137446f21002380f9b8868e758eec110a443123a77efe`。复用了另一条任务已有的匿名 APK 目录结果，没有接入其时间代理或鉴权分类接口。[MIoT 匿名 model 清单](https://miot-spec.org/miot-spec-v2/instances?status=all)只作发现线索，设备有效性由[米家官方 baike](https://home.mi.com/webapp/content/baike/product/index.html?model=mibx5.washer.x15)复核。

## 复跑

```bash
export PYTHONPATH=src:scripts
python3 scripts/collect_mijia_baike.py --output docs/mijia-baike-20261106
python3 scripts/map_mijia_baike.py --goods /path/goods.json --apk /path/com.xiaomi.smarthome.apk --output docs/mijia-baike-20261106
python3 scripts/enrich_mijia_baike.py --output docs/mijia-baike-20261106
python3 scripts/build_mijia_baike.py --goods /path/goods.json --output docs/mijia-baike-20261106
# 如有失败项，限时匿名重试并重新构建清单：
python3 scripts/retry_mijia_baike_manuals.py --output docs/mijia-baike-20261106
python3 scripts/build_mijia_baike.py --goods /path/goods.json --output docs/mijia-baike-20261106
PYTHONPATH=src python3 -m pytest -q -m "not live"
```

结论：这条线能提供官方设备名、说明书和粗品类证据，但商城 ID 到设备 model 的覆盖仍有限，且多规格身份需要进一步核验；**本轮不能宣称已解决名称或品类修正，实际覆盖率提升为 0**。日期路线无增益。发布提交与 run id 见 [publication.json](publication.json)。

## 发布与线上核验

代码提交 `c3c3e360`（功能提交 `9dd29f05`）；[发布 run 42064779520](https://github.com/null-object-0000/goodsdex/actions/runs/42064779520) **success**，发布门禁 **651 passed**；[CI run 42064779025](https://github.com/null-object-0000/goodsdex/actions/runs/42064779025) **success，1041 passed、8 deselected**。数据提交 `223eb14bbd3cdc8dd06077b98be22c2f002799eb`，OSS revision `ff6d996a7e8843ecbe17fd1ac77b6a41`。

[线上读回结果](online-verification.json)：经 SHA-256 验证的整库包含 **362 条 mijia_baike、314 条 miio_model**，缺失预期元数据 **0**；5 个不可变详情分片逐字段核对通过。对全量公共 ID 的 name/category/categories/release/release_date/release_upper_bound 比较，变化均为空。发布总行数仍为 3572。完整运行日志与验证脚本同目录留存。
