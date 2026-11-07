# refresh-images 换源实测（2026-11-07）

本机真实联网测试；未修改发布数据、未触发 workflow。
数据基线：origin/data `e53260e967235b93eac08b3831ee3bd4006ac88a` 的 public/goods.json.gz。
144 条真实缺图候选均无 miio_model。取 productId < 100000、按数值降序前 20 条；另外取数值升序前 20 条历史记录。
通过 refresh(selected, fetch=session.get, post=session.post, limit=20) 调用生产函数；本机 requests Session 设置 trust_env=False（本机环境的 SOCKS 依赖未安装），脚本默认网络设置未改。
两轮各 added=0 / no_official_image=20 / network_error=0；均由 mtop 返回已下架/不存在业务码。没有图片 URL 或尺寸可报告，不将已有图商品冒充补图成功。
断言除图片、sources 和 display.image 外所有字段与输入一致；display 的其余字段不变。

## 20 条较新缺图记录

| id | 图源 | 图片 URL | 实际尺寸 | 结果 |
|---|---|---|---|---|
| CN:mi_cn:product:22581 | mtop | —（上游无图） | — | no_official_image |
| CN:mi_cn:product:22580 | mtop | —（上游无图） | — | no_official_image |
| CN:mi_cn:product:22579 | mtop | —（上游无图） | — | no_official_image |
| CN:mi_cn:product:22578 | mtop | —（上游无图） | — | no_official_image |
| CN:mi_cn:product:18426 | mtop | —（上游无图） | — | no_official_image |
| CN:mi_cn:product:8915 | mtop | —（上游无图） | — | no_official_image |
| CN:mi_cn:product:8914 | mtop | —（上游无图） | — | no_official_image |
| CN:mi_cn:product:8912 | mtop | —（上游无图） | — | no_official_image |
| CN:mi_cn:product:8911 | mtop | —（上游无图） | — | no_official_image |
| CN:mi_cn:product:8909 | mtop | —（上游无图） | — | no_official_image |
| CN:mi_cn:product:8907 | mtop | —（上游无图） | — | no_official_image |
| CN:mi_cn:product:8881 | mtop | —（上游无图） | — | no_official_image |
| CN:mi_cn:product:8871 | mtop | —（上游无图） | — | no_official_image |
| CN:mi_cn:product:8845 | mtop | —（上游无图） | — | no_official_image |
| CN:mi_cn:product:8835 | mtop | —（上游无图） | — | no_official_image |
| CN:mi_cn:product:8830 | mtop | —（上游无图） | — | no_official_image |
| CN:mi_cn:product:8828 | mtop | —（上游无图） | — | no_official_image |
| CN:mi_cn:product:8811 | mtop | —（上游无图） | — | no_official_image |
| CN:mi_cn:product:8803 | mtop | —（上游无图） | — | no_official_image |
| CN:mi_cn:product:8784 | mtop | —（上游无图） | — | no_official_image |

## 成功取图对照（不计入缺图补全）

20545 原来已有图，单独验证两个源均能下载并以 Pillow 解码：

- mtop：800×800，https://cdn.cnbj1.fds.api.mi-img.com/nr-pub/202409291501_1e44fa68ae42c3f8f59ae427a6b773ff.png
- realIcon：480×480，https://cdn.cnbj1.fds.api.mi-img.com/iotweb-product-center/091457cecc65cba81f74d021b89109cc_1717731345251.png?GalaxyAccessKeyId=AKVGLQWBOVIRQ3XLEW&Expires=9223372036854775807&Signature=IezWM4Az/akHllVf1wTyGjQSY8E=

## CI 证据与边界

- [refresh-prices 42309714078](https://github.com/null-object-0000/goodsdex/actions/runs/42309714078) success，collect 日志 updated=1224，价格变化 58 条；但当前代码 scripts/ci_refresh_prices.py → goodsdex.prices.fetch_prices 实际使用 dynamicv2，不能当作 mtop 已在 CI 成功的直接证据。
- [crawl-all 42256534105](https://github.com/null-object-0000/goodsdex/actions/runs/42256534105) crawl 日志：93 类成功，0 类失败，累计 3626 款商品（2026-11-06T18:08:38Z）；整体 workflow 为 failure，不能说整体成功。mi_cn 采集器包含相同 MTOP_URL 和 MTOP_HEADERS。
- 刷新脚本已不含被封域名，不会再请求旧 product/view；本机两个新源均成功，但没有触发 CI，不能保证新端点永不返回 406/429。

## 测试

`PYTHONPATH=src:scripts /var/tmp/user-items-release-venv/bin/python -m pytest -q tests/test_refresh_missing_images.py tests -k "image or publish"`

结果：141 passed, 1052 deselected, 4 subtests passed。覆盖切源成功、无图、网络失败、realIcon 优先与回退、白底优先、尺寸下限、100 条上限及旧域名移除。
