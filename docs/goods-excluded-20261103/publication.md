# 正式发布与验收

- 代码提交：`eb39acd78a7074f417a73b112e435990b321a351`（main，已推送）。
- data 提交：`73f3c9d0f5276860ccd9ff09b22ba7f4fe23a192`。
- [正式发布运行](https://github.com/null-object-0000/goodsdex/actions/runs/41665839751)：success；发布门禁 **242 passed**；OSS 全部回读校验后最后发布 meta。
- [云端全量离线测试](https://github.com/null-object-0000/goodsdex/actions/runs/41665839569)：**542 passed / 8 deselected**。本地修改前 **538 passed / 8 deselected**，修改后 **542 passed / 8 deselected**，无新增失败。8 项原有 live 按 CI 原命令排除；本次没有改测试选择规则。

## 实际数据

`total_all = total_published + total_excluded`：**3978 = 2898 + 1080**。
本次 finalize 于 `2026-11-03T15:40:10.041297+00:00` 生成，revision 为 `fab4d2a79aad4884898c387c3eab0e98`；meta、排除视图及所有 excluded_at 一致。

| 主理由 | 条数 |
|---|---:|
| accessory:sticker | 7 |
| accessory:screen_film | 23 |
| accessory:cleaning_consumable | 3 |
| accessory:category | 649 |
| accessory:name | 388 |
| container | 0 |
| duplicate | 0 |
| invalid | 6 |
| manual | 4 |

按实际 items 顺序的前 3 条（完整字段见 acceptance.json 的 first_three_items）：

| id | name | price | excluded_reason |
|---|---|---:|---|
| CN:apple_cn:commodity:MFE94CH/A | AirTag | 249 | accessory:category |
| CN:apple_cn:commodity:MFEA4CH/A | AirTag | 849 | accessory:category |
| CN:dji:sku:101241 | 御 Mavic 2 行业版智能飞行电池 | 1000 | accessory:category |

## 独立线上回读

实际 `curl --noproxy '*' -fSs https://spend-good.oss-cn-shanghai.aliyuncs.com/data/public/goods-excluded.json`：**HTTP 200**，1,314,124 字节，1080 条完整明细。

SHA-256：`5d82a89531e9f4c9ab55ed3b376c7dac0c3d413f80811545dbbc047a499be2e2`。
与线上 meta 的 `files["goods-excluded.json"].sha256`、data 分支文件逐字节一致；count、bytes、所有理由计数也校验通过。线上 goods 与 data 同样逐字节一致；2898 条已发布对象与发布前逐对象完全相同，排除项未回流到 C 端视图。

可重跑：

```sh
PYTHONPATH=src python3 docs/goods-excluded-20261103/verify_online.py \
  --data-revision 73f3c9d0f5276860ccd9ff09b22ba7f4fe23a192
```

## 误伤复核

完整原始类目分布见 `acceptance.json.category_distribution` 和 `oss-readback.log`，不能把原类目改成配件后宣称整机类目不存在。
主类目手机 **0**、相机 **0**、相机镜头 **0**。笔记本 **5** 全为已知定制贴纸；家电 **9** 为新风机/净化扇/除湿机滤芯、清洁剂、冲牙器喷嘴，均非家电整机。

进一步列出并复核了 240 条敏感原类目命中（详见 `sensitive_category_review`）：空调类是滤芯/滤网/新风面板，冰箱类是制冰机配件，电视类是移动支架，净水器类是滤芯，洗地机等类是滤芯/滚刷/边刷/主刷罩/自动上下水装置/抑味棒等；未发现手机、笔记本、相机或家电整机主体。
`电脑` 的四条是已审核的 macOS/Mac OS X 软件页面，按 manual 排除；不能被配件分类器的宽泛 Mac 名称匹配当作 Mac 整机。验收脚本对审核删除与配件判定分别校验。

文件：`acceptance.json` 为真实回读报告与完整前三条；`published-meta.json` 为真实 meta；`publication.log`、`ci-tests.log`、`tests-*.log` 保留发布与测试证据。`preview.log` 仅为本地预跑，不作为正式发布数字来源。
