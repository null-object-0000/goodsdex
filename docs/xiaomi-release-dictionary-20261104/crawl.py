"""Public archive fetches, serialized with >=2.1s between request starts. No auth/retries."""
from pathlib import Path
import requests,time,json,hashlib,re,sys,subprocess
from datetime import datetime,timezone
import html
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
def capture(url):
    log=OUT/'fetches.jsonl'
    records=[json.loads(x) for x in log.read_text().splitlines()] if log.exists() else []
    prior=next((x for x in records if x['url']==url),None)
    if prior:return prior
    if records:time.sleep(max(0,2.1-(time.time()-records[-1]['started_epoch'])))
    key=hashlib.sha256(url.encode()).hexdigest()[:16]
    rec=dict(url=url,started_epoch=time.time(),captured_at=datetime.now(timezone.utc).isoformat())
    try:
        s=requests.Session();s.trust_env=False
        r=s.get(url,timeout=35,allow_redirects=False)
        rec.update(status=r.status_code,location=r.headers.get('Location'))
        p=OUT/'evidence'/f'{key}.bin';p.write_bytes(r.content)
        rec.update(capture_file=str(p.relative_to(ROOT)),sha256=hashlib.sha256(r.content).hexdigest())
        if r.status_code==200:
            if r.content[:4]==b'%PDF':
                subprocess.run(['pdftotext','-layout',str(p),str(p.with_suffix('.txt'))],check=True)
            else:
                charset=re.search(br'charset\s*=\s*[\"\']?([\w-]+)',r.content[:3000],re.I)
                r.encoding=charset[1].decode() if charset else 'utf-8'
                value=re.sub(r'<(script|style)\b[^>]*>.*?</\1>', '', r.text, flags=re.S|re.I)
                p.with_suffix('.txt').write_text(re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]+>', ' ', value))).strip())
        else:rec['error']='non-200; no challenge handling'
    except Exception as exc:rec['error']=str(exc)
    with log.open('a') as f:f.write(json.dumps(rec,ensure_ascii=False)+'\n')
    print(json.dumps(rec,ensure_ascii=False),flush=True)
    return rec
if __name__=='__main__':
    for url in sys.argv[1:]:capture(url)
