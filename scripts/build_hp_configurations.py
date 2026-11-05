#!/usr/bin/env python3
"""Build exact HP configuration supplements from captured public parts responses."""
import argparse
import gzip
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from goodsdex.hp_configurations import parse_parts


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--captures', type=Path, required=True)
    ap.add_argument('--history', type=Path, default=ROOT / 'data/official/hp-history.json')
    ap.add_argument('--out', type=Path, default=ROOT / 'data/official/hp-configurations.json')
    args = ap.parse_args()
    captures = (json.loads(gzip.decompress(args.captures.read_bytes())) if args.captures.is_file()
                else [json.loads(p.read_text()) for p in sorted(args.captures.glob('*.json'))])
    rows = {r['part_number']: r for r in json.loads(args.history.read_text())['rows'] if r.get('part_number')}
    supplements, missing = [], []
    for capture in captures:
        sku = capture['part_number']
        try:
            supplement = parse_parts(capture, rows[sku])
        except (ValueError, KeyError) as exc:
            missing.append(dict(part_number=sku, reason=str(exc)))
        else:
            supplements.append(supplement)
    args.out.write_text(json.dumps(dict(schema=1, rows=supplements, missing=missing), ensure_ascii=False, indent=1) + '\n')
    print(json.dumps(dict(count=len(supplements), missing=missing)))


if __name__ == '__main__':
    main()
