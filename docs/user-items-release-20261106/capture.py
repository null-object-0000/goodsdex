"""Bounded read-only HTTP capture; raw SHA256 covers decompressed response bytes."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import gzip, hashlib, json, pathlib, subprocess, sys
from bs4 import BeautifulSoup
ROOT=pathlib.Path(__file__).resolve().parent

def fetch(url, body=None, headers=None):
    key=hashlib.sha256((url+(body or '')).encode()).hexdigest()[:20]
    p=ROOT/'evidence'/key;p.parent.mkdir(exist_ok=True)
    if p.with_suffix('.json').exists():return json.loads(p.with_suffix('.json').read_text())
    now=datetime.now(timezone.utc).isoformat()
    cmd=['curl','-L','-sS','--compressed','--max-time','35','--proxy','socks5h://127.0.0.1:7890','-A','Mozilla/5.0','-w','\n%{http_code}']
    for k,v in (headers or {}).items():cmd+=['-H',f'{k}: {v}']
    if body is not None:cmd+=['--data-raw',body]
    r=subprocess.run(cmd+[url],capture_output=True)
    raw,_,status=r.stdout.rpartition(b'\n')
    try: decoded=raw.decode('utf-8')
    except UnicodeDecodeError: decoded=raw.decode('gb18030',errors='replace')
    soup=BeautifulSoup(decoded,'html.parser')
    for tag in soup(['script','style','nav','footer','header']):tag.decompose()
    text=soup.get_text('\n',strip=True)
    p.with_suffix('.html.gz').write_bytes(gzip.compress(raw,mtime=0));p.with_suffix('.txt').write_text(text)
    result=dict(url=url,status=int(status or 0),curl_exit=r.returncode,error=r.stderr.decode(errors='replace')[:400],sha256=hashlib.sha256(raw).hexdigest(),captured_at=now,raw_file=str(p.with_suffix('.html.gz').relative_to(pathlib.Path.cwd())),text_file=str(p.with_suffix('.txt').relative_to(pathlib.Path.cwd())))
    if body is not None:result['request']={'body':body,'headers':headers}
    p.with_suffix('.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result
if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=5) as pool:
        for c in pool.map(fetch,sys.argv[1:]):print(c['status'],c['url'],c['text_file'])
