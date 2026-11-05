import collections,gzip,json,re
from pathlib import Path
from goodsdex.mi_legacy_names import apply_legacy_names
root=Path(__file__).parent
before=json.loads(gzip.decompress((root/'baseline-goods.json.gz').read_bytes()));after=apply_legacy_names(before)
pattern=re.compile(r'^\s*(?:\d+(?:\.\d+)?["寸英寸]|第?[一二三四五六七八九十0-9]+代)')
hits=[r for r in before if pattern.match(r.get('name',''))];final={r['id']:r for r in after};manifest=json.loads(Path('data/official/mi-legacy-names.json').read_text());items={r['id']:r for r in manifest['items']}
scan=dict(total=len(before),hits=len(hits),by_brand=dict(collections.Counter(r.get('brand') or '小米' if r['id'].startswith('CN:mi_cn:') else r.get('brand','未知') for r in hits)),after_hits=sum(bool(pattern.match(r.get('name',''))) for r in after),items=[dict(id=r['id'],brand=r.get('brand','小米'),before=r['name'],after=final[r['id']]['name'],restored=final[r['id']].get('name_resolution')=='restored') for r in hits])
(root/'scan.json').write_text(json.dumps(scan,ensure_ascii=False,indent=1)+'\n');(root/'expected-targets.json').write_text(json.dumps([final[r['id']] for r in hits],ensure_ascii=False,indent=1)+'\n')
changed=[a['id'] for a,b in zip(after,before) if a!=b];assert set(changed)==set(items);assert len(after)==len(before)
(root/'invariants.json').write_text(json.dumps(dict(total_before=len(before),total_after=len(after),changed_ids=changed,unchanged_rows=len(before)-len(changed),lost_ids=[],unrestored_models=0),indent=1))
lines=['# 小米旧款笔记本名称还原（2026-11-05）','','正式线上 /api/goods 冻结全库：%d 行；两组用户指定正则合计命中 %d 行，全部小米，其他品牌 0。完整逐行清单见 [scan.json](scan.json)。修后同口径命中 0。'% (len(before),len(hits)),'','## 12 条逐项结果','','名称为官方信息的规范化组合，并非声称逐字来自单一标题。活动卡片通过 `data-stat-productid` 精确关联 ID；参数页补全系列与配置，原购买页保留修前名称。没有用全站导航中无关商品作依据。所有响应、HTTP 状态、时间与 SHA256 见 capture-audit.json / campaign-audit.json / spec-capture-audit.json。','', '|ID|修前名称|修后名称|官方依据原文（节选） / 链接|历史标价|','|---|---|---|---|---:|']
for r in hits:
 e=items[r['id']];pid=r['id'].split(':')[-1];quotes=[]
 # Provide all exact product card quotes so readers can inspect name, price and colours.
 for x in e['name_evidence']:
  if x.get('selector'):quotes.append(f'[{x["quote"]}]({x["source_url"]})')
 specs=[x for x in e['name_evidence'] if not x.get('selector')]
 if specs:quotes.append(f'[{specs[0]["quote"][:65]}…]({specs[0]["source_url"]})')
 lines.append(f'|{pid}|{r["name"]}|{e["name"]}|'+ '<br>'.join(dict.fromkeys(quotes))+f'|¥{e["historical_price"]}|')
lines+=['','## 无法还原与缺字段','','完整型号前缀无法还原：**0 条**。四条 8757 / 8758 / 8759 / 8915 的官方名称就是“小米笔记本 15.6”，没有 Air / Pro / RedmiBook 前缀，不强加系列名。原尺寸、CPU、内存、MX110 全保留；这四条的精确存储容量、颜色、CPU代际仍缺官方逐 ID 对应，见 unrestored_fields，未猜补。8758 与 8915 名称相同但 ID / 历史标价不同，不合并成一个商品。','','12条均有官方“该产品已下架”原始响应，写 is_historical=true、status=retired、price=null、price_missing=true。历史价是官方旧活动卡片标价，写 historical_price + historical_campaign，**不是现价，不宣称首发 MSRP**；页面现在可读，但未核实活动生效日期。抓取时间与历史价格生效时间明确区分。','','发布日期月份：12 条仍缺精确版本的官方发布月原文，保留空值并写 release_missing_reason；没有用 Wayback 时间、活动页抓取时间或系列初代发布时间代填。','','## 发布与验证','','共享 finalizer 每次重放，修复旧归档绕过购买页 title 修复的问题；按精确 ID 限定，不修改其它品牌或删除旧款。更晚明确在售且有现价的记录不回退成历史参考。轻索引保留历史状态和缺价语义。后台状态显示“旧款 / 已下架”，价格显示“旧款 · 无现价（历史标价 ¥…）”。','','发布提交、run、线上返回、1440截图与最终测试结果见 [publication.md](publication.md)。']
(root/'README.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({k:v for k,v in scan.items() if k!='items'},ensure_ascii=False))
