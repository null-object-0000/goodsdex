# 正式发布与线上验收

- 规则提交：`e8a153ddc395be94cd8d225e681908517eddbf91`（main，已推送）。
- data 提交：`163549785bcc56081d521d5279d723e8bd073b2b`。
- revision：`f6278029f82344fb9dfda12ff46aafed`。
- [正式流水线](https://github.com/null-object-0000/goodsdex/actions/runs/41675989351)：success，发布门禁 **359 passed**；完整 finalize、data 提交、OSS 镜像成功。没有修改 meta 或 goods 字段语义。
- [云端离线全量测试](https://github.com/null-object-0000/goodsdex/actions/runs/41675992165)：**659 passed / 8 deselected**。本地基线542项、修后659项通过；8项原有live测试按CI原命令排除，没有改测试选择规则。没有新增失败。
- 线上同步真实返回：`{"ok":true,"count":2898,"errors":[]}`（`api-sync.log`）。

`audit-published.json` 确认正式两档3978行，命名空间全覆盖、未知0、跨品牌改派0、小米已发布1684不减少。正式 goods 与冻结基线经品牌归一的结果逐值完全相同；排除 items 除本次发布判定时间 excluded_at 外逐值相同。未知样本为0条，没有伪造10条。

`online-verification.json` 确认 API meta 与 data meta 完全相同；完整 `/api/goods` 及 OSS `goods-excluded.json` 的字节哈希均与本次发布清单一致：

- goods：`07484be0b6fbe5d67766f77ae2167e32342b46a1c149d968e16a50d13218125b`
- excluded：`c534b365e34d7b68624374cae4f689933b5d29299d2f29433c7c1a7127a15c32`

## curl 实测

完整响应见 api-meta-after.json、api-search-after.json、api-search-v1-after.json；可重跑 `bash docs/brand-namespace-20261104/curl-acceptance.sh`。

```sh
curl --noproxy '*' --compressed -fsS https://spend.snewbie.site/api/meta \
  | jq '{count,brands,total_all,total_published,total_excluded,revision}'
```

```json
{"count":2898,"brands":{"Apple":635,"比亚迪":14,"大疆":281,"富士":63,"惠普":218,"小米":1684,"小米汽车":3},"total_all":3978,"total_published":2898,"total_excluded":1080,"revision":"f6278029f82344fb9dfda12ff46aafed"}
```

```sh
curl --noproxy '*' --compressed -fsSG https://spend.snewbie.site/api/goods/search \
  --data-urlencode 'brand=小米' --data-urlencode 'limit=1' \
  | jq '{total,productTotal,facets_version}'
```

```json
{"total":1457,"productTotal":1457,"facets_version":2}
```

显式 facets_version=1 返回 `{"total":1681,"productTotal":1681,"facets_version":1}`。搜索沿用现有API的按ID去重、本地补充及默认隐藏旧款口径：1684−5个重复行+2条既有API补充−224条旧款=1457。没有为了凑1684修改search/meta语义。

截图中的冒号ID在当前冻结正式两档、main旧缓存中均未出现；故没有声称线上修复了原本并不存在于这些快照的unknown。已用给定ID做真实排除生成回归；该ID及所有审核别名的分隔符变体在后续采集重放、共享finalize中都会自动归一。
