# 正式发布与线上验收

惠普 **218 → 790**：787条有货号、3条为明确缺号原因的官方系列记录。新增569个历史货号；全部来自官方支持接口，不在本次完整商城目录。原有HP ID全部保留。

实现提交：[aa7bea96](https://github.com/null-object-0000/goodsdex/commit/aa7bea9654ab47357856b74492d9af8e05da6a85)；已发布的留档边界修复：[d4309557](https://github.com/null-object-0000/goodsdex/commit/d430955773642a6460ec96a90315857ee2e35bf9)。全量采集入口另确保先复制本轮新档案，再执行重建/丢ID门禁，并有实际CLI重建回归。

最终正式发布：[41883103308](https://github.com/null-object-0000/goodsdex/actions/runs/41883103308)，collect与publish均success；门禁 **553 passed**；data提交 `f16a874`；OSS逐文件GET哈希读回通过。原始完成状态摘录见final-run.json / final-jobs.json，发布日志见publication-final-excerpts.log。

曾有一轮旧候选因 `collection-status.json.checked_at` 并发变化被门禁拦截（41881333830），未覆盖线上商品；以上最终任务从最新data重新采集后成功。没有绕过发布锁或强行合并冲突。

最终revision：`a76e0d07e13c44eea2ad3cccf4f242f4`；整库SHA256：`5b1a5b4c9eb046d9aec5c6397175712f72f949cf1cfe71839f0bad1cf2cea890`。部署端既有同步器返回 `{"ok":true,"count":3414,"succeeded":9,"errors":[]}`，未部署API代码。

线上共3414行，HP790行；`retired_count=578`，`retired_by_brand={"惠普": 578}`。原有9个HP下架记录的首次时间保留；抽查3条旧记录的原字段全部逐值保留。30条对照样本再次在正式线上核验通过。`/api/goods` 与不可变OSS blob逐值相等，详见online-verification.json。

## 两条实际API请求

**兼容导出接口忽略q，返回完整3414行。下面是这两次原始响应中的目标记录摘录，不声称服务端执行了过滤。** 完整原文：api-zhan66.json.gz / api-omen.json.gz；对应单条详情也返回200并逐值相等。

`GET https://spend.snewbie.site/api/goods?q=%E6%88%9866`

HTTP200；返回3414行，其中惠普名称含关键字的记录52条。

```json
{
 "id": "CN:hp_cn:family:zhan66-generation6-14",
 "name": "战66 六代 14英寸商务笔记本电脑",
 "part_number": null,
 "part_number_missing": "official_marketing_page_describes_configurable_family_without_orderable_part_number",
 "series": "战66",
 "generation": "六代",
 "category": "笔记本",
 "source_url": "https://www.hpstore.cn/laptops-tablets.html",
 "status": "unknown"
}
```

`GET https://spend.snewbie.site/api/goods?q=%E6%9A%97%E5%BD%B1%E7%B2%BE%E7%81%B5`

HTTP200；返回3414行，其中惠普名称含关键字的记录23条。

```json
{
 "id": "CN:hp_cn:family:omen-generation10-25l",
 "name": "暗影精灵 10 全面版游戏台式电脑",
 "part_number": null,
 "part_number_missing": "official_marketing_page_describes_configurable_family_without_orderable_part_number",
 "series": "暗影精灵",
 "generation": "10",
 "category": "台式机",
 "source_url": "https://www.hp.com/cn-zh/gaming-pc/desktops.html",
 "status": "unknown"
}
```

两个目标系列已可查。官方页没有唯一订购货号，故明确标注part_number_missing；销售状态未明示为unknown。它们不能替代机身货号的具体配置识别。

## 测试与边界

本地完整基线828 passed / 8 deselected；最终851 passed / 8 deselected。云端已发布源码完整测试：[41881365183](https://github.com/null-object-0000/goodsdex/actions/runs/41881365183)，850 passed / 8 deselected；额外1项端到端回归验证全量采集先安装新档案再重建的入口顺序。原有8项live未新增跳过。

历史支持目录的较旧分类缺席事件，不能覆盖另一分类的较新在场记录，也不能覆盖更晚的商品观察；新增回归防止先误下架再复活。冻结基线重放时非HP对象逐值不变，见local-invariants.json。

星Book、光影精灵等消费系列的旧代仍有覆盖缺口；没有宣称穷尽所有系列/所有配置。新增SKU的未标存储单位/GPU不推测，默认占位图剔除，缺图写明原因。

5候选入口、逐系列/代际分布、3条真实下架样本和30条对照见README.md / retired-samples.json / samples.md。

```bash
python3 docs/hp-history-20261105/verify_online.py
```
