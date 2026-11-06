"""Probe only the 12 user items and the six requested Xiaomi category gaps."""
import gzip,json,sys,subprocess
from concurrent.futures import ThreadPoolExecutor
sys.path[:0]=['src',str(__import__('pathlib').Path(__file__).resolve().parent)]
from goodsdex.sources.mi_cn import MTOP_URL,MTOP_HEADERS
from capture import fetch, ROOT
rows=json.loads(gzip.decompress(subprocess.check_output(['git','show','origin/data:public/goods.json.gz'])))
targets=json.loads((ROOT/'baseline-targets.json').read_text()); ids={r['id'] for r in targets}
categories={'宠物饮水机','路由器','REDMI路由器','智能门锁','小爱音箱','除湿机','智能家庭','插座'}
selected=[r for r in rows if r['id'].startswith('CN:mi_cn:product:') and (r['id'] in ids or r.get('category') in categories and not (r.get('release') or {}).get('display_allowed',bool((r.get('release') or {}).get('date'))))]
(ROOT/'official-scope.json').write_text(json.dumps([dict(id=r['id'],name=r['name'],category=r.get('category')) for r in selected],ensure_ascii=False,indent=2)+'\n')
def run(row):
    c=fetch(MTOP_URL,json.dumps([{},dict(productId=row['id'].split(':')[-1])]),MTOP_HEADERS)
    body=json.loads(gzip.decompress(__import__('pathlib').Path(c['raw_file']).read_bytes())) if c['status']==200 else {}
    vals=[]
    def walk(v,path='$'):
        if isinstance(v,dict):
            if any(k in str(v.get('name','')) for k in ('发布时间','上市时间')): vals.append(dict(path=path,value=v))
            for k,x in v.items():walk(x,path+'.'+k)
        elif isinstance(v,list):
            for i,x in enumerate(v):walk(x,path+f'[{i}]')
    walk(body)
    o=dict(id=row['id'],name=row['name'],capture=c,dates=vals)
    print(row['id'],row['name'],c['status'],json.dumps(vals,ensure_ascii=False)[:550],flush=True)
    return o
with ThreadPoolExecutor(max_workers=3) as pool:out=list(pool.map(run,selected))
(ROOT/'official-probes.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
