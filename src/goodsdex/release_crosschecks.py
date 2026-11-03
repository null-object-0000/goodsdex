"""Deterministic release conflict policy; provenance never changes on agreement."""
from copy import deepcopy
from datetime import date
import re
from urllib.parse import urlparse


def delta_days(left, right):
    """Month comparison: same month=0, otherwise 30*month distance.

    Whenever either value has only month precision, discard both day parts.
    Day/day pairs use actual calendar days. No invented day-of-month.
    """
    def parse(value):
        parts = [int(p) for p in value.split('-')]
        if len(parts) not in (2, 3):
            raise ValueError('Expected ISO month or day')
        return date(*parts, *([1] if len(parts) == 2 else []))
    a, b = parse(left), parse(right)
    if len(left) == 7 or len(right) == 7:
        return abs((a.year-b.year)*12+a.month-b.month)*30
    return abs((a-b).days)


def verdict(delta):
    return 'corroborated' if delta <= 14 else 'disagreement' if delta <= 45 else 'conflict'


def traceable(assertion):
    """A reason is model prose, never a citation. Keep citations separately."""
    e = assertion.get('evidence') or {}
    if not isinstance(e, dict):
        return False
    u = urlparse(e.get('url') or '')
    return bool((u.scheme in ('http', 'https') and u.hostname) or
                (isinstance(e.get('quote'), str) and e['quote'].strip()))


def hard_evidence(assertion):
    e = assertion.get('evidence') or {}
    if not isinstance(e, dict) or not traceable(assertion):
        return False
    captured = bool(e.get('url') and e.get('quote') and e.get('sha256') and e.get('captured_at'))
    # A model-supplied URL/quote can trigger internal checking; it becomes hard
    # evidence only after a reviewer verifies identity, market, event and date.
    return captured and (assertion['source'] != 'llm' or e.get('verified') is True)


def contemporary(assertion):
    e = assertion.get('evidence') or {}
    stamp = e.get('published_at') or e.get('quote') or ''
    match = re.search(r'(20\d{2}|19\d{2})[-/](\d{1,2})[-/]\d{1,2}', stamp)
    return bool(assertion['source'] == 'third_party' and hard_evidence(assertion)
                and match and f'{match[1]}-{int(match[2]):02}' == assertion.get('date', '')[:7])


def reconcile(release, observations=(), previous_checks=()):
    """Re-evaluate historical assertions under the evidence policy, without deletion.

    Numeric verdicts remain audit data. Unsupported model disagreement has no
    negative decision weight, including model/model pairs. Only two contradictory
    hard sources may erase a date; all other conflicts retain an internal value.
    """
    r = deepcopy(release)
    original = dict(source=r['source'], date=r['date'])
    primary = dict(original, evidence=deepcopy(r.get('evidence')))
    checks = []
    def add(item):
        if item not in checks:
            checks.append(item)
    for check in previous_checks:
        item = deepcopy(check)
        # Policy annotations are derived, never trusted from an old build.
        for key in ('effective_verdict', 'decision_reason', 'hard_conflict'):
            item.pop(key, None)
        if item.get('verdict') == 'original' and all(item.get(k) == v for k, v in original.items()):
            item['evidence'] = primary['evidence']
        add(item)
    add(dict(primary, delta_days=0, verdict='original'))
    known = [original]
    for check in previous_checks:
        value = dict(source=check['source'], date=check.get('date'))
        if value['date'] and value not in known:
            known.append(value)
    for observation in observations:
        obs = deepcopy(observation)
        if not obs.get('date'):
            add(dict(obs, delta_days=None, verdict='unverified', compared_to=original))
            continue
        for other in known:
            if other != original and other == dict(source=obs['source'], date=obs['date']):
                continue
            delta = delta_days(other['date'], obs['date'])
            add(dict(obs, delta_days=delta, verdict=verdict(delta), compared_to=other))
        value = dict(source=obs['source'], date=obs['date'])
        if value not in known:
            known.append(value)
    def assertion_for(ref):
        if ref == original:
            return primary
        return next((c for c in checks if c['source'] == ref['source']
                     and c.get('date') == ref.get('date') and traceable(c)), ref)
    for check in checks:
        raw = check['verdict']
        check['effective_verdict'] = raw
        if raw not in ('conflict', 'disagreement'):
            continue
        other = assertion_for(check.get('compared_to', original))
        unsupported = any(a['source'] == 'llm' and not traceable(a) for a in (check, other))
        if unsupported:
            check.update(effective_verdict='unverified', decision_reason='unsupported_model_dissent_ignored')
        elif (contemporary(primary) and not (hard_evidence(check) and hard_evidence(other))):
            check.update(effective_verdict='unverified', decision_reason='contemporary_report_precedes_model_memory')
        elif raw == 'conflict':
            check['hard_conflict'] = hard_evidence(check) and hard_evidence(other)
    r['checks'] = checks
    severity = {'corroborated': 0, 'unverified': 1, 'disagreement': 2, 'conflict': 3}
    worst = max((severity.get(c['effective_verdict'], -1) for c in checks), default=-1)
    official = r['source'] in ('official', 'official_hidden')
    has_independent = any(c['source'] == 'llm' and c.get('independent') is True
                          and c.get('date') and c['verdict'] == 'corroborated' for c in checks)
    # Abstentions and unsupported dissent cannot subtract an existing agreement.
    r['corroborated'] = has_independent and worst < 2
    if official:
        r['crosscheck_status'] = 'official_preserved' if any(c['verdict'] in ('conflict', 'disagreement') for c in checks) else 'official'
        return r
    status = 'conflict' if worst == 3 else 'disagreement' if worst == 2 else 'corroborated' if r['corroborated'] else 'unverified'
    r['crosscheck_status'] = status
    r['manual_review_required'] = any(c.get('hard_conflict') is True for c in checks)
    if status != 'corroborated':
        r.update(display_allowed=False, internal_only=True)
        if status != 'unverified' or r['source'] != 'llm':
            r.update(usage='disabled', display=None)
        if r['manual_review_required']:
            r['date'] = None
    return r
