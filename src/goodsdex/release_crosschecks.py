"""Deterministic release conflict policy; provenance never changes on agreement."""
from copy import deepcopy
from datetime import date


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


def reconcile(release, observations=(), previous_checks=()):
    """Retain original assertion and every comparison, including official conflicts.

    Observations are assertions, not replacements. LLM/LLM pairwise conflicts
    also invalidate nonofficial dates. Missing independent results fail closed.
    """
    r = deepcopy(release)
    original = dict(source=r['source'], date=r['date'])
    checks = []
    def add(item):
        if item not in checks:
            checks.append(item)
    for check in previous_checks:
        add(deepcopy(check))
    add(dict(**original, delta_days=0, verdict='original'))
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
        known.append(dict(source=obs['source'], date=obs['date']))
    r['checks'] = checks
    # Historical checks survive rebuilds, so a later agreement cannot silently
    # erase an earlier conflict. A manual review must explicitly resolve it.
    worst = max(({'corroborated': 0, 'unverified': 1, 'disagreement': 2, 'conflict': 3}.get(c['verdict'], -1)
                 for c in checks), default=-1)
    official = r['source'] in ('official', 'official_hidden')
    has_independent = any(c['source'] == 'llm' and c.get('independent') is True
                          and c.get('date') and c['verdict'] == 'corroborated' for c in checks)
    r['corroborated'] = has_independent and worst == 0
    if official:
        r['crosscheck_status'] = 'official_preserved' if worst > 0 else 'official'
        return r
    status = 'conflict' if worst == 3 else 'disagreement' if worst == 2 else 'corroborated' if r['corroborated'] else 'unverified'
    r['crosscheck_status'] = status
    if status != 'corroborated':
        r.update(display_allowed=False, internal_only=True)
        if status != 'unverified' or r['source'] != 'llm':
            # Existing clients suppress year/month fallbacks for disabled usage.
            # Dates retained here remain available only for internal review.
            r.update(usage='disabled', display=None)
        if status == 'conflict':
            r['date'] = None
            r['manual_review_required'] = True
    return r
