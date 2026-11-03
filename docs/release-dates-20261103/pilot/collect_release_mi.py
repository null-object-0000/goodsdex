import json,re,concurrent.futures,sys,hashlib
from pathlib import Path
sys.path.insert(0,'src')
from goodsdex.sources.mi_cn import _mtop_call,fetch_pc
rows=json.load(open('/tmp/goodsdex-release-dates/public/goods.json'))
selected=[r for r in rows if r['id'].startswith('CN:mi_cn:') and any(k in (r.get('params') or {}) for k in ['发布时间','release.date','上市时间'])]
selected += [r for r in rows if r['id']=='CN:mi_cn:product:18520']
for pattern in [r'^Xiaomi 14$',r'^Xiaomi 15$',r'^小米14$',r'^小米手环9$',r'^米家高速吹风机 H501$']:
 a=[r for r in rows if re.search(pattern,r.get('name',''))];selected+=a[:1]
selected=list({r['id']:r for r in selected}.values());print('requests families',len(selected),flush=True)
out=Path('docs/release-dates-20261103/evidence')
def collect(r):
 pid=r['id'].split(':')[-1]
 try:
  d,raw,http,err=_mtop_call(pid)
  o={'url':'https://m.mi.com/mtop/xiaomishop/product/info','request':{'method':'POST','productId':pid},'id':r['id'],'name':r['name'],'http_status':http,'error':err,'raw':d,'sha256':hashlib.sha256(raw.encode()).hexdigest()}
  (out/('mi-'+pid+'.json')).write_text(json.dumps(o,ensure_ascii=False,indent=1));return (pid,http,err,len(raw))
 except Exception as e:return(pid,str(e))
for o in concurrent.futures.ThreadPoolExecutor(3).map(collect,selected):print(o,flush=True)
