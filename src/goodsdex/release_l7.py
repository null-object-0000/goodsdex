"""Captured, reviewed exact-model month evidence. Model output alone is inert."""
from copy import deepcopy
from datetime import date
import gzip
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlparse
from .release_media import normalize, protected

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT/'data/third-party/l7-release-evidence.json'
POLICY = 'l7-exact-model-captured-month-v1'
DOMAINS = ('mi.com','xiaomi.com','ithome.com','news.mydrivers.com','tech.sina.com.cn',
           'finance.sina.com.cn','zol.com.cn','pconline.com.cn','wikipedia.org','yaduo.com')

def publisher(url, brand=None):
    u=urlparse(url)
    if u.scheme not in ('http','https') or u.username or u.password or u.port not in (None,80,443): return None
    host=u.hostname or ''
    for d in DOMAINS:
        allowed={d,'www.'+d,'m.'+d}
        if d in ('zol.com.cn','pconline.com.cn'): allowed|={'detail.'+d,'product.'+d,'news.'+d}
        if d=='wikipedia.org': allowed|={'zh.wikipedia.org','en.wikipedia.org'}
        if d in ('mi.com','xiaomi.com','yaduo.com'): allowed|={'ir.'+d}
        if host in allowed: return d
    return None

def body_text(raw):
    encoding='utf-8'
    m=re.search(br'charset\s*=\s*["\']?([\w-]+)',raw[:8000],re.I)
    if m: encoding=m[1].decode()
    class Parser(HTMLParser):
        def __init__(self): super().__init__(); self.parts=[]; self.skip=0
        def handle_starttag(self,tag,attrs):
            if tag in ('head','script','style','noscript'): self.skip+=1
        def handle_endtag(self,tag):
            if tag in ('head','script','style','noscript'): self.skip=max(0,self.skip-1)
        def handle_data(self,data):
            if not self.skip and data.strip(): self.parts.append(data.strip())
    p=Parser();p.feed(raw.decode(encoding,errors='replace'))
    return ' '.join(p.parts)

def month_tokens(value):
    date.fromisoformat(value+'-01')
    y,m=map(int,value.split('-'))
    return [f'{y}{sep}{mm}' for sep in ('-','/') for mm in (str(m),f'{m:02}')] + [f'{y}年{mm}月' for mm in (str(m),f'{m:02}')]

def has_month(text,value):
    return any(re.search(re.escape(t)+r'(?!\d)',normalize(text)) for t in month_tokens(value))

def fingerprint(row):
    identity={k:v for k,v in row.items() if k in ('id','name','brand','model','sku','params','attributes','variant_attributes')}
    if row.get('id', '').startswith('CN:mi_cn:') and not identity.get('brand'):
        identity['brand'] = '小米'  # Same deterministic brand normalization as finalizer.
    return hashlib.sha256(json.dumps(identity,ensure_ascii=False,sort_keys=True).encode()).hexdigest()

def check(entry,row):
    if entry['id']!=row['id'] or entry['name']!=row['name'] or entry['identity_sha256']!=fingerprint(row):
        raise ValueError('Catalogue identity changed')
    r=entry['release']; e=r['evidence']
    if (r.get('policy')!=POLICY or r.get('source')!='llm_verified' or r.get('granularity')!='month'
        or r.get('level')!='product' or r.get('confidence')!='medium' or r.get('market')!='CN'
        or r.get('event') not in ('announcement','availability') or entry.get('reviewed') is not True
        or not entry.get('identity_reason') or not entry.get('event_reason')):
        raise ValueError('Unreviewed exact-model event')
    if not publisher(e['url'],row.get('brand')) or not publisher(e['final_url'],row.get('brand')):
        raise ValueError('source_not_allowed')
    if e.get('http_status')!=200 or not e.get('captured_at'): raise ValueError('link_unavailable')
    path=(ROOT/e['capture_file']).resolve()
    if not path.is_relative_to(ROOT): raise ValueError('Capture outside repository')
    raw=gzip.decompress(path.read_bytes())
    if hashlib.sha256(raw).hexdigest()!=e['sha256']: raise ValueError('Capture hash mismatch')
    body=normalize(body_text(raw))
    terms=entry.get('identity_terms') or []
    if not terms or any(not normalize(t) or normalize(t) not in body for t in terms): raise ValueError('page_no_model')
    if not has_month(body,r['date']): raise ValueError('page_no_month')
    quote=e['quote']
    if any(normalize(part) not in body for part in quote.split(' […] ')):
        raise ValueError('Quote missing from capture')
    if any(normalize(t) not in normalize(quote) for t in terms) or not has_month(quote,r['date']):
        raise ValueError('Quote must show model and month')
    return r

def apply(rows,bundle=None):
    if bundle is None:
        if not INPUT.exists(): return rows
        bundle=json.loads(INPUT.read_text())
    if bundle.get('policy')!=POLICY: raise ValueError('Unknown L7 policy')
    out=deepcopy(rows)
    entries={}
    for entry in bundle.get('entries',[]): entries.setdefault(entry['id'],[]).append(entry)
    from .release_coverage import effective
    for row in out:
        for entry in entries.get(row['id'],[]):
            if entry['identity_sha256']!=fingerprint(row): continue
            r=check(entry,row)
            if row.get('release') != r and (protected(row) or effective(row)): continue
            row['release']=deepcopy(r)
            row.update(release_source='llm_verified',release_precision='month',release_confidence='medium',
                       release_evidence=r['evidence']['url'],release_quote=r['evidence']['quote'])
    return out
