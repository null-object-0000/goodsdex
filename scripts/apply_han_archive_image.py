"""Apply the reviewed image-only Han 2022 amendment; preserve every other record."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from goodsdex.car_images import IMAGE_FIELDS, validate_historical_image
from goodsdex.car_structure import migrate

TARGET = 'CN:byd:car:han:2022:dmi'
AMENDED = {'image', 'image_scope', *IMAGE_FIELDS}


def apply(rows):
    reviewed = json.loads((ROOT / 'data/car-history-20261029/byd-verified.json').read_text())
    approved = {r['id']: r for r in reviewed}
    assert len(approved) == 5
    result = deepcopy(rows)
    targets = [r for r in result if r['id'] == TARGET]
    if len(targets) != 1:
        raise ValueError('Expected exactly one canonical Han 2022 product')
    parent = targets[0]
    if {t['id'] for t in parent['trims']} != approved.keys():
        raise ValueError('Unexpected Han 2022 trim IDs')
    sources = []
    for trim in parent['trims']:
        old = trim['source_record']
        new = deepcopy(approved[trim['id']])
        # The release finalizer adds this lossless category projection.
        if old.get('categories') == [new.get('category')] and 'categories' not in new:
            new['categories'] = old['categories']
        if {k:v for k,v in old.items() if k not in AMENDED} != {k:v for k,v in new.items() if k not in AMENDED}:
            raise ValueError('Image amendment would change configuration evidence')
        validate_historical_image(new)
        sources.append(new)
    amended = migrate(sources)[0]
    result = [amended if r['id'] == TARGET else r for r in result]
    if [r for r in rows if r['id'] != TARGET] != [r for r in result if r['id'] != TARGET]:
        raise ValueError('Non-target records changed')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--public', type=Path, required=True)
    args = parser.parse_args()
    target = args.public / 'goods.json'
    old = json.loads(target.read_text())
    new = apply(old)
    temp = target.with_suffix('.tmp')
    temp.write_text(json.dumps(new, ensure_ascii=False, indent=1) + '\n')
    temp.replace(target)
    print(json.dumps(dict(target=TARGET, changed=sum(a != b for a,b in zip(old,new)), records=len(new))))
