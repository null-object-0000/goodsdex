# HP 下架分类与发布验收（2026-11-03）

修复代码：`1acd9d0382cecac243d4fb8745b7db383d3b82e2`。

- 分类：仅官方已知电脑列表目的页 + HTTP 200 + 商品链接 + 无 setProduct 上下文。
  不接受陌生非详情页、验证码、登录页、详情解析异常为下架。
- 留档：保留原始商品全部字段；新增 sale_status、delisted_at、delisted_evidence。
  archived-delisted.json 保存首次本地实采的九条完整档案。
- 默认跳过已留证下架 URL；不重复请求，不刷新首次发现时间。
- 门禁：新增下架 URL / 实际待检查 URL >10% 判红，真实抓取/解析错误一条也判红。
  9/218=4.128%，允许小批撤页；大批统一跳转触发门禁。既有下架不稀释分母。
  失败轮只写 audit/raw，不写 goods，避免重跑跳过下架绕过门禁。
- 未修改 refresh-hp / publish-release 的超时、依赖关系或发布步骤。

真实执行：

```sh
python3 scripts/crawl_hp.py --out /tmp/hp-delisting-live/data/hp \
  --raw /tmp/hp-delisting-live/raw --reuse-images --known-only --interval-from-start
```

第一次从 data 分支的 218 条历史档案开始完整联网采集，exit 0。
collect-local-1.json 为真实最终 JSON（仅排除 images/requests，与终端摘要一致）。
核对全部 218 个 ID 保留；九条下架记录除新增状态/时间/证据，全部字段与基线完全相同。

云端手动触发：

https://github.com/null-object-0000/goodsdex/actions/runs/41558289249

使用修复提交，collect 成功、publish 成功；collect-actions.json 从该 collect job 原始日志提取，
actions-jobs.json 保留各步骤结论，actions-run.json 保留整轮结论。
证据 artifact（GitHub 保留 7 天）：
https://github.com/null-object-0000/goodsdex/actions/runs/41558289249/artifacts/13196935574

正式 data 提交 d0bdbd19b933a6c531aef850f133d0279d969c32。
published-verification.json 记录从 origin/data 读取 HP 档案与 public/goods.json 的核对结果：
均有 218 条 HP 商品、9 条下架、全部历史 ID 保留、全部下架有时间及证据。
publish-excerpts.log 保留 data 推送与 OSS SHA-256 校验日志摘录。

回归验证：70 passed（HP、候选合并、发布策略、补充发布、去重、分片、镜像、汽车结构），
包含 10% 边界、超限不更新档案、详情结构损坏仍判红、重复采集跳过下架。
云端发布门禁另有 53 passed（见 publish-excerpts.log）。

第二次使用同样命令完整联网采集，exit 0（collect-local-2.json）：
209 条成功、errors=[]、delisted=[]、delisted_count=0、delisted_skipped_count=9、
delisted_total_count=9、attempted_count=209。
repeat-verification.json 根据真实请求日志核对九个下架 URL 均未被请求；
九条下架档案与第一轮完全相同（含首次发现时间/证据），全部 218 个 ID 仍保留。
219 次实际 GET 中 209 次为存续 SKU 详情，另 10 次是既有图片回退检查。
