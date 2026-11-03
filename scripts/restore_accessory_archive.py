"""Restore first-exclusion snapshots from a reviewed data commit via a locked candidate.

Used once to repair stale supplement overwrites discovered during replay testing.
Other data files are never modified. Displaced observations remain nested in the archive.
"""
import argparse
import json
import re
import subprocess
from pathlib import Path


def restore(current, first):
    byid = {r['id']: r for r in first}
    if len(byid) != len(first) or not byid.keys() <= {r['id'] for r in current}:
        raise ValueError('Restoration must preserve all current archive identities')
    if any(r.get('excluded_reason') != 'accessory' for r in [*first, *current]):
        raise ValueError('Only accessory archives can be restored')
    output = []
    for row in current:
        original = byid.get(row['id'], row)
        if original != row:
            original = {**original, 'subsequent_observations': [row]}
        output.append(original)
    return output


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, required=True)
    ap.add_argument('--commit', required=True)
    args = ap.parse_args()
    if not re.fullmatch(r'[0-9a-f]{40}', args.commit):
        ap.error('A full reviewed data commit SHA is required')
    name = 'public/archive/accessories.json'
    first = json.loads(subprocess.check_output(['git', '-C', str(args.root), 'show', f'{args.commit}:{name}']))
    target = args.root / name
    current = json.loads(target.read_text())
    restored = restore(current, first)
    target.write_text(json.dumps(restored, ensure_ascii=False, indent=1)+'\n')
    print(f'Restored first-exclusion snapshots from {args.commit}; archive identities={len(restored)}')


if __name__ == '__main__':
    main()
