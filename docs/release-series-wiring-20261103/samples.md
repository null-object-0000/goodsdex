# 线上五条抽查

|ID|名称|单品日期|系列日期|批次|证据|
|---|---|---|---|---|---|
|CN:mi_cn:product:23270|巨省电Pro 大1匹 超一级能效 米家空调|null|2026-02|mi-ac-pro-202602|[原文](https://www.ithome.com/0/924/464.htm)|
|CN:mi_cn:product:22339|巨省电 大1.5匹 双排铜管 米家空调|null|2025-12|mi-ac-double-202512|[原文](https://www.ithome.com/0/902/637.htm)|
|CN:mi_cn:product:21825|米家扫拖机器人 5C 水箱版|null|2025-08|mi-reviewed-0878384|[原文](https://www.ithome.com/0/878/384.htm)|
|CN:mi_cn:product:23577|米家冰箱Pro 法式508L 自动制冰 冰羽白|null|2026-05|mi-reviewed-0954285|[原文](https://www.ithome.com/0/954/285.htm)|
|CN:mi_cn:product:10050236|小米电视S Pro RGB-Mini LED 2027|2026-08|2026-09|mi-reviewed-1002763|[原文](https://www.ithome.com/1/002/763.htm)|

巨省电真实详情摘录（完整字段见 verification.json）：

```json
{
  "id": "CN:mi_cn:product:23270",
  "name": "巨省电Pro 大1匹 超一级能效 米家空调",
  "release": null,
  "release_series": {
    "date": "2026-02",
    "granularity": "month",
    "source": "third_party",
    "level": "series",
    "market": "CN",
    "event": "announcement",
    "evidence": {
      "url": "https://www.ithome.com/0/924/464.htm",
      "sha256": "26e82d512142dcbf9be3994a05b8f0835c53ef0771a71969126f1d3677641945",
      "captured_at": "2026-11-03T09:45:03.459522+00:00",
      "quote": "小米今日发布了全新 2026 款米家空调巨省电 Pro 系列",
      "locator": "div.post_content 首段及挂机规格段",
      "source_type": "third_party",
      "capture_type": "http_response",
      "capture_file": "docs/series-release-pilot-20261103/evidence/924464.html"
    },
    "batch_id": "mi-ac-pro-202602",
    "series": "米家空调（巨省电）",
    "generation": "2026 Pro 挂机 2026-02 发布批次",
    "usage": "reference",
    "label": "系列推出时间",
    "display": "该系列 2026 年 2 月发布",
    "inherited": true
  },
  "api": "https://spend.snewbie.site/api/goods/CN%3Ami_cn%3Aproduct%3A23270"
}
```

最后一条为并存反例：单品日期 2026-08 原样保留，系列日期为 2026-09，inherited=false。
