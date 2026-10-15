# A / B 复核与修复报告

复核日期：2026-10-15（北京时间）。代码基线 `1b86ec1`；数据基线 `2aadd93`（用户预置的 gdx-data 工作树 HEAD）。修改分支 `fix/archive-partial-missing`，仅本地提交，不 push。

## 1. 独立复核结论

### 缺陷 A 成立，但原说明有几处表述需要收窄

- 基线 `pipeline.py:287` 未向 `merge_archive` 传完整性；基线 `archive.py:108-115` 对所有未见 ID 无条件写 `missing_since`。用已有 A、B 两件商品的档案，模拟只返回 A 的 partial 采集，旧实现确实给 B 写了缺席时间。新测试在改生产代码前运行：**6 failed / 1 passed**，失败均包含实际误写 `missing_since`，不是因新增参数不兼容而失败。
- 数据基线家电档案 589 条，快照 490 条，缺席 99 条；快照的 `discovery` 是 `found=357 / total_reported=778 / partial / max_pages_reached`。490 包含容器展开，不能把它当搜索枚举条数。旧 `pages_fetched=21` 还有越界计数问题，实际限额是 20 页。
- **99 条时间戳并不相同**：10-15 07:41:33 为 59 条，10-13 10:35:42 为 23 条，10-14 08:20:55 为 15 条，10-12 08:06:20 为 2 条（均 +08:00）。滚动积累方向成立。数据历史依次是 `c7c15e4:43 → e4c2bff:64 → 2b150e2:82 → a46332f:107 → a0d4104:99`；提交标题的 UTC 日期不等于本地采集日期。
- 99 条里确有 **16 个 ID 不在发布集**。不过这不是 `missing_since` 直接造成的：`src/goodsdex/publish.py:66` 只遍历分类快照，不读取档案或缺席标记。短快照同时造成假缺席与发布遗漏，二者共享采集覆盖不足的原因。
- 指定的 8 个 ID 均成功取得 `code=200` 和非空 `data.goods_list`。`13117` 熨烫机首项 `goods_info` 为价格 499、`is_sale=true`、`is_stock=true`；`15061` 净化器为 599、true、true。但 `16735` 水壶为 189、true、**false**，`16725` 吹风机首变体也为 false，所以“8/8 全部有货”不能照搬。注意销售/库存标志在 `data.goods_list[*].goods_info` 下，不在 `data` 顶层。
- 对 99 件发起详情核对时，57 件取得非空 goods_list，42 件 HTTP 429；未把限流算下架，也未证明 99 件全都在售。8 个样本足以证明存在假缺席，不足以外推全部 99 件。

以上数据可用下面的只读命令复核（无需新增工作树；后续在线结果会随时间变化）：

```bash
PYTHONPATH=src python3 - <<'PY'
import json, subprocess
from collections import Counter

def load(path):
    return json.loads(subprocess.check_output(['git', 'show', '2aadd93:' + path], text=True))
a = load('data/archive/家电.json')
c = load('data/categories/家电.json')
pub = {r['id'] for r in load('public/goods.json')}
missing = {k: v for k, v in a['items'].items() if v.get('missing_since')}
print(a['count'], a['present'], a['missing'], len(c), c[0]['discovery'])
print(Counter(v['missing_since'] for v in missing.values()))
print('发布集缺少的旧 missing ID 数', len(missing.keys() - pub))
PY
# 查看上述历史版本，无需切换分支：
git log -5 --format='%h %s' 2aadd93 -- data/archive/家电.json
```

### 缺陷 B 成立；分页上限不是唯一的不完整来源

基线枚举、pipeline 默认值和两个 CLI 入口均为 20 页，见本次修改对应位置：`src/goodsdex/sources/mi_cn.py:188`、`src/goodsdex/pipeline.py:178,334`、`scripts/crawl_all.py:54`。

首次独立线上枚举显式给 100 页，`pause=0`：得到 **710 / 780，41 页，no_sellable_items**，耗时 37.09 秒。修复后使用新默认值、不传 max_pages：得到 **713 / 780，41 页，partial / no_sellable_items**，耗时 45.75 秒。官方总数已经从历史的 778 变成 780。提高限额确实找回很多商品，但连续空页早停仍不能声称覆盖全集。

```bash
PYTHONPATH=src python3 - <<'PY'
import urllib.request
from goodsdex.sources import mi_cn
# 此脚本只在进程内对小米直连，不修改系统代理。
urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler({})))
e = mi_cn.enumerate_products('家电')
print(e['discovery'])
PY
```

### 五个空分类：官方关键词映射与接口返回共同造成，不能据此认定下架

通过 `mi_cn.list_categories()` 获取的关键词及同一搜索接口第一页响应如下，均为 `code=200`、`pc_list=[]`，`list_v2` 也没有提供可补录的商品。当前未复现 `total_reported=None`。旧空快照是 `[]`，无法从该文件恢复当时的 discovery，也不能反推当时为何缺 total。

| 分类 | 官方关键词 | 当前 total | 换词探针（仅调查，不修改分类） |
| --- | --- | ---: | --- |
| 儿童滑板车 | 儿童滑板车 | 55 | 滑板车仍是 55、空 pc_list |
| 收纳袋 | 收纳袋 | 11 | 收纳返回 4 项，不证明是收纳袋 |
| 毛巾/浴巾 | 毛巾 | 55 | 浴巾返回 1 项，却是 ID 14521“米家浴霸安装服务” |
| 米家跑步机 | 跑步机 | 11 | 跑步返回 4 项，不证明是跑步机 |
| 驱蚊器 | 驱蚊器 | 55 | 驱蚊返回 3 项，含空调健康滤网、挂机驱蚊滤网、电蚊拍 |

证据说明接口确有“非零 total 但无商品列表”的行为，关键词也显著影响结果；宽化关键词会引入模糊匹配污染。不能把非零 total 简单解释成同数量的在售商品，也不能把空列表解释成官方没有商品。因此保留原分类/命名，未补造记录、未改关键词。

复现时用上面的直连初始化，再执行：

```python
cats = mi_cn.list_categories()
for name in ['儿童滑板车', '收纳袋', '毛巾/浴巾', '米家跑步机', '驱蚊器']:
    kw = cats[name]
    print(name, kw, mi_cn.enumerate_products(kw)['discovery'])
for kw in ['滑板车', '收纳', '浴巾', '跑步', '驱蚊']:
    e = mi_cn.enumerate_products(kw)
    print(kw, e['discovery'], [(r['pid'], r['name']) for r in e['items']])
```

详情样本复现（需留意 HTTP 429；失败不表示缺货）：

```python
import json, urllib.parse
for pid in ['15061', '13117', '10050167', '10050211', '11216', '14905', '16725', '16735']:
    url = mi_cn.VIEW_URL + '?' + urllib.parse.urlencode({'product_id': pid, 'version': 2})
    try:
        d = json.loads(mi_cn._get(url, retries=0))
        flags = [g.get('goods_info', {}) for g in (d.get('data') or {}).get('goods_list', [])]
        print(pid, d.get('code'), [(g.get('product_id'), g.get('price'),
              g.get('is_sale'), g.get('is_stock')) for g in flags])
    except Exception as e:
        print(pid, type(e).__name__, str(e))
```

## 2. 修复规则与范围

`src/goodsdex/archive.py:64-153`：新增可选 discovery 参数；不提供时默认不完整。只有以下白名单能新增缺席标记：

1. `completeness=complete`，明确的非负整数 total/found，`found >= total`，且 `stop_reason=reached_total`。
2. `completeness=complete`，`stop_reason=empty_page`，且 `total=found=0`：接口明确报零且列表为空。

`partial / failed / unknown / no_sellable_items / max_pages_reached / no_new_items` 都不授权缺席；即使 complete 标签与这些早停原因矛盾也拒绝。total 未知也拒绝。`no_sellable_items` 不论少 1、2 件还是更多，都不能证明覆盖完整。

不完整观测只更新实际见到的商品，未见条目保持原状；见到旧 missing 商品仍可正常复活，不需要等 complete。档案增加 `last_discovery`、`last_incomplete_at`、`last_incomplete_reason`，后续完整观测保留最后一次不完整观测线索。`missing` 统计实际带标记条目；`present=count-missing` 表示未标缺席，不能当本次实见数或已证实在售数。

`src/goodsdex/pipeline.py:185-237,275-294`：传递 discovery；limit 截断、主商品或容器子商品采集抛异常都降级 partial。失败空响应保留旧快照时仍记录不完整档案观测，避免原来的提前 return 绕过记录。

`mi_cn.py:188-295` 及两处 CLI 默认值：统一把分页上限从 20 提高至 100（正常每页 20 条时容量 2000）；显式更小上限仍有效。达到上限或有结果但未达 total 的空页早停保持 partial，接口错误保持 failed。修正 pages_fetched 的越界计数。保留零条结果时的旧状态名称 no_sellable_items，以兼容既有产物，但不再赋予“已经证明没有在售”的解释。

未更改 `public/goods.json` 的字段、发布筛选或分类规则；档案是向后兼容的字段增加。未手改现有数据。快照仍表示本次观测，partial 时发布集仍可能只含已抓到商品；本次扩大分页修复已知 20 页瓶颈，未把历史档案混入当前快照冒充本次观测（见 `publish.py:66`）。

## 3. 下一次采集的可验证恢复预期

不能承诺下一次一定 complete，也不能承诺 99 件全部恢复。首次实搜 710 个 ID 与历史 99 个 missing ID 交集是 **75**；历史从发布集消失的 16 个 ID 中有 **15** 在这 710 个里。假定这组 ID 保持可发现、详情采集成功，则下一次应至少复活这 **75 条**旧缺席记录，至少 **15 个**遗漏 ID 应回到发布集；容器展开还可能带回其他条目。

已在临时目录复制家电档案，用这 710 个实搜 ID 做仅验证身份集合的离线合并（不是详情重采）：`revived=75, went_missing=0, missing=24`。即使这次还是 partial，也能复活见到的商品，并且不会给其余未见商品加新章。如果未来有真正 complete 的采集，恢复数严格等于“旧 missing 集合与成功采集集合的交集”，99 是这批旧标记的恢复上限，而不是已经证实的必达值。

下面的命令重新在线枚举并计算当时的恢复下界，不写任何档案：

```bash
PYTHONPATH=src python3 - <<'PY'
import json, subprocess, urllib.request
from goodsdex.sources import mi_cn
urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler({})))
def load(p):
    return json.loads(subprocess.check_output(['git', 'show', '2aadd93:' + p], text=True))
a = load('data/archive/家电.json')
m = {k for k, v in a['items'].items() if v.get('missing_since')}
p = {r['id'] for r in load('public/goods.json')}
e = mi_cn.enumerate_products('家电')
s = {'CN:mi_cn:product:' + str(r['pid']) for r in e['items']}
print(e['discovery'])
print('可预期直接复活', len(m & s), '可预期重回发布集', len((m - p) & s))
print('待容器展开或后续观测验证', sorted(m - s))
PY
```

## 4. 测试与耗时

有鉴别力的新增测试在 `tests/test_archive_coverage.py`、`tests/test_search_pagination.py`；原 `tests/test_archive.py` 中“未见即下架”的测试补上明确完整证据，同时新增对应 partial 反例，未放宽断言。`tests/test_failure_semantics.py` 的空页测试修正文义，并由分页测试中的“有结果但未达 total”反例限定旧状态名的含义。

覆盖：完整/partial 对照、缺证据/矛盾元数据、既有 missing 保留、partial 更新价格及复活、limit 截断、主商品/容器子商品失败、失败空快照保护及档案记录、完整零结果、跨 20 页边界（模拟 778 件需 39 页）、显式页数上限、空页/重复页提前终止、部分结果后接口失败、两个 CLI 默认上限。

执行：`PYTHONPATH=src:scripts python3 -m pytest tests/ -q`；最终结果见本节末尾。环境原先没有 pytest，使用 uv 安装测试依赖，没有改 requirements 或运行时依赖。另执行 `git diff --check`。

耗时估算依据：仓库本地 `data/_progress.json` 共计 1415.4 秒，家电 494 件用 188.2 秒；`.github/workflows/crawl-all.yml` 设置 runner 约慢 5 倍、workers=4、预算 150 分钟。按历史搜索 357 → 当前 713，最多约新增 356 次主商品详情任务（与已有容器子商品有交集，所以不能简单视为最终净增 356 件）。用历史每件 `188.2/494≈0.38` 秒粗估，本地详情增加约 136 秒，runner 约 11.3 分钟。搜索额外约 21 页，以实测整次枚举 45.75 秒作保守增量上界再乘 5，约 3.8 分钟，合计约 **15 分钟量级**。

这只是粗算：基线全量 23.6 分钟乘 5 约 118 分钟，加约 15 分钟约 133 分钟，接近但低于 150 分钟预算；未计其他大类突破 20 页后的额外商品、429 重试和容器展开变化，不能保证不超时。100 是最大限额，不是强制请求 100 页，小分类仍按原早停结束。没有为压缩时间而降完整性标准，也没有改 workflow 超时或并发。

最终验证：全量 **178 passed in 25.31s**；定向回归 **39 passed**；`git diff --check` 通过。

## 5. 提交与工作树

仅修改 A/B 所需实现、回归测试和本报告。分支为 `fix/archive-partial-missing`，不 push。没有创建临时 Git 工作树；用户预置的 gdx-data 工作树仅只读访问，未删除或修改。离线档案回放用 TemporaryDirectory，完成即自动清理。

## 我不确定的地方

- 小米 search 的 total 与返回 pc_list 之间的精确定义，以及非零总数但空列表的业务原因；本次没有足够官方证据把它判成全部下架或售罄。
- 99 件旧 missing 中全部商品的当前销售/库存状态：42 件详情请求被 429 拦住，且销售/库存本身会变化。已有 8 个成功样本不等于全量证明。
- 下一次是否能完整覆盖官方总数、容器展开能额外恢复多少件；75/15 是基于首次实搜集合、采集成功这一前提的恢复下界，不是未来网络结果保证。
- 未在 GitHub runner 跑全量，150 分钟内完成只是条件估算。批量详情复核出现限流，实际退避可能明显拉长耗时。
- `missing_since` 即使来自完整搜索也只证明未在该搜索范围出现，不严格等同官方下架。保留既有字段名与语义范围，没有扩大成库存证明。
- 背景的价格 30/30、96,911 条 locator、10,262 个 hash、全档案 3,638 条，以及跨分类重复/kind/参数问题不属于 A/B 必需复核范围，本轮未重新验证，也未据此改无关代码。
