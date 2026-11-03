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
    assert [{k: v for k, v in r.items() if k not in ('series_release', 'release_series')} for r in result] == [
        {k: v for k, v in r.items() if k not in ('series_release', 'release_series')} for r in before]
    assert apply_series_releases(result) == result
    by_id = {r['id']: r for r in result}
    for sample in json.loads((DOC / 'sample-30.json').read_text()):
        assert by_id[sample['id']].get('release_series', {}).get('date') == sample['correct_value']
    # Same name / capacity alone is insufficient; later white 6 Max has its own batch.
    assert by_id['CN:mi_cn:product:23615']['release_series']['date'] == '2026-03'
    assert by_id['CN:mi_cn:product:25466']['release_series']['date'] == '2026-09'
    assert 'release_series' not in by_id['CN:mi_cn:product:23676']


def test_unreviewed_scope_is_rejected(tmp_path):
    bundle = json.loads((ROOT / 'data/official/series-releases.json').read_text())
    bundle['scope'] = 'automatic_fuzzy_rollout'
    p = tmp_path / 'batches.json'
    p.write_text(json.dumps(bundle))
    with pytest.raises(ValueError, match='explicitly reviewed'):
        apply_series_releases([], p)


def test_real_finalizer_publishes_exact_reviewed_memberships_and_replays(tmp_path):
    import subprocess
    import sys
    from goodsdex.shards import shard_for

    before = json.loads(gzip.decompress((DOC / 'baseline-goods.json.gz').read_bytes()))
    (tmp_path / 'goods.json').write_text(json.dumps(before))
    (tmp_path / 'meta.json').write_text('{}')
    (tmp_path / 'prices.json').write_text('{}')
    manifest = json.loads((DOC / 'batches.json').read_text())
    expected = {key: b for b in manifest for key in b['ids']}
    assert len(expected) == sum(b['members'] for b in manifest) == 149
    # Retain the historical manifest checks and independently add the reviewed
    # expansion manifest. Only memberships present in this old snapshot apply.
    present = {r['id'] for r in before}
    expansion = json.loads((ROOT / 'docs/xiaomi-series-expansion-20261104/reviewed-new-batches.json').read_text())
    for b in expansion:
        r = b['series_release']
        for m in b['members']:
            if m['id'] in present:
                assert m['id'] not in expected
                expected[m['id']] = dict(date=r['date'],batch_id=b['id'],url=r['evidence']['url'],granularity=r['granularity'])
    command = [sys.executable, str(ROOT / 'scripts/finalize_public.py'), '--public', str(tmp_path)]
    subprocess.run(command, check=True)
    result = json.loads((tmp_path / 'goods.json').read_text())
    by_id = {r['id']: r for r in result}
    assert sum(bool(r.get('release')) for r in result) == sum(bool(r.get('release')) for r in before) == 671
    excluded=json.loads((tmp_path / 'archive/accessories.json').read_text())
    assert len(excluded)==11 and all(not r.get('release') for r in excluded)
    excluded_ids={r['id'] for r in excluded}
    assert {r['id']: r.get('release') for r in result} == {r['id']: r.get('release') for r in before if r['id'] not in excluded_ids}
    assert {r['id'] for r in result if r.get('release_series')} == expected.keys()
    assert all('series_release' not in r for r in result)
    for key, batch in expected.items():
        row = by_id[key]
        series = row['release_series']
        assert (series['date'], series['batch_id'], series['evidence']['url']) == (batch['date'], batch['batch_id'], batch['url'])
        assert series['granularity'] == batch.get('granularity','month') and series['level'] == 'series'
        assert series['inherited'] is (not bool((row.get('release') or {}).get('date')))
        assert series['evidence']['quote'] and len(series['evidence']['sha256']) == 64
        detail = json.loads((tmp_path / f'detail/{shard_for(key):02x}.json').read_text())
        assert detail[key]['release_series'] == series
    for filename in (tmp_path / 'index').glob('*.json'):
        assert all('release_series' not in row for row in json.loads(filename.read_text())['items'])
    # A collector may replace all rows; the next ordinary finalize restores the field.
    stripped = [{k: v for k, v in r.items() if k != 'release_series'} for r in result]
    (tmp_path / 'goods.json').write_text(json.dumps(stripped))
    subprocess.run(command, check=True)
    assert json.loads((tmp_path / 'goods.json').read_text()) == result
