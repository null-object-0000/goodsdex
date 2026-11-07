# 说明书参数分支 rebase 验收（2026-11-07）

目标分支 `feat/manual-params`，原 HEAD `8f5d9b3e`；fetch 后 rebase 到 `origin/main` 的 `9a14ff5e`。保留两条参数采集提交，额外提交本次字段隔离与验收记录。未 push、未部署、未触发 workflow。

四个关注文件的合并方式：

- `.gitignore`：自动合并后核对为并集，保留 main 全部规则及参数采集缓存忽略项。
- `src/goodsdex/dedupe.py`：自动合并后核对 main finalizer 全部逻辑保留，普通模式末尾重放家电与 PDF 参数；专用模式维持跳过规则，证据写独立审计文件。
- `src/goodsdex/publish.py`：手动解冲突，保留 main `record_cover` 与标准化，再串接参数重放，`collect_public` 和承前发布路径原样保留。
- `tests/test_date_enrichment.py`：手动解冲突，保留 main catalog/cover 回放顺序，在其后加入参数回放与独立审计文件断言。

相对 main，delisted、supplements、realIcon/mtop 图源、图片刷新脚本与 workflow 文件均无修改。完整文件清单见 `diff-files.txt`。

## 字段边界

原参数函数会返回 `params_sources` / `params_missing` / `params_missing_evidence` / `params_conflicts` / `params_source_type`；保留这些函数用于采集验证，在发布入口增加 `apply_public_params` 投影，仅把 `params` 写回商品，证据与结果写入新增的 `public/parameter-audit.json`。输入已有的所有非 params 字段保持原值。

这些改动对发布商品记录只影响 `params`，另新增参数审计文件；不修改价格、release、下架/在售承前标记、图片字段或门禁实现。

467 条冻结记录实际离线回放：134 条记录参数发生变化，所有非 params 字段不变，已有参数值不覆盖，重复回放幂等（`field-scope.json`）。新增四种下架/在售承前/realIcon/商城图源状态的交叉测试，逐项断言非 params 字段完全相同。参数与 finalizer 相关测试 48 passed（含三份真实 PDF 解析）。

## 测试

最终版本使用用户指定命令：

```bash
PYTHONPATH=src:scripts /var/tmp/user-items-release-venv/bin/python -m pytest -q tests
```

全套结果：1232 passed，0 failed，4 subtests passed，耗时 92.57 秒。全套日志：`full-tests.log`（包含 live 测试，没有排除模块或测试）。

另一次独立兼容性回归：

```bash
PYTHONPATH=src:scripts /var/tmp/user-items-release-venv/bin/python -m pytest -q tests/test_delisted_carry.py tests/test_supplement_publish.py tests/test_refresh_missing_images.py tests/test_xiaomi_baike_images.py
```

结果：70 passed，0 failed，4 subtests passed（`compatibility-tests.log`）。无缺失依赖。
