"""Mandatory final merge + invariant gate, after all publishers and before push."""
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
    args = ap.parse_args()
    print(json.dumps(finalize_public(args.public), ensure_ascii=False))
    build_shards(args.public)
