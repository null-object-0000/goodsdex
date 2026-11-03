# 正式发布与线上验收

完成时间：2026-11-03 23:27:35（北京时间）。

- GoodsDex 规则提交：`adab3715bc793b9feb3a6b33ee9ac5f8b00b4765`（main，已推送）。
- data 发布提交：`47cfd505f3c0b77c030c4fe384c06556e6e86b81`。
- API 清单兼容修复：`aa4d896e4cd6dad2089a56acd7b4a9bcbe23dc71`（spend-good 仓库分支 `fix/catalog-sources-status-20261103`，已推送且单模块部署）。
- [正式发布流水线](https://github.com/null-object-0000/goodsdex/actions/runs/41662687650)：成功，发布门禁 238 项通过；新增配件排除 11/2887=0.381%，green，无放行参数。排除输入 62 条包含补充缓存重放的 51 条历史配件，不重复计为新增。
- [云端离线测试](https://github.com/null-object-0000/goodsdex/actions/runs/41662686283)：538 passed，8 项原有 live 未选中；本地全量含 live **546 passed**。API 全量 **288 passed**。日志分别保留。

本轮正式发布前仍为 b07660b0，发布对比 `published-comparison.json` 与离线对比一致：2909→2898 行，1552 个空品牌全部按 ID 明确归属；小米只回填后1695、过滤后1684，未知0%。新增排除11、累计档案1070；原1059条首次快照逐值不变。

`published-integrity.json` 证明发布前后 `data` 源档案树、`public/prices` 价格历史树哈希均不变。所有保留商品除 brand/brand_source 外的字段和重复冲突 ID 各行顺序逐值不变。

## 线上同步兼容性处理

首次调用现有 primeCatalog() 返回 `ok:false/count:2909/errors:["无效的商品文件清单"]`，原目录保留。逐行对照已部署模块，实际原因是其文件名白名单不接受发布端已有的 `sources-status.json`；空索引 count=0 本身被正确支持。未删除或改变 meta 里的 sources-status 描述符来绕过校验。

在隔离的 spend-good 工作树中只增加该精确文件名，继续校验路径、SHA-256、count、bytes；新增真实分片同步用例及非法描述符反例，API 全量288项通过。没有纳入相邻仓库其它未提交工作。部署从线上现有镜像派生，只 COPY `catalog-files.mjs` 一个模块，校验部署前后哈希，保留旧模块/旧镜像和失败回滚；未替换其它服务端模块或依赖。

部署前模块 SHA256 `bb325dc7a4e695fbfd2ec3c6cd1da9481711017343407b5ef1b008aa7a8c15ac`；部署后 `c3a7254bd04945fe25a32e1ecfaacda339babe637e0b76419fea3877d7e12695`。构建日志、健康检查、回滚脚本见 api-deploy.*。重新同步真实返回 `{"ok":true,"count":2898,"errors":[]}`。

## 实际 curl 返回

命令与完整输出：[curl-results.log](curl-results.log)，可重跑 `bash docs/brand-accessory-20261103/curl-acceptance.sh`。

```sh
curl --noproxy '*' -fsS https://spend.snewbie.site/api/meta \
  | jq '{count,brands,xiaomi_index_count:.files["index/mi_cn.json"].count,unknown_index_count:.files["index/other.json"].count}'
```

```json
{
  "count": 2898,
  "brands": {"Apple":635,"比亚迪":14,"大疆":281,"富士":63,"惠普":218,"小米":1684,"小米汽车":3},
  "xiaomi_index_count": 1684,
  "unknown_index_count": 0
}
```

```sh
curl --noproxy '*' -fsSG https://spend.snewbie.site/api/goods/search \
  --data-urlencode 'brand=小米' --data-urlencode 'limit=1' \
  | jq '{total,productTotal,facets_version}'
```

```json
{"total":1457,"productTotal":1457,"facets_version":2}
```

默认搜索保留原两级分类口径：按 ID 去重（小米原发布行含5行重复），加入API既有的2条本地补充商品，再默认隐藏224条旧款：1684−5+2−224=1457。该2条为 `CN:mi_cn:reference:C102CN`（米家全能扫拖机器人2）和 `CN:mi_cn:product:19511`（米家智能宠物喂食器2），本轮没有新增。显式 `facets_version=1`（包含旧款的旧口径）返回 `total=1681/productTotal=1681`；品牌分面同为1681。不能把原始行数1684伪报为默认搜索total。

`online-verification.json`、api-meta-after.json、api-search-after.json、api-search-v1-after.json 和 api-goods-after.json.gz 保留真实响应。线上完整导出与 data 逐字节一致，SHA256：`139ebb86943fec20aa16bfd2c30df3ec8995680dc0d3888257f7c0e2ed1952d1`，与 manifest 一致。全部2898条均有明确 brand/brand_source=id_prefix；other索引为0。

详情实测：`CN:mi_cn:product:10000292`、`CN:mi_cn:product:13929` 均HTTP404；完整净水器 `CN:mi_cn:product:16549` HTTP200，brand=小米、brand_source=id_prefix。全部11条新排除ID在完整线上目录中均不存在。

完整逐品牌表、剩余unknown前缀（空）、20条样本与主类目前后对比见 [README.md](README.md)。
