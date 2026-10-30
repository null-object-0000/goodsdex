"""Offline, reviewed migration; finalize_public.py performs the same grouping daily."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from goodsdex.car_structure import migrate, mappings, assert_preserved
from goodsdex.supplements import metadata


def migrate_public(public):
    public = Path(public)
    before = json.loads((public / 'goods.json').read_text())
    after = migrate(before)
    assert_preserved(before, after)
    for filename, value in [('goods.json', after), ('meta.json', metadata(after, json.loads((public / 'meta.json').read_text()))),
                            ('car-migration.json', mappings(after))]:
        target = public / filename
        temp = target.with_suffix('.tmp')
        temp.write_text(json.dumps(value, ensure_ascii=False, indent=1) + '\n')
        temp.replace(target)
    return after

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--public', type=Path, required=True)
    args = ap.parse_args()
    migrate_public(args.public)
