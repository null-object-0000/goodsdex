"""Build a frozen, reviewable backfill only after the 20-product Xiaomi gate."""
import gzip
import json
import sys
from collections import Counter
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from verify_source_urls import is_official
root=Path(__file__).resolve().parent
rows=json.loads(gzip.decompress((root/'baseline-goods.json.gz').read_bytes()))
samples=json.loads((root/'samples.json').read_text())
# Existing marketplace URLs must never count as official page validation.
for s in samples:
    if not is_official(s['brand'],s['url']) or not is_official(s['brand'],s['final_url']):
        s.update(passed=False,reason='已有非官方链接（保留，不作为官方验证通过）')
(root/'samples.json').write_text(json.dumps(samples,ensure_ascii=False,indent=2)+'\n')
mi=[s for s in samples if s['brand']=='小米']
assert len(mi)==20 and len({s['id'] for s in mi})==20
passed={s['id'] for s in mi if s['passed']}
failed={s['id'] for s in mi if not s['passed']}
full=len(passed)/20>=.8
approved=[]
from verify_source_urls import normalize
for r in rows:
    if r['brand']!='小米' or r.get('source_url') or r['id'] in failed:continue
    if not full and r['id'] not in passed:continue
    suffix=r['id'].removeprefix('CN:mi_cn:product:')
    if not suffix.isascii() or not suffix.isdigit():continue
    approved.append(dict(id=r['id'],name=r['name'],url='https://www.mi.com/shop/buy/detail?product_id='+suffix))
# Same-ID projections may occur: approval is one identity/name, and replay preserves all rows.
approved=list({(a['id'],a['name']):a for a in approved}.values())
assert len({a['id'] for a in approved})==len(approved)
manifest=dict(schema=1,rule='CN:mi_cn:product:<digits> => https://www.mi.com/shop/buy/detail?product_id=<digits>',
              sample_seed=20261104,minimum_interval_seconds=2.15,threshold=.8,samples=mi,approved=approved)
Path('data/official/source-url-backfill.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
summary={}
for brand in sorted({r['brand'] for r in rows}):
    items=[s for s in samples if s['brand']==brand]
    summary[brand]=dict(sampled=len(items),passed=sum(s['passed'] for s in items),ratio=sum(s['passed'] for s in items)/len(items) if items else None,reasons=dict(Counter(s['reason'] for s in items)))
(root/'sample-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
lines=['# 逐条抽样结果','', '随机种子 20261104；小米从缺 URL 的1482行抽20行，其它品牌从现有发布行抽取。比亚迪14行和小米汽车3行均全查。间隔≥2.15秒；判定仅使用商品页title/h1/h2，未用全站导航中的名称。','', '|品牌|商品ID / 名称|请求URL|HTTP|最终URL|标题片段|相似度 / 关键型号|判定|', '|---|---|---|---:|---|---|---|---|']
for s in samples:
    clean=lambda v:str(v).replace('|','\\|').replace('\n',' ')
    lines.append('|'+ '|'.join(map(clean,[s['brand'],s['id']+' / '+s['name'],s['url'],s['status'],s['final_url'],s['title'][:100],str(s['score'])+' / '+str(s['model_hit']),s['reason']]))+'|')
(root/'samples.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(dict(full=full,approved=len(approved),summary=summary),ensure_ascii=False,indent=2))
