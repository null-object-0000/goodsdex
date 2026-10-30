"""Final CI gate, after all brand publishers and before committing the release."""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from goodsdex.cars import assert_cars_unchanged
from goodsdex.supplements import DEFAULT_SUPPLEMENTS, merge, metadata
from goodsdex.release_policy import remove_reviewed_non_goods


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--public", type=Path, required=True)
    ap.add_argument("--previous", type=Path, required=True)
    ap.add_argument("--supplements", type=Path, default=DEFAULT_SUPPLEMENTS)
    args = ap.parse_args()
    goods_path = args.public / "goods.json"
    original = json.loads(goods_path.read_text())
    # Brand publishers can replay tombstones from old category caches. Apply the
    # same exact-ID policy as merge before comparing the final release.
    current = remove_reviewed_non_goods(original)
    previous = json.loads(args.previous.read_text())
    assert_cars_unchanged(previous, current)
    supplements = json.loads(args.supplements.read_text())
    checked, verification = merge(current, supplements, previous)
    if Counter(r["id"] for r in checked) != Counter(r["id"] for r in current):
        restored = Counter(r["id"] for r in checked) - Counter(r["id"] for r in current)
        raise ValueError(f"Release is missing supplemental/retained IDs: {dict(restored)}")
    audit = json.loads((args.public / "merge-audit.json").read_text())
    if audit["count"] != audit["rebuilt_count"] + audit["added_count"]:
        raise ValueError("count != rebuilt_count + added_count")
    if len(current) < audit["count"]:
        raise ValueError("Later publisher reduced the release count")
    meta_path = args.public / "meta.json"
    old_meta = json.loads(meta_path.read_text())
    # Only persist reviewed removals after every release invariant has passed.
    if current != original:
        goods_path.write_text(json.dumps(current, ensure_ascii=False, indent=1) + "\n")
    # Later brand publishers can replace meta; always calculate all four totals last.
    meta_path.write_text(json.dumps(metadata(current, old_meta), ensure_ascii=False, indent=1) + "\n")
    (args.public / "verification.json").write_text(json.dumps(verification, ensure_ascii=False, indent=1) + "\n")


if __name__ == "__main__":
    main()
