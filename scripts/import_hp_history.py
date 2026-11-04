#!/usr/bin/env python3
"""Import reviewed official history through the existing HP candidate publisher."""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from goodsdex.hp_history import apply_history, enrich_store_fields
from goodsdex.retirement import reconcile


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=1) + '\n')
    temporary.replace(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--public', type=Path, required=True)
    args = ap.parse_args()
    path = args.out / 'goods.json'
    previous = json.loads(path.read_text()) if path.exists() else []
    archive = apply_history(previous)
    archive = [r for r in archive if r.get('record_level') != 'model_family']
    archive = [enrich_store_fields(r) for r in reconcile(previous, archive)]
    public_path = args.public / 'goods.json'
    old = json.loads(public_path.read_text())
    result = apply_history(old)
    result = [enrich_store_fields(r) if r.get('source') == 'hp_cn' else r for r in reconcile(old, result)]
    assert {r['id'] for r in old}.issubset({r['id'] for r in result})
    assert [r for r in old if r.get('source') != 'hp_cn'] == [r for r in result if r.get('source') != 'hp_cn']
    write(path, archive)
    write(public_path, result)
    status = dict(conclusion='success', checked_at=datetime.now(timezone.utc).isoformat(),
                  count=sum(r.get('source') == 'hp_cn' for r in result),
                  mode='reviewed_official_history_import', live_store_refresh=False)
    write(args.out / 'collection-status.json', status)
    print(json.dumps(status, ensure_ascii=False))


if __name__ == '__main__':
    main()
