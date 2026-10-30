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
    print(json.dumps(finalize_public(args.public), ensure_ascii=False))
    if args.previous:
        previous = json.loads(args.previous.read_text())
        current = json.loads((args.public / "goods.json").read_text())
        from goodsdex.car_structure import mappings
        retained = {r['id'] for r in current} | {m['old_id'] for m in mappings(current)}
        missing = {r['id'] for r in previous} - retained
        if missing:
            raise ValueError(f"Final release lost previous IDs: {sorted(missing)}")
    build_shards(args.public)
