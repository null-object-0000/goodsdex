from copy import deepcopy
import gzip
import json
from pathlib import Path

import pytest
from goodsdex.series_release import apply_series_releases

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / 'docs/series-release-rollout-20261103'


def test_full_reviewed_census_preserves_every_other_field():
    rows = json.loads(gzip.decompress((DOC / 'baseline-goods.json.gz').read_bytes()))
    before = deepcopy(rows)
    result = apply_series_releases(rows)
    assert rows == before
    assert [r.get('release') for r in result] == [r.get('release') for r in before]
    assert [{k: v for k, v in r.items() if k != 'series_release'} for r in result] == [
        {k: v for k, v in r.items() if k != 'series_release'} for r in before]
    assert apply_series_releases(result) == result
    by_id = {r['id']: r for r in result}
    for sample in json.loads((DOC / 'sample-30.json').read_text()):
        assert by_id[sample['id']].get('series_release', {}).get('date') == sample['correct_value']
    # Same name / capacity alone is insufficient; later white 6 Max has its own batch.
    assert by_id['CN:mi_cn:product:23615']['series_release']['date'] == '2026-03'
    assert by_id['CN:mi_cn:product:25466']['series_release']['date'] == '2026-09'
    assert 'series_release' not in by_id['CN:mi_cn:product:23676']


def test_unreviewed_scope_is_rejected(tmp_path):
    bundle = json.loads((ROOT / 'data/official/series-releases.json').read_text())
    bundle['scope'] = 'automatic_fuzzy_rollout'
    p = tmp_path / 'batches.json'
    p.write_text(json.dumps(bundle))
    with pytest.raises(ValueError, match='explicitly reviewed'):
        apply_series_releases([], p)
