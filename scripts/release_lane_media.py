#!/usr/bin/env python3
"""Resumable L5 collection: exact reviewed product assertions; discoveries queued.

Request start times (including redirects) separated >=2.1s per publisher.
No authentication, browser challenges, proxy rotation or CAPTCHA solving.
"""
from collections import Counter, defaultdict
from datetime import datetime, timezone
import fcntl
import gzip
import hashlib
import json
from pathlib import Path
import time
from urllib.parse import urljoin
import urllib.request
import urllib.error

from goodsdex.release_media import ROOT, REVIEW, POLICY, publisher, check, decide, protected


def fetch(url, directory, live=True):
    directory = Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode()).hexdigest()[:20]
    meta = directory / (key + '.json')
    if meta.exists():
        try:
            cached = json.loads(meta.read_text())
        except (OSError, ValueError):
            cached = None  # Interrupted metadata write: retry with the same throttle.
        if cached and not (cached.get('reason') == 'transport_error' and 'is not in the subpath' in cached.get('error','')):
            return cached
    if not live: return dict(url=url, reason='not_captured')
    if not publisher(url, primary=False): return dict(url=url, reason='source_not_allowed')
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs): return None
    opener = urllib.request.build_opener(NoRedirect())
    state_dir = ROOT/'docs/release-coverage/L5/throttle'
    state_dir.mkdir(parents=True, exist_ok=True)
    target = url
    result = dict(url=url, captured_at=datetime.now(timezone.utc).isoformat())
    try:
        for _ in range(6):
            domain = publisher(target, primary=False)
            if not domain: raise ValueError('redirect_source_not_allowed')
            with (state_dir/(domain+'.lock')).open('a+') as lock:
                fcntl.flock(lock, fcntl.LOCK_EX)
                stamp = state_dir/(domain+'.json')
                prior = json.loads(stamp.read_text()) if stamp.exists() else {}
                time.sleep(max(0, 2.1-(time.time()-prior.get('started_epoch',0))))
                record = dict(url=target, started_epoch=time.time())
                stamp.write_text(json.dumps(record))
                with (state_dir/'requests.jsonl').open('a') as log: log.write(json.dumps(record)+'\n')
                try:
                    response = opener.open(urllib.request.Request(target, headers={'User-Agent':'Goodsdex-release-evidence/1.0'}), timeout=25)
                except urllib.error.HTTPError as error:
                    response = error
                raw = response.read()
            if response.code in (301,302,303,307,308):
                target = urljoin(target,response.headers['Location']); continue
            path = directory/(key+'.html.gz')
            path.write_bytes(gzip.compress(raw,mtime=0))
            result.update(status=response.code, final_url=target, sha256=hashlib.sha256(raw).hexdigest(),
                          capture_file=str(path.relative_to(ROOT)), reason='retrieved' if response.code==200 else 'http_'+str(response.code))
            # Stop at challenges. Store failure, never try logging in or bypassing it.
            if any(x in raw.lower() for x in (b'captcha', b'cf-chl-', '验证码'.encode())):
                result['reason']='challenge_or_captcha'
            break
        else: result['reason']='redirect_limit'
    except (OSError, ValueError) as error:
        result.update(reason='transport_error',error=str(error))
    temporary = meta.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    temporary.replace(meta)
    print('L5 '+url+' '+result['reason'],flush=True)
    return result


def run(rows, output, *, live=True, review_path=REVIEW):
    output = Path(output); output.mkdir(parents=True,exist_ok=True)
    review = json.loads(Path(review_path).read_text()) if Path(review_path).exists() else dict(entries=[])
    entries = review['entries']
    by_id = defaultdict(list)
    for e in entries: by_id[e['id']].append(e)
    directory = output/'captures'/str(datetime.now(timezone.utc).date())
    captures = {u:fetch(u,directory,live) for u in dict.fromkeys(e['assertion']['evidence']['url'] for e in entries)}
    # New headlines remain a review queue: the cron never manufactures dates
    # from metadata, prefixes or unreviewed series mentions.
    feed = fetch('https://www.ithome.com/rss/', directory, live)
    captures[feed['url']] = feed
    discovery = []
    if feed.get('status') == 200 and feed.get('reason') == 'retrieved':
        import xml.etree.ElementTree as ET
        try:
            raw = gzip.decompress((ROOT/feed['capture_file']).read_bytes())
            for item in ET.fromstring(raw).findall('.//item')[:80]:
                title, url = item.findtext('title') or '', item.findtext('link') or ''
                if publisher(url):
                    discovery.append(dict(title=title,url=url,published_at=item.findtext('pubDate'),status='requires_exact_model_event_review'))
        except (ET.ParseError,OSError):
            pass
    (output/'discovery-queue.json').write_text(json.dumps(discovery,ensure_ascii=False,indent=2)+'\n')
    accepted, records, conflicts, rejected = [], [], [], []
    checked = {}
    for index,row in enumerate(rows):
        es=[]; errors=[]
        for e in by_id.get(row['id'],[]):
            try:
                # Includes original archived body+hash, quote, reviewed exact row fingerprint.
                check(e,row); es.append(e)
            except (ValueError, OSError, KeyError) as error:
                errors.append(str(error)); rejected.append(dict(id=row['id'],url=e['assertion']['evidence']['url'],reason=str(error)))
        reason='no_reviewed_exact_model_first_report'
        decision=decide(es) if es else dict(status='missing',release=None)
        if protected(row): reason='official_date_preserved'
        elif decision['status']=='accepted': reason='exact_model_first_report'
        elif es: reason=decision['status']
        elif errors: reason='archived_evidence_rejected'
        r=dict(id=row['id'],row_index=index,name=row['name'],brand=row.get('brand'),reason=reason,
               status='crosscheck' if protected(row) and es else 'hit' if decision['release'] and not protected(row) else 'missing',
               precision=decision['release']['granularity'] if decision['release'] else None)
        records.append(r)
        if decision['status'] in ('conflict','uncertain_interval'):
            conflicts.append(dict(r,decision=decision,entries=es))
        for e in es:
            key=json.dumps(e,ensure_ascii=False,sort_keys=True)
            if key not in checked: accepted.append(e); checked[key]=True
    def stats(rs):
        return dict(total=len(rs),hits=sum(r['status']=='hit' for r in rs),
                    precision=dict(Counter(r['precision'] for r in rs if r['status']=='hit')),
                    reasons=dict(Counter(r['reason'] for r in rs)))
    summary=stats(records)
    summary.update(brands={b:stats([r for r in records if r.get('brand')==b]) for b in sorted({r.get('brand') or '未知' for r in records})},
                   source_requests=len(captures),reviewed_entries=len(entries),conflicts=len(conflicts),rejected=len(rejected))
    bundle=dict(schema=1,lane='L5',policy=POLICY,captured_at=datetime.now(timezone.utc).isoformat(),
                entries=accepted,summary=summary,records=records,captures=list(captures.values()),conflicts=conflicts,rejected=rejected)
    for filename,value in [('result.json',bundle),('conflicts.json',conflicts),('rejected.json',rejected)]:
        (output/filename).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    return bundle
