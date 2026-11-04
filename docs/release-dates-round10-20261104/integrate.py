"""Integrate reviewed evidence only; preserve locked product/series assertions."""
import gzip,json,pathlib
from goodsdex.release_dates import digest
from goodsdex.series_release import identity
ROOT=pathlib.Path(__file__).resolve().parent
rows=json.loads(gzip.decompress((ROOT/'baseline.json.gz').read_bytes()));idx={r['id']:r for r in rows}
cs=json.load(open(ROOT/'new-candidates.json'))+json.load(open(ROOT/'apple-new-candidates.json'))
ids={i for c in cs for i in c['ids']};p=pathlib.Path('data/official/release-dates.json');b=json.load(open(p))
old=[c for c in b['candidates'] if ids.intersection(c['ids']) and c['family'] not in {x['family'] for x in cs}]
if not (ROOT/'replaced-candidates.json').exists():(ROOT/'replaced-candidates.json').write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n')
for c in old:assert c['release']['source']=='third_party', 'Never replace official/LLM sample universe'
for c in b['candidates']:c['ids']=[i for i in c['ids'] if i not in ids]
b['candidates']=[c for c in b['candidates'] if c['ids']]+cs
p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
p=pathlib.Path('data/official/series-releases.json');b=json.load(open(p));managed={m['id'] for a in b['batches'] for m in a['members']};new=[]
cap=json.load(open(ROOT/'evidence/53179b5d4ec4eb226ca8.json'));data=json.load(open(ROOT/'mi-history-structured.json'))
hist=next(json.loads(s['body']['content'])['data'] for s in data['main_body']['section'] if 'about_history' in s['body'].get('content',''))
for key,y,m,name,needle in [('CN:mi_cn:product:3488','2016','03','米家压力IH电饭煲','米家压力IH电饭煲'),('CN:mi_cn:product:6334','2017','07','小米AI音箱','小米AI音箱')]:
 batchid='round10-history:'+key
 if key in managed:continue
 paragraph=next(t for a in hist for year,months in a.items() if year==y for month,ts in months.items() if month==m for t in ts if needle in t)
 e={k:cap[k] for k in ('url','sha256','captured_at')};e.update(quote=paragraph,date_context=f'{y}年{m}月',locator=f'$GLOBAL_PAGE.PageData.main_body.section / about_history.data / {y}/{m}',source_type='official',capture_type='embedded_json',capture_file=str(ROOT.relative_to(pathlib.Path.cwd())/'evidence/53179b5d4ec4eb226ca8.html'))
 batch=dict(id=batchid,series=name,generation=f'官网发展历程{y}-{m}原始发布代',series_release=dict(date=f'{y}-{m}',granularity='month',source='official',level='series',market='CN',event='announcement',evidence=e),members=[dict(id=key,identity_sha256=digest(identity(idx[key])),identity_reason='精确基础型号与官网历史产品名匹配，不包含升级代、加配套装或不同容量；只写系列时间，原单品日期不变')])
 new.append(batch)
b['batches']+=new;p.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n');(ROOT/'new-series-batches.json').write_text(json.dumps([a for a in b['batches'] if a['id'].startswith('round10-history:')],ensure_ascii=False,indent=2)+'\n')
print('product candidates',len(cs),'new series',len(new))
