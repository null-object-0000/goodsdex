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
LLM_INPUT = Path(__file__).resolve().parents[2] / 'data/llm/release-dates.json'
CROSSCHECK_INPUT = LLM_INPUT.with_name('release-crosschecks.json')


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest()


def validate(candidate):
    if not candidate.get('family') or not candidate.get('ids'):
        raise ValueError('Release candidate needs exact family and IDs')
    r = candidate['release']
    if r.get('level', 'product') != 'product' or r.get('source') == 'series':
        raise ValueError('Series assertions belong in release_series, never release')
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
    model_citation = r['source'] == 'llm' and e.get('capture_type') == 'model_output'
    valid_url = url.scheme in ('https', 'http') and bool(url.hostname)
    if (not e.get('locator') or
            (not (valid_url or e.get('quote')) if model_citation else not (valid_url and e.get('quote')))):
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


def brand_sample(families, seed):
    """Ten per full 100; ceil(10%) of the last block, independently per brand."""
    import random
    import math
    rng = random.Random(seed)
    ordered = sorted(families)
    return [f for i in range(0, len(ordered), 100)
            for f in rng.sample(ordered[i:i+100], math.ceil(len(ordered[i:i+100])/10))]


def brand_llm_gate(candidates, reviews):
    gates = {}
    for brand in sorted({c['brand'] for c in candidates}):
        cs = [c for c in candidates if c['brand'] == brand]
        r = reviews.get(brand, {})
        if r.get('universe_sha256') != digest(cs):
            raise ValueError('Brand LLM review does not cover this candidate universe')
        by_family = {c['family']: c for c in cs}
        if len(by_family) != len(cs):
            raise ValueError('Duplicate brand LLM family')
        expected = brand_sample(by_family, r['seed'])
        samples = r.get('samples', [])
        if [s['family'] for s in samples] != expected:
            raise ValueError('Brand review is not the reproducible 10% sample')
        for s in samples:
            c = by_family[s['family']]
            if (s.get('candidate_sha256') != digest(c) or not isinstance(s.get('correct'), bool)
                    or not s.get('checked_at') or not s.get('verification_url')
                    or not s.get('verification_quote') or not s.get('verdict_reason')):
                raise ValueError('Incomplete brand LLM review')
            # A date match alone is insufficient: model, event, market and evidence
            # must also be checked. Unverifiable sources count as failures.
            matched = s.get('correct_date') == c['release']['date']
            if s['correct'] and not (matched and s.get('identity_match') is True
                                     and s.get('evidence_supported') is True):
                raise ValueError('Brand LLM sample does not support its verdict')
        accuracy = sum(s['correct'] for s in samples) / len(samples)
        gates[brand] = dict(usage='disabled' if accuracy < .90 else 'reference',
            confidence='high' if accuracy >= .97 else 'medium' if accuracy >= .90 else 'low',
            sample_size=len(samples), accuracy=accuracy, universe_sha256=digest(cs))
    return gates


def apply_release_dates(rows, path=DEFAULT_INPUT, llm_path=None, crosscheck_path=None):
    path = Path(path)
    if not path.exists():
        raise ValueError(f'Missing reviewed release input: {path}')
    bundle = json.loads(path.read_text())
    from goodsdex.release_crosschecks import reconcile
    check_path = Path(crosscheck_path) if crosscheck_path is not None else CROSSCHECK_INPUT if path == DEFAULT_INPUT else None
    check_bundle = json.loads(check_path.read_text()) if check_path and check_path.exists() else {}
    if check_bundle and check_bundle.get('schema') != 1:
        raise ValueError('Unsupported independent check schema')
    independent_checks = check_bundle.get('checks', {})
    if any(c.get('source') != 'llm' or c.get('independent') is not True for c in independent_checks.values()):
        raise ValueError('Independent checks must retain LLM provenance')
    if bundle.get('schema') != 1:
        raise ValueError('Unsupported release input schema')
    candidates = bundle['candidates']
    # A separate, removable sidecar: never merges candidates into official inputs.
    extra_path = Path(llm_path) if llm_path is not None else LLM_INPUT if path == DEFAULT_INPUT else None
    extra = json.loads(extra_path.read_text()) if extra_path and extra_path.exists() else {}
    extra_cs = extra.get('candidates', []) if extra.get('enabled', False) else []
    if extra and extra.get('schema') != 1:
        raise ValueError('Unsupported LLM sidecar schema')
    extra_ids = [key for c in extra_cs for key in c['ids']]
    if len(extra_ids) != len(set(extra_ids)):
        raise ValueError('Conflicting LLM sidecar IDs')
    if any(c['release']['source'] != 'llm' for c in extra_cs):
        raise ValueError('LLM sidecar may only contain LLM candidates')
    brand_gates = brand_llm_gate(extra_cs, extra.get('reviews', {}))
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
    for c in extra_cs:
        validate(c)
        for key in c['ids']:
            if key in withdrawn:
                continue
            if key in by_id:
                # Existing reviewed data always wins, especially official evidence.
                continue
            by_id[key] = c
    extra_families = {c['family'] for c in extra_cs}
    managed_ids = set(extra.get('managed_ids', []))
    output = deepcopy(rows)
    for row in output:
        previous_release = deepcopy(row.get('release') or {})
        if row['id'] in withdrawn:
            row.pop('release', None)
            continue
        c = by_id.get(row['id'])
        if not c:
            if row['id'] in managed_ids and (row.get('release') or {}).get('source') == 'llm':
                row.pop('release', None)
            # Recover old policy nulls from the retained original assertion.
            # This also covers third-party rows outside managed candidates.
            existing = row.get('release') or {}
            if existing.get('source') == 'third_party' and not existing.get('date'):
                originals = {p['date'] for p in existing.get('checks', [])
                             if p.get('verdict') == 'original' and p.get('source') == 'third_party'
                             and p.get('date')}
                if len(originals) == 1:
                    existing['date'] = originals.pop()
            # Existing dates must still satisfy the provenance contract.
            if row.get('release') and row['release'].get('date'):
                validate(dict(family=row['id'], ids=[row['id']], release=row['release']))
                if row['release']['source'] in ('llm', 'official_hidden'):
                    raise ValueError(f'Unreviewed LLM/hidden release outside sampled universe: {row["id"]}')
                if row['release']['source'] == 'third_party':
                    family = row['release'].get('family') or row['id']
                    check = independent_checks.get(family)
                    if check and check['original_sha256'] != digest(row['release']):
                        prior = row['release'].get('checks', [])
                        replay = (any(p.get('original_sha256') == check['original_sha256'] for p in prior)
                                  and any(p.get('verdict') == 'original' and p['date'] == row['release']['date']
                                          and p['source'] == 'third_party' for p in prior))
                        if not replay:
                            raise ValueError(f'Stale independent release check: {family}')
                    row['release'] = reconcile(row['release'], [check] if check else [], row['release'].get('checks', []))
            continue
        if c['family'].startswith('CN:apple_cn:product:') and row.get('product_id') != c['family']:
            raise ValueError(f'Release family identity changed: {row["id"]}')
        r = deepcopy(c['release'])
        inferred = r['source'] == 'llm'
        current_gate = brand_gates[c['brand']] if c['family'] in extra_families else gate
        is_hidden = r['source'] == 'official_hidden'
        if is_hidden and hidden.get(c['category'], {}).get('usage') != 'reference':
            row.pop('release', None)
            continue
        if inferred and current_gate['usage'] == 'disabled' and previous_release.get('source') not in ('official', 'official_hidden', 'third_party'):
            row.pop('release', None)
            continue
        planned = r['event'] == 'planned_availability'
        r['usage'] = 'reference' if planned or is_hidden or inferred else 'fact'
        r['inferred'] = inferred
        r['family'] = c['family']
        year, month = map(int, r['date'].split('-'))
        r['display'] = (f'约 {year} 年 {month} 月（推断）' if inferred else
                        f'预计 {year} 年 {month} 月（官方计划）' if planned else f'{year} 年 {month} 月')
        r['label'] = ('推出月份（推断）' if inferred else '预计发售' if planned else
                      '发布时间' if r['event'] == 'announcement' else '发售时间')
        if r.get('retrospective') and r['source'] == 'official':
            market_label = {'JP': '日本', 'US': '美国',
                            'GLOBAL_REPORTED_BY_CN_OFFICIAL': '全球'}.get(r.get('market'), '')
            r['label'] = market_label + ('推出月份（官方回溯）' if r['event'] == 'announcement' else '发售时间')
        if is_hidden:
            r['label'] = '推出月份（参考）'
            r['display'] = f'{year} 年 {month} 月（参考）'
            r['validation'] = hidden[c['category']]
        if inferred:
            r['validation'] = current_gate
            r['confidence'] = current_gate.get('confidence') or ('high' if current_gate['accuracy'] >= .97 else 'medium')
            r['display_allowed'] = False
            r['internal_only'] = True
            r['estimate_notice'] = '按型号世代估算'
        observations = []
        check = independent_checks.get(c['family'])
        if check:
            if check['original_sha256'] != digest(c['release']):
                raise ValueError(f'Stale independent release check: {c["family"]}')
            observations.append(check)
        # Preserve official priority and document the rejected assertion.
        old = previous_release
        if old.get('date') and ((old.get('source') in ('official', 'official_hidden') and r['source'] not in ('official', 'official_hidden')) or (old.get('source') == 'third_party' and inferred)):
            observations.insert(0, dict(source=r['source'], date=r['date'], family=c['family'], evidence=deepcopy(r.get('evidence'))))
            r = old
        elif old.get('date') and (old['date'], old['source']) != (r['date'], r['source']):
            observations.insert(0, dict(source=old['source'], date=old['date'], evidence=deepcopy(old.get('evidence'))))
        # Sidecar overlap is audited even when a reviewed source wins.
        for alt in extra_cs:
            if row['id'] in alt['ids'] and alt['family'] != c['family']:
                observations.append(dict(source='llm', date=alt['release']['date'], family=alt['family'], evidence=deepcopy(alt['release'].get('evidence'))))
                alt_check = independent_checks.get(alt['family'])
                if alt_check:
                    if alt_check['original_sha256'] != digest(alt['release']):
                        raise ValueError('Stale independent sidecar check')
                    observations.append(alt_check)
        row['release'] = reconcile(r, observations, old.get('checks', []))
    if path == DEFAULT_INPUT:
        from goodsdex.third_party_release import apply_third_party
        output = apply_third_party(output)
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
    return dict(deprecated=True, scope='legacy_all_published_rows', not_for_external_reporting=True,
                total=len(rows), covered=count, coverage=count / len(rows) if rows else 0,
                sources=sources, brands=brands)
