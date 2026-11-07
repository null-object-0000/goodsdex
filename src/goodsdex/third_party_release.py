"""Reviewed exact-SKU media assertions; fail closed without two real origins."""
from copy import deepcopy
from datetime import date
import json
import re
from pathlib import Path
from urllib.parse import urlparse
from .release_scope import release_scope

INPUT = Path(__file__).resolve().parents[2] / 'data/third-party/release-dates.json'
PUBLISHERS = ('ithome.com', 'mydrivers.com', 'zol.com.cn', 'pconline.com.cn')
OFFICIAL = ('apple.com', 'apple.com.cn', 'mi.com', 'dji.com', 'hp.com', 'fujifilm.com', 'fujifilm-x.com', 'byd.com', 'bydauto.com.cn')


def origin(assertion):
    e = assertion.get('evidence') or {}
    host = urlparse(e.get('url', '')).hostname or ''
    domain = next((d for d in (*PUBLISHERS, *OFFICIAL) if host == d or host.endswith('.'+d)), host)
    # Explicit attribution to a shared upstream does not become independent.
    return e.get('upstream_origin') or domain


def assess(assertions):
    valid = []
    for a in assertions:
        e = a.get('evidence') or {}
        if (a.get('source') not in ('official', 'third_party') or a.get('market') != 'CN'
            or a.get('event') not in ('announcement', 'availability')
            or not all(e.get(k) for k in ('url','quote','sha256','captured_at','locator'))
            or e.get('identity_verified') is not True or e.get('event_verified') is not True):
            continue
        u = urlparse(e['url'])
        allowed = PUBLISHERS if a['source'] == 'third_party' else OFFICIAL
        if u.scheme not in ('http', 'https') or not any(u.hostname == d or (u.hostname or '').endswith('.'+d) for d in allowed):
            raise ValueError('Unapproved evidence source')
        if e.get('source_type') != a['source']:
            raise ValueError('Evidence provenance mismatch')
        if not re.fullmatch('[a-f0-9]{64}', e['sha256']) or not origin(a):
            raise ValueError('Invalid captured evidence')
        if a['source'] == 'third_party' and not any((urlparse(e['url']).hostname or '').endswith('.'+d) or urlparse(e['url']).hostname == d for d in PUBLISHERS):
            raise ValueError('Unapproved media source')
        date.fromisoformat(a['date'])  # Exact days: never compare fabricated month day 1.
        valid.append(a)
    pairs = [(a,b) for i,a in enumerate(valid) for b in valid[i+1:]
             if origin(a) != origin(b) and a['evidence']['sha256'] != b['evidence']['sha256'] and a['event'] == b['event']]
    if not pairs:
        return dict(status='unverified', delta_days=None, display_allowed=False)
    # Every verified same-event source participates; a third conflicting source
    # cannot be hidden by selecting the closest pair.
    delta = max(abs((date.fromisoformat(a['date'])-date.fromisoformat(b['date'])).days) for a,b in pairs)
    status = 'corroborated' if delta <= 14 else 'disagreement' if delta <= 45 else 'conflict'
    return dict(status=status, delta_days=delta, display_allowed=status=='corroborated')



def _same_name(a, b):
    """商品名的空白差异（全角/连续空格）不算身份变化。"""
    return " ".join(str(a or "").split()) == " ".join(str(b or "").split())

def apply_third_party(rows, path=INPUT):
    bundle = json.loads(Path(path).read_text()) if Path(path).exists() else dict(schema=1,candidates=[])
    if bundle.get('schema') != 1:
        raise ValueError('Unknown media release schema')
    by_id = {}
    for c in bundle['candidates']:
        if c['id'] in by_id:
            raise ValueError('Duplicate media release ID')
        by_id[c['id']] = c
    output = deepcopy(rows)
    for row in output:
        c = by_id.get(row['id'])
        old = row.get('release') or {}
        if c and old.get('source') not in ('official', 'official_hidden'):
            # 同一商品可能出现在多个分类快照里（同 id 多行），按 id 去重后
            # 再判断"名字是否唯一属于它"。
            same_name_ids = {r['id'] for r in rows if _same_name(r.get('name'), c['name'])}
            if (not _same_name(row['name'], c['name']) or release_scope(row)['tier'] != 'machine'
                or len(same_name_ids) != 1):
                raise ValueError('Media identity/scope changed: '+row['id'])
            assertions = c['assertions']
            decision = assess(assertions)
            if not assertions or assertions[0]['source'] != 'third_party':
                raise ValueError('Media primary must retain third_party provenance')
            a = assertions[0]
            value = a['date'][:7]
            y,m = map(int,value.split('-'))
            r = dict(date=value if decision['status']!='conflict' else None,
                granularity='month', source='third_party', event=a['event'], market='CN',
                confidence='high' if decision['display_allowed'] else 'low',
                evidence=deepcopy(a['evidence']), assertions=deepcopy(assertions),
                family='media:'+row['id'], crosscheck_status=decision['status'],
                crosscheck_delta_days=decision['delta_days'], corroborated=decision['display_allowed'],
                display_allowed=decision['display_allowed'], internal_only=not decision['display_allowed'],
                usage='fact' if decision['display_allowed'] else 'disabled',
                display=f'{y} 年 {m} 月' if decision['display_allowed'] else None,
                label='发布时间' if a['event']=='announcement' else '发售时间',
                manual_review_required=decision['status']=='conflict')
            # Preserve legacy evidence without accumulating on every replay.
            if old.get('previous_release'):
                r['previous_release'] = deepcopy(old['previous_release'])
            elif old and 'assertions' not in old:
                r['previous_release'] = deepcopy(old)
            row['release'] = r
        elif old.get('source') == 'third_party':
            # Model memory is audit material, never an independent media source.
            assertions = old.get('assertions') or []
            decision = assess(assertions)
            old.update(display_allowed=decision['display_allowed'], internal_only=not decision['display_allowed'],
                       corroborated=decision['display_allowed'], crosscheck_delta_days=decision['delta_days'])
            if not decision['display_allowed']:
                old.update(usage='disabled', display=None, crosscheck_status=decision['status'],
                           policy_reason='two_independent_original_sources_required')
    return output
