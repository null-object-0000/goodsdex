"""Validate an offline normalization candidate, including actual API query/detail code."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from goodsdex.dedupe import dedupe_rows, group_by_id
from goodsdex.public_fields import PROTECTED_IDS, assert_public_fields, normalize_public_row


def verify(before_dir, public, api_module, output):
    before = json.loads((before_dir / 'goods.json').read_bytes())
    after = json.loads((public / 'goods.json').read_bytes())
    expected, audit = dedupe_rows(before)
    if after != expected:
        raise ValueError('Candidate differs from fully validated normalization')
    assert_public_fields(after)
    old, new = group_by_id(before), group_by_id(after)
    for pid in PROTECTED_IDS:
        if pid not in old or new[pid] != old[pid]:
            raise ValueError(f'Protected group missing/modified: {pid}')
    # Include aliases, counters, missing specifications and container metadata.
    preferred = ['10050249', '12639', '18262', '19435', '21432',
                 '21587', '25488', '25712', '25720', '10000407']
    ids = [f'CN:mi_cn:product:{suffix}' for suffix in preferred]
    ids = [pid for pid in ids if pid in audit['merged_ids']]
    ids += [pid for pid in audit['merged_ids'] if pid not in ids][:10-len(ids)]
    if len(ids) != 10:
        raise ValueError('Need 10 merged IDs to verify release details')
    sample = []
    for pid in ids:
        union = {}
        for row in old[pid]:
            for key, value in normalize_public_row(row).get('params', {}).items():
                if key in union and union[key] != value:
                    raise ValueError(f'Original parameter conflict: {pid}/{key}')
                union[key] = value
        if new[pid][0].get('params', {}) != union:
            raise ValueError(f'Candidate lost original union: {pid}')
        sample.append(dict(id=pid, params=union, unionKeys=len(union),
                           originalKeys=max(len(normalize_public_row(r).get('params', {})) for r in old[pid])))
    with tempfile.TemporaryDirectory() as folder:
        oracle = Path(folder) / 'expected.json'
        oracle.write_text(json.dumps(sample, ensure_ascii=False))
        subprocess.run(['node', str(Path(__file__).with_suffix('.mjs')), str(api_module.resolve()),
                        str(before_dir.resolve()), str(public.resolve()), str(oracle), str(output.resolve())], check=True)
    evidence = json.loads(output.read_text())
    evidence['merge'] = audit
    evidence['before_sha256'] = hashlib.sha256((before_dir / 'goods.json').read_bytes()).hexdigest()
    evidence['after_sha256'] = hashlib.sha256((public / 'goods.json').read_bytes()).hexdigest()
    output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')
    return evidence


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--before', type=Path, required=True)
    ap.add_argument('--public', type=Path, required=True)
    ap.add_argument('--api-module', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    verify(a.before, a.public, a.api_module, a.output)
