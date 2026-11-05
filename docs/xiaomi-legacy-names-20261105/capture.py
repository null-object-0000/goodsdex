import sys,json,time,subprocess,gzip,hashlib,re,html
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).parent; dest=root/'responses';dest.mkdir(exist_ok=True)
rows=json.load(open('_data/public/goods.json'));targets=[r for r in rows if re.match(r'^\d+(\.\d+)?["寸英寸]',r['name'])]
(root/'targets.json').write_text(json.dumps(targets,ensure_ascii=False,indent=1))
audit=[]
for r in targets:
 pid=r['id'].split(':')[-1]
 urls=[('nav',f'https://api.order.mi.com/product/getTabInfo?product_id={pid}&callback=productNav')]
 if r.get('source_url','').startswith('https://web.archive.org'):
  urls.append(('archive',r['source_url']))
 for kind,url in urls:
  raw=dest/f'{pid}-{kind}.tmp';start=datetime.now(timezone.utc).isoformat()
  p=subprocess.run(['curl',*(['--noproxy','*'] if kind=='nav' else []),'--compressed','-sSL','--connect-timeout','8','--max-time','25','-o',str(raw),'-w','%{http_code}\n%{url_effective}',url],capture_output=True,text=True)
  body=raw.read_bytes() if raw.exists() else b'';raw.unlink(missing_ok=True)
  f=dest/f'{pid}-{kind}.html.gz';f.write_bytes(gzip.compress(body,mtime=0));parts=p.stdout.splitlines()
  entry=dict(id=r['id'],kind=kind,url=url,status=int(parts[0]) if parts else 0,final_url=parts[-1] if parts else url,requested_at=start,sha256=hashlib.sha256(body).hexdigest(),file=str(f),error=p.stderr)
  audit.append(entry);(root/'capture-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=1));print(pid,kind,entry['status'],len(body),flush=True)
  time.sleep(2.15)
