"""Produce inspectable statistics and the 30-row official comparison."""
from pathlib import Path
import json,random,hashlib,gzip,sys
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from goodsdex.hp_history import validate,apply_history,enrich_store_fields
from goodsdex.retirement import reconcile
here=Path(__file__).parent
bundle=json.loads((ROOT/'data/official/hp-history.json').read_text()); history=bundle['rows']
before=json.loads((here/'baseline-hp.json').read_text()); rows=apply_history(before);rows=[enrich_store_fields(r) for r in reconcile(before,rows)]
for r in history:validate(r)
actual={r['id']:r for r in rows};old={r['id'] for r in before}
new=[r for r in rows if r['id'] not in old]
by_series=defaultdict(Counter)
for r in rows:by_series[r['series']][r.get('generation') or '未明示']+=1
stats=dict(before=len(before),after=len(rows),added=len(new),added_skus=sum(bool(r.get('part_number')) for r in new),
           added_families=sum(r.get('record_level')=='model_family' for r in new),
           added_status=dict(Counter(r.get('status') for r in new)),
           status=dict(Counter(r.get('status') for r in rows)),
           categories=dict(Counter(r['category'] for r in rows)),
           by_series={k:dict(v) for k,v in sorted(by_series.items())},
           with_image=sum(bool(r.get('image')) for r in rows),
           part_number_missing=[dict(id=r['id'],name=r['name'],reason=r['part_number_missing']) for r in rows if not r.get('part_number')],
           image_missing=sum(not r.get('image') for r in rows))
(here/'summary.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n')
captures={}
for c in json.loads(gzip.decompress((here/'support-evidence.json.gz').read_bytes())):
 if c.get('status')==200 and c.get('body'):
  p=json.loads(c['body']).get('data',{}).get('devices',[{}])[0].get('productSpecs',{}).get('data',{})
  if p.get('productNumber'):captures[p['productNumber']]=(c,p)
groups=defaultdict(list)
for r in history:
 if r.get('part_number'):groups[(r['series'],r.get('generation'))].append(r)
chosen=[]
for k,group in sorted(groups.items(),key=lambda x:str(x[0])):
 chosen.append(sorted(group,key=lambda r:r['part_number'])[0])
rng=random.Random(20261105);remaining=[r for r in history if r.get('part_number') and r not in chosen];rng.shuffle(remaining);chosen=(chosen+remaining)[:30]
assert len(chosen)==30
lines=['# 30 条官方逐项对照','',
       '固定种子 20261105，先覆盖系列×代际，再补足 30 个不同货号。官方页的名称来自其产品上下文接口；每行保存实际 POST、HTTP 状态、产品 OID、时间及原响应 SHA256。表内名称为官方原文，配置缩写保留，不推测未明示的存储单位或显卡。','',
       '|库里名称|官方产品上下文名称（链接为官方产品页）|货号|系列 / 代际|HTTP / 一致|',
       '|---|---|---|---|---|']
comparison=[]
for r in chosen:
 c,p=captures[r['part_number']]
 assert c['status']==200 and p['productNumber']==r['part_number'] and p['productName']==r['name']
 assert hashlib.sha256(c['body'].encode()).hexdigest()==r['support_evidence']['response_sha256']
 assert r['generation'] in p['productSeriesName'] if r['generation'] else r['generation_missing']
 text=r['name'].replace('|','\\|');lines.append(f"|{text}|[{text}]({r['source_url']})|{r['part_number']}|{r['series']} / {r.get('generation') or '未明示'}|200 / 是|")
 comparison.append(dict(id=r['id'],name=r['name'],official_name=p['productName'],part_number=r['part_number'],official_part_number=p['productNumber'],series=r['series'],generation=r.get('generation'),official_series_name=p['productSeriesName'],source_url=r['source_url'],request_url=c['url'],request_payload=c['payload'],http_status=c['status'],observed_at=c['observed_at'],sha256=c['sha256'],match=True))
(here/'samples.md').write_text('\n'.join(lines)+'\n');(here/'samples.json').write_text(json.dumps(comparison,ensure_ascii=False,indent=1)+'\n')
samples=[r for r in rows if r.get('sale_status')=='delisted'][:3]
for r in samples:assert r['retired_at']==r['delisted_at'] and r['status']=='retired'
(here/'retired-samples.json').write_text(json.dumps([{k:r.get(k) for k in ('id','name','status','retired_at','source_url')} for r in samples],ensure_ascii=False,indent=1)+'\n')
print(json.dumps({k:v for k,v in stats.items() if k not in ['by_series','part_number_missing']},ensure_ascii=False))
