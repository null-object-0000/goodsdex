"""Reviewed release batches; never write a series assertion into product release.

Membership is an exact ID plus a frozen identity (name, model, parameters).
New variants and identity drift require review, not fuzzy matching.
The reviewed input keeps its legacy series_release key; public rows expose only
release_series. inherited means no product-level release.date is present.
"""
from copy import deepcopy
from datetime import date
import json
from pathlib import Path
import re
from urllib.parse import urlparse

from goodsdex.release_dates import digest
from goodsdex.release_crosschecks import delta_days, verdict

DEFAULT_INPUT = Path(__file__).resolve().parents[2] / 'data/official/series-releases.json'


def is_accessory(row):
    # Multi-category tags include whole machines (even watches under 穿戴配件).
    # Count only explicit kind or unambiguous accessory names.
    return (row.get('kind') == 'accessory'
            or bool(re.search(r'配件|滤芯|滤网|尘袋|主刷|边刷|拖布|充电器|保护壳|底座|基座|上下水装置|喷嘴|抑味棒|气囊', row.get('name', ''))))


def identity(row):
    return {k: row.get(k) for k in ('id', 'name', 'model', 'params')}


def validate_batch(batch):
    r = batch['series_release']
    pattern = r'(?:19|20)\d{2}'
    if r.get('granularity') in ('month', 'day'):
        pattern += r'-(?:0[1-9]|1[0-2])'
        if r['granularity'] == 'day':
            pattern += r'-(?:0[1-9]|[12]\d|3[01])'
    else:
        raise ValueError('Series precision must be month or day')
    if not re.fullmatch(pattern, str(r.get('date', ''))):
        raise ValueError('Invalid series date/precision')
    if r['granularity'] == 'day':
        date.fromisoformat(r['date'])
    if (r.get('level') != 'series' or r.get('source') not in ('official', 'third_party')
            or not r.get('market') or r.get('event') not in ('announcement', 'availability')):
        raise ValueError('Invalid series provenance/market/event')
    e = r.get('evidence') or {}
    u = urlparse(e.get('url', ''))
    if (u.scheme not in ('http', 'https') or not u.hostname or not e.get('quote')
            or not e.get('locator') or not e.get('captured_at')
            or not re.fullmatch('[a-f0-9]{64}', e.get('sha256', ''))
            or e.get('source_type') != r['source']):
        raise ValueError('Series release requires captured evidence')
    if r['source'] == 'official' and not (u.hostname == 'mi.com' or u.hostname.endswith('.mi.com')):
        raise ValueError('Unofficial series source')
    if not all(batch.get(k) for k in ('id', 'series', 'generation', 'members')):
        raise ValueError('Series batch needs explicit generation and members')
    for member in batch['members']:
        if (not member.get('id') or not member.get('identity_reason')
                or not re.fullmatch('[a-f0-9]{64}', member.get('identity_sha256', ''))):
            raise ValueError('Series member needs reviewed identity')
        if not all(re.fullmatch('[a-f0-9]{64}', h) for h in member.get('identity_sha256_alternates', [])):
            raise ValueError('Invalid alternate reviewed identity')
    return r


def reconcile_series(release, batch_id):
    """Same-batch, same-market/event corroboration; never use model filling.

    Publisher identifies the original newsroom, including on a syndication site.
    Independence is an explicit reviewed assertion, not a different URL alone.
    Recompute decisions on every replay; never trust stored status flags.
    Year-only third-party claims cannot prove a <=14-day agreement.
    """
    r = deepcopy(release)
    checks = []
    primary_publisher = (r.get('evidence') or {}).get('publisher')
    for obs in r.pop('crosschecks', []):
        e = obs.get('evidence') or {}
        valid = (obs.get('source') in ('official', 'third_party')
                 and obs.get('independent') is True
                 and obs.get('independence_reason')
                 and obs.get('batch_id') == batch_id
                 and obs.get('market') == r['market']
                 and obs.get('event') == r['event']
                 and primary_publisher and e.get('publisher')
                 and e['publisher'] != primary_publisher
                 and e.get('url') != (r.get('evidence') or {}).get('url')
                 and urlparse(e.get('url') or '').scheme in ('http', 'https')
                 and urlparse(e.get('url') or '').hostname
                 and (obs.get('source') != 'official' or
                      (urlparse(e['url']).hostname == 'mi.com' or urlparse(e['url']).hostname.endswith('.mi.com')))
                 and e.get('verified') is True
                 and e.get('url') and e.get('quote')
                 and re.fullmatch('[a-f0-9]{64}', e.get('sha256', ''))
                 and e.get('captured_at'))
        delta = None
        if valid and len(r['date']) >= 7 and len(obs.get('date') or '') >= 7:
            try:
                delta = delta_days(r['date'], obs['date'])
            except (ValueError, TypeError):
                pass
        checks.append(dict(deepcopy(obs), delta_days=delta,
                           verdict=verdict(delta) if delta is not None else 'unverified'))
    r['checks'] = checks
    if r['source'] == 'official':
        r.update(crosscheck_status='official', display_allowed=True, internal_only=False)
        return r
    statuses = {c['verdict'] for c in checks}
    status = ('conflict' if 'conflict' in statuses else 'disagreement' if 'disagreement' in statuses
              else 'corroborated' if 'corroborated' in statuses else 'unverified')
    allowed = status == 'corroborated'
    r.update(crosscheck_status=status, display_allowed=allowed,
             internal_only=not allowed, manual_review_required=status == 'conflict')
    if not allowed:
        r.update(usage='disabled', display=None)
    if status == 'conflict':
        r.update(original_date=r['date'], date=None)
    return r



def _strip_colour(name):
    """去掉名称末尾的颜色词（……灰色 / 深锖色），颜色不算型号身份。"""
    parts = str(name or "").split()
    while parts and parts[-1].endswith("色"):
        parts.pop()
    return " ".join(parts)


def _same_series_identity(row, member):
    """只容忍「名称末尾多/少一个颜色词」：把审过的名字代回去重算哈希，必须命中。"""
    reviewed = member.get("reviewed_name")
    pinned = member.get("identity_sha256")
    if not reviewed or not pinned:
        return False
    if _strip_colour(row.get("name")) != _strip_colour(reviewed):
        return False
    # 除名称以外（型号、参数）必须完全一致，否则仍是身份漂移。
    probe = dict(identity(row))
    probe["name"] = reviewed
    return digest(probe) == pinned

def apply_series_releases(rows, path=DEFAULT_INPUT):
    bundle = json.loads(Path(path).read_text())
    if bundle.get('schema') != 1 or bundle.get('scope') not in ('pilot', 'reviewed_rollout'):
        raise ValueError('Only explicitly reviewed series batches are enabled')
    by_id, batches = {}, set()
    for batch in bundle['batches']:
        validate_batch(batch)
        if batch['id'] in batches:
            raise ValueError('Duplicate series batch')
        batches.add(batch['id'])
        for member in batch['members']:
            if member['id'] in by_id:
                raise ValueError('Conflicting series membership')
            by_id[member['id']] = (batch, member)
    output = deepcopy(rows)
    for row in output:
        # Rebuild the managed projection; removed memberships cannot linger.
        row.pop('series_release', None)  # Retire the old public spelling.
        row.pop('release_series', None)
        if not bundle.get('enabled', False) or row['id'] not in by_id:
            continue
        batch, member = by_id[row['id']]
        if is_accessory(row) or row.get('kind') == 'service':
            raise ValueError(f'Accessory cannot inherit series date: {row["id"]}')
        if (digest(identity(row)) not in [member['identity_sha256'], *member.get('identity_sha256_alternates', [])]
                and not _same_series_identity(row, member)
                or not row['id'].startswith('CN:mi_cn:')
                or row.get('market', 'CN') != batch['series_release']['market']):
            raise ValueError(f'Series membership identity/market drift: {row["id"]}')
        r = reconcile_series(batch['series_release'], batch['id'])
        r.update(batch_id=batch['id'], series=batch['series'], generation=batch['generation'],
                 label='系列推出时间')
        if r['display_allowed']:
            r['usage'] = 'reference'
            parts = r['date'].split('-')
            when = f'{parts[0]} 年' + (f' {int(parts[1])} 月' if len(parts) >= 2 else '')
            if len(parts) == 3:
                when += f' {int(parts[2])} 日'
            r['display'] = f'该系列 {when}' + ('发布' if r['event'] == 'announcement' else '开售')
        r['inherited'] = not bool((row.get('release') or {}).get('date'))
        row['release_series'] = r
    return output


def effective_release(row):
    """Internal order: product official > third party > series > LLM.

    Return provenance intact, including level; callers must not promote to release.
    """
    product = row.get('release') or {}
    series = row.get('release_series') or {}
    if is_accessory(row) or row.get('kind') == 'service':
        return None
    if product.get('date') and product.get('usage') != 'disabled' and product.get('level', 'product') == 'product' and product.get('source') in ('official', 'official_hidden', 'third_party'):
        return dict(product, level='product')
    if series.get('date') and series.get('usage') != 'disabled' and series.get('level') == 'series' and series.get('source') in ('official', 'third_party'):
        return deepcopy(series)
    if product.get('date') and product.get('usage') != 'disabled' and product.get('source') == 'llm':
        return dict(product, level='product')
    return None


def coverage(rows):
    result = dict(total=len(rows), product=0, series=0, missing=0, accessories=0)
    for row in rows:
        result['accessories'] += is_accessory(row)
        # Coverage counts retained assertions, including disabled product claims.
        # Usability for internal decisions is separately resolved above.
        if (row.get('release') or {}).get('date'):
            result['product'] += 1
        elif (row.get('release_series') or {}).get('date'):
            result['series'] += 1
        else:
            result['missing'] += 1
    assert result['product'] + result['series'] + result['missing'] == result['total']
    return result
