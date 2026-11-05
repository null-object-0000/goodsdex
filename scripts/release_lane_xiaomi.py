#!/usr/bin/env python3
"""L3: re-fetch official newsroom/China product paths; never infer from timestamps.

run(rows, output_dir, refresh=True) returns a lane bundle. Publication accepts only
reviewed exact-ID statements; discovery diagnostics never become release dates.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import re
import requests

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / 'data/official/xiaomi-priority-release-evidence.json'


def in_scope(row):
    if not row.get('id','').startswith('CN:mi_cn:'):
        return False
    name = row.get('name','')
    if re.search(r'贴纸|贴膜|滤芯|换新服务|悬浮键盘|配件', name):
        return False
    return (row.get('category') in ('笔记本','台式机','显示器','办公娱乐显示器','游戏电竞显示器','键鼠套装','宠物饮水机')
            or bool(re.search(r'笔记本|游戏本|[Bb]ook|鼠标|键鼠|宠物',name)))


def fetch(url, directory, refresh):
    key = hashlib.sha256(url.encode()).hexdigest()[:20]
    meta = directory / (key + '.json')
    if not refresh and meta.exists():
        return json.loads(meta.read_text())
    result = dict(url=url, captured_at=datetime.now(timezone.utc).isoformat())
    try:
        response = requests.get(url, timeout=22)
        result.update(status=response.status_code, final_url=response.url,
                      sha256=hashlib.sha256(response.content).hexdigest())
        raw = directory / (key + '.bin')
        raw.write_bytes(response.content)
        result['capture_file'] = str(raw.relative_to(ROOT)) if raw.is_relative_to(ROOT) else str(raw)
        if response.status_code != 200:
            result['reason'] = 'http_' + str(response.status_code)
        elif len(response.content) < 100:
            result['reason'] = 'empty_or_shell_response'
        else:
            result['reason'] = 'retrieved_requires_exact_model_event_review'
    except requests.RequestException as error:
        result.update(reason='transport_error', error=str(error))
    meta.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    return result


def run(rows, output_dir=None, refresh=True, live=None):
    if live is not None:
        refresh = live
    out = Path(output_dir or ROOT/'docs/release-coverage/l3-xiaomi')
    captures = out/'captures'
    captures.mkdir(parents=True, exist_ok=True)
    selected = {r['id']:r for r in rows if in_scope(r)}
    # Follow the actual article JSON behind the rendered official newsroom page.
    discovery_urls = [
        'https://www.mi.com/about/history',
        'https://go.buy.mi.com/global/page/discovery?from=pc&page_num=1&show_type=newsroom',
        'https://go.buy.mi.com/global/discovery/land?from=pc&id=1668',
        'https://go.buy.mi.com/global/discovery/land?from=pc&id=2722',
        'https://www.mi.com/redmi-monitors/g27q-2025',
        'https://www.mi.com/redmibook/pro14',
        'https://drive.google.com/drive/folders/16J9lT8YIxiLrb2ySSX30JPAvG1miZuf-?usp=sharing',
        'https://blog.mi.com/en/2017/09/11/mi-mix-2-mi-note-3-mi-notebook-pro/',
    ]
    urls = list(dict.fromkeys(discovery_urls + [r.get('source_url') for r in selected.values()
                            if r.get('source_url','').startswith('https://www.mi.com/')]))
    with ThreadPoolExecutor(max_workers=5) as pool:
        results = list(pool.map(lambda u:fetch(u,captures,refresh), urls))
    by_url = {r['url']:r for r in results}
    records=[]
    for key,row in selected.items():
        url=row.get('source_url')
        capture=by_url.get(url)
        reason = (capture['reason'] if capture and capture['reason'].startswith(('http_','transport_','empty_'))
                  else 'no_verified_month_level_statement_for_exact_model')
        records.append(dict(id=key,name=row['name'],category=row.get('category'),source_url=url,
                            status='missing',missing_reason='not_obtained',reason=reason,
                            official_absence_confirmed=False,capture=capture))
    # A real primary-source date was found, but its generation is absent from the
    # current catalogue. Keep it as discovery evidence, never copy to 2024/25/26.
    discoveries=[]
    article=by_url[discovery_urls[2]]
    if article.get('status') == 200:
        p=Path(article['capture_file']);p=p if p.is_absolute() else ROOT/p
        try:
            body=json.loads(p.read_bytes())['data']['content']
            text=html.unescape(re.sub('<[^>]+>',' ',body))
            needle='Official sales start from March 4th, 2021 via all Xiaomi official channels in Mainland China.'
            if needle in text and '11th Gen Intel' in text:
                discoveries.append(dict(product='RedmiBook Pro 14/15 2021 Intel H35',date='2021-03-04',
                    granularity='day',event='availability',market='CN',url=article['url'],
                    quote=needle,sha256=article['sha256'],captured_at=article['captured_at'],
                    locator='data.content / RedmiBook Pro section',
                    disposition='not_applied_model_generation_not_in_catalogue'))
        except (ValueError,KeyError,TypeError):pass
    bundle=dict(schema=1,lane='L3',captured_at=datetime.now(timezone.utc).isoformat(),
                scope='priority_categories_all_xiaomi_candidates',total=len(records),
                summary=dict(total=len(records), hits=0, missing=len(records)),
                observations=[dict(id=r['id'],reason=r['reason'],url=r['source_url']) for r in records],
                candidates=[],records=records,captures=results,discoveries=discoveries,
                policy='No page archive, publication metadata, testing report, model-year or overseas launch date is a China release assertion.')
    out.mkdir(parents=True, exist_ok=True)
    (out/'result.json').write_text(json.dumps(bundle,ensure_ascii=False,indent=2)+'\n')
    return bundle


# Full-catalogue lane: shared official corpus, one auditable decision per ID.
def normalize(value):
    import unicodedata
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', value)).casefold()


def official(url):
    from urllib.parse import urlparse
    host = urlparse(url).hostname or ''
    return host == 'mi.com' or host.endswith('.mi.com')


def capture_serial(url, directory, live):
    """Daily resumable captures. Request starts, including redirects, are >=2.1s apart."""
    import time
    directory.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode()).hexdigest()[:20]
    meta = directory / (key + '.json')
    if meta.exists():
        try:
            return json.loads(meta.read_text())
        except ValueError:
            pass  # Resume a capture interrupted during its metadata write.
    if not live:
        return dict(url=url, reason='not_captured', status=None)
    if not official(url):
        return dict(url=url, reason='unofficial_url_rejected', status=None)
    log = directory / 'requests.jsonl'
    def request(target):
        from urllib.parse import urljoin
        for _ in range(6):
            prior = json.loads(log.read_text().splitlines()[-1]) if log.exists() else {}
            time.sleep(max(0, 2.1 - (time.time() - prior.get('started_epoch', 0))))
            rec = dict(url=target, started_epoch=time.time(), captured_at=datetime.now(timezone.utc).isoformat())
            with log.open('a') as f:
                f.write(json.dumps(rec) + '\n')
            response = requests.get(target, timeout=25, allow_redirects=False)
            if response.is_redirect:
                target = urljoin(target, response.headers['Location'])
                if not official(target):
                    raise ValueError('Redirect outside official mi.com corpus')
                continue
            return response, rec
        raise ValueError('Too many redirects')
    try:
        response, rec = request(url)
        raw = directory / (key + '.bin')
        raw.write_bytes(response.content)
        result = dict(url=url, final_url=response.url, status=response.status_code,
                      captured_at=rec['captured_at'], sha256=hashlib.sha256(response.content).hexdigest(),
                      capture_file=str(raw.relative_to(ROOT)), reason='retrieved' if response.status_code == 200 else 'http_' + str(response.status_code))
    except (requests.RequestException, ValueError) as exc:
        result = dict(url=url, status=None, reason='transport_error', error=str(exc))
    temporary = meta.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(meta)
    print('L3 source ' + url + ' ' + result['reason'], flush=True)
    return result


def run_all(rows, output_dir=None, *, live=True, entries=None, enumerate_newsroom=True):
    """Check every Xiaomi row against captured official launch materials.

    Exact reviewed aliases only; version/capacity/bundle expansion is forbidden.
    Unreviewed freshly discovered articles remain a research queue, never dates.
    """
    from collections import Counter
    from copy import deepcopy
    from goodsdex.release_coverage import precision
    out = Path(output_dir or ROOT/'docs/release-coverage/l3-xiaomi/full')
    out.mkdir(parents=True, exist_ok=True)
    captures_dir = out/'captures'/datetime.now(timezone.utc).date().isoformat()
    selected = [r for r in rows if r.get('id', '').startswith('CN:mi_cn:')]
    entries = entries if entries is not None else json.loads((ROOT/'data/official/xiaomi-release-dictionary.json').read_text())['entries']
    # Existing product parameters are outside this launch-material census.
    es = [e for e in entries if e.get('origin') in ('archive', 'official_newsroom', 'reviewed_32_batch_seed')
          and e.get('market') == 'CN' and precision(e) and e['evidence'].get('source_type') == 'official'
          and official(e['evidence'].get('url', ''))]
    captures = {}
    def get(url):
        if url not in captures:
            captures[url] = capture_serial(url, captures_dir, live)
        return captures[url]
    index = []
    index_complete = False
    if enumerate_newsroom:
        # Follow all published pages, without a title/category filter.
        for page in range(1, 101):
            u = f'https://go.buy.mi.com/global/page/discovery?from=pc&page_num={page}&show_type=newsroom'
            c = get(u)
            if c.get('status') != 200:
                break
            data = json.loads((ROOT/c['capture_file']).read_bytes())
            items = [a for p in (data.get('data', {}).get('page_data') or []) for a in p.get('assembly_info', []) if a.get('go_to_url')]
            if not items:
                index_complete = True
                break
            for a in items:
                extra = json.loads(a.get('extended') or '{}')
                mid = extra.get('material_id')
                if mid:
                    index.append(dict(title=a.get('title'), url='https://go.buy.mi.com/global/discovery/land?from=pc&id='+str(mid)))
            (out/'newsroom-index.json').write_text(json.dumps(index, ensure_ascii=False, indent=2)+'\n')
        for a in index:
            get(a['url'])
    for e in es:
        get(e['evidence']['url'])
    # Validate the exact archived evidence behind every reviewed assertion.
    checked = []
    for e in es:
        ev = e['evidence']
        path = ROOT/ev.get('capture_file', '')
        reason = None
        if not path.is_file():
            reason = 'missing_archived_evidence'
        elif hashlib.sha256(path.read_bytes()).hexdigest() != ev.get('sha256'):
            reason = 'archived_hash_mismatch'
        else:
            raw = path.read_bytes()
            if raw.startswith(b'%PDF'):
                import subprocess
                body = subprocess.run(['pdftotext', '-layout', str(path), '-'], check=True,
                                      capture_output=True).stdout.decode('utf-8')
            else:
                body = raw.decode('utf-8', errors='replace')
                def strings(value):
                    if isinstance(value, str): return [value]
                    if isinstance(value, dict): return [s for v in value.values() for s in strings(v)]
                    if isinstance(value, list): return [s for v in value for s in strings(v)]
                    return []
                try:
                    body = ' '.join(strings(json.loads(body)))
                except ValueError:
                    pass
            text = html.unescape(re.sub('<[^>]+>', ' ', body))
            fragments = re.split(r'\s*\[…\]\s*', ev.get('quote', ''))
            if not fragments or any(not fragment or normalize(fragment) not in normalize(text) for fragment in fragments):
                reason = 'archived_quote_not_found'
        checked.append(dict(entry=e, eligible=reason is None, rejection=reason,
                            live_capture=captures[ev['url']]))
    corpus = []
    for article in index:
        c = captures[article['url']]
        if c.get('status') != 200: continue
        try:
            body = json.loads((ROOT/c['capture_file']).read_bytes())['data']['content']
            corpus.append((article['url'], normalize(html.unescape(re.sub('<[^>]+>', ' ', body)))))
        except (KeyError, TypeError, ValueError):
            continue
    name_counts = Counter(name for name, key in {(normalize(r['name']), r['id']) for r in selected})
    records, candidates, inherited = [], [], []
    for row_index, row in enumerate(selected):
        matches, rejected = [], []
        for item in checked:
            e = item['entry']
            if normalize(row['name']) not in {normalize(n) for n in [e['product_name'], *e.get('aliases', [])]}:
                continue
            if e.get('reviewed_ids') and row['id'] not in e['reviewed_ids']:
                continue
            if name_counts[normalize(row['name'])] > 1 and not e.get('reviewed_ids'):
                rejected.append('ambiguous_same_name')
                continue
            if not item['eligible']:
                rejected.append(item['rejection'])
                continue
            matches.append(e)
        if len({e['date'][:7] for e in matches}) > 1:
            matches = []
            rejected.append('conflicting_official_months')
        record = dict(id=row['id'], row_index=row_index, name=row['name'], source_url=row.get('source_url'),
                      status='missing', reason=sorted(rejected)[0] if rejected else 'no_exact_model_month_statement_in_official_corpus',
                      official_absence_confirmed=False, matched_entries=[e['id'] for e in matches])
        record['official_article_mentions'] = [url for url, text in corpus if normalize(row['name']) in text]
        if not matches and record['official_article_mentions']:
            record['reason'] = 'official_model_mention_without_reviewed_event_month'
        if matches:
            e = sorted(matches, key=lambda e: (-len(e['date']), e['id']))[0]
            ev = deepcopy(e['evidence'])
            # Retain original capture time/hash. A new HTTP attempt is separate evidence.
            r = dict(date=e['date'], granularity=e['granularity'], source='official', confidence='high',
                     market='CN', event=e['event'], evidence=ev)
            if e['origin'] == 'reviewed_32_batch_seed' or '系列' in e['product_name']:
                r.update(date=e['date'][:7], granularity='month', source='series_inherit',
                         release_source='series_inherit', level='series', usage='reference',
                         inherited=True, inherited_from=e['id'], scope='Exact reviewed CN series member; not SKU first sale')
                inherited.append(dict(ids=[row['id']], release=r))
            else:
                candidates.append(dict(family=row['id'], ids=[row['id']], brand='小米',
                                       method='exact_official_launch_material', release=r))
            record.update(status='hit', reason='official_exact_model_statement', release=r,
                          live_capture=captures[ev['url']])
        records.append(record)
    summary = dict(total=len(records), processed=len(records), hits=sum(r['status']=='hit' for r in records),
                   missing=sum(r['status']=='missing' for r in records),
                   hit_precision=dict(Counter(r['release']['granularity'] for r in records if r['status']=='hit')),
                   reasons=dict(Counter(r['reason'] for r in records)),
                   source_requests=len(captures), newsroom_articles=len({a['url'] for a in index}),
                   newsroom_index_complete=index_complete, reviewed_official_entries=len(es),
                   rejected_entries=dict(Counter(i['rejection'] for i in checked if i['rejection'])))
    bundle = dict(schema=2, lane='L3', captured_at=datetime.now(timezone.utc).isoformat(),
                  scope='all_xiaomi_published_rows_against_official_launch_corpus', summary=summary,
                  total=len(records), records=records, candidates=candidates, inherited_candidates=inherited,
                  observations=[dict(id=r['id'], reason=r['reason'], url=r.get('source_url')) for r in records],
                  captures=list(captures.values()), entry_checks=[dict(entry_id=i['entry']['id'], eligible=i['eligible'], rejection=i['rejection']) for i in checked],
                  policy='Official launch materials only. Exact names and reviewed IDs; no third-party sole source, year dates, metadata dates or version inheritance. Missing is not official absence. Fresh unreviewed articles require review.')
    (out/'result.json').write_text(json.dumps(bundle, ensure_ascii=False, indent=2)+'\n')
    (out/'review-queue.json').write_text(json.dumps([a for a in index if a['url'] not in {e['evidence']['url'] for e in es}],ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary, ensure_ascii=False), flush=True)
    return bundle


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--goods',type=Path,required=True)
    parser.add_argument('--output',type=Path,default=DEFAULT)
    parser.add_argument('--evidence-dir',type=Path,default=ROOT/'docs/release-coverage/l3-xiaomi')
    parser.add_argument('--reuse-captures',action='store_true')
    args=parser.parse_args()
    bundle=run_all(json.loads(args.goods.read_text()), args.evidence_dir/'full', live=not args.reuse_captures)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(bundle,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(lane='L3',total=bundle['total'],hits=bundle['summary']['hits'],discoveries=len(bundle.get('discoveries',[]))),ensure_ascii=False))


if __name__=='__main__':main()
