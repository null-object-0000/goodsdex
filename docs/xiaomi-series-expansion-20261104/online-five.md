# 线上 search 的五条真实返回

固定种子20261104，从本轮53个不同ID抽取5条。基础search沿用轻索引；已有 `ids` 参数负责补全详情，未修改接口或字段语义。完整原响应见 search-five-after.json。

请求：`https://spend.snewbie.site/api/goods/search?brand=%E5%B0%8F%E7%B1%B3&ids=CN%3Ami_cn%3Aproduct%3A7897%2CCN%3Ami_cn%3Aproduct%3A6632%2CCN%3Ami_cn%3Aproduct%3A20350%2CCN%3Ami_cn%3Aproduct%3A21659%2CCN%3Ami_cn%3Aproduct%3A21872`

以下只省略无关字段，日期对象来自同一次真实search响应：

```json
[
  {
    "id": "CN:mi_cn:product:7897",
    "name": "小米6X 6GB+128GB",
    "release_series": {
      "date": "2018-04-25",
      "granularity": "day",
      "source": "third_party",
      "level": "series",
      "event": "announcement",
      "display": "该系列 2018 年 4 月 25 日发布",
      "crosscheck_status": "corroborated",
      "display_allowed": true
    }
  },
  {
    "id": "CN:mi_cn:product:6632",
    "name": "小米电视4A 43英寸",
    "release_series": {
      "date": "2017-03-21",
      "granularity": "day",
      "source": "third_party",
      "level": "series",
      "event": "announcement",
      "display": "该系列 2017 年 3 月 21 日发布",
      "crosscheck_status": "corroborated",
      "display_allowed": true
    }
  },
  {
    "id": "CN:mi_cn:product:20350",
    "name": "米家吸顶灯套系",
    "release_series": {
      "date": "2024-08-29",
      "granularity": "day",
      "source": "third_party",
      "level": "series",
      "event": "announcement",
      "display": "该系列 2024 年 8 月 29 日发布",
      "crosscheck_status": "corroborated",
      "display_allowed": true
    }
  },
  {
    "id": "CN:mi_cn:product:21659",
    "name": "REDMI Note 15 Pro",
    "release_series": {
      "date": "2025-08-21",
      "granularity": "day",
      "source": "third_party",
      "level": "series",
      "event": "announcement",
      "display": "该系列 2025 年 8 月 21 日发布",
      "crosscheck_status": "corroborated",
      "display_allowed": true
    }
  },
  {
    "id": "CN:mi_cn:product:21872",
    "name": "Xiaomi Pad 8",
    "release_series": {
      "date": "2025-09",
      "granularity": "month",
      "source": "official",
      "level": "series",
      "event": "announcement",
      "display": "该系列 2025 年 9 月发布",
      "crosscheck_status": "official",
      "display_allowed": true
    }
  }
]
```
