"""Mandatory public-field normalization, final merge + invariant gate, after all publishers and before push."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from goodsdex.dedupe import finalize_public
from goodsdex.shards import build_shards
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--public", type=Path, required=True)
    ap.add_argument("--previous", type=Path)
    args = ap.parse_args()
    from migrate_car_structure import migrate_public
    migrate_public(args.public)
    previous = json.loads(args.previous.read_text()) if args.previous else None
    from goodsdex.car_structure import mappings, assert_unique_car_ids
    current = json.loads((args.public / "goods.json").read_text())
    assert_unique_car_ids(current)
    retained = {m['old_id'] for m in mappings(current)}
    print(json.dumps(finalize_public(args.public, previous, retained), ensure_ascii=False))
    build_shards(args.public)
