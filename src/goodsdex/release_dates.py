"""Evidence-backed, month-only release dates. Unknown is always absent.

Candidates are reviewed inputs, never a lookup from model names or model years.
LLM eligibility is bound to the exact candidate universe that was sampled.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse

DEFAULT_INPUT = Path(__file__).resolve().parents[2] / 'data/official/release-dates.json'


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest()


def validate(candidate):
    if not candidate.get('family') or not candidate.get('ids'):
        raise ValueError('Release candidate needs exact family and IDs')
    r = candidate['release']
    if not re.fullmatch(r'(?:19|20)\d{2}-(?:0[1-9]|1[0-2])', str(r.get('date', ''))):
        raise ValueError('Release date must have month precision')
    if r.get('granularity') != 'month' or r.get('source') not in ('official', 'official_hidden', 'third_party', 'llm'):
        raise ValueError('Invalid release provenance/granularity')
    if r.get('confidence') not in ('high', 'medium', 'low'):
        raise ValueError('Invalid release confidence')
    if r.get('event') not in ('announcement', 'availability', 'planned_availability'):
        raise ValueError('Release event must distinguish announcement and sale')
    e = r.get('evidence') or {}
    url = urlparse(e.get('url', ''))
    if url.scheme not in ('https', 'http') or not url.hostname or not e.get('quote') or not e.get('locator'):
        raise ValueError('Release date requires retrievable evidence and locator')
    if not re.fullmatch('[a-f0-9]{64}', e.get('sha256', '')) or not e.get('captured_at'):
        raise ValueError('Release evidence requires capture hash/time')
    if e.get('source_type') not in ('official', 'third_party'):
        raise ValueError('Evidence must identify its underlying source')
    official_domains = ('mi.com', 'apple.com', 'apple.com.cn', 'hpstore.cn',
                        'fujifilm-x.com', 'fujifilm.com', 'fujifilm.com.cn',
                        'bydauto.com.cn', 'byd.com', 'dji.com')
    if e['source_type'] == 'official' and not any(
            url.hostname == d or url.hostname.endswith('.'+d) for d in official_domains):
        raise ValueError('Unofficial domain cannot be marked official')
    if e.get('isPageShow') is False and r['source'] != 'official_hidden':
        raise ValueError('Hidden official parameter must use reviewed official_hidden provenance')
    if r['source'] == 'official_hidden':
        if (e['source_type'] != 'official' or e.get('isPageShow') is not False
                or not candidate.get('category') or candidate.get('method') != 'hidden_official_parameter'):
            raise ValueError('Hidden release requires official hidden evidence and category')
    elif r['source'] != 'llm' and r['source'] != e['source_type']:
        raise ValueError('Release source cannot impersonate underlying evidence')
    if r['source'] == 'llm' and not r.get('model'):
        raise ValueError('LLM release must retain model provenance')
    if candidate.get('method') == 'explicit_official_parameter' and e.get('isPageShow') is not True:
        raise ValueError('Hidden official parameter is not an explicit page date')
    return r


def hidden_gate(candidates, review):
    """Only the reviewed universe and independently checked categories may roll out.

    Fewer than 30 distinct products never unlocks publication, even a small census.
    90–97% candidates stay in the internal review file, outside the public release.
    """
    universe = [c for c in candidates if c['release']['source'] == 'official_hidden']
    if not universe:
        return {}
    if review.get('universe_sha256') != digest(universe):
        raise ValueError('Hidden review does not cover this candidate universe')
    samples = review.get('samples', [])
    by_family = {c['family']: c for c in universe}
    if len(samples) < 30 or len({s['family'] for s in samples}) != len(samples):
        raise ValueError('Hidden rollout requires at least 30 distinct products')
    categories = {}
    for s in samples:
        c = by_family.get(s['family'])
        if (not c or s.get('candidate_sha256') != digest(c)
                or not s.get('verification_url') or not s.get('verification_quote')
                or not s.get('correct_date') or not s.get('checked_at')
                or not isinstance(s.get('correct'), bool)
                or s['correct'] != (s['correct_date'] == c['release']['date'])):
            raise ValueError('Incomplete hidden release sample review')
        if urlparse(s['verification_url']).hostname == urlparse(c['release']['evidence']['url']).hostname:
            raise ValueError('Hidden dates require an independent second source')
        categories.setdefault(c['category'], []).append(s['correct'])
    return {cat: dict(sample_size=len(values), accuracy=sum(values)/len(values),
                     usage='reference' if sum(values)/len(values) >= .97 else 'internal' if sum(values)/len(values) >= .90 else 'disabled')
            for cat, values in categories.items()}


def llm_gate(candidates, review):
    universe = [c for c in candidates if c['release']['source'] == 'llm']
    if not universe:
        return {'usage': 'disabled', 'sample_size': 0, 'accuracy': None}
    if review.get('universe_sha256') != digest(universe):
        raise ValueError('LLM review does not cover this candidate universe')
    samples = review.get('samples', [])
    by_family = {c['family']: c for c in universe}
    # Family sampling prevents 30 capacity/color variants counting as 30 checks.
    if len(samples) != 30 or len({s['family'] for s in samples}) != 30:
        raise ValueError('LLM rollout requires 30 distinct reviewed model families')
    import random
    expected = random.Random(review['seed']).sample(sorted(by_family), 30)
    if [s['family'] for s in samples] != expected:
        raise ValueError('Review is not the reproducible random sample')
    for s in samples:
        c = by_family[s['family']]
        if (s.get('candidate_sha256') != digest(c) or not s.get('verification_url')
                or not s.get('verification_quote') or not s.get('correct_date')
                or not s.get('checked_at') or not isinstance(s.get('correct'), bool)):
            raise ValueError('Incomplete release sample review')
        if s['correct'] != (s['correct_date'] == c['release']['date']):
            raise ValueError('Release sample result disagrees with correct date')
    accuracy = sum(s['correct'] for s in samples) / 30
    usage = 'disabled' if accuracy < .90 else 'reference' if accuracy < .97 else 'fact'
    return dict(usage=usage, sample_size=30, accuracy=accuracy,
                universe_sha256=review['universe_sha256'])


def apply_release_dates(rows, path=DEFAULT_INPUT):
    path = Path(path)
    if not path.exists():
        raise ValueError(f'Missing reviewed release input: {path}')
    bundle = json.loads(path.read_text())
    if bundle.get('schema') != 1:
        raise ValueError('Unsupported release input schema')
    candidates = bundle['candidates']
    withdrawn = bundle.get('withdrawn_release_ids', {})
    for c in candidates:
        validate(c)
    if len({c['family'] for c in candidates}) != len(candidates):
        raise ValueError('Duplicate release family')
    gate = llm_gate(candidates, bundle.get('review', {}))
    hidden = hidden_gate(candidates, bundle.get('hidden_review', {}))
    by_id = {}
    for c in candidates:
        for key in c['ids']:
            if key in withdrawn:
                raise ValueError(f'Withdrawn release evidence cannot be published: {key}')
            if key in by_id:
                raise ValueError(f'Conflicting release candidates for {key}')
            by_id[key] = c
    output = deepcopy(rows)
    for row in output:
        if row['id'] in withdrawn:
            row.pop('release', None)
            continue
        c = by_id.get(row['id'])
        if not c:
            # Existing dates must still satisfy the provenance contract.
            if row.get('release'):
                validate(dict(family=row['id'], ids=[row['id']], release=row['release']))
                if row['release']['source'] in ('llm', 'official_hidden'):
                    raise ValueError(f'Unreviewed LLM/hidden release outside sampled universe: {row["id"]}')
            continue
        if c['family'].startswith('CN:apple_cn:product:') and row.get('product_id') != c['family']:
            raise ValueError(f'Release family identity changed: {row["id"]}')
        r = deepcopy(c['release'])
        inferred = r['source'] == 'llm'
        is_hidden = r['source'] == 'official_hidden'
        if is_hidden and hidden.get(c['category'], {}).get('usage') != 'reference':
            row.pop('release', None)
            continue
        if inferred and gate['usage'] == 'disabled':
            row.pop('release', None)
            continue
        planned = r['event'] == 'planned_availability'
        r['usage'] = 'reference' if planned or is_hidden else gate['usage'] if inferred else 'fact'
        r['inferred'] = inferred
        r['family'] = c['family']
        year, month = map(int, r['date'].split('-'))
        r['display'] = (f'约 {year} 年 {month} 月（推断）' if inferred else
                        f'预计 {year} 年 {month} 月（官方计划）' if planned else f'{year} 年 {month} 月')
        r['label'] = ('推出月份（推断）' if inferred else '预计发售' if planned else
                      '发布时间' if r['event'] == 'announcement' else '发售时间')
        if is_hidden:
            r['label'] = '推出月份（参考）'
            r['display'] = f'{year} 年 {month} 月（参考）'
            r['validation'] = hidden[c['category']]
        if inferred:
            r['validation'] = gate
        row['release'] = r
    return output


def coverage(rows):
    brands = {}
    sources = {s: 0 for s in ('official', 'official_hidden', 'third_party', 'llm')}
    for row in rows:
        brand = row.get('brand') or ('小米' if row['id'].startswith('CN:mi_cn:') else '其他')
        counts = brands.setdefault(brand, dict(total=0, true_source=0, official_hidden=0, llm=0, missing=0))
        counts['total'] += 1
        r = row.get('release') or {}
        if r.get('date'):
            sources[r['source']] += 1
            counts[r['source'] if r['source'] in ('llm', 'official_hidden') else 'true_source'] += 1
        else:
            counts['missing'] += 1
    count = sum(sources.values())
    return dict(total=len(rows), covered=count, coverage=count / len(rows) if rows else 0,
                sources=sources, brands=brands)
