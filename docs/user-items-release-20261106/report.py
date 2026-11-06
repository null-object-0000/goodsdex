"""Render the 12 per-item evidence records and bounded category-gap report."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
before={r['id']:r for r in read(ROOT/'baseline-targets.json')};after={r['id']:r for r in read(ROOT/'after-targets.json')}
media={c['id']:c for c in read(ROOT/'new-media-candidates.json')};kit=read(ROOT/'new-official-candidate.json')
order=['20833','21630','CN:fuji:kit:x-s20-16-50mm','9726','15061','15755','20545','20807','18520','20981','19409','20276']
ids=[v if v.startswith('CN:') else 'CN:mi_cn:product:'+v for v in order]
probes={p['id']:p for p in read(ROOT/'official-gid-probes.json')}
captures={c['url']:c for p in (ROOT/'evidence').glob('*.json') if (c:=read(p))}
items=ROOT/'items';items.mkdir(exist_ok=True)
status=lambda r: (r.get('release') or {}).get('date') or '空'
lines=['# 用户录入的 12 件物品：发布日期定向补证','',
'本地完成：12 件可展示 **4 → 11**。原来 7 条空白补入 6 条日期，H501 保持 2023-05 并补成双源（展示事件改为发布）；空调伴侣 2 仍空、未验证。同品类仅新增 **2** 条原空缺（BE6500 Pro、小爱音箱 Play）。合计新增 8 条日期、补证更新 1 条，共新增 9 个可展示单品。', '',
'依据：**official 1 条**（富士套机美国公布月份），**third_party 双原始来源 8 条**（用户 6 件 + 同类 2 件）。所有第三方均交由现有 `third_party_release.assess` 判定；同事件、不同媒体原始域、不同正文哈希，均 corroborated / delta_days=0。没有用 LLM 作第二来源。','',
'**日期事件不可混读**：富士 2024-05 是美国官方公告单独列出的 X-S20 + XF16–50 完整套机公布月份，显示“美国推出月份（官方回溯）”，不是国行首销；公告中预计 2024-06 上市没有当作实际首销写入。音箱 Pro、H501 也是 announcement，其余本轮新增为 availability。沿用仓库 event/market 定义及既有门禁。','',
'| # | 物品 | 之前 | 之后 | 依据 / 事件 |','|---|---|---|---|---|']
records=[]
for n,key in enumerate(ids,1):
    a=before[key];b=after[key];r=b.get('release') or {};old=a.get('release') or {}
    evidence=[];note=''
    if key in media:
        evidence=[s['evidence'] for s in media[key]['assertions']]
        conclusion=r['date']+'，可展示（third_party 双源，'+r['event']+'）'
        if key.endswith(':18520'):note='两家原始媒体均明确 2023-05-25 公布 H501；仅用 announcement 互证。旧 2023-05 上市原句与独立 LLM 2023-08 反证完整保留在 previous_release，旧 candidate 另存 h501-superseded-candidate.json；原 data/llm/release-crosschecks.json 不改。旧反证绑定旧 family/hash，没有拿它反证新 announcement 或作为第二来源。'
    elif key==kit['ids'][0]:
        evidence=[r['evidence']];conclusion='2024-05，美国公布完整套机（official，announcement）；实际首销 / 国行首销仍未验证'
        note='核对本行“含镜头”=XF16-50mmF2.8-4.8 R LM WR，与公告套机 bullet 完全一致。日期来自公告自身 05/16/2024；不继承机身 2023-06，也不采用镜头预计上市月代替套机实际首销。curl 403 已留档；实际采用浏览工具读取的官方网页文本，sha256 对应该工具文本原字节，capture_type=web_tool_page_text，非 HTTP 原 HTML。'
    elif key.endswith(':9726'):
        conclusion='未找到满足现有双源门禁的日期证据，未验证；保持空白'
        note='快科技回顾明确单品 2019-05-07 开售；IT之家只说“近日发布”，无法提供同事件精确日。CNMO 有原创开售报道但不在现有第三方允许来源内，未放宽来源门禁。没有把文章发表日冒充发布日，也不把多只套装日期当单品日期。'
        for u in ['https://news.mydrivers.com/1/629/629476.htm','https://www.ithome.com/0/422/457.htm','https://tech.cnmo.com/news/661874.html']:
            c=captures[u];t=Path(c['text_file']).read_text();q='米家空调伴侣2于5月7日开售' if 'mydrivers' in u else '近日，小米米家发布了最新的空调伴侣2' if 'ithome' in u else '近日米家上架了新款的米家空调伴侣2'
            i=t.find(q);evidence.append(dict(**c,quote=t[i:i+140] if i>=0 else '参见留档全文；未用于日期断言'))
    else:
        evidence=[r['evidence']];conclusion=r['date']+'，沿用已核发布集可展示值，本轮不改'
        note='按任务给定现状直接采信；原 evidence 字段和 release 对象完整不变，未将既有条目计作新增。'
    prefix=f'{n:02}-{key.split(":")[-1]}';path=items/(prefix+'.md')
    item=dict(id=key,name=a['name'],before=old,after=r,conclusion=conclusion,note=note,evidence=evidence)
    records.append(item)
    content=[f'# {a["name"]}','',f'- id：`{key}`',f'- 之前：{status(a)}'+('（不可展示）' if old.get('display_allowed') is False else ''),f'- 结论：{conclusion}','',note,'']
    for i,e in enumerate(evidence,1):
        content += [f'## 来源 {i}','',f'- URL：{e["url"]}',f'- 抓取时间：`{e.get("captured_at","未验证")}`',f'- SHA256：`{e.get("sha256","未验证")}`',f'- 原文片段：{e.get("quote","未找到")}',f'- 原始留档：`{e.get("capture_file") or e.get("raw_file") or "沿用发布集 evidence；见 baseline-targets.json"}`','']
    if key in probes:
        p=probes[key];c=p['capture'];content += ['## 本轮官网接口核查','',f'URL：{c["url"]}；HTTP {c["status"]}；抓取时间 `{c["captured_at"]}`；SHA256 `{c["sha256"]}`。',f'参数与完整响应：`{c["raw_file"]}`；本次未取得可用发布时间字段，不能据此断言“官方无日期”。','']
    path.write_text('\n'.join(content))
    after_label=r.get('date') or '空（未验证）'
    if key.endswith(':18520'):after_label+='（补证解锁）'
    typ='official / 美国 announcement' if key==kit['ids'][0] else '双源 / '+r['event'] if key in media else '未验证' if not r else '沿用发布集'
    lines.append(f'| {n} | [{a["name"]}](items/{path.name}) | {status(a)}'+('（不可展示）' if old.get('display_allowed') is False else '')+f' | {after_label} | {typ} |')
write(ROOT/'items.json',records)
lines+=['','## 同品类扩展与边界','', '| id | 商品 | 新增日期 | 依据 |','|---|---|---|---|']
for key in ['CN:mi_cn:product:19332','CN:mi_cn:product:10015']:
    c=media[key];day=c['assertions'][0]['date'];lines.append(f'| `{key}` | {c["name"]} | {day[:7]} / availability | third_party 双源 |')
lines+=['','两条扩展的每个 URL、原句、抓取时间和 SHA256 见 [新增双源清单](new-media-candidates.json)。BE6500 Pro 采用其自己 2023-10-31 开卖证据，与用户的 BE6500（2024-08-16 开卖）分别核实；Play 不与增强版 / Redmi Play 合并。','',
'扩展官方探测范围限定宠物饮水机、路由器、智能门锁、小爱音箱、除湿机、智能家庭/插座的当前空缺，加上 12 件中的小米条目，共 77 个精确产品。完整 [范围](official-scope.json)、[官网探测](official-probes.json)、[带 gid 重试](official-gid-probes.json) 均落盘；未扩展相机同类或其他全库品类。','',
'未进入生产数据的发现：米家智能除湿机 22L 有 2021-10 众筹发布、2021-12 再次“推出/预售”的报道，未贸然统一事件；13L 只抓到单一媒体明确首销与另一家预售，未混事件凑双源。智能插座基础版未找到满足规则的原始日期双源。饮水机 2 除菌版在当前发布快照已可展示，未覆盖原数据或计新增。其余类别探测未取到日期的不编值；这不表示全互联网均无资料。','',
'## 落地与验证','',
'主输入：`data/official/release-dates.json` 新增 8 条候选、替换 H501 1 条（保存旧候选）；依照已有链路，同时在 `data/third-party/release-dates.json` 新增 8 组双源断言。只写主输入无法通过既有第三方门禁，因此必须保留这份 sidecar。没有新增导入逻辑，没有改发布门禁、release_policy、允许来源或判定阈值。','',
'冻结基线：代码 `5b6dddc7`；已在本地的 data 分支快照 `2cd5f4173b420a8c51b674a293313f544233f4e7:public/goods.json.gz`，4491 行。本轮未 fetch / push、未开 PR、未触发 workflow、未部署；主仓未写入。','',
'[本地验收结果](verification.json)：实际 `finalize_public` + `build_shards` 生成 4491 行；9 个本轮条目的 release 与详情分片一致，原 4 件可展示值完整不变。输入重放幂等，相对旧代码输入恰好 9 个 release 变化，非 release 字段不变。此为本地生成验收，不声称已上线。','',
'测试命令：','```bash','PYTHONPATH=src:scripts /var/tmp/user-items-release-venv/bin/python -m pytest -q tests/test_release_dates.py tests/test_release_crosschecks.py tests/test_release_scope_media.py tests/test_official_retrospective_release.py tests/test_release_candidate.py tests/test_release_policy.py tests/test_dedupe.py tests/test_shards.py tests/test_date_enrichment.py tests/test_series_release.py tests/test_series_release_rollout.py tests/test_release_precision.py tests/test_product_sources.py tests/test_lineage.py','```','',
'结果：`162 passed in 49.43s`（[原始日志](tests.log)）。原始工具文本改为 gzip 留档以完整保留空白字节后，针对证据格式再次验证：`22 passed in 1.98s`（[日志](capture-format-tests.log)）。3 个测试文件只更新新增证据的固定期望、留档路径与旧证据保留断言；没有放宽生产规则。','',
'复算：`PYTHONPATH=src:scripts python docs/user-items-release-20261106/verify.py`；需要已存在的上述冻结 data git 对象。`capture.py` / 采集脚本另需 beautifulsoup4，产品运行时无新依赖。','',
'## 提交状态','', '提交后实际执行的 `git log --oneline -2` 与 `git status --porcelain` 原文见最终交付消息，避免在同一提交内伪造自引用 commit hash。']
(ROOT/'README.md').write_text('\n'.join(lines)+'\n')
# The category gap ledger never promotes probe failures or empty fields to verified absence.
changed=set(media)|{kit['ids'][0]}
write(ROOT/'category-gap-ledger.json',[dict(**r,result='本轮补证；见清单' if r['id'] in changed else '本轮未写新日期；未验证' if r['id'] not in before else '原有值沿用；未计新增') for r in read(ROOT/'official-scope.json')])
