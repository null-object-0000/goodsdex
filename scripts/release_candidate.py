"""Pack collector changes; rebase field deltas onto latest data under publication lock.

Generated metadata/shards never enter the candidate. Conflicting edits fail closed;
JSONL observations are append-only and deduplicated by observation hour.
"""
from __future__ import annotations
import argparse
import base64
import json
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from goodsdex.release_policy import assert_no_lost_ids

MISSING = object()
SCOPES = ('prices', 'apple', 'hp', 'atour', 'cars', 'legacy', 'all')
RUN_REPORTS = {'data/hp/audit.json': 'fetched_at',
               'data/hp/collection-status.json': 'checked_at'}


def git(root, *args):
    # core.quotePath would escape non-ASCII paths ("\347\263\273..."), which then
    # fail the prefix allowlist below. Keep real UTF-8 names.
    return subprocess.check_output(['git', '-C', str(root), '-c', 'core.quotePath=false', *args])


def allowed_path(name):
    p = PurePosixPath(name)
    # 采集过程的节流/请求日志是诊断产物，不参与发布，也不该走候选增量比对。
    if name.startswith('docs/release-coverage/') and name.endswith('.jsonl'):
        return False
    return not p.is_absolute() and '..' not in p.parts and (
        name == 'public/goods.json' or
        any(name.startswith(prefix) for prefix in ('public/prices/', 'public/archive/',
            'docs/release-coverage/', 'data/categories/', 'data/archive/', 'data/hp/', 'data/prices/', 'data/price-observations/')))


TIMESTAMP_FIELDS = ('updated_at', 'fetched_at', 'last_seen_at', 'first_seen_at',
                    'checked_at', 'observed_at', 'collected_at', 'crawled_at')


def _is_timestamp_key(key):
    return key in TIMESTAMP_FIELDS or key.endswith('_at')


# 采集观测账本：不是商品资料，是「我们看过它几次」。两条采集线各记各的必然不同，
# 取较大值即可，不该让整轮采集因为计数器不同而报废。
COUNTER_FIELDS = ('times_seen', 'seen_count', 'hit_count', 'miss_count')


def _is_counter_key(key):
    return key in COUNTER_FIELDS or key.endswith('_count')


def _largest(*values):
    numbers = [v for v in values if v is not MISSING and isinstance(v, (int, float)) and not isinstance(v, bool)]
    if not numbers:
        return MISSING
    return max(numbers)


def merge_value(before, after, latest, label):
    if before == after or latest == after:
        return latest
    if latest == before:
        return after
    if all(isinstance(v, dict) for v in (before, after, latest)):
        out = dict(latest)
        for key in dict.fromkeys([*before, *after]):
            value = merge_value(before.get(key, MISSING), after.get(key, MISSING),
                                latest.get(key, MISSING), f'{label}.{key}')
            if value is MISSING:
                out.pop(key, None)
            else:
                out[key] = value
        return out
    # 时间戳不是数据：别人刚写过 updated_at / last_seen_at 不该逼整个采集重跑一轮。
    # 采集线的「最后一次看到」字段不止这两个名字，凡是 *_at 一律按时间戳处理。
    leaf = label.rsplit('.', 1)[-1]
    if _is_timestamp_key(leaf):
        print(f'watch: bookkeeping timestamp moved at {label}', file=sys.stderr)
        return latest if latest is not MISSING else after
    if _is_counter_key(leaf):
        merged = _largest(before, after, latest)
        if merged is not MISSING:
            print(f'watch: observation counter moved at {label}: {merged}', file=sys.stderr)
            return merged
    raise ValueError(f'Concurrent change at {label}; re-run this collector against latest data')


def observation_time(value):
    """Compare source observations, never publication time or lexical ISO strings."""
    try:
        stamp = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return stamp if stamp.utcoffset() is not None else None
    except (AttributeError, TypeError, ValueError):
        return None


def merge_run_report(before, after, latest, label):
    """A run's audit and its arrays/counters are one observation, not product deltas."""
    if before == after or after == latest:
        return latest
    if latest == before:
        return after
    field = RUN_REPORTS[label]
    if isinstance(after, dict) and isinstance(latest, dict):
        at, ct = (observation_time(row.get(field)) for row in (after, latest))
        if at is not None and ct is not None and at != ct:
            return after if at > ct else latest
    raise ValueError(f'Concurrent change at {label}; no unambiguous report order')


def merge_evidence(before, after, latest, key, label):
    def index(rows):
        out = {}
        for row in rows:
            identity = row.get(key) if isinstance(row, dict) else None
            if not isinstance(identity, str) or not identity or identity in out:
                raise ValueError(f'Ambiguous evidence identity at {label}')
            out[identity] = row
        return out
    b, a, c = (index(rows) for rows in (before, after, latest))
    result = dict(c)
    for identity, row in a.items():
        if identity in c and c[identity] != row:
            raise ValueError(f'Conflicting immutable evidence at {label}.{identity}')
        result[identity] = row
    # Keep the evidence that either concurrent observation still references.
    for identity, row in b.items():
        result.setdefault(identity, row)
    return list(result.values())


def merge_record(before, after, latest, label):
    """Merge views with their selected assertion, retaining both evidence bundles."""
    if before == after or after == latest:
        return latest
    if latest == before:
        return after
    if not all(isinstance(row, dict) for row in (before, after, latest)):
        return merge_value(before, after, latest, label)
    records = (before, after, latest)
    special = {'view', 'captures', 'assertions', 'fetched_at'}
    # Price metadata must follow the selected price observation as one unit.
    price_fields = {'price_fetched_at', 'price_status', 'price_kind', 'currency'}
    plain = [{k: v for k, v in row.items() if k not in special} for row in records]
    for row in plain:
        row['product'] = {k: v for k, v in row.get('product', {}).items()
                          if k not in price_fields}
    result = merge_value(*plain, label)
    for field, key in (('captures', 'capture_id'), ('assertions', 'assertion_id')):
        result[field] = merge_evidence(*(row.get(field, []) for row in records),
                                       key, f'{label}.{field}')

    def selection(record, field):
        view = record.get('view', {})
        return (view.get('values', {}).get(field, MISSING),
                view.get('selected_from', {}).get(field, MISSING))

    def selected_time(record, field):
        _, aid = selection(record, field)
        assertion = next((a for a in record.get('assertions', [])
                          if a.get('assertion_id') == aid), {})
        capture = next((c for c in record.get('captures', [])
                        if c.get('capture_id') == assertion.get('capture_id')), {})
        if capture.get('status') != 'success':
            return None
        return observation_time(capture.get('fetched_at'))

    views = [row.get('view', {}) for row in records]
    view = merge_value(*({k: v for k, v in v.items()
                         if k not in ('values', 'selected_from')} for v in views),
                       f'{label}.view')
    view.update(values={}, selected_from={})
    fields = dict.fromkeys(k for v in views for k in v.get('values', {}))
    for field in fields:
        b, a, c = (selection(row, field) for row in records)
        if a == b or a == c:
            chosen = latest
        elif c == b:
            chosen = after
        else:
            at, ct = selected_time(after, field), selected_time(latest, field)
            if at is None or ct is None or (at == ct and a[0] != c[0]):
                raise ValueError(f'Concurrent change at {label}.view.{field}; '
                                 'no unambiguous observation order')
            chosen = after if at > ct else latest
        value, aid = selection(chosen, field)
        if value is not MISSING:
            view['values'][field] = value
        if aid is not MISSING:
            view['selected_from'][field] = aid
        if field == 'price':
            for key in price_fields:
                if key in chosen.get('product', {}):
                    result['product'][key] = chosen['product'][key]
    if 'price' not in fields:
        for key in price_fields:
            value = merge_value(*(r.get('product', {}).get(key, MISSING)
                                  for r in records), f'{label}.product.{key}')
            if value is not MISSING:
                result['product'][key] = value
    result['view'] = view
    stamps = [(observation_time(row.get('fetched_at')), row.get('fetched_at'))
              for row in (after, latest)]
    if all(t is not None for t, _ in stamps):
        result['fetched_at'] = max(stamps, key=lambda pair: pair[0])[1]
    else:
        result['fetched_at'] = merge_value(*(r.get('fetched_at', MISSING)
                                            for r in records), f'{label}.fetched_at')
        if result['fetched_at'] is MISSING:
            result.pop('fetched_at')
    return result


def merge_category(before, after, latest, label):
    """A category is a set of independently observed variants, not an atomic list."""
    if before == after or after == latest:
        return latest
    if latest == before:
        return after
    if not all(isinstance(rows, list) for rows in (before, after, latest)):
        return merge_value(before, after, latest, label)
    from goodsdex.publish import record_id
    def index(rows):
        out = {}
        for row in rows:
            identity = record_id(row)
            if not identity or identity in out:
                raise ValueError(f'Ambiguous category identity at {label}')
            out[identity] = row
        return out
    b, a, c = (index(rows) for rows in (before, after, latest))
    out = dict(c)
    for identity in dict.fromkeys([*b, *a]):
        old, new, current = (rows.get(identity, MISSING) for rows in (b, a, c))
        value = merge_record(old, new, current, f'{label}[{identity}]')
        if value is MISSING:
            out.pop(identity, None)
        else:
            out[identity] = value
    return list(out.values())


def groups(rows):
    result = defaultdict(list)
    for row in rows:
        result[row['id']].append(row)
    return result


def owns(row, scope):
    from goodsdex.cars import is_car
    source = row.get('source', '')
    key = row['id']
    if scope == 'all':
        return True
    if scope == 'cars':
        return is_car(row)
    if scope == 'apple':
        return source in ('apple_cn', 'apple_support') or key.startswith(('CN:apple_cn:', 'GLOBAL:apple_support:'))
    if scope == 'atour':
        return source == 'atour' and key.startswith('CN:atour:spu:')
    if scope == 'hp':
        return source == 'hp_cn'
    if scope == 'legacy':
        return key.startswith('CN:mi_cn:') and not is_car(row)
    return not is_car(row) and source not in ('apple_cn', 'apple_support', 'hp_cn', 'atour') and row.get('brand') != 'Apple' and not key.startswith(('CN:apple_cn:', 'GLOBAL:apple_support:'))


def merge_goods(before, after, latest, scope):
    assert_no_lost_ids(before, after)
    b, a, c = groups(before), groups(after), groups(latest)
    out = dict(c)
    for key in dict.fromkeys([*b, *a]):
        old, new = b.get(key, MISSING), a.get(key, MISSING)
        if old == new:
            continue
        for row in (b.get(key, []) + a.get(key, [])):
            if not owns(row, scope):
                raise ValueError(f'{scope} candidate modifies another responsibility: {key}')
        current = c.get(key, MISSING)
        # Field-level merge for unique rows; ambiguous versions stay atomic.
        if all(isinstance(v, list) and len(v) == 1 for v in (old, new, current)):
            value = [merge_value(old[0], new[0], current[0], key)]
        else:
            value = merge_value(old, new, current, key)
        if value is MISSING:
            out.pop(key, None)
        else:
            out[key] = value
    remaining = {key: list(rows) for key, rows in out.items()}
    result = []
    for row in latest:
        if remaining.get(row["id"]):
            result.append(remaining[row["id"]].pop(0))
    for rows in remaining.values():
        result.extend(rows)
    assert_no_lost_ids(latest, result)
    return result


def pack(root, scope, target):
    # Stage only candidate inputs. Never include stale finalize output.
    tracked = git(root, 'ls-files').decode().splitlines()
    names = set(n for n in tracked if allowed_path(n))
    for prefix in ('docs/release-coverage', 'data/categories', 'data/archive', 'data/hp', 'data/prices', 'data/price-observations', 'public/prices', 'public/archive'):
        if (root / prefix).exists():
            # 同一套 allowed_path 判定：不允许发布的文件连暂存都不进，
            # 否则会被后面的校验拦成 "Unexpected staged candidate path"。
            names.update(rel for p in (root / prefix).rglob('*') if p.is_file()
                         and allowed_path(rel := p.relative_to(root).as_posix()))
    for name in sorted(names):
        git(root, 'add', '-f', '--', name)
    changed = git(root, 'diff', '--cached', '--name-only').decode().splitlines()
    files = {}
    for name in changed:
        if not allowed_path(name):
            raise ValueError(f'Unexpected staged candidate path: {name}')
        try:
            before = git(root, 'show', f'HEAD:{name}')
        except subprocess.CalledProcessError:
            before = None
        after = (root / name).read_bytes() if (root / name).exists() else None
        files[name] = {k: base64.b64encode(v).decode() if v is not None else None
                       for k, v in (('before', before), ('after', after))}
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(dict(schema=1, scope=scope, base=git(root, 'rev-parse', 'HEAD').decode().strip(), files=files)))
    print(f'{scope}: packed {len(files)} changed inputs')


def merge_candidate(root, candidate):
    bundle = json.loads(candidate.read_text())
    if bundle['schema'] != 1 or bundle['scope'] not in SCOPES:
        raise ValueError('Unsupported candidate')
    writes = {}
    for name, delta in bundle['files'].items():
        if not allowed_path(name):
            raise ValueError(f'Forbidden candidate path: {name}')
        path = root / name
        before, after = (base64.b64decode(delta[k]) if delta[k] is not None else None for k in ('before', 'after'))
        latest = path.read_bytes() if path.exists() else None
        if name == 'public/goods.json':
            result = merge_goods(json.loads(before), json.loads(after), json.loads(latest), bundle['scope'])
            value = (json.dumps(result, ensure_ascii=False, indent=1) + '\n').encode()
        elif name.endswith('.jsonl'):
            old_lines = (before or b'').splitlines()
            new_lines = (after or b'').splitlines()
            if new_lines[:len(old_lines)] != old_lines:
                raise ValueError(f'Candidate rewrites price history: {name}')
            lines = (latest or b'').splitlines()
            def observation_key(line):
                event = json.loads(line)
                if 'gid' in event and 'at' in event:
                    from goodsdex.price_history import key
                    return key(event)
                stamp = str(event.get('fetched_at'))
                return (event['id'], stamp) if 'id' in event else stamp[:13]
            hours = {observation_key(line) for line in lines}
            observations = {observation_key(line): json.loads(line) for line in lines}
            for line in new_lines[len(old_lines):]:
                hour = observation_key(line)
                if name.startswith('data/price-observations/') and hour in observations:
                    from goodsdex.price_history import signature
                    if signature(observations[hour]) != signature(json.loads(line)):
                        raise ValueError(f'Conflicting candidate observation: {hour}')
                if hour not in hours:
                    lines.append(line)
                    hours.add(hour)
                    observations[hour] = json.loads(line)
            value = b'\n'.join(lines) + (b'\n' if lines else b'')
        elif name.endswith('.json'):
            def decode(raw):
                return json.loads(raw) if raw is not None else MISSING
            from goodsdex.publish import is_category_snapshot_file
            merge = (merge_run_report if name in RUN_REPORTS else
                     merge_category if name.startswith('data/categories/')
                     and is_category_snapshot_file(name) else merge_value)
            result = merge(decode(before), decode(after), decode(latest), name)
            value = None if result is MISSING else (json.dumps(result, ensure_ascii=False, indent=1) + '\n').encode()
        else:
            value = merge_value(before, after, latest, name)
        writes[path] = value
    # Validate the entire delta before the first write.
    for path, value in writes.items():
        if value is None:
            path.unlink(missing_ok=True)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(value)
    print(f"Merged {bundle['scope']} candidate from {bundle['base']}: {len(writes)} files")


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('mode', choices=('pack', 'merge'))
    ap.add_argument('--root', type=Path, required=True)
    ap.add_argument('--candidate', type=Path, required=True)
    ap.add_argument('--scope', choices=SCOPES)
    args = ap.parse_args()
    if args.mode == 'pack':
        if not args.scope:
            ap.error('pack requires --scope')
        pack(args.root, args.scope, args.candidate)
    else:
        merge_candidate(args.root, args.candidate)
