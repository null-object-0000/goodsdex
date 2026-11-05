"""L6 structured product fields: exact model, captured bytes, conservative dates."""
from copy import deepcopy
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import calendar
import gzip
import hashlib
import json
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT/'data/third-party/l6-release-evidence.json'
POLICY = 'l6-structured-v1'
SITES = {'zol': 'detail.zol.com.cn', 'pconline': 'product.pconline.com.cn', 'baike': 'baike.baidu.com'}


def norm(value):
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', value)).casefold()


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.parts=[]; self.headings=[]; self.links=[]; self.skip=0; self.heading=None; self.in_title=False
        self.feed(html)
        self.text=' '.join(self.parts)
    def handle_starttag(self, tag, attrs):
        if tag=='title': self.in_title=True
        if tag in ('script','style'): self.skip+=1
        if tag in ('title','h1'): self.heading=[]
        if tag=='a':
            url=dict(attrs).get('href')
            if url:self.links.append(url)
    def handle_endtag(self, tag):
        if tag=='title': self.in_title=False
        if tag in ('script','style'): self.skip=max(0,self.skip-1)
        if tag in ('title','h1') and self.heading is not None:
            self.headings.append(' '.join(self.heading)); self.heading=None
    def handle_data(self, data):
        if not self.skip:
            if not self.in_title:self.parts.append(data.strip())
            if self.heading is not None:self.heading.append(data.strip())


def identity(row):
    # Do not collapse a configured SKU into its family. Bare iPad/series are insufficient.
    name=row['name'].strip()
    if row['id'].startswith('CN:hp_cn:'): return row['id'].rsplit(':',1)[-1]
    if not re.search(r'\d',name):return None
    if re.search(r'系列|套装|组合|\d+\s*(?:GB|TB)\s*[+/]',name,re.I):return None
    return name


def identity_proof(row, page):
    term=identity(row)
    if not term:return None
    aliases=[term]
    if term.startswith('小米'):aliases.append('Xiaomi'+term[2:])
    if term.startswith('红米'):aliases.append('Redmi'+term[2:])
    # Exact model segment in title/h1; suffix variants cannot satisfy a shorter model.
    for h in page.headings:
        h=re.sub(r'^[【〖\[]','',h)
        h=re.split(r'参数|报价|价格|_百度百科|_太平洋|_ZOL|】|〗',h)[0]
        h=re.sub(r'(?:配置|详细|手机)$','',h).strip()
        h=re.sub(r'[（(]全网通[）)]','',h)
        if any(norm(h)==norm(a) for a in aliases) and norm(term) in norm(page.text):
            return dict(model=term,title=h,body_quote=term,confidence='high')
    return None


FIELD = re.compile(r'(?<!\S)(国内发布时间|上市日期|发布时间|上市时间)\s*[:：]?\s*(?:(\d{4})\s*年\s*(\d{1,2})\s*月(?:\s*(\d{1,2})\s*日)?|(\d{4})[-/.](\d{1,2})(?:[-/.](\d{1,2}))?)(?!\d)')


def parse_field(page, site):
    hits=[]
    for m in FIELD.finditer(page.text):
        label,y,mo,d,yi,mi,di=m.groups()
        y,mo,d=(y,mo,d) if y else (yi,mi,di)
        if site=='pconline' and label not in ('发布时间','上市日期','上市时间'):continue
        try:
            stamp=date(int(y),int(mo),int(d or 1))
        except ValueError:continue
        if stamp>date.today():continue
        value=stamp.isoformat() if d else stamp.isoformat()[:7]
        precision='day' if d else 'month'
        downgraded=site=='baike' and precision=='day'
        if downgraded:value=value[:7];precision='month'
        hits.append(dict(date=value,granularity=precision,quote=m.group(0),label=label,
                         raw_date=stamp.isoformat() if d else value,baike_downgraded=downgraded,
                         event='announcement' if '发布' in label else 'availability'))
    if not hits:return None
    # Prefer domestic announcement, then availability. Never borrow a narrative year.
    hits.sort(key=lambda h: (('国内发布时间','上市日期','发布时间','上市时间').index(h['label'])))
    return hits[0]


def fingerprint(row):
    return hashlib.sha256(json.dumps({k:row[k] for k in ('id','name','brand','model','sku','params','attributes','variant_attributes') if k in row},sort_keys=True,ensure_ascii=False).encode()).hexdigest()


def check(entry,row):
    site=entry['site']; e=entry['evidence']
    u=urlparse(e['url'])
    if u.scheme not in ('http','https') or u.hostname!=SITES.get(site) or u.username or u.password or (site=='zol' and '/series/' in u.path):raise ValueError('Not a single product URL')
    if fingerprint(row)!=entry['identity_sha256']:raise ValueError('Catalogue identity changed')
    path=(ROOT/e['capture_file']).resolve()
    if not path.is_relative_to(ROOT):raise ValueError('Capture outside repository')
    raw=path.read_bytes()
    if path.suffix=='.gz':raw=gzip.decompress(raw)
    if hashlib.sha256(raw).hexdigest()!=e['sha256']:raise ValueError('Capture hash mismatch')
    page=Page(raw.decode(e.get('encoding','utf-8'),errors='replace'))
    proof=identity_proof(row,page); field=parse_field(page,site)
    if not proof or proof!=entry['match_evidence']:raise ValueError('Exact product not proven')
    if not field or field!=entry['field'] or field['quote']!=e['quote']:raise ValueError('Structured field changed')
    if not e.get('captured_at'):raise ValueError('Missing capture time')
    return field


def bounds(value):
    if len(value)==10:
        d=date.fromisoformat(value);return d,d
    y,m=map(int,value.split('-'));return date(y,m,1),date(y,m,calendar.monthrange(y,m)[1])


def conflict(a,b):
    x,y=bounds(a),bounds(b)
    # Ambiguous month ranges crossing 45 days also require review.
    return max(abs((x[0]-y[1]).days),abs((y[0]-x[1]).days))>45


def apply(rows,bundle=None):
    from .release_media import protected
    if bundle is None:
        if not INPUT.exists():return deepcopy(rows)
        bundle=json.loads(INPUT.read_text())
    if bundle.get('policy')!=POLICY:raise ValueError('Unknown L6 policy')
    out=deepcopy(rows)
    for row in out:
        entries=[e for e in bundle.get('entries',[]) if e['id']==row['id']]
        valid=[]
        for e in entries:
            try:check(e,row);valid.append(e)
            except (ValueError,OSError,KeyError):continue
        old=row.get('release') or {}
        if old.get('policy')==POLICY:
            old=old.get('previous_release') or {};row['release']=deepcopy(old)
            for k in ('release_source','release_precision','release_evidence','release_quote','release_confidence','release_cross_check'):row.pop(k,None)
        if not valid:continue
        valid.sort(key=lambda e:list(SITES).index(e['site']))
        row['release_structured_crosschecks']=deepcopy(valid)
        if protected(row):
            official=next((row[k] for k in ('release','release_inherited','release_series') if (row.get(k) or {}).get('source') in ('official','official_hidden') and (row.get(k) or {}).get('date')),None)
            if official:
                a=bounds(official['date'])
                row['release_structured_official_conflicts']=[deepcopy(e) for e in valid if a[0]>bounds(e['field']['raw_date'])[1] or a[1]<bounds(e['field']['raw_date'])[0]]
            continue
        dates=[e['field']['raw_date'] for e in valid]
        if old.get('policy')=='l5-first-report-v1' and old.get('date'):dates.append(old['date'])
        if any(conflict(a,b) for i,a in enumerate(dates) for b in dates[i+1:]) or row.get('release_media_review'):
            row['release_structured_review']=dict(reason='date_conflict_over_45_days_or_ambiguous_interval',entries=deepcopy(valid),previous_release=deepcopy(old))
            row['release']=dict(date=None,source='third_party',policy=POLICY,usage='disabled',display_allowed=False,manual_review_required=True,previous_release=deepcopy(old))
            row.pop('release_inherited',None);row.pop('release_series',None)
            for k in ('release_source','release_precision','release_evidence','release_quote','release_confidence','release_cross_check'):row.pop(k,None)
            continue
        first=valid[0];f=first['field'];e=first['evidence'];second=next((x['evidence']['url'] for x in valid[1:] if x['site']!=first['site']),'')
        r=dict(date=f['date'],granularity=f['granularity'],source='third_party',policy=POLICY,lane='L6',level='product',event=f['event'],market='CN',confidence='medium' if first['site']=='baike' else 'high',evidence=deepcopy(e),usage='fact',display_allowed=True,internal_only=False,crosscheck_status='structured_verified',manual_review_required=False,alternates=deepcopy(valid[1:]),previous_release=deepcopy(old),label='发布时间（第三方结构化）')
        r['display']=f['date']
        row['release']=r;row.pop('release_structured_review',None)
        row.update(release_source='third_party',release_precision=r['granularity'],release_evidence=e['url'],release_quote=e['quote'],release_confidence=r['confidence'],release_cross_check=second)
    return out
