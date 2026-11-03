"""Archive source bytes and text. Search results are leads, never assertions."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import re
import requests
import sys

OUT = Path(__file__).parent

def plain(value):
    value = re.sub(r'<(script|style)\b[^>]*>.*?</\1>', '', value, flags=re.S | re.I)
    return re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]+>', ' ', value))).strip()

def capture(url):
    key = hashlib.sha256(url.encode()).hexdigest()[:16]
    path = OUT / 'evidence' / (key + '.html')
    path.parent.mkdir(exist_ok=True)
    meta = path.with_suffix('.json')
    if meta.exists():
        old = json.loads(meta.read_text())
        if not old.get('error'):
            return old
    s = requests.Session()
    s.trust_env = False
    result = dict(url=url, captured_at=datetime.now(timezone.utc).isoformat())
    try:
        r = s.get(url, timeout=25)
        if r.status_code in (403, 429) and 'www.ithome.com' in url:
            number = ''.join(re.findall(r'\d', url))
            r = s.get('https://m.ithome.com/html/' + str(int(number)) + '.htm', timeout=25)
        r.raise_for_status()
        path.write_bytes(r.content)
        charset = re.search(br'charset\s*=\s*["\']?([\w-]+)', r.content[:2000], re.I)
        r.encoding = charset[1].decode() if charset else 'utf-8'
        text = plain(r.text)
        result.update(capture_url=r.url, http_status=r.status_code,
                      sha256=hashlib.sha256(r.content).hexdigest(),
                      capture_file=str(path.relative_to(OUT.parents[1])), text=text)
    except Exception as exc:
        result['error'] = str(exc)
    meta.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    return result

if __name__ == '__main__':
    for r in ThreadPoolExecutor(4).map(capture, sys.argv[1:]):
        print(json.dumps({k: v for k, v in r.items() if k != 'text'}, ensure_ascii=False))
