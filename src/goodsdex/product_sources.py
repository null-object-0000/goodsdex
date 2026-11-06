"""Product source envelopes and explainable display policy.

Collectors submit observations through upsert_source. Legacy columns are accepted
only by migrate_row; they are never used by the resolver itself.
"""
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import json
from urllib.parse import urlsplit

POLICY = 'product-sources-v1'
# Tier 5 publishers can contribute dates, never product identity or price.
SOURCE_TIERS = {
    'mi_store': 1, 'apple_store': 1, 'hp_store': 1, 'atour_official': 1,
    'dji_official': 1, 'fujifilm_official': 1, 'byd_official': 1, 'xiaomi_ev': 1,
    'mi_support': 2, 'apple_support': 2, 'hp_support': 2,
    'hp_quickspecs': 2, 'mihome_directory': 3, 'youpin': 3,
    'zol': 4, 'baike': 4, 'pcauto': 4, 'jd': 4,
}
HOSTS = {
    'home.mi.com': 'mihome_directory', 'xiaomiyoupin.com': 'youpin',
    'support.apple.com': 'apple_support', 'apple.com.cn': 'apple_store',
    'apple.com': 'apple_store', 'support.hp.com': 'hp_support',
    'h20195.www2.hp.com': 'hp_quickspecs', 'hpstore.cn': 'hp_store',
    'hp.com': 'hp_store', 'mi.com': 'mi_store', 'yaduo.com': 'atour_official',
    'dji.com': 'dji_official', 'fujifilm-x.com': 'fujifilm_official',
    'fujifilm.com': 'fujifilm_official', 'fujifilm.com.cn': 'fujifilm_official', 'bydauto.com.cn': 'byd_official',
    'byd.com': 'byd_official', 'xiaomiev.com': 'xiaomi_ev',
    'pcauto.com.cn': 'pcauto', 'jd.com': 'jd', 'zol.com.cn': 'zol',
    'baike.baidu.com': 'baike',
}
DEFAULT_RULES = {
    'name': ['mi_store', 'apple_store', 'hp_store', 'atour_official', 'youpin'],
    'image': ['mi_store', 'apple_store', 'hp_store', 'atour_official'],
    'category': ['mihome_directory'],
    'price': ['mi_store', 'apple_store', 'hp_store', 'atour_official'],
}


def publisher(url):
    host = urlsplit(str(url or '')).hostname or ''
    # Archive URLs retain the original publisher, and explicitly record the archive.
    if host == 'web.archive.org':
        tail = str(url).split('/http', 1)
        return publisher('http' + tail[1]) if len(tail) == 2 else None
    matches = [(len(h), s) for h, s in HOSTS.items() if host == h or host.endswith('.' + h)]
    return max(matches, default=(0, None))[1]


def validate_source(s):
    from .lineage import REGISTRY
    if s.get('source') not in REGISTRY:
        raise ValueError('source must be a registered publisher identifier')
    if not isinstance(s.get('fields'), dict):
        raise ValueError('source fields must be an object')
    if urlsplit(str(s.get('source_url') or '')).scheme not in ('http', 'https'):
        raise ValueError('source requires an evidence URL')
    if not (s.get('evidence') or {}).get('method'):
        raise ValueError('source requires an evidence method')
    timestamp = s.get('captured_at')
    if timestamp is None:
        if not s['evidence'].get('capture_time_missing'):
            raise ValueError('missing capture time must be explicit')
    else:
        try:
            if datetime.fromisoformat(timestamp.replace('Z', '+00:00')).utcoffset() is None:
                raise ValueError('capture time must include timezone')
        except (TypeError, AttributeError):
            raise ValueError('invalid capture time') from None
    if s['source'] == 'llm_verified' and not s['evidence'].get('verified'):
        raise ValueError('llm_verified requires a verified evidence URL')
    if s['source'] == 'series_inherit' and (not s['fields'].get('source_series') or not s['fields'].get('samples')):
        raise ValueError('series_inherit requires source_series and samples')
    # Dates are independent secondary observations.
    actual = publisher(s['source_url'])
    if s['source'] not in SOURCE_TIERS and s['source'] not in ('series_inherit','llm_verified','llm_estimate'):
        from .lineage import publisher as registered_publisher
        if registered_publisher(s['source_url']) != s['source']:
            raise ValueError('publisher does not match registered evidence URL: '+s['source'])
    if s['source'] in SOURCE_TIERS and actual != s['source']:
        raise ValueError('publisher does not match source evidence URL: ' + s['source'])


def _signature(s):
    return json.dumps({k: v for k, v in s.items() if k not in ('role', 'observations')}, sort_keys=True, ensure_ascii=False)


def envelopes(observations):
    """One envelope per publisher; keep conflicting/older observations verbatim."""
    grouped = {}
    for original in observations:
        s = deepcopy(original)
        nested = s.pop('observations', [])
        for obs in nested or [s]:
            validate_source(obs)
            bucket = grouped.setdefault(obs['source'], {})
            bucket[_signature(obs)] = obs
    result = []
    for name, bucket in grouped.items():
        values = sorted(bucket.values(), key=lambda s: (_time(s), _signature(s)))
        # The envelope is a full observation, never a field-wise merge of captures.
        head = deepcopy(values[-1]); head['role'] = 'secondary'
        head['fields'] = {k: deepcopy(v) for obs in values for k, v in obs['fields'].items()}
        head['observations'] = values
        result.append(head)
    return sorted(result, key=lambda s: s['source'])


def _time(s):
    t = s.get('captured_at')
    return datetime.fromisoformat(t.replace('Z', '+00:00')).timestamp() if t else float('-inf')


def _product(s):
    return (SOURCE_TIERS.get(s['source'], 5) < 5 and s.get('eligible', True)
            and s['fields'].get('name') is not None)


def derive(sources, rules=None):
    overrides = rules or {}
    rules = {**DEFAULT_RULES, **overrides}
    display = {}
    for field in ('name', 'image', 'category', 'price'):
        candidates = []
        for envelope in sources:
            observations = [s for s in envelope['observations'] if field in s['fields'] and s.get('eligible', True) and s.get('captured_at')]
            if not observations or SOURCE_TIERS.get(envelope['source'], 5) >= 5:
                continue
            latest = max(observations, key=lambda s: (_time(s), _signature(s)))
            # An explicit null clears this publisher's previous assertion.
            if latest['fields'][field] is not None:
                if field == 'image':
                    from .lineage import REGISTRY
                    if REGISTRY[latest['source']]['group'] != 'official': continue
                    f=latest['fields']; kind=f.get('image_kind',f.get('image_type','product_photo'))
                    if kind not in ('product_main','product_photo','white_background','specification','device_icon'): continue
                    if kind=='device_icon' and not (f.get('width')==168 and f.get('height')==168 and f.get('is_product_main') is False): continue
                candidates.append(latest)
        def rank(s):
            preference = rules.get(field, [])
            preference_rank = preference.index(s['source']) if s['source'] in preference else len(preference)
            tier = SOURCE_TIERS.get(s['source'], 5)
            policy_rank = (preference_rank, tier) if field in overrides or field == 'category' else (tier, preference_rank)
            image_rank={'product_main':0,'product_photo':0,'white_background':1,'specification':1,'device_icon':2}.get(s['fields'].get('image_kind',s['fields'].get('image_type','product_photo')),3) if field=='image' else 0
            return (image_rank,*policy_rank, -_time(s), s['source'], _signature(s))
        if not candidates:
            display[field] = None
            continue
        chosen = min(candidates, key=rank)
        value = dict(value=deepcopy(chosen['fields'][field]), source=chosen['source'], field=field,
                     source_url=chosen['source_url'], captured_at=chosen.get('captured_at'),
                     policy=POLICY, reason='field preference, publisher tier, latest capture')
        if field == 'image':
            value['type'] = chosen['fields'].get('image_kind',chosen['fields'].get('image_type', 'product_photo'))
        if field == 'price':
            value['kind'] = chosen['fields'].get('price_kind', 'unknown')
        if field == 'category' and chosen['source'] == 'mihome_directory':
            value['refined_by'] = 'mihome'
        from .lineage import assertion
        proof = assertion(chosen, field)
        value.update(proof)
        value['alternatives'] = [assertion(o,field) for e in sources for o in e['observations'] if field in o['fields'] and o is not chosen]
        if field=='price':
            value['price_kind']=chosen['fields'].get('price_kind','unknown')
            value['promo']=chosen['fields'].get('promo',value['price_kind'] in ('promotion','promo'))
        value['reason'] = {'name':'按官方商城、官方支持站、自有App目录、第三方顺序选取', 'image':'按官方商品主图、白底或规格图、168×168设备图标顺序选取', 'price':'按官方商城现价、渠道价顺序选取，保留促销标记', 'category':'按字段规则和来源优先级选取'}[field] + '：' + chosen['source']
        display[field] = value
    return display


def materialize(row, previous=None, observations=(), rules=None, at=None):
    """Resolve independently of primary; exact one primary with identity evidence."""
    result = deepcopy(row); previous = previous or row
    sources = envelopes([*previous.get('sources', []), *row.get('sources', []), *observations])
    eligible = [s for s in sources if any(_product(o) for o in s['observations'])]
    if not eligible:
        raise ValueError(str(row.get('id')) + ': no evidence-backed product identity source')
    old = previous.get('primary_source')
    chosen = min(eligible, key=lambda s: (SOURCE_TIERS[s['source']], s['source'] != old, s['source']))['source']
    for s in sources:
        s['role'] = 'primary' if s['source'] == chosen else 'secondary'
        for obs in s['observations']:
            obs['role'] = 'secondary'  # roles belong to envelopes, not historical captures
    history = deepcopy(previous.get('source_history', []))
    if old and old != chosen:
        history.append(dict(at=at or datetime.now(timezone.utc).isoformat(),
                            **{'from': old, 'to': chosen}, reason='higher priority evidence-backed product source', policy=POLICY))
    display = derive(sources, rules)
    from .lineage import enrich_display
    display, conflicts, field_history = enrich_display(sources, display, previous, at)
    result.update(conflicts=conflicts, field_history=field_history, lineage_policy='field-lineage-v1')
    result.update(sources=sources, primary_source=chosen, source_history=history,
                  display=display, source_policy=POLICY)
    from .release_coverage import effective
    result['release_effective']=effective(result)
    if previous.get('discovered_by'):
        result['discovered_by'] = previous['discovered_by']
    if not result.get('discovered_by') and SOURCE_TIERS[chosen] >= 3:
        result['discovered_by'] = chosen
    for field in ('name', 'image', 'category', 'price'):
        result[field] = deepcopy(display[field]['value']) if display[field] else (row.get(field) if field=='name' else None)
    if result['price'] is None:
        result['price_missing'] = row.get('price_missing') or True
    else:
        result['price_missing'] = False
    if 'price_comparable' in row:
        from .price_semantics import comparable
        result['price_comparable'] = comparable(result)
    return result


def _observation(source, url, timestamp, fields, evidence=None):
    proof = {'method': 'legacy_capture', **(evidence or {})}
    if timestamp:
        try:
            if datetime.fromisoformat(timestamp.replace('Z', '+00:00')).utcoffset() is None:
                proof['legacy_capture_time'] = timestamp
                timestamp = None
        except (ValueError, TypeError, AttributeError):
            proof['legacy_capture_time'] = timestamp
            timestamp = None
    if timestamp is None:
        proof['capture_time_missing'] = True
    return dict(source=source, role='secondary', source_url=url, captured_at=timestamp,
                fields=deepcopy(fields), evidence=proof)


def legacy_observations(row):
    """Source-specific migration only; never copy Mi Home values into store slots."""
    if row.get('source_policy') == POLICY:
        refreshed = []
        for field in ('name', 'image', 'category', 'price'):
            old = (row.get('display') or {}).get(field)
            if row.get(field) == (old or {}).get('value'):
                continue
            url = row.get(field + '_source_url') or row.get('source_url')
            owner = publisher(url)
            if not owner:
                raise ValueError('Refreshed field lacks registered source: ' + field)
            stamp = row.get(field + '_captured_at') or row.get(field + '_fetched_at') or row.get('fetched_at') or row.get('captured_at')
            from .lineage import valid_time
            if field=='name' and old is None and not valid_time(stamp) and any(o['fields'].get('name')==row.get('name') for e in row.get('sources',[]) for o in e.get('observations',[e])):
                continue  # the readable legacy name is already retained as an unadopted observation
            refreshed.append(_observation(owner, url, stamp, {field: row.get(field), **({'price_kind': row.get('price_kind')} if field == 'price' else {})}))
        return refreshed
    source = publisher(row.get('source_url'))
    timestamp = row.get('fetched_at') or row.get('captured_at')
    observations = []
    if source:
        fields = {k: deepcopy(row[k]) for k in ('name', 'category', 'price', 'price_kind', 'image', 'params') if k in row}
        # Explicit source-specific overrides cannot be attributed to the base page.
        for field in ('name', 'image', 'category', 'price'):
            explicit = row.get(field + '_source_url')
            named = row.get(field + '_source')
            if (explicit and publisher(explicit) != source) or (named in ('mijia_baike', 'mihome_directory') and not row.get('catalog_display')):
                fields.pop(field, None)
        if row.get('name_before_baike_repair'):
            fields['name'] = row['name_before_baike_repair']
        # Mi Home discovery rows contain no official shop assertion.
        if source == 'mihome_directory':
            fields = {k: row[k] for k in ('name', 'category') if k in row}
        for field in ('image', 'price'):
            if row.get(field + '_captured_at') or row.get(field + '_fetched_at'):
                fields.pop(field, None)
        observations.append(_observation(source, row['source_url'], timestamp, fields))
        for field in ('image', 'price'):
            url = row.get(field + '_source_url') or row['source_url']
            owner = publisher(url)
            if owner and field in row and (owner != source or row.get(field + '_captured_at') or row.get(field + '_fetched_at')):
                observations.append(_observation(owner, url, row.get(field + '_captured_at') or row.get(field + '_fetched_at') or timestamp,
                                                 {field: row[field], **({'price_kind': row.get('price_kind')} if field == 'price' else {})}))
    if row.get('name_mihome'):
        proof = row.get('mihome_catalog_evidence') or {}
        url = proof.get('source_url')
        model = row.get('mihome_model') or row.get('miio_model')
        # A deterministic official model URL is a legacy locator, not a claimed new fetch.
        url = url or (row.get('source_url') if source == 'mihome_directory' else
                      'https://home.mi.com/webapp/content/baike/product/index.html?model=' + model if model else None)
        if url:
            fields = dict(name=row['name_mihome'], category=row.get('category_mihome'), model=model, pd_id=row.get('mihome_pd_id'))
            icon = row.get('image_mihome')
            if icon:
                fields['icon'] = icon.get('url') if isinstance(icon, dict) else icon
            observations.append(_observation('mihome_directory', url, proof.get('captured_at') or (timestamp if source == 'mihome_directory' else None),
                                             fields, {'method': 'legacy_directory_mapping', 'mapping': deepcopy(proof), 'icon_scope': 'device_icon'}))
    baike = row.get('mijia_baike') or {}
    if baike.get('product_url'):
        observations.append(_observation('mihome_directory', baike['product_url'], baike.get('captured_at'),
            dict(name=baike.get('productName'), model=baike.get('model'), parameters=baike.get('parameters')),
            {'method': 'legacy_baike_mapping', 'sha256': baike.get('product_sha256')}))
    for observation in observations:
        if 'image' in observation['fields']:
            for key in ('image_kind','image_type','width','height','is_product_main'):
                value=row.get(key) if key in ('image_kind','image_type','is_product_main') else row.get('image_'+key)
                if value is not None: observation['fields'][key]=value
            if row.get('image_source_type'):
                observation['fields'].setdefault('image_kind',row['image_source_type'])
    return observations


def migrate_row(row, previous=None, **kwargs):
    from .lineage import legacy_sources
    dates,issues=legacy_sources(row,dates_only=True)
    result=materialize(row, previous, [*legacy_observations(row),*dates], **kwargs)
    for envelope in result['sources']:
        for o in envelope['observations']:
            if not o.get('captured_at'):
                issues.append(dict(source=o['source'],fields=list(o['fields']),reason='历史证据缺少真实抓取时间；保留原始观察，不作为display候选'))
    import json
    retained=[*(previous or {}).get('lineage_issues',[]),*row.get('lineage_issues',[]),*issues]
    result['lineage_issues']=list({json.dumps(i,sort_keys=True,ensure_ascii=False):i for i in retained}.values())
    return result


def coverage(rows):
    primary = Counter(r.get('primary_source') for r in rows)
    distribution = Counter('3+' if len(r['sources']) >= 3 else str(len(r['sources'])) for r in rows)
    return dict(policy=POLICY, total=len(rows), primary_source=dict(primary),
                source_count={k: distribution[k] for k in ('1', '2', '3+')},
                primary_only=sum(len(r['sources']) == 1 for r in rows))


def upsert_source(row, observation, **kwargs):
    """Collector boundary: no collector may assign a different publisher's fields."""
    validate_source(observation)
    from .lineage import valid_time
    if not valid_time(observation.get('captured_at')):
        raise ValueError('new observations require actual field capture time')
    return materialize(row, observations=[observation], **kwargs)


def apply_sources(rows, previous=()):
    from collections import defaultdict, deque
    by_id = defaultdict(deque)
    for row in previous:
        by_id[row['id']].append(row)
    return [migrate_row(row, by_id[row['id']].popleft() if by_id[row['id']] else None) for row in rows]
