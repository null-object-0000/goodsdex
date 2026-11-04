# 待人工核对（1 个 id）

- id：`CN:mi_cn:product:20425`，G088，Redmi Note 14 Pro+。
- 12GB 说法：[小米官方商品接口](https://api2.order.mi.com/product/view?product_id=20425&version=2)，`goods_id=2230002455`，原文：`Redmi Note 14 Pro+ 12GB+512GB 镜瓷白，价格 ¥1899`。
- 16GB 说法：[小米官方商品接口](https://api2.order.mi.com/product/view?product_id=20425&version=2)，`goods_id=2230002458`，原文：`Redmi Note 14 Pro+ 16GB+512GB 镜瓷白，价格 ¥1999`。
- 两份证据均采集于 `2026-11-04T22:40:48+08:00`；完整结构见 `source-conflicts.json`。
- 无法判定原因：同一 product_id 返回两个真实 SKU，现有 id 只含 product_id，不能唯一代表其中一种内存配置。data 中该 id 的两个冲突行仍保留，不能按价格或名称猜测属性归属。
- 已决定：该 id 的所有行均不写 `attrs`、`attrs_source`、`attrs_confidence`。两份候选属性以 `withheld_attrs` 留在证据输入中，等待人工确认身份粒度后再处理。
