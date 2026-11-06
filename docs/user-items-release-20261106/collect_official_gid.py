import json,gzip,pathlib,sys
from concurrent.futures import ThreadPoolExecutor
sys.path[:0]=['src',str(pathlib.Path(__file__).resolve().parent)]
from capture import fetch, ROOT
from goodsdex.sources.mi_cn import MTOP_URL, MTOP_HEADERS
probes=json.loads((ROOT/'official-probes.json').read_text())
def run(p):
    old=p['capture'];d=json.loads(gzip.decompress(pathlib.Path(old['raw_file']).read_bytes())) if old['status']==200 else {}
    gid=d.get('data',{}).get('product',{}).get('defaultGid')
    if not gid:return dict(**p,reason='official product unavailable; no gid')
    cap=fetch(MTOP_URL,json.dumps([{},dict(productId=p['id'].split(':')[-1],gid=str(gid))]),MTOP_HEADERS)
    raw=gzip.decompress(pathlib.Path(cap['raw_file']).read_bytes())
    d=json.loads(raw) if cap['status']==200 else {};vals=[]
    def walk(v,path='$'):
        if isinstance(v,dict):
            if any(k in str(v.get('name','')) for k in ('发布时间','上市时间')):vals.append(dict(path=path,value=v))
            for k,x in v.items():walk(x,path+'.'+k)
        elif isinstance(v,list):
            for i,x in enumerate(v):walk(x,path+f'[{i}]')
    walk(d)
    print(p['id'],p['name'],json.dumps(vals,ensure_ascii=False)[:700],flush=True)
    return dict(id=p['id'],name=p['name'],capture=cap,dates=vals)
with ThreadPoolExecutor(max_workers=3) as pool:out=list(pool.map(run,probes))
(ROOT/'official-gid-probes.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
