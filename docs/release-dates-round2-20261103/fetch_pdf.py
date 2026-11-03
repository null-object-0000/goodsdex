import urllib.request,urllib.error,pathlib,json,hashlib,concurrent.futures,subprocess,sys
from datetime import datetime,timezone
root=pathlib.Path(__file__).resolve().parent/'evidence'
def fetch(kv):
 k,u=kv;p=root/(k+'.pdf');o=dict(url=u,captured_at=datetime.now(timezone.utc).isoformat())
 try:
  if p.exists():b=p.read_bytes();status=200
  else:
   with urllib.request.urlopen(u,timeout=35) as r:b=r.read();status=r.status
   assert b.startswith(b'%PDF'),b[:100];p.write_bytes(b)
  subprocess.run(['pdftotext','-layout',str(p),str(root/(k+'.txt'))],check=True,stderr=subprocess.DEVNULL)
  o.update(http_status=status,bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
 except Exception as e:o.update(error=str(e),http_status=getattr(e,'code',0))
 (root/(k+'.json')).write_text(json.dumps(o,indent=2));print(k,o.get('http_status'),o.get('bytes'),flush=True)
if __name__=='__main__':list(concurrent.futures.ThreadPoolExecutor(4).map(fetch,json.load(open(sys.argv[1])).items()))
