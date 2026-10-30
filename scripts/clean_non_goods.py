"""Publish only the six reviewed non-product deletions; preserve all other rows exactly."""
import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from goodsdex.release_policy import remove_reviewed_non_goods, assert_no_lost_ids, allowed_deletions
from goodsdex.supplements import publish
from goodsdex.dedupe import finalize_public
from goodsdex.shards import build_shards


def clean(public):
    public = Path(public)
    previous = json.loads((public / 'goods.json').read_text())
    expected = remove_reviewed_non_goods(previous)
    with tempfile.TemporaryDirectory() as d:
        stage = Path(d)
        shutil.copyfile(public / 'meta.json', stage / 'meta.json')
        extra = stage / 'extra.json'
        extra.write_text('[]')
        publish(previous, stage, previous, extra)
        finalize_public(stage)
        actual = json.loads((stage / 'goods.json').read_text())
        if actual != expected:
            raise ValueError('Cleanup changed rows outside the six reviewed IDs')
        assert_no_lost_ids(previous, actual)
        meta = build_shards(stage)
        report = dict(before_rows=len(previous), after_rows=len(actual),
                      before_unique_ids=len({r['id'] for r in previous}),
                      after_unique_ids=len({r['id'] for r in actual}),
                      allowed_deletions=allowed_deletions(previous, actual),
                      retained_rows_equal=True)
        for name in [*meta['files'], 'merge-audit.json', 'meta.json']:
            target = public / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(stage / name, target.with_suffix('.tmp'))
            target.with_suffix('.tmp').replace(target)
    return report


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--public', type=Path, required=True)
    print(json.dumps(clean(p.parse_args().public), ensure_ascii=False, indent=2))
