# L1 惠普官方支持站实测（2026-11-05）

线上基线791条（用户原790条后新增7Z8L4PC），788个可订购货号，3个无唯一货号的官方系列记录。本轮没有拿到可确认商品发布/上市事件的月级日期：**0/791**。

| 逐条最终诊断 | 条数 | 解释 |
|---|---:|---|
| no_release_field | 570 | 已有可校验原文哈希的精确货号支持响应，未提供商品发布/上市字段 |
| access_failed | 218 | 未取得可审计精确货号原文；本轮返回应用406 invalid captcha |
| model_mismatch | 3 | 官方系列记录没有唯一可订购货号，不能当SKU查询 |
| http_404 | 0 | 本轮未取得404 |

所有791条均归入“可得未取到/尚未获得”，没有任何一条被断言为“官方无此信息”。`no_release_field`只指该响应无商品发布日期字段，不表示惠普其他官方页面也没有。

本轮40批实际POST覆盖全部788个货号（每批20，间隔至少2.1秒）：HTTP均200，业务返回406，原文`Bad data in payload. invalid captcha.`。浏览器加载支持站后fetch同样返回406，见`probe.json`；仅凭HTTP200不能当采集成功。`network.json.gz`保存所有真实请求体、原响应、UTC时间及SHA256。既有570份有效SKU原文（本轮范围569份）来自`docs/hp-history-20261105/support-evidence.json.gz`，新增一份在本目录`supplemental-support.json`。所有精确货号旧响应均只有`webFirstPublishingDate`/`webReleaseDate`：没有官方证据说明它们表示硬件上市事件，全部拒绝用于商品日期。它们也没有被改叫归档日期再混入。

`results.json`包含791条详细结果、各条本次尝试及历史响应诊断。`data/official/hp-release-evidence.json`是统一runner输入，candidates为空，observations完整。

```bash
python3 scripts/release_lane_hp.py --goods docs/release-coverage/before.json \
  --cache docs/hp-history-20261105/support-evidence.json.gz \
  --cache docs/release-coverage/l1-hp/supplemental-support.json
PYTHONPATH=src python3 -m pytest tests/test_release_lane_hp.py tests/test_release_lane_series.py -q
```

L4另使用实际取得的HP官方2023-03-29新闻稿为112条精确ProBook G10官方平台成员提供2023-03全球系列公告月份；保存在`release_inherited`，不冒充中国配置SKU首售日，见`../l4-series/results.json`。
