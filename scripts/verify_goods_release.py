"""Final CI gate, after all brand publishers and before committing the release."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from goodsdex.cars import assert_cars_unchanged
from goodsdex.supplements import DEFAULT_SUPPLEMENTS, merge, metadata


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--public", type=Path, required=True)
    ap.add_argument("--previous", type=Path, required=True)
    ap.add_argument("--supplements", type=Path, default=DEFAULT_SUPPLEMENTS)
    args = ap.parse_args()
    current = json.loads((args.public / "goods.json").read_text())
    previous = json.loads(args.previous.read_text())
    assert_cars_unchanged(previous, current)
    supplements = json.loads(args.supplements.read_text())
    checked, verification = merge(current, supplements, previous)
    if len(checked) != len(current):
        raise ValueError("Release is missing supplemental IDs")
    audit = json.loads((args.public / "merge-audit.json").read_text())
    if audit["count"] != audit["rebuilt_count"] + audit["added_count"]:
        raise ValueError("count != rebuilt_count + added_count")
    if len(current) < audit["count"]:
        raise ValueError("Later publisher reduced the release count")
    meta_path = args.public / "meta.json"
    old_meta = json.loads(meta_path.read_text())
    # Later brand publishers can replace meta; always calculate all four totals last.
    meta_path.write_text(json.dumps(metadata(current, old_meta), ensure_ascii=False, indent=1) + "\n")
    (args.public / "verification.json").write_text(json.dumps(verification, ensure_ascii=False, indent=1) + "\n")


if __name__ == "__main__":
    main()
