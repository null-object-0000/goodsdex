# 提交与线上验收

实现提交：`2d8d23318d626148a5cda6d4e64e2a63981fcc24`，已推送main。

云端完整测试 [41851414045](https://github.com/null-object-0000/goodsdex/actions/runs/41851414045) 成功：766 passed / 8 deselected；本地修后同为766 passed / 8 deselected，修前759 passed / 8 deselected。没有新增skip；8个live沿用仓库选择器。

正式发布成功：[41851590851](https://github.com/null-object-0000/goodsdex/actions/runs/41851590851)，使用上述实现提交。网络重试产生的重复任务41851609293已取消，未绕开发布锁或直接手写线上商品。

## 抽样命中率

|品牌|通过 / 实查|命中率|未通过原因|
|---|---:|---:|---|
|小米|20 / 20|100%|0条；达到80%门槛，补齐1482行（1477唯一ID）|
|Apple|20 / 20|100%|无；已有链接保持|
|大疆|20 / 20|100%|无；已有链接保持|
|惠普|19 / 20|95%|1条200但内容不能匹配；已有链接保持|
|富士|0 / 20|0%|17条官方403，3条既有京东链接；均未被当作官方成功|
|比亚迪|0 / 14|0%|现行7条官方动态配置壳未见车型名；历史7条原第三方页面，不计官方通过|
|小米汽车|0 / 3|0%|共用动态配置页，返回标题为“参数配置”，未确认具体车型|

比亚迪不足20行，14行全查；小米汽车3行全查。只有小米有缺URL，非小米缺失均为0，所以本次未向其它品牌新增或替换链接。

## 反例与边界

- **小米新增推导不成立0条 / 20条样本**。只在门槛通过后按规则写入本轮冻结范围；未声称对所有1482行逐页验证。
- 按本次内容匹配标准“推导不成立/未确认”11条：惠普1条、比亚迪7条、小米汽车3条。动态壳未确认不等于证明原链接已失效。以上全部既有值保持，不用第三方地址替换。
- HTTP403共17条，全部富士；已有第三方链接10条（富士3、比亚迪7），不计官方验证通过。全部38条未通过结果逐项见 [counterexamples.md](counterexamples.md)。
- 用户举例10000292已在修前发布集之外，真实API返回404；官网页是笔记本贴纸。没有为演示重新发布已排除商品。
- 额外核验当前仍发布的 `CN:mi_cn:product:10050230`：HTTP200，标题“米家高速水离子吹风机 Pro立即购买-小米商城”，见 extra-hairdryer.json / responses/117.html.gz；不加入20条随机样本分母。

## 发布与线上实测结果

- data提交：`88a038ab1c4b85082fb47d70896947783b72b2c4`；revision：`6166e43511c9422e84b563bd495fcbf9`。
- 正式任务success，门禁与OSS原文GET哈希读回均通过，见 publication.json / publication-excerpts.log。
- 服务端既有同步器成功返回 `{"ok":true,"succeeded":9,"errors":[]}`，见 api-sync.log；未部署API代码。
- 全量线上 `/api/goods` 与本次发布产物逐值相等，SHA256 `47bb3c1609861cb2c522d19324313659878bf22239c65b7a1802dea55f0a0b77`。相对冻结修前基线，唯一商品字段变化为1482个source_url；原有URL和其它字段全部保持，见 online-invariants.json。
- 线上 `/api/meta` 的 source_url_coverage 已实测：全库2856/2856；小米1638/1638；其余品牌计数同README前后表。原文见 online-meta.json。
- 三条实际 `/api/goods/<id>` 返回与发布行完整相等：25627（桌面灯）、10000082（历史笔记本）、10050230（吹风机Pro）；其source_url均再次GET为200，见 online-verification.json 与 online-detail-*.json。

真实curl摘录（仅选取字段，未伪造响应）：

```sh
curl -sS 'https://spend.snewbie.site/api/goods/CN%3Ami_cn%3Aproduct%3A10050230' | jq -c '{id,name,source_url}'
```

```json
{"id":"CN:mi_cn:product:10050230","name":"米家高速水离子吹风机 Pro","source_url":"https://www.mi.com/shop/buy/detail?product_id=10050230"}
```

完整线上快照：online-goods.json.gz；验证可复现：`python3 docs/source-url-20261104/verify_online.py --public <本轮data提交的public目录>`。

