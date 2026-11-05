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
    # Add independently frozen dictionary additions; split legacy batches retain
    # their original assertion, evidence and explicit lineage.
    audit = ROOT / 'docs/xiaomi-release-dictionary-20261104'
    for m in json.loads((audit / 'new-memberships.json').read_text()):
        if m['id'] in present:
            assert m['id'] not in expected
            expected[m['id']] = dict(date=m['date'], batch_id=m['batch_id'],
                                    url=m['evidence']['url'], granularity='day')
    for repair in json.loads((audit / 'legacy-repairs.json').read_text()):
        for key in repair['ids']:
            if key in present:
                assert expected[key]['batch_id'] == repair['original_batch_id']
                expected[key] = dict(expected[key], batch_id=repair['batch_id'])
    retrospective = ROOT / 'docs/release-dates-round10-20261104'
    for batch in json.loads((retrospective / 'new-series-batches.json').read_text()):
        for member in batch['members']:
            if member['id'] in present:
                assert member['id'] not in expected
                r = batch['series_release']
                expected[member['id']] = dict(date=r['date'], batch_id=batch['id'],
                                              url=r['evidence']['url'], granularity=r['granularity'])
    replacements = {key for c in json.loads((retrospective / 'replaced-candidates.json').read_text())
                    for key in c['ids']}
    command = [sys.executable, str(ROOT / 'scripts/finalize_public.py'), '--public', str(tmp_path)]
    subprocess.run(command, check=True)
    result = json.loads((tmp_path / 'goods.json').read_text())
    by_id = {r['id']: r for r in result}
    from goodsdex.release_dates import apply_release_dates
    product_expected = apply_release_dates(before)
    assert sum(bool(r.get('release')) for r in before) == 671
    # New reviewed product assertions are a separate finalizer stage; series
    # rollout must preserve its output, including every pre-existing release.
    for old, updated in zip(before, product_expected, strict=True):
        if old.get('release'):
            prior = old['release']
            if old['id'] in replacements:
                assert prior['source'] == 'third_party'
                assert updated['release']['source'] == 'official'
                # The reviewed official assertion replaces an internal media value;
                # retain the original statement even when market/event differ.
                assert any(c.get('source') == prior['source'] and c.get('date') == prior['date']
                           and c.get('evidence') == prior['evidence']
                           for c in updated['release']['checks'])
            elif prior.get('source') == 'third_party':
                # Round 7 requires two captured real sources; LLM agreement is
                # retained as audit evidence but no longer unlocks display.
                assert updated['release']['date'] == prior['date']
                assert updated['release']['evidence'] == prior['evidence']
                assert updated['release']['checks'] == prior['checks']
                assert updated['release']['display_allowed'] is False
                assert updated['release']['display'] is None
            else:
                assert updated['release'] == prior
    excluded=json.loads((tmp_path / 'archive/accessories.json').read_text())
    reviewed=json.loads((ROOT/'docs/name-fidelity-20261104/historical-exclusion-expectations.json').read_text())['docs/series-release-rollout-20261103/baseline-goods.json.gz']
    legacy_review=json.loads((ROOT/'docs/legacy-catalog-20261105/reviewed-accessory-ids.json').read_text())
    legacy_ids={r['id'] for r in legacy_review} & present
    assert {r['id'] for r in excluded} == {r['id'] for r in reviewed} | legacy_ids
    assert all(not r.get('release') for r in excluded if r['id'] not in legacy_ids)
    # Reclassified accessories retain their already reviewed date evidence.
    from goodsdex.release_dates import apply_release_dates as reviewed_dates
    legacy_expected = {r['id']:r for r in reviewed_dates(excluded)}
    assert all(r.get('release') == legacy_expected[r['id']].get('release') for r in excluded if r['id'] in legacy_ids)
    excluded_ids={r['id'] for r in excluded}
    excluded_ids.update(r['id'] for r in json.loads((tmp_path / 'archive/services.json').read_text()))
    apparel = json.loads((tmp_path / 'archive/apparel.json').read_text())
    assert len(apparel) == 54  # Frozen snapshot predates the Atour collection.
    excluded_ids.update(r['id'] for r in apparel)
    # The L1-L4 stage independently replays exact official product statements,
    # including reviewed month-to-day upgrades, after the legacy date stage.
    from goodsdex.release_coverage import apply_priority_dates
    # Date identities use the independently reviewed official page names too.
    # This frozen input still has truncated "Xiaomi" and a spurious "沙色";
    # the real finalizer repairs both before checking captured product evidence.
    from goodsdex.mi_names import apply_page_names
    product_expected = apply_priority_dates(apply_page_names(product_expected))
    product_by_id = {r['id']: r for r in product_expected}
    assert product_by_id['CN:mi_cn:product:19703']['release']['date'] == '2024-02'
    assert product_by_id['CN:mi_cn:product:20375']['release']['date'] == '2024-09'
    assert {r['id']: r.get('release') for r in result} == {r['id']: r.get('release') for r in product_expected if r['id'] not in excluded_ids}
    expected = {key: value for key, value in expected.items() if key not in excluded_ids}
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
