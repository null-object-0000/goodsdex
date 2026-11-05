"""Strict day/month coverage of published rows, including retained history.

Page existence and model-only estimates are never release evidence. Missing
means not obtained unless an explicit, captured official absence statement exists.
"""
from copy import deepcopy
from datetime import date
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
LANE_FILES = ['hp-release-evidence.json', 'atour-release-evidence.json', 'xiaomi-priority-release-evidence.json', 'priority-series-release-evidence.json']
GROUPS = {
    '笔记本 / 台式机': {'笔记本', '台式机', '电脑', '工作站', '旧款机型'},
    '显示器': {'显示器', '办公娱乐显示器', '游戏电竞显示器'},
    '电脑外设': {'键鼠套装'},
    '宠物用品': {'宠物饮水机'},
    '床品': {'床品', '枕芯', '枕头', '床垫', '被芯', '组合装', '抱枕', '盖毯'},
    '汽车': {'汽车'},
}

def priority_group(row):
    c = row.get('category')
    # Apple historical phones/tablets are also called 旧款机型: require computer identity.
    if c == '旧款机型' and not re.search(r'Mac|笔记本|游戏本|[Bb]ook|台式|电脑', row.get('name', ''), re.I):
        return None
    if '宠物' in row.get('name', '') and not re.search(r'滤芯|抑味棒|配件', row.get('name', '')):
        return '宠物用品'
    return next((g for g, cats in GROUPS.items() if c in cats), None)


def precision(r):
    value = r.get('date') or ''
    if r.get('granularity') == 'day' and re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        try:
            date.fromisoformat(value)
            return 'day'
        except ValueError:
            pass
    if r.get('granularity') == 'month' and re.fullmatch(r'\d{4}-\d{2}', value):
        try:
            date.fromisoformat(value + '-01')
            return 'month'
        except ValueError:
            pass
    return None


def usable(r):
    if not precision(r) or r.get('usage') in ('disabled', 'internal') or r.get('display_allowed') is False or r.get('internal_only'):
        return False
    if r.get('source') not in ('official', 'official_hidden', 'third_party', 'series_inherit'):
        return False
    if r.get('source') == 'third_party' and r.get('crosscheck_status') != 'corroborated':
        return False
    if r.get('source') == 'series_inherit' and (r.get('granularity') != 'month' or r.get('level') != 'series'):
        return False
    e = r.get('evidence') or {}
    return bool(e.get('url') and e.get('quote') and e.get('sha256') and e.get('captured_at'))


def effective(row):
    r = row.get('release') or {}
    if usable(r):
        return r
    r = row.get('release_inherited') or {}
    if usable(r) and r.get('source') == 'series_inherit' and r.get('level') == 'series':
        return r
    r = row.get('release_series') or {}
    if usable(r) and r.get('level') == 'series':
        return dict(r, date=r['date'][:7], granularity='month', release_source='series_inherit')
    return None


def apply_priority_dates(rows, lane_files=None):
    output = deepcopy(rows)
    by_id = {r['id']: r for r in output}
    for path in lane_files or [ROOT / 'data/official' / n for n in LANE_FILES]:
        path = Path(path)
        if not path.exists():
            continue
        bundle = json.loads(path.read_text())
        for candidate in bundle.get('candidates', []):
            from goodsdex.release_dates import validate
            r = validate(candidate)
            for key in candidate['ids']:
                row = by_id.get(key)
                if row and priority_group(row) and not (row.get('release') or {}).get('date'):
                    row['release'] = dict(deepcopy(r), usage='fact', display_allowed=True)
        for candidate in bundle.get('inherited_candidates', []):
            r = candidate['release']
            if r.get('source') != 'series_inherit' or r.get('release_source') != 'series_inherit' or r.get('granularity') != 'month' or not usable(r) or r.get('level') != 'series':
                raise ValueError('Series inheritance requires captured month evidence')
            for key in candidate['ids']:
                row = by_id.get(key)
                if row and priority_group(row) and not effective(row):
                    row['release_inherited'] = deepcopy(r)
                    row['release_source'] = 'series_inherit'
        for obs in bundle.get('observations', []):
            row = by_id.get(obs.get('id'))
            if row and not effective(row):
                row['release_missing'] = dict(reason='not_obtained', lane=bundle.get('lane'),
                    detail=obs.get('reason') or obs.get('status') or 'not_collected',
                    url=obs.get('url'), checked_at=obs.get('captured_at') or bundle.get('captured_at'))
    for row in output:
        if not priority_group(row) or usable(row.get('release') or {}):
            continue
        r = row.get('release_series') or {}
        if usable(r) and r.get('level') == 'series' and not row.get('release_inherited'):
            row['release_inherited'] = dict(deepcopy(r), date=r['date'][:7], granularity='month',
                source='series_inherit', release_source='series_inherit', usage='reference',
                label='系列推出月份（继承）', inherited_from=r.get('batch_id'))
            row['release_source'] = 'series_inherit'
    return output


def missing_reason(row):
    m = row.get('release_missing') or {}
    e = m.get('evidence') or {}
    # An empty field or a failed request is never evidence of official absence.
    return 'official_absent' if m.get('reason') == 'official_absent' and e.get('url') and e.get('quote') and e.get('sha256') and e.get('captured_at') and e.get('explicit_absence') is True else 'not_obtained'


def matrix(rows):
    def empty():
        return dict(total=0, day=0, month=0, none=0, not_obtained=0, official_absent=0, series_inherit=0)
    brands, groups, total = {}, {}, empty()
    for row in rows:
        b = row.get('brand') or '未知'
        g = priority_group(row)
        targets = [total, brands.setdefault(b, empty())]
        if g:
            targets.append(groups.setdefault(g, empty()))
        r = effective(row)
        p = precision(r) if r else 'none'
        for t in targets:
            t['total'] += 1
            t[p] += 1
            if p == 'none':
                t[missing_reason(row)] += 1
            if r and (r.get('release_source') == 'series_inherit' or r.get('source') == 'series_inherit'):
                t['series_inherit'] += 1
    for t in [total, *brands.values(), *groups.values()]:
        t['covered'] = t['day'] + t['month']
        t['ratio'] = t['covered'] / t['total'] if t['total'] else None
    return dict(policy='day-preferred-month-minimum-v1', counting_unit='published_rows', total=total, brands=brands, priority=groups)
