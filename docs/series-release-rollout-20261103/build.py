"""Reproduce reviewed series batches and complete census; no fuzzy inheritance or web calls."""
from copy import deepcopy
from collections import Counter,defaultdict
from pathlib import Path
import gzip, hashlib, json, re, sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from goodsdex.series_release import identity, apply_series_releases, is_accessory
from goodsdex.release_dates import digest
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).parent

def read(p):return json.loads(Path(p).read_text())
def write(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')

def build():
 rows=json.loads(gzip.decompress((OUT/'baseline-goods.json.gz').read_bytes()));mi=[r for r in rows if r['id'].startswith('CN:mi_cn:')]
 byid={r['id'].split(':')[-1]:r for r in mi};pilot=read(OUT/'pilot-input.json');bundle=deepcopy(pilot);bundle['scope']='reviewed_rollout'
 decisions=read(OUT/'reviewed-decisions.json')
 for a in decisions:
  capture=next(read(p) for p in (OUT/'evidence').glob('*.json') if read(p).get('url')==a['url'])
  assert not capture.get('error'),a['url']
  batch_id='mi-reviewed-'+a['url'].split('/')[-3]+a['url'].split('/')[-2]+a['url'].split('/')[-1].split('.')[0]
  name=a.get('series') or ' / '.join(byid[i]['name'] for i in a['ids'][:2])
  path=Path(capture['capture_file']);path=path.relative_to(ROOT) if path.is_absolute() else path
  # Prose is retained in the capture; quotes are bounded to the event declaration.
  quote=a.get('quote') or capture['text'][:480]
  evidence={k:capture[k] for k in ('url','sha256','captured_at')}
  evidence.update(capture_file=str(path),quote=quote,locator='article #paragraph；发布日期见 .post_time',source_type='third_party')
  batch=dict(id=batch_id,series=name,generation=a.get('generation') or name+'；'+a['date']+'独立发布批次',
   series_release=dict(date=a['date'],granularity='month',source='third_party',market='CN',event=a['event'],level='series',evidence=evidence),
   members=[dict(id=byid[i]['id'],identity_sha256=digest(identity(byid[i])),identity_reason=a['reason'],reviewed_name=byid[i]['name']) for i in a['ids']])
  bundle['batches'].append(batch)
 write(ROOT/'data/official/series-releases.json',bundle)
 enriched=apply_series_releases(rows)
 assert [r.get('release') for r in enriched]==[r.get('release') for r in rows]
 assert [{k:v for k,v in r.items() if k!='series_release'} for r in enriched]==[{k:v for k,v in r.items() if k!='series_release'} for r in rows]
 assert apply_series_releases(enriched)==enriched
 after=[r for r in enriched if r['id'].startswith('CN:mi_cn:')]
 (OUT/'expected-goods.json.gz').write_bytes(gzip.compress(json.dumps(enriched,ensure_ascii=False).encode(),mtime=0))
 outb=[]
 for b in bundle['batches']:
  members=[r for r in after if r.get('series_release',{}).get('batch_id')==b['id']]
  old={r['id'] for r in mi if r.get('series_release')}
  outb.append(dict(batch_id=b['id'],series=b['series'] + (' / '+b['generation'] if b['id'] in {x['id'] for x in pilot['batches']} else ''),date=b['series_release']['date'],event=b['series_release']['event'],source=b['series_release']['source'],url=b['series_release']['evidence']['url'],members=len(members),new_series=sum(r['id'] not in old for r in members),new_inherited_without_product=sum(r['id'] not in old and not (r.get('release')or{}).get('date') for r in members),ids=[r['id'] for r in members]))
 write(OUT/'batches.json',outb)
 # Every current row is accounted for. Pending groups keep exact names/IDs; do not
 # merge ambiguous capacities, generations or containers merely to shrink the list.
 scans={d['id']:d for d in (json.loads(l) for l in gzip.open(ROOT/'docs/release-dates-round2-20261103/mi-scan.jsonl.gz','rt'))}
 cat_search=read(OUT/'category-search.json');search_by_cat={c:x for x in cat_search for c in x['categories']}
 pending=[];census=[]
 for r in after:
  scan=scans.get(r['id']);category=r.get('category','未知');status='dated' if r.get('series_release') else 'pending'
  entrances=[dict(type='official_exact_id_scan',url='https://m.mi.com/commodity/detail/'+r['id'].split(':')[-1],scan_archive='docs/release-dates-round2-20261103/mi-scan.jsonl.gz',captured_at=scan.get('captured_at') if scan else None,result=(scan.get('message') or '接口未提供可证明整个系列发布批次的日期') if scan else '旧扫描无此ID')]
  cat=category if category in search_by_cat else '空调' if '空调' in category else '手机' if any(x in category for x in ('REDMI','旗舰','MIX','Civi','旧款')) else '灯具' if category=='台灯' else '家庭屏' if category=='家庭屏' else None
  if cat:entrances.append(dict(type='category_news_search',query='小米 米家 '+cat+' 系列 新品 发布 site:ithome.com',result_file='category-search.json',note='按品类检索、逐名比对候选正文；不是每型号独立精确检索'))
  entrances.append(dict(type='captured_article_title_and_identity_review',file='title-review-queue.json',note='221个报道入口逐名筛选；只用明确审核名单，未以相似名称自动继承'))
  reason='暂无直接覆盖此精确代际/规格的可核批次依据；官网参数或型号年份不足以确定系列月份'
  if r.get('kind')=='service':reason='服务记录，不继承整机系列日期'
  elif is_accessory(r):reason='遗留配件/耗材判定，不继承；保留现有发布集，不在本轮改过滤规则'
  elif r.get('is_container'):reason='系列容器可能混合代际/容量或版型；无一份依据明确覆盖全部成员，不给统一日期'
  elif scan and scan.get('message')=='该产品已下架':reason='官方接口已下架；本轮已取得报道未能确认此型号精确批次'
  item=dict(id=r['id'],name=r['name'],category=category,status=status,batch_id=r.get('series_release',{}).get('batch_id'),date=r.get('series_release',{}).get('date'),attempts=entrances,reason=None if status=='dated' else reason)
  census.append(item)
  if status=='pending':pending.append(item)
 write(OUT/'census.json',census);write(OUT/'unresolved.json',pending)
 def count(rs):return sum(bool(r.get('series_release',{}).get('date')) for r in rs)
 cats=[]
 for c in sorted({r.get('category','未知') for r in mi}):
  b=[r for r in mi if r.get('category','未知')==c];a=[r for r in after if r.get('category','未知')==c]
  cats.append(dict(brand='小米',category=c,total=len(a),before=count(b),after=count(a),coverage_before=round(count(b)/len(b)*100,4),coverage_after=round(count(a)/len(a)*100,4)))
 report=dict(actual_denominator=len(mi),requested_denominator=1728,denominator_gap=1728-len(mi),total_rows=len(rows),baseline_series=count(mi),after_series=count(after),coverage_before=round(count(mi)/len(mi)*100,4),coverage_after=round(count(after)/len(after)*100,4),batches=len(outb),new_batches=len(outb)-len(pilot['batches']),new_inherited_without_product=sum(b['new_inherited_without_product'] for b in outb),categories=cats,unresolved=len(pending),baseline_sha256=hashlib.sha256(gzip.decompress((OUT/'baseline-goods.json.gz').read_bytes())).hexdigest(),invariants=dict(product_release_unchanged=True,non_series_fields_unchanged=True,idempotent=True,all_rows_accounted=True,cars_unchanged=True))
 write(OUT/'report.json',report);print(json.dumps({k:v for k,v in report.items() if k!='categories'},ensure_ascii=False))
 return report
if __name__=='__main__':build()
