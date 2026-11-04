# 发布后真实 API 摘录

/api/meta：

```json
{
  "revision": "14707400f2c64332a4fa199f86c59d81",
  "total_published": 2902,
  "release_series": {
    "count": 211,
    "inherited_without_product": 163,
    "batch_count": 129
  }
}
```

3个真实 /api/goods/<id>：

```json
[
  {
    "id": "CN:mi_cn:product:20618",
    "name": "Xiaomi 15",
    "release_series": {
      "date": "2024-10-29",
      "granularity": "day",
      "source": "official",
      "crosscheck_status": "official",
      "display_allowed": true,
      "internal_only": false,
      "usage": "reference",
      "display": "该系列 2024 年 10 月 29 日发布"
    }
  },
  {
    "id": "CN:mi_cn:product:21765",
    "name": "小米电视S Pro 85 Mini LED 2026",
    "release_series": {
      "date": "2025-09",
      "granularity": "month",
      "source": "third_party",
      "crosscheck_status": "corroborated",
      "display_allowed": true,
      "internal_only": false,
      "usage": "reference",
      "display": "该系列 2025 年 9 月发布"
    }
  },
  {
    "id": "CN:mi_cn:product:25291",
    "name": "小米智能门锁 5 Max 深锖色",
    "release_series": {
      "date": "2026-09",
      "granularity": "month",
      "source": "third_party",
      "crosscheck_status": "unverified",
      "display_allowed": false,
      "internal_only": true,
      "usage": "disabled",
      "display": null
    }
  }
]
```
