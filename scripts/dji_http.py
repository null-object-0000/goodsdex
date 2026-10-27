"""Serial, persisted and bounded public-HTML client. Every attempt is counted."""
import datetime as dt
import fcntl
import gzip
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path
from urllib.parse import urljoin, urlsplit


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=1) + '\n')
    tmp.replace(path)


class Client:
    def __init__(self, root, offline=False, limit=1198, delay=2.1):
        if not 1 <= limit <= 1198 or delay < 2.1:
            raise ValueError('limit <=1198 (two preliminary requests); delay >=2.1')
        self.root = Path(root)
        self.cache = self.root / 'http'
        self.cache.mkdir(parents=True, exist_ok=True)
        self.lock = (self.root / 'crawl.lock').open('w')
        fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self.ledger = self.root / 'requests.jsonl'
        self.used = len(self.ledger.read_text().splitlines()) if self.ledger.exists() else 0
        self.limit, self.delay, self.offline = limit, delay, offline
        self.last = {}
        self.network = 0

    def fetch(self, url, hops=0):
        u = urlsplit(url)
        if u.scheme != 'https' or u.hostname not in {'store.dji.com','www.dji.com','www1.djicdn.com','assets.djicdn.com','store-cdn.djiits.com','se-cdn.djiits.com','www-cdn.djiits.com'} or (re.search(r'/(api|klapi|pwa|cart|checkout|account)(/|$)', u.path) and not re.fullmatch(r'/api/ec-cms/pages/list/[a-z-]+/products',u.path)):
            return '', {'url': url, 'status': 0, 'reason': 'url_policy'}
        key = hashlib.sha256(url.encode()).hexdigest()
        meta, body = self.cache / (key+'.json'), self.cache / (key+'.body')
        if meta.exists() and body.exists():
            record, data = json.loads(meta.read_text()), body.read_bytes()
        else:
            if self.offline or self.used >= self.limit:
                raise RuntimeError('offline cache miss / persistent request budget exhausted: '+url)
            # First request after resume waits too. Serial curl, including each redirect.
            time.sleep(max(0, self.delay - (time.monotonic()-self.last.get(u.hostname,time.monotonic()))))
            started = dt.datetime.now(dt.timezone.utc).isoformat()
            self.used += 1
            self.network += 1
            with self.ledger.open('a') as fp:
                fp.write(json.dumps({'attempt':self.used,'url':url,'started_at':started})+'\n')
            bp, hp = self.root/'response.body', self.root/'response.headers'
            bp.unlink(missing_ok=True); hp.unlink(missing_ok=True)
            proc = subprocess.run(['curl','-q','-sS','--compressed','--max-time','40','--max-filesize','30000000',
                '-A','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36',
                '-D',str(hp),'-o',str(bp),'-w','%{http_code}',url],capture_output=True,text=True)
            self.last[u.hostname] = time.monotonic()
            data = bp.read_bytes() if bp.exists() else b''
            headers = hp.read_text() if hp.exists() else ''
            def header(key):
                hits = re.findall(r'^'+key+r':\s*(.+)$',headers,re.M|re.I)
                return hits[-1].strip() if hits else None
            status = int(proc.stdout or 0)
            record = {'url':url,'status':status,'fetched_at':started,'content_type':header('content-type'),
                      'location':header('location'),'error':proc.stderr or None,
                      'reason':'rate_limited' if status==429 else None,
                      'sha256':hashlib.sha256(data).hexdigest()}
            dump(meta,record); body.write_bytes(data)
            self.log(f'{self.used}/{self.limit} HTTP {status} {url}')
            if status==429:
                self.log('rate_limited; backing off 60s; stop for operator resume')
                time.sleep(60)
                raise RuntimeError('rate_limited')
            if status==403:
                raise RuntimeError('source_denied')
        if record['status']==429:
            raise RuntimeError('cached rate_limited; inspect before resuming')
        if record.get('location') and record['status'] in {301,302,303,307,308} and hops<3:
            target = urljoin(url,record['location'])
            # Official public redirects occasionally downgrade to http; use HTTPS only.
            if target.startswith('http://www.dji.com/'):
                target = 'https://'+target[7:]
            if '/404' not in target:
                return self.fetch(target,hops+1)
        if data[:2]==b'\x1f\x8b': data=gzip.decompress(data)
        return data.decode('utf-8',errors='replace'), record

    def log(self, message):
        line = dt.datetime.now(dt.timezone.utc).isoformat()+' '+message
        print(line,flush=True)
        with (self.root/'progress.log').open('a') as fp: fp.write(line+'\n')
