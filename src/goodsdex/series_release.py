"""Reviewed release batches; never write a series assertion into product release.

Membership is an exact ID plus a frozen identity (name, model, parameters).
New variants and identity drift require review, not fuzzy matching.
"""
from copy import deepcopy
import json
from pathlib import Path
import re
from urllib.parse import urlparse

from goodsdex.release_dates import digest

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
    if r.get('granularity') == 'month':
        pattern += r'-(?:0[1-9]|1[0-2])'
    elif r.get('granularity') != 'year':
        raise ValueError('Series precision must be year or month')
    if not re.fullmatch(pattern, str(r.get('date', ''))):
        raise ValueError('Invalid series date/precision')
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
    return r


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
        row.pop('series_release', None)
        if not bundle.get('enabled', False) or row['id'] not in by_id:
            continue
        batch, member = by_id[row['id']]
        if is_accessory(row) or row.get('kind') == 'service':
            raise ValueError(f'Accessory cannot inherit series date: {row["id"]}')
        if (digest(identity(row)) != member['identity_sha256']
                or not row['id'].startswith('CN:mi_cn:')
                or row.get('market', 'CN') != batch['series_release']['market']):
            raise ValueError(f'Series membership identity/market drift: {row["id"]}')
        r = deepcopy(batch['series_release'])
        r.update(batch_id=batch['id'], series=batch['series'], generation=batch['generation'],
                 usage='reference', label='系列推出时间')
        parts = r['date'].split('-')
        when = f'{parts[0]} 年' + (f' {int(parts[1])} 月' if len(parts) == 2 else '')
        r['display'] = f'该系列 {when}' + ('发布' if r['event'] == 'announcement' else '开售')
        row['series_release'] = r
    return output


def effective_release(row):
    """Internal order: product official > third party > series > LLM.

    Return provenance intact, including level; callers must not promote to release.
    """
    product = row.get('release') or {}
    series = row.get('series_release') or {}
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
        elif (row.get('series_release') or {}).get('date'):
            result['series'] += 1
        else:
            result['missing'] += 1
    assert result['product'] + result['series'] + result['missing'] == result['total']
    return result
