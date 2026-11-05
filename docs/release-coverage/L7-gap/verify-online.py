"""Verify immutable live export bytes and every brand against the reviewed matrix."""
import gzip,hashlib,json,sys,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'src'))
from goodsdex.release_coverage import matrix
OUT=Path(__file__).resolve().parent

def get(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'Cache-Control':'no-cache','User-Agent':'GoodsDex-L7-Gap-Acceptance/1.0','Accept-Encoding':'gzip'}),timeout=120) as r:
  assert r.status==200
  raw=r.read()
  return gzip.decompress(raw) if r.headers.get('Content-Encoding')=='gzip' else raw

def main():
 print('Fetching compressed OSS/API exports',flush=True)
 suffix='?l7_gap='+str(int(time.time()))
 oss=json.loads(get('https://spend-good.oss-cn-shanghai.aliyuncs.com/data/public/meta.json'+suffix))
 api=json.loads(get('https://spend.snewbie.site/api/meta'+suffix))
 raw=get('https://spend.snewbie.site/api/goods'+suffix)
 sha=hashlib.sha256(raw).hexdigest();assert sha==api['files']['goods.json']['sha256']
 m=matrix(json.loads(raw));expected=json.loads((OUT/'summary.json').read_text())['after']
 assert m==expected,(m['total'],expected['total'])
 assert oss['release_precision']==api['release_precision']==m
 assert oss['revision']==api['revision']
 for name,value in [('online-meta.json',api),('oss-meta.json',oss),('online-coverage.json',m),('online-bytes.json',dict(sha256=sha,bytes=len(raw),revision=api['revision']))]:
  (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
 print('Verified API bytes, OSS, all brands:',m['total'],flush=True)
if __name__=='__main__':main()
