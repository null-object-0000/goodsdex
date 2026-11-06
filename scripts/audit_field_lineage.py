"""Reproducible migration audit; never fetches pages or invents capture timestamps."""
import argparse
from collections import Counter
import json
import gzip
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from goodsdex.lineage import coverage,REGISTRY
from goodsdex.product_sources import apply_sources as apply_lineage
from goodsdex.release_coverage import matrix,effective

p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
rows=json.loads(a.input.read_text());out=apply_lineage(rows,rows);a.output.mkdir(parents=True,exist_ok=True)
def write(name,value): (a.output/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
(a.output/'goods.json.gz').write_bytes(gzip.compress(json.dumps(out,ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
write('registry.json',REGISTRY)
samples=[]
for group in ('third_party','official','none','series','llm'):
 r=next((r for r in out if (REGISTRY[(r['display']['release_date'])['source']]['group'] if r['display']['release_date'] else 'none')==group),None)
 if r and r['id'] not in {s['id'] for s in samples}: samples.append(r)
for r in out:
 if len(samples)==5:break
 if r['id'] not in {s['id'] for s in samples}:samples.append(r)
write('samples.json',[{k:r[k] for k in ('id','name','sources','display','field_history','conflicts','lineage_issues') if k in r} for r in samples])
write('conflicts.json',[r for r in out if r['conflicts']])
write('issues.json',[{'id':r['id'],'issues':r['lineage_issues']} for r in out if r['lineage_issues']])
old=matrix(rows);new=coverage(out)
changes=[]
for before,after in zip(rows,out):
 b=effective(before);d=after['display']['release_date']
 if (b or {}).get('date')!=(d or {}).get('value'):
  changes.append(dict(id=after['id'],before=b,after=d,conflicts=after['conflicts'],issues=after['lineage_issues']))
report=dict(baseline=old,lineage=new,delta_rows=len(changes),issues=dict(Counter(i['reason'] for r in out for i in r['lineage_issues'])),changes=changes)
write('coverage.json',report)
write('reconciliation.json',dict(historical={'covered':1646,'total':3572,'ratio':1646/3572},before=old['total'],after=new,reason='新增896条设备不新增日期；旧llm_crossed按实际被抓取发布者归类，不当作裸LLM'))
print(json.dumps({'baseline':old['total'],'lineage':new,'issues':report['issues'],'delta_rows':len(changes)},ensure_ascii=False,indent=2))
