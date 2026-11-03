"""Bounded, cached HTTP evidence. A 200 response is not a successful extraction."""
import concurrent.futures
import gzip
import hashlib
import json
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent

class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []; self.hidden = 0
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'): self.hidden += 1
    def handle_endtag(self, tag):
        if tag in ('script', 'style'): self.hidden = max(0, self.hidden - 1)
    def handle_data(self, data):
        if not self.hidden: self.parts.append(data)

def get(url):
    key = hashlib.sha256(url.encode()).hexdigest()[:20]
    path = ROOT / 'evidence' / (key + '.json')
    if path.exists(): return json.loads(path.read_text())
    o = dict(url=url, captured_at=datetime.now(timezone.utc).isoformat())
    raw = b''
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Accept-Encoding': 'identity'})
        with urllib.request.urlopen(req, timeout=25) as response:
            raw = response.read(); o.update(http_status=response.status, final_url=response.url)
    except urllib.error.HTTPError as exc:
        raw = exc.read(); o.update(http_status=exc.code, final_url=exc.url, error=str(exc))
    except Exception as exc:
        o.update(http_status=0, error=str(exc))
    decoded = gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw
    html = decoded.decode('utf-8', 'replace')
    parser = Text(); parser.feed(html)
    o.update(sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw),
             text=re.sub(r'\s+', ' ', ' '.join(parser.parts)).strip(),
             raw_file=key+'.response.gz')
    (path.parent / o['raw_file']).write_bytes(gzip.compress(raw, mtime=0))
    path.write_text(json.dumps(o, ensure_ascii=False, indent=2)+'\n')
    return o

def many(urls):
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        return list(pool.map(get, urls))

if __name__ == '__main__':
    import sys
    for o in many(json.loads(Path(sys.argv[1]).read_text())):
        print(o['url'], o['http_status'], o['bytes'],
              [o['text'][max(0,m.start()-60):m.end()+180] for m in re.finditer('上市|发售|开售|发布|验证|登录', o['text'])][:12], flush=True)
