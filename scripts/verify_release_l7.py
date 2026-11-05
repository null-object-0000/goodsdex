"""Fetch untrusted proposals once, globally paced, and queue evidence for review."""
import gzip
import fcntl
import hashlib
import json
from pathlib import Path
import re
import time
from datetime import datetime, timezone
import urllib.error
import urllib.request
from urllib.parse import urljoin
from goodsdex.release_l7 import publisher, body_text, month_tokens, has_month
from goodsdex.release_media import normalize

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/release-coverage/L7'

def fetch(url):
    OUT.mkdir(parents=True, exist_ok=True)
    # Discovery and verification share one publisher request clock.
    with (OUT/'fetch.lock').open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        return _fetch(url)

def _fetch(url):
    key=hashlib.sha256(url.encode()).hexdigest()[:20]
    folder=OUT/'captures';folder.mkdir(exist_ok=True)
    path=folder/(key+'.json')
    if path.exists(): return json.loads(path.read_text())
    record=dict(url=url,captured_at=datetime.now(timezone.utc).isoformat())
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,*args,**kwargs): return None
    opener=urllib.request.build_opener(NoRedirect())
    target=url
    for _ in range(6):
        if not publisher(target): record.update(reason='source_not_allowed');break
        stamp=OUT/'last-request.json'
        prior=json.loads(stamp.read_text()) if stamp.exists() else {}
        time.sleep(max(0,2.15-(time.time()-prior.get('started_epoch',0))))
        attempt=dict(url=target,started_epoch=time.time())
        stamp.write_text(json.dumps(attempt))
        with (OUT/'requests.jsonl').open('a') as log: log.write(json.dumps(attempt)+'\n')
        try:
            try: response=opener.open(urllib.request.Request(target,headers={'User-Agent':'GoodsDex-Release-Evidence/1.0'}),timeout=20)
            except urllib.error.HTTPError as error: response=error
            raw=response.read()
            if response.code in (301,302,303,307,308):
                target=urljoin(target,response.headers['Location']);continue
            capture=folder/(key+'.html.gz');capture.write_bytes(gzip.compress(raw,mtime=0))
            record.update(http_status=response.code,final_url=target,capture_file=str(capture.relative_to(ROOT)),
                          sha256=hashlib.sha256(raw).hexdigest(),reason='retrieved' if response.code==200 else 'link_unavailable')
            if response.code in (403,429):
                time.sleep(5) # back off and skip; never retry the blocked URL
            break
        except (OSError,ValueError) as error:
            record.update(reason='link_unavailable',error=str(error));break
    else: record.update(reason='link_unavailable',error='redirect_limit')
    path.write_text(json.dumps(record,ensure_ascii=False,indent=2))
    print(url,record['reason'],flush=True)
    return record

def proposals():
    output=[]
    discovery=OUT/'search-proposals.json'
    if discovery.exists(): output.extend(json.loads(discovery.read_text()))
    for path in sorted((OUT/'proposals').glob('*.json')):
        if '.prompt.' in path.name or '.error.' in path.name: continue
        result=json.loads(path.read_text())
        value=result['choices'][0]['message']['content']
        try:
            rows=json.loads(re.sub(r'^```(?:json)?\s*|\s*```$','',value.strip()))
            if not isinstance(rows,list): continue
            for row in rows:
                if isinstance(row,dict): output.append(dict(row,proposal_file=str(path.relative_to(ROOT))))
        except (ValueError,TypeError): pass
    return output

def main():
    results=[]
    targets={(r['id'],r['name']):r for r in json.loads((OUT/'targets.json').read_text())}
    abstentions=[]
    for p in proposals():
        if (p.get('id'),p.get('name')) not in targets: continue
        if not p.get('url') or not p.get('date'):
            abstentions.append(p);continue
        result=dict(p)
        if not publisher(p['url']): result['rejection']='source_not_allowed'
        else:
            capture=fetch(p['url']);result['capture']=capture
            if capture.get('http_status')!=200 or capture.get('reason')!='retrieved': result['rejection']='link_unavailable'
            else:
                text=body_text(gzip.decompress((ROOT/capture['capture_file']).read_bytes()))
                result['body_file']=capture['capture_file']
                try: tokens=month_tokens(p['date'])
                except (ValueError,TypeError): tokens=[]
                full=normalize(p['name'])
                if full not in normalize(text): result['rejection']='page_no_model'
                elif not tokens or not has_month(text,p['date']): result['rejection']='page_no_month'
                else: result['status']='requires_event_review'
        results.append(result)
        (OUT/'verification.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
    (OUT/'abstentions.json').write_text(json.dumps(abstentions,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
