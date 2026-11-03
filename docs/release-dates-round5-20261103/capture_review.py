"""Read-only capture of original citations and independent sample checks."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.path[:0] = ['src', 'scripts']
from release_family_llm import write

ROOT = Path(__file__).resolve().parent
SOURCES = {
 'lidar': 'https://www.dji.com/newsroom/news/dji-ronin-4d',
 'action5': 'https://www.dji.com/no/media-center/announcements/dji-osmo-action-5-pro-en',
 'osmo360': 'https://www.dji.com/pr/newsroom/news/dji-release-osmo-360-us',
 'xc35': 'https://cameratimes.org/fujifilm-x-t200-xc-35mm-f-2-lens-officially-announced/',
 'xc50230': 'https://www.dpreview.com/articles/9503379114/fujifilm-unveils-fujinon-xc16-50mm-ii-and-xc50-230mm-ii-kit-lenses-for-x-a2/',
 'xf8': 'https://www.fujifilm-x.com/en-sg/news/introducing-xf8mmf3-5-r-wr/',
 'xt50': 'https://www.fujifilm.com/jp/ja/news/list/11349',
 'be6500': 'https://www.ithome.com/0/806/503.htm',
}


def capture(url):
    key = hashlib.sha256(url.encode()).hexdigest()[:20]
    path = ROOT / 'verification-sources' / (key + '.json')
    if path.exists():
        return json.loads(path.read_text())
    raw = path.with_suffix('.html')
    raw.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(['curl', '--noproxy', '*', '-L', '-sS', '--max-time', '45',
        '-A', 'Mozilla/5.0', '-o', str(raw), '-w', '%{http_code}\n%{url_effective}', url], capture_output=True, text=True)
    data = raw.read_bytes() if raw.exists() else b''
    fields = result.stdout.splitlines()
    o = dict(url=url, final_url=fields[-1] if len(fields)>1 else url,
        status=int(fields[0]) if fields and fields[0].isdigit() else 0,
        error=result.stderr, sha256=hashlib.sha256(data).hexdigest(),
        captured_at=datetime.now(timezone.utc).isoformat(), bytes=len(data))
    path.with_suffix('.html.gz').write_bytes(gzip.compress(data, mtime=0))
    raw.unlink(missing_ok=True)
    write(path, o)
    return o


if __name__ == '__main__':
    q = json.loads((ROOT / 'review-queue.json').read_text())
    urls = list(dict.fromkeys([s['candidate']['release']['evidence']['url']
        for r in q.values() for s in r['samples']] + list(SOURCES.values())))
    with ThreadPoolExecutor(max_workers=2) as pool:
        for o in pool.map(capture, urls):
            print(o['status'], o['url'], flush=True)
