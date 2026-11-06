import json,gzip,collections,hashlib,tarfile
from pathlib import Path
from goodsdex.mihome_catalog import apply_catalog,norm
from goodsdex.release_coverage import effective
Path('.task-tmp').mkdir(exist_ok=True)
root=Path('docs/mihome-independent-20261106');origin=Path('docs/mihome-catalog-20261106')
changes=json.loads((origin/'changes.json').read_text());m=json.loads(Path('data/official/mihome-catalog.json').read_text());entries={e['id']:e for e in m['items']}
ns={'__name__':'goodsdex.old','__package__':'goodsdex','__file__':str(Path('src/goodsdex/mihome_catalog.py').resolve())};exec((root/'legacy-writer.py.txt').read_text(),ns)
before=json.loads(gzip.decompress((origin/'goods-before.json.gz').read_bytes()));legacy=ns['apply_catalog'](before);after=apply_catalog(legacy)
reviews=[]
for i,c in enumerate(changes,1):
 decisions=[]
 for f in c['fields']:
  a,b=c['before'][f],c['after'][f]
  if f=='name':
   status='回滚' if norm(a)==norm(b) else '待定'
   reason='仅 NFKC/大小写/空白不同；原商城名保留；米家原名独立存入 name_mihome' if status=='回滚' else '语义差异需额外证据'
  else:
   status='真修正';reason='补图证据有效，迁入 image_mihome；官方 image 恢复，展示缺图时降级为设备图标' if f=='image' else '粗类到细类有效，迁入 category_mihome；官方品类恢复，展示选择细类'
  decisions.append(dict(field=f,status=status,reason=reason,before=a,after=b))
 status='待定' if any(d['status']=='待定' for d in decisions) else '回滚' if any(d['status']=='回滚' for d in decisions) else '真修正'
 reviews.append(dict(number=i,id=c['id'],status=status,decisions=decisions))
(root/'review-90.json').write_text(json.dumps(reviews,ensure_ascii=False,indent=2)+'\n')
counts=collections.Counter(r['status'] for r in reviews);fc={f:dict(collections.Counter(d['status'] for r in reviews for d in r['decisions'] if d['field']==f)) for f in ('name','image','category')}
lines=['# 90 条逐条判定','', '记录级：含格式名回滚则归回滚，否则有效补图/细类归真修正；多字段决策逐项列出。真修正指补图/分类证据有效，不表示名称有语义修正。','', '|序号|ID|记录判定|字段判定与原因|','|---|---|---|---|']
for r in reviews:lines.append('|'+ '|'.join([str(r['number']),r['id'],r['status'],'；'.join(d['field']+'：'+d['status']+'，'+d['reason'] for d in r['decisions'])])+'|')
(root/'review-90.md').write_text('\n'.join(lines)+'\n')
lookup={r['id']:r for r in after};examples=[lookup['CN:mi_cn:product:'+k] for k in ['12136','10330','3488']]
fields='id name name_mihome name_source image image_mihome category categories category_mihome miio_model mihome_model mihome_pd_id catalog_display'.split()
(root/'examples.json').write_text(json.dumps([{k:r.get(k) for k in fields} for r in examples],ensure_ascii=False,indent=2)+'\n')
# Source titles already captured by the official-title lane; sample current page again separately.
titles={e['id']:e for e in json.loads(Path('data/official/mi-page-names.json').read_text())['items']}
changed_names=[c['id'] for c in changes if 'name' in c['fields']]
candidates=[k for k in changed_names if k in titles and titles[k]['name']==lookup[k]['name']]
print('counts',dict(counts),'fields',fc,'available title samples',len(candidates),candidates[:10])
(root/'sample-candidates.json').write_text(json.dumps(candidates,indent=2))
(root/'local-summary.json').write_text(json.dumps(dict(record_decisions=dict(counts),field_decisions=fc,dated_before=sum(bool(effective(r)) for r in legacy),dated_after=sum(bool(effective(r)) for r in after),row_count=len(after),date_fields_unchanged=all({k:v for k,v in a.items() if k.startswith(('release','page_first_archived'))}=={k:v for k,v in b.items() if k.startswith(('release','page_first_archived'))} for a,b in zip(legacy,after)),official_fields_restored=all(all(a.get(k)==b.get(k) for k in ('name','image','category','categories')) for a,b in zip(before,after))),ensure_ascii=False,indent=2)+'\n')
Path('.task-tmp/goods-after.json').write_text(json.dumps(after,ensure_ascii=False))
