"""L5 single first-report policy. Captured exact product evidence, official wins.

Separate from the older two-origin media policy; never relabel a series as SKU.
"""
from collections import defaultdict
from copy import deepcopy
from datetime import date
import gzip
import hashlib
import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / 'data/third-party/l5-release-evidence.json'
REVIEW = ROOT / 'data/third-party/l5-reviewed.json'
POLICY = 'l5-first-report-v1'
PRIMARY = ('ithome.com', 'finance.sina.com.cn', 'tech.sina.com.cn', 'news.mydrivers.com')
CROSSCHECK = ('zol.com.cn', 'pconline.com.cn', 'cnmo.com')


def normalize(text):
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', text)).casefold()


def publisher(url, primary=True):
    u = urlparse(url)
    if u.scheme not in ('https', 'http') or u.username or u.password:
        return None
    hosts = {'ithome.com': 'ithome.com', 'www.ithome.com':'ithome.com', 'm.ithome.com':'ithome.com',
             'finance.sina.com.cn':'finance.sina.com.cn', 'tech.sina.com.cn':'tech.sina.com.cn',
             'news.mydrivers.com':'news.mydrivers.com'}
    if not primary:
        for domain in CROSSCHECK:
            for host in (domain, 'www.'+domain, 'detail.'+domain, 'product.'+domain, 'm.'+domain):
                hosts[host] = domain
    return hosts.get(u.hostname)


def capture_text(e):
    """Verify bytes and exact excerpts on every replay, not just collection."""
    path = (ROOT / e['capture_file']).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError('Capture outside repository')
    raw = path.read_bytes()
    if path.suffix == '.gz':
        raw = gzip.decompress(raw)
    if hashlib.sha256(raw).hexdigest() != e['sha256']:
        raise ValueError('Capture hash mismatch')
    from html.parser import HTMLParser
    class Parser(HTMLParser):
        def __init__(self):
            super().__init__(); self.parts = []; self.skip = 0
        def handle_starttag(self, tag, attrs):
            if tag in ('script', 'style'): self.skip += 1
        def handle_endtag(self, tag):
            if tag in ('script', 'style'): self.skip = max(0, self.skip - 1)
        def handle_data(self, data):
            if not self.skip: self.parts.append(data)
    encoding = e.get('encoding') or 'utf-8'
    parser = Parser(); parser.feed(raw.decode(encoding, errors='replace'))
    text = normalize(' '.join(parser.parts))
    for field in ('quote', 'identity_quote'):
        if not e.get(field) or normalize(e[field]) not in text:
            raise ValueError('Capture excerpt missing: ' + field)
    return text


def check(entry, row):
    from .release_coverage import precision
    from .brands import namespace_brand
    row = dict(row, brand=row.get('brand') or namespace_brand(row['id']))
    if entry.get('name') != row.get('name') or entry.get('brand') != row.get('brand'):
        raise ValueError('Exact catalogue identity changed')
    a = entry['assertion']; e = a['evidence']
    if (a.get('source') != 'third_party' or e.get('source_type') != 'third_party'
        or a.get('market') != 'CN' or a.get('event') not in ('announcement', 'availability')
        or not precision(a) or not publisher(e.get('url', ''), primary=False)
        or not e.get('captured_at') or not e.get('locator')
        or not re.fullmatch('[a-f0-9]{64}', e.get('sha256', ''))):
        raise ValueError('Invalid L5 source/date/provenance')
    if entry.get('identity_kind') != 'exact_product' or not entry.get('identity_reason'):
        raise ValueError('Series mention cannot be a product assertion')
    terms = entry.get('identity_terms') or []
    if not terms or any(normalize(t) not in normalize(e.get('identity_quote', '')) for t in terms):
        raise ValueError('Exact model/configuration not in article')
    # The reviewed identity is bound to this row, including all SKU/configuration fields.
    identity = {k: v for k, v in row.items() if k in ('id', 'name', 'brand', 'model', 'sku', 'params', 'attributes', 'variant_attributes')}
    fingerprint = hashlib.sha256(json.dumps(identity, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    if entry.get('identity_sha256') != fingerprint:
        raise ValueError('Exact catalogue configuration changed')
    text = capture_text(e)
    reported = date.fromisoformat(a['reported_at'][:10])
    y,m,d = reported.year,reported.month,reported.day
    stamps = [f'{y}{sep}{mm}{sep}{dd}' for sep in ('/', '-') for mm in (str(m),f'{m:02}') for dd in (str(d),f'{d:02}')]
    stamps += [f'{y}年{mm}月{dd}日' for mm in (str(m),f'{m:02}') for dd in (str(d),f'{d:02}')]
    if not any(stamp in text for stamp in stamps):
        raise ValueError('Reported date not present in captured page')
    if a['granularity'] == 'month' and a['date'] != reported.isoformat()[:7]:
        raise ValueError('First-report month must match reporting month')
    if a['granularity'] == 'day':
        # A dateline, "today" or a publication timestamp alone never grants day.
        day = date.fromisoformat(a['date'])
        explicit = e.get('explicit_event_quote') or ''
        if (not explicit or normalize(explicit) not in normalize(e['quote'])
            or not re.search(rf'{day.month}\s*月\s*{day.day}\s*[日号]', explicit)
            or not re.search(r'发布|开售|发售|上市', explicit)
            or re.search(r'将于|预计|拟于|计划|预告', explicit) or day > reported):
            raise ValueError('Day requires explicit month/day release event')
    if not a.get('first_report_review'):
        raise ValueError('Unreviewed first-report semantics')
    if a['date'][:7] > reported.isoformat()[:7]:
        raise ValueError('Future/preorder date is not a release')
    return a


def protected(row):
    # Even an internal/hidden official date must never be replaced by a media value.
    return any((row.get(k) or {}).get('date') and (row.get(k) or {}).get('source') in ('official', 'official_hidden')
               and (k == 'release' or (row.get(k) or {}).get('level') != 'series')
               for k in ('release', 'release_inherited', 'release_series'))


def decide(entries):
    """Compare actual reported days; month-only event bounds are conservative.

    Origins deduplicate reposts; all conflicting exact-model sources still count.
    Dates for different events stay in the audit trail, not a fabricated conflict.
    """
    primaries = [e for e in entries if publisher(e['assertion']['evidence']['url'])]
    if not primaries:
        return dict(status='crosscheck_only', release=None)
    first = min(primaries, key=lambda e: (e['assertion']['reported_at'], PRIMARY.index(publisher(e['assertion']['evidence']['url']))))
    a = first['assertion']
    same = [e['assertion'] for e in entries if e['assertion']['event'] == a['event']]
    def bounds(v):
        import calendar
        if len(v) == 10:
            d = date.fromisoformat(v); return d, d
        y,m = map(int,v.split('-'))
        return date(y,m,1), date(y,m,calendar.monthrange(y,m)[1])
    # Prove >45 days even with unknown month days; ambiguous intervals require review.
    pairs = [(bounds(x['date']), bounds(y['date'])) for i,x in enumerate(same) for y in same[i+1:]]
    minimum = max((max(0,(a[0]-b[1]).days,(b[0]-a[1]).days) for a,b in pairs), default=0)
    maximum = max((max(abs((a[0]-b[1]).days),abs((b[0]-a[1]).days)) for a,b in pairs), default=0)
    if maximum > 45:
        return dict(status='conflict' if minimum > 45 else 'uncertain_interval', release=None,
                    delta_days_min=minimum, delta_days_max=maximum)
    r = deepcopy(a)
    r.pop('reported_at', None); r.pop('first_report_review', None)
    r.update(policy=POLICY, lane='L5', level='product', release_source='third_party',
             confidence='high' if r['granularity']=='day' else 'medium', usage='fact',
             display_allowed=True, internal_only=False, crosscheck_status='first_report_verified',
             manual_review_required=False, assertions=[deepcopy(e['assertion']) for e in entries])
    parts = r['date'].split('-')
    r.update(display=' 年 '.join(parts[:1])+' 年 '+str(int(parts[1]))+' 月'+(' '+str(int(parts[2]))+' 日' if len(parts)==3 else ''),
             label='发布时间（第三方）' if r['event']=='announcement' else '发售时间（第三方）')
    return dict(status='accepted', release=r, delta_days_min=minimum, delta_days_max=maximum)


def apply(rows, bundle=None):
    if bundle is None:
        if not INPUT.exists(): return deepcopy(rows)
        bundle = json.loads(INPUT.read_text())
    if bundle.get('policy') != POLICY or bundle.get('lane') != 'L5':
        raise ValueError('Unknown L5 policy')
    by_id = defaultdict(list)
    for e in bundle.get('entries', []): by_id[e['id']].append(e)
    output = deepcopy(rows)
    for row in output:
        entries = by_id.get(row['id'], [])
        if not entries: continue
        eligible = []
        for e in entries:
            try:
                check(e, row); eligible.append(e)
            except ValueError as error:
                if str(error) not in ('Exact catalogue identity changed', 'Exact catalogue configuration changed'):
                    raise
                row['release_media_skipped'] = dict(reason=str(error), lane='L5')
        entries = eligible
        if not entries:
            if (row.get('release') or {}).get('policy') == POLICY:
                row.pop('release', None)
                for field in ('release_source','release_precision','release_evidence','release_quote','release_confidence'):
                    row.pop(field, None)
            continue
        row.pop('release_media_skipped', None)
        if protected(row):
            row['release_media_crosschecks'] = deepcopy(entries)
            if row.get('release_source') == 'third_party':
                for field in ('release_source','release_precision','release_evidence','release_quote','release_confidence'):
                    row.pop(field, None)
            continue
        decision = decide(entries)
        if decision['release']:
            row.pop('release_media_review', None)
            row['release'] = deepcopy(decision['release'])
            row.update(release_source='third_party', release_precision=row['release']['granularity'],
                       release_evidence=row['release']['evidence']['url'], release_quote=row['release']['evidence']['quote'],
                       release_confidence=row['release']['confidence'])
        elif decision['status'] in ('conflict', 'uncertain_interval'):
            # No fallback to inherited/previous media dates after a hard conflict.
            row['release'] = dict(date=None, source='third_party', policy=POLICY, lane='L5',
                                  manual_review_required=True, display_allowed=False, usage='disabled')
            row.pop('release_inherited', None); row.pop('release_series', None)
            for field in ('release_source','release_precision','release_evidence','release_quote','release_confidence'):
                row.pop(field, None)
            row['release_media_review'] = dict(decision, entries=deepcopy(entries))
    return output
