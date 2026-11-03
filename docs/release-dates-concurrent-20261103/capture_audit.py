"""Capture exactly the frozen audit citations, without calling an LLM."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import re
import urllib.request
from html.parser import HTMLParser

class TextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self.skip += 1
    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript"):
            self.skip = max(0, self.skip - 1)
    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)

ROOT = Path(__file__).resolve().parent

def capture(item):
    evidence = item['proposal'].get('evidence') or {}
    url = evidence.get('url')
    result = dict(family=item['family'], url=url, captured_at=datetime.now(timezone.utc).isoformat())
    if not url:
        return {**result, 'status': 'no_original_citation'}
    key = hashlib.sha256(url.encode()).hexdigest()[:24]
    dest = ROOT/'verification-sources'
    dest.mkdir(exist_ok=True)
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req, timeout=25) as res:
            raw=res.read()
            result.update(http_status=res.status, final_url=res.url)
        (dest/(key+'.html.gz')).write_bytes(gzip.compress(raw, mtime=0))
        parser = TextParser()
        parser.feed(raw.decode('utf-8', errors='replace'))
        text=re.sub(r'\s+',' ', ' '.join(parser.parts)).strip()
        (dest/(key+'.txt')).write_text(text)
        result.update(sha256=hashlib.sha256(raw).hexdigest(), text_artifact='verification-sources/'+key+'.txt', text_chars=len(text), status='captured')
    except Exception as exc:
        result.update(status='fetch_failed',http_status=getattr(exc,'code',None), error=str(exc))
    return result

if __name__=='__main__':
    items=json.loads((ROOT/'audit-sample.json').read_text())['samples']
    results=list(ThreadPoolExecutor(max_workers=6).map(capture,items))
    (ROOT/'citation-captures.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps([{k:v for k,v in x.items() if k in ('family','status','http_status','text_chars')} for x in results],ensure_ascii=False,indent=2))
