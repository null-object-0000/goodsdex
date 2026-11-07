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
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from goodsdex.release_policy import assert_no_lost_ids

MISSING = object()
SCOPES = ('prices', 'apple', 'hp', 'atour', 'cars', 'legacy', 'all')


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
    raise ValueError(f'Concurrent change at {label}; re-run this collector against latest data')


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
            result = merge_value(decode(before), decode(after), decode(latest), name)
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
