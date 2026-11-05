import subprocess,gzip,json,hashlib,time
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).parent;out=[]
for key,path in [('launch','f4e369c0a468d3aeeda0593ba90b5e55'),('spring','58ec72df0caca51df569d0b497c33805'),('fall','15bb63b28926cd083b15e3b97567bbea'),('brandday','3f4366aeb9c157cf9a30c90693eafc55')]:
 u=f'https://s1.mi.com/pages/{path}/index.html';f=root/'responses'/f'campaign-{key}.tmp';at=datetime.now(timezone.utc).isoformat();p=subprocess.run(['curl','--noproxy','*','-sSL','--max-time','25','-o',str(f),'-w','%{http_code}',u],capture_output=True,text=True);b=f.read_bytes() if f.exists() else b'';f.unlink(missing_ok=True);dest=f.with_suffix('.html.gz');dest.write_bytes(gzip.compress(b,mtime=0));out.append(dict(url=u,status=p.stdout,file=str(dest),requested_at=at,sha256=hashlib.sha256(b).hexdigest()));print(key,p.stdout,len(b),flush=True);time.sleep(2.15)
(root/'campaign-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=1))
