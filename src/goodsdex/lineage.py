"""Source assertions are immutable observations; display is a reproducible policy view.

Legacy adapters run only at the boundary. The resolver needs no product columns.
"""
from copy import deepcopy
from datetime import date, datetime, timezone
from calendar import monthrange
from collections import Counter
from urllib.parse import urlparse
import json

# Ordered whitelist; new publishers MUST register here, never add product columns.
REGISTRY = {}
def register(name, group, hosts=(), tier=3):
    REGISTRY[name] = dict(group=group, hosts=hosts, tier=tier, order=len(REGISTRY))

for name, hosts, tier in [
 ('mi_store',('mi.com','m.mi.com'),0), ('mi_official_newsroom',('ir.mi.com',),0),
 ('mi_mtop',('api2.order.mi.com',),0), ('mihome_directory',('home.mi.com',),2),
 ('youpin',('xiaomiyoupin.com',),3), ('apple_newsroom',('apple.com','apple.com.cn'),0),
 ('apple_support',('support.apple.com',),1), ('apple_store',('store.apple.com','store.apple.com.cn'),0),
 ('hp_support',('support.hp.com',),1), ('hp_quickspecs',('h20195.www2.hp.com',),1),
 ('hp_store',('hp.com','hpstore.cn'),0), ('fujifilm_official',('fujifilm.com','fujifilm.com.cn','fujifilm-x.com','mall-jp.fujifilm.com'),0),
 ('dji_official',('dji.com',),0), ('byd_official',('byd.com','bydauto.com.cn'),0),
 ('atour_official',('yaduo.com',),0),
 ('mi_support',('support.mi.com',),1), ('xiaomi_ev',('xiaomiev.com',),0),
]: register(name,'official',hosts,tier)
for name, hosts in [
 ('ithome',('ithome.com',)), ('tencent_news',('qq.com',)), ('sina_tech',('sina.com.cn',)),
 ('kuaikeji',('mydrivers.com',)), ('zol',('zol.com.cn',)), ('pconline',('pconline.com.cn',)),
 ('baike',('baike.baidu.com',)), ('ea360',('ea360.com',)), ('ifeng_tech',('ifeng.com',)), ('pchome',('pchome.net',)), ('jd',('jd.com',)), ('pcauto',('pcauto.com.cn',)), ('cnr',('cnr.cn',)), ('people_tech',('people.com.cn',)),
 ('eastmoney',('eastmoney.com',)), ('xitek',('xitek.com',)), ('anzhuo',('anzhuo.cn',)),
 ('gsmarena',('gsmarena.com',)), ('google_search_snippet',('google.com',)),
 ('bing_search_snippet',('bing.com',)),
]: register(name,'third_party',hosts)
register('llm_verified','llm')
register('llm_estimate','llm')  # retained evidence only; never selectable
register('series_inherit','series')
METHODS = {'page_fetch','api','manual','series_inherit'}
POLICY = 'field-lineage-v1'


def publisher(url):
    parsed = urlparse(str(url or ''))
    host = parsed.hostname or ''
    if host == 'web.archive.org':
        tail = str(url).split('/http', 1)
        return publisher('http'+tail[1]) if len(tail)==2 else None
    if host in ('apple.com','www.apple.com','apple.com.cn','www.apple.com.cn') and '/newsroom/' in parsed.path:
        return 'apple_newsroom'
    if (host == 'mi.com' or host.endswith('.mi.com')) and ('/discover/' in parsed.path or '/newsroom/' in parsed.path):
        return 'mi_official_newsroom'
    matches = [(len(h), name) for name, spec in REGISTRY.items() for h in spec['hosts']
               if host == h or host.endswith('.'+h)]
    return max(matches, default=(0,None))[1]


def interval(value, precision):
    try:
        if precision == 'day' and len(value) == 10:
            d = date.fromisoformat(value); return d,d
        if precision == 'month' and len(value) == 7:
            d = date.fromisoformat(value+'-01')
            return d, d.replace(day=monthrange(d.year,d.month)[1])
    except (TypeError, ValueError): pass
    return None


def valid_time(value):
    try: return datetime.fromisoformat(value.replace('Z','+00:00')).utcoffset() is not None
    except (ValueError, TypeError, AttributeError): return False


def validate_source(s):
    if s.get('source') not in REGISTRY: raise ValueError('Unregistered source: '+str(s.get('source')))
    if not valid_time(s.get('captured_at')): raise ValueError('Source requires observed captured_at with timezone')
    if urlparse(str(s.get('source_url') or '')).scheme not in ('http','https'):
        raise ValueError('Source requires evidence URL')
    if (s.get('evidence') or {}).get('method') not in METHODS: raise ValueError('Source requires method')
    if s['source'] == 'llm_verified' and not s['evidence'].get('verified'):
        raise ValueError('llm_verified requires verified URL')
    if s['source'] == 'series_inherit':
        f=s.get('fields') or {}
        if not f.get('source_series') or not f.get('samples'):
            raise ValueError('series_inherit requires source_series and samples')


def assertion(s, field):
    f=s['fields']; e=s['evidence']
    return dict(value=deepcopy(f[field]), source=s['source'], field=field,
                captured_at=s['captured_at'], method=e['method'], evidence_url=s['source_url'],
                quote=f.get('quote',e.get('quote')), http_status=e.get('http_status'),
                confidence=e.get('confidence','high' if e.get('verified') else 'low'),
                source_group=REGISTRY[s['source']]['group'],capture_time_missing=not bool(s.get('captured_at')),
                **{k:f[k] for k in ('precision','price_kind','promo','image_kind','width','height','is_product_main','source_series','samples') if k in f})


def resolve(sources):
    candidates={}; conflicts=[]
    metadata={'precision','quote','price_kind','promo','image_kind','width','height','is_product_main','source_series','samples'}
    for s in sources:
        validate_source(s)
        for field in s['fields'].keys()-metadata:
            if s['fields'][field] is None: continue
            a=assertion(s,field)
            a['eligible']=s.get('eligible',True) and s['source']!='llm_estimate'
            if field=='release_date' and not interval(a['value'],a.get('precision')): a['eligible']=False
            if field=='image':
                kind=a.get('image_kind')
                a['eligible'] &= REGISTRY[a['source']]['group']=='official' and kind in ('product_main','white_background','specification','device_icon')
                if kind=='device_icon': a['eligible'] &= a.get('width')==168 and a.get('height')==168 and a.get('is_product_main') is False
            if field=='price' and not a.get('price_kind'): a['eligible']=False
            candidates.setdefault(field,[]).append(a)
    display={}
    for field, all_values in candidates.items():
        values=[a for a in all_values if a['eligible']]
        if field=='release_date':
            pairs=[]
            for i,a in enumerate(values):
                ai=interval(a['value'],a['precision'])
                for b in values[i+1:]:
                    bi=interval(b['value'],b['precision'])
                    gap=max((ai[0]-bi[1]).days,(bi[0]-ai[1]).days)
                    if gap>45: pairs.append(dict(left=a,right=b,gap_days=gap))
            if pairs:
                conflicts.append(dict(field=field,reason='来源日期相差超过45天，等待人工核查',pairs=pairs,alternatives=all_values))
                display[field]=None; continue
        def rank(a):
            spec=REGISTRY[a['source']]
            observed=datetime.fromisoformat(a['captured_at'].replace('Z','+00:00')).timestamp()
            base=(spec['order'],observed if field=='release_date' else -observed)
            if field=='release_date': return ({'day':0,'month':1}[a['precision']],0 if spec['group']=='official' else 1,*base)
            if field=='image': return ({'product_main':0,'white_background':1,'specification':1,'device_icon':2}[a['image_kind']],spec['tier'],*base)
            if field in ('name','price'): return (spec['tier'],*base)
            return (spec['tier'],*base)
        values.sort(key=rank)
        if not values: display[field]=None; continue
        chosen=deepcopy(values[0]);chosen.pop('eligible',None)
        alternatives=[];skipped=False
        for a in all_values:
            if a is values[0] and not skipped: skipped=True;continue
            alternatives.append(deepcopy(a))
        reasons={'release_date':'按日期精度、官方优先、来源白名单和最早捕获时间选取',
                 'name':'按官方商城、官方支持站、自有App目录、第三方顺序选取',
                 'image':'按官方商品主图、白底或规格图、168×168设备图标顺序选取',
                 'price':'按官方商城现价、渠道价顺序选取，并保留价格类型和促销标记'}
        chosen.update(alternatives=alternatives,reason=reasons.get(field,'按登记来源优先级和最早捕获时间选取')+'：'+chosen['source'],policy=POLICY)
        display[field]=chosen
    display.setdefault('release_date',None)
    return display,conflicts


def legacy_sources(row, dates_only=False):
    """Retain all old assertions, checks, estimates, and conflicts without inventing evidence."""
    sources=[];issues=[]
    def add_release(r, origin, inherited_eligible=True, inherited_series=None):
        if not isinstance(r,dict): return
        e=r.get('evidence') or {};url=e.get('url'); source=r.get('source')
        series=inherited_series is not None or source=='series_inherit' or r.get('inherited') or origin in ('release_series','release_inherited')
        name=('series_inherit' if series else 'llm_verified' if source=='llm_verified' else 'llm_estimate' if source=='llm' else publisher(url))
        if not r.get('date'): return
        fields=dict(release_date=r['date'],precision=r.get('granularity') or ('day' if len(r['date'])==10 else 'month'),quote=e.get('quote'))
        if series:
            fields.update(source_series=(inherited_series or {}).get('source_series') or r.get('series') or r.get('family') or r.get('inherited_from'),
                          samples=(inherited_series or {}).get('samples') or r.get('membership_evidence') or r.get('samples') or r.get('checks') or [])
        method='series_inherit' if series else e.get('method') or ('api' if e.get('capture_type')=='api' else 'page_fetch')
        s=dict(source=name,role='primary' if name in REGISTRY and REGISTRY[name]['group']=='official' else 'secondary',
               kind='release_date',captured_at=e.get('captured_at'),source_url=url,fields=fields,
               evidence={**deepcopy(e),'method':method,'verified':e.get('verified',bool(e.get('sha256'))),'confidence':r.get('confidence','medium')},
               eligible=inherited_eligible and r.get('usage') not in ('disabled','internal') and r.get('display_allowed') is not False and not r.get('internal_only') and source!='llm',
               legacy_origin=origin)
        try: validate_source(s)
        except ValueError as error: issues.append(dict(field='release_date',origin=origin,reason=str(error),assertion=deepcopy(r)))
        else: sources.append(s)
        for key in ('checks','alternates','assertions'):
            for c in r.get(key,[]) or []:
                if isinstance(c,dict): add_release({**c,'granularity':c.get('granularity') or ('day' if len(c.get('date') or '')==10 else 'month')},origin+'.'+key,s['eligible'],fields if series else None)
    for key in ('release','release_series','release_inherited','release_llm','release_crossed','release_effective'):
        if key=='release_effective' and row.get('lineage_policy')==POLICY: continue
        r=row.get(key)
        add_release(r,key)
    for c in row.get('release_conflicts',[]) or []: add_release(c.get('assertion'), 'release_conflicts',False)
    archive=row.get('page_first_archived') or {}
    if archive.get('date') and archive.get('evidence_url') and archive.get('captured_at'):
        owner=publisher(archive['evidence_url'])
        if owner:
            sources.append(dict(source=owner,role='secondary',kind='page_first_archived',captured_at=archive['captured_at'],source_url=archive['evidence_url'],fields={'page_first_archived':archive['date']},evidence={'method':'page_fetch','verified':False,'confidence':'low'},legacy_origin='page_first_archived'))
    if dates_only: return sources,issues
    # The original captured row is a single source observation, not insertion time.
    source_alias={'mi_cn':'mi_store','apple_cn':'apple_store','apple_support':'apple_support','hp_cn':'hp_store','dji':'dji_official','fuji':'fujifilm_official','byd':'byd_official'}
    name=source_alias.get(row.get('source')) or publisher(row.get('source_url'))
    captured=row.get('fetched_at') or row.get('captured_at')
    fields={k:deepcopy(row[k]) for k in ('name','category') if row.get(k) is not None}
    fields.update({'params.'+k:deepcopy(v) for k,v in (row.get('params') or {}).items()})
    s=dict(source=name,role='primary',kind='product',captured_at=captured,source_url=row.get('source_url'),fields=fields,evidence=dict(method='page_fetch',verified=False,confidence='low'),legacy_origin='captured_row')
    try: validate_source(s)
    except ValueError as error:
        issues.append(dict(field='product',reason=str(error)))
    else:
        sources.append(s)
        for field in ('price','image'):
            if row.get(field) is None: continue
            obs=deepcopy(s);obs['kind']=field
            obs['captured_at']=row.get(field+'_captured_at') or row.get('price_fetched_at') if field=='price' else row.get('image_captured_at')
            # Only explicit field capture time, or the source row's actual fetch time.
            obs['captured_at']=obs['captured_at'] or captured
            obs['source_url']=row.get(field+'_source_url') or s['source_url']
            obs['source']=publisher(obs['source_url']) or name
            obs['fields']={field:row[field]}
            if field=='price': obs['fields'].update(price_kind=row.get('price_kind'),promo=row.get('promo',False))
            else:
                obs['fields'].update(image_kind=row.get('image_kind') or row.get('image_source_type'),width=row.get('image_width'),height=row.get('image_height'),is_product_main=row.get('is_product_main'))
            try: validate_source(obs)
            except ValueError as error: issues.append(dict(field=field,reason=str(error)))
            else: sources.append(obs)
    return sources,issues


def materialize(row, previous=None, at=None, migrate=True):
    result=deepcopy(row);previous=previous or row
    sources=deepcopy(previous.get('sources') or []) + deepcopy(row.get('sources') or [])
    issues=[]
    if migrate:
        additions,issues=legacy_sources(row);sources+=additions
    # Exact-observation dedup only. Same source/value at different times is retained.
    unique={json.dumps(s,sort_keys=True,ensure_ascii=False):s for s in sources}
    sources=list(unique.values())
    display,conflicts=resolve(sources)
    old=previous.get('display') or {};history=deepcopy(previous.get('field_history') or [])
    for field in old.keys()|display.keys():
        before=old.get(field);after=display.get(field)
        # Evidence refreshes and alternative additions are not adopted-value changes.
        signature=lambda a: (a or {}).get('value')
        if signature(before)!=signature(after):
            history.append(dict(at=at or datetime.now(timezone.utc).isoformat(),field=field,
                                **{'from':{k:deepcopy(v) for k,v in (before or {'value':None}).items() if k!='alternatives'},'to':{k:deepcopy(v) for k,v in (after or {'value':None}).items() if k!='alternatives'}},
                                reason=(after or {}).get('reason','来源冲突或缺少合格证据，清空采纳值'),actor='policy:'+POLICY))
    selected=display.get('release_date')
    mirror=({'date':selected['value'],'granularity':selected['precision'],'source':selected['source'],
             'evidence':{'url':selected['evidence_url'],'captured_at':selected['captured_at'],'quote':selected['quote'],'http_status':selected['http_status']},
             'policy':POLICY,'release_source':{'official':'official','third_party':'third_party','series':'series_inherit','llm':'llm_verified'}[REGISTRY[selected['source']]['group']]} if selected else None)
    result.update(sources=sources,display=display,conflicts=conflicts,field_history=history,lineage_issues=issues,lineage_policy=POLICY,release_effective=mirror)
    return result


def apply_lineage(rows, previous=()):
    from collections import defaultdict, deque
    by_id=defaultdict(deque)
    for r in previous: by_id[r['id']].append(r)
    return [materialize(r,by_id[r['id']].popleft() if by_id[r['id']] else None) for r in rows]


def coverage(rows):
    counts=Counter();publishers=Counter();missing=conflicts=0
    for r in rows:
        a=(r.get('display') or {}).get('release_date')
        if a:
            counts[REGISTRY[a['source']]['group']]+=1;publishers[a['source']]+=1
        else: missing+=1
        conflicts+=any(c['field']=='release_date' for c in r.get('conflicts',[]))
    return dict(policy=POLICY,counting_unit='published_rows',total=len(rows),covered=sum(counts.values()),missing=missing,conflicts=conflicts,
                groups={k:counts[k] for k in ('official','third_party','series','llm')},sources=dict(publishers),ratio=sum(counts.values())/len(rows) if rows else 0)


def enrich_display(sources, display, previous, at=None):
    """Envelopes retain every capture; only individual captures supply field proof."""
    observations=[o for envelope in sources for o in envelope.get('observations',[envelope])]
    dates=[s for s in observations if 'release_date' in s['fields']]
    resolved,conflicts=resolve(dates)
    display['release_date']=resolved['release_date']
    # Every additional source field has lineage, including nested specification values.
    metadata={'precision','quote','price_kind','promo','image_kind','image_type','width','height','is_product_main','source_series','samples'}
    extra={}
    for o in observations:
        for field,value in o['fields'].items():
            if field in metadata or field in display: continue
            extra.setdefault(field,[]).append((o,value))
            if isinstance(value,dict):
                def leaves(prefix,tree):
                    for key,v in tree.items():
                        path=prefix+'.'+key
                        if isinstance(v,dict): yield from leaves(path,v)
                        else: yield path,v
                for path,v in leaves(field,value):
                    nested=deepcopy(o);nested['fields'][path]=v
                    extra.setdefault(path,[]).append((nested,v))
    for field,values in extra.items():
        eligible=[pair for pair in values if pair[0].get('captured_at') and pair[0].get('eligible',True)]
        if not eligible: display[field]=None;continue
        latest=sorted(eligible,key=lambda pair:(REGISTRY[pair[0]['source']]['tier'], -datetime.fromisoformat(pair[0]['captured_at'].replace('Z','+00:00')).timestamp() if pair[0].get('captured_at') else float('inf')))
        o,value=latest[0]
        if value is None: display[field]=None;continue
        selected=assertion(o,field)
        selected.update(alternatives=[assertion(other,field) for other,_ in values if other is not o],reason='按来源优先级和最近字段抓取时间选取：'+o['source'],policy=POLICY)
        display[field]=selected
    history=deepcopy(previous.get('field_history') or [])
    old=previous.get('display') or {}
    for field in sorted(old.keys()|display.keys()):
        before=old.get(field);after=display.get(field)
        if (before or {}).get('value') != (after or {}).get('value'):
            history.append(dict(at=at or datetime.now(timezone.utc).isoformat(),field=field,
                **{'from':{k:deepcopy(v) for k,v in (before or {'value':None}).items() if k!='alternatives'},'to':{k:deepcopy(v) for k,v in (after or {'value':None}).items() if k!='alternatives'}},
                reason=(after or {}).get('reason','来源冲突或缺少合格证据，清空采纳值'),actor='policy:'+POLICY))
    return display,conflicts,history
