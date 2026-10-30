"""Replay supplement channel over a data-branch release, with no source requests."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from goodsdex.supplements import publish
from goodsdex.dedupe import finalize_public
from goodsdex.car_structure import migrate
from goodsdex.shards import build_shards
p=argparse.ArgumentParser();p.add_argument('--public',type=Path,required=True);a=p.parse_args()
previous=json.loads((a.public/'goods.json').read_text())
publish(previous,a.public,previous,include_new_cars=True)
rows=json.loads((a.public/'goods.json').read_text())
assert migrate(rows)==rows
finalize_public(a.public)
rows=json.loads((a.public/'goods.json').read_text())
from goodsdex.release_policy import assert_no_lost_ids
assert_no_lost_ids(previous, rows)
build_shards(a.public)
