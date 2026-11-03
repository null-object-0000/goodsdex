# 线上详情真实返回摘录

取自 live-api-samples.json 的真实HTTP返回，只选取ID、名称和对应字段；完整返回保留在该文件。

## page_first_archived

[真实详情接口](https://spend.snewbie.site/api/goods/CN%3Aapple_cn%3Acommodity%3AMD3Y4CH%2FA)

```json
{
  "id": "CN:apple_cn:commodity:MD3Y4CH/A",
  "name": "iPad",
  "page_first_archived": {
    "date": "2022-10-18",
    "evidence_url": "https://web.archive.org/web/20221018150759/https://www.apple.com.cn/shop/buy-ipad/ipad",
    "count_200": 544,
    "captured_at": "2026-11-03T13:23:21.707905+00:00"
  }
}
```

## release_llm

[真实详情接口](https://spend.snewbie.site/api/goods/CN%3Afuji%3Amodel%3Ax-h2)

```json
{
  "id": "CN:fuji:model:x-h2",
  "name": "FUJIFILM X-H2",
  "release_llm": {
    "date": "2022-09",
    "granularity": "month",
    "source": "llm",
    "model": "deepseek-v4.1-flash-1017",
    "confidence": "medium",
    "evidence": {
      "quote": null,
      "reason": "富士官方X-H2产品页可确认该型号族存在；已知官方于2022年9月发布X-H2，故按机身世代给出2022-09候选。未引用具体原句，因无法在当前环境核验页面原文。",
      "url": "https://fujifilm-x.com/global/products/cameras/x-h2/",
      "capture_type": "model_output",
      "family": "富士|相机|fujifilmx-h2",
      "response_file": "staging/release-full-20261103/responses/61bb9eafd534dc17a5d9b493.json",
      "response_sha256": "60d752900335afca6320ef9bacb35e5527bbaf36bcb8011e7c984f6ec642c263",
      "captured_at": "2026-11-03T08:39:49.655268+00:00"
    },
    "brand_accuracy": 0.9
  }
}
```

## release_series

[真实详情接口](https://spend.snewbie.site/api/goods/CN%3Ami_cn%3Aproduct%3A10000079)

```json
{
  "id": "CN:mi_cn:product:10000079",
  "name": "红米5",
  "release_series": {
    "date": "2017-12",
    "granularity": "month",
    "source": "third_party",
    "market": "CN",
    "event": "announcement",
    "level": "series",
    "evidence": {
      "url": "https://www.ithome.com/0/337/624.htm",
      "sha256": "200efd7f106da56f2e2b67c7731d0c7ae1f6e85401e9db0bccd8da7bb7bfe911",
      "captured_at": "2026-11-03T10:33:28.415951+00:00",
      "capture_file": "docs/series-release-rollout-20261103/evidence/8dd0387e40d7e857.html",
      "quote": "红米5/5Plus正式发布：搭载全面屏，799元起 - IT之家 首页 安卓之家 安卓手机 红米5/5Plus正式发布：搭载全面屏，799元起 2017-12-07 15:01 IT之家 - 远洋 IT之家12月7日消息 今天下午小米正式发布了千元全面屏新机红米5和红米5 Plus，小米称新机是迄今为止颜值最高的红米国民手机。小米在发布会上表示，小米第三季度出货量2760万台，增长102.6%实现翻番，海外14个国家进入前五，印度市场取得第一。 红米5和红米5 Plus分别采用了5.7 HD+和5.99英寸FHD 18:9全面屏，并经过圆角处理，机身采用中线对称设计，侧面收弧贴合手掌，手感更佳，后置指纹识别，有四种颜色可选：金色，玫瑰金，黑色，浅蓝色。另外手机采用了四角缓冲设计，可缓解跌落屏幕易碎的问题。 配置方面，红米5 Plus搭载骁龙625处理器，红米5则为骁龙450，红米5 Plus内置4000mAh电池，红米5内置3300mAh电池，官方称“妥妥用两天”。 拍照方面，红米5和红米5 Plus后置1.25μm大像素相机，前置柔光灯，无论拍",
      "locator": "article #paragraph；发布日期见 .post_time",
      "source_type": "third_party"
    },
    "batch_id": "mi-reviewed-0337624",
    "series": "红米5/5 Plus首发批次",
    "generation": "红米5/5 Plus首发批次；2017-12独立发布批次",
    "usage": "reference",
    "label": "系列推出时间",
    "display": "该系列 2017 年 12 月发布",
    "inherited": true
  }
}
```

