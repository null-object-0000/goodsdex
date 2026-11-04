import gzip
import json
from pathlib import Path

from goodsdex.series_release import apply_series_releases

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / 'docs/xiaomi-release-dictionary-20261104'


def test_dictionary_provenance_and_special_edition_boundary():
    entries = json.loads((ROOT / 'data/official/xiaomi-release-dictionary.json').read_text())['entries']
    assert len(entries) == len({e['id'] for e in entries}) == 256
    assert all(e['product_name'] and e['date'] and e['evidence']['quote']
               and e['evidence']['url'].startswith(('http://', 'https://')) for e in entries)
    twelve = next(e for e in entries if e['product_name'] == '小米12系列')
    assert '小米12系列发布' in twelve['evidence']['quote']
    airdots = [e for e in entries if e['date'] == '2022-03-17' and 'AirDots' in e['product_name']]
    assert [e['product_name'] for e in airdots] == ['Redmi AirDots 3 Pro Genshin Impact Edition']
    assert 'Redmi AirDots 3 Pro' not in airdots[0]['aliases']


def test_legacy_repair_keeps_unsupported_event_disabled():
    before = json.loads(gzip.decompress((DOC / 'baseline.json.gz').read_bytes()))
    after = apply_series_releases(before)
    legacy = json.loads((DOC / 'legacy-149.json').read_text())
    assert len(legacy) == 149
    assert sum(x['repaired'] for x in legacy) == 57
    assert sum(not x['repaired'] for x in legacy) == 92
    rejected = {'CN:mi_cn:product:' + p for p in ('10050241', '25284', '25291')}
    for row in after:
        if row['id'] in rejected:
            release = row['release_series']
            assert release['date'] == '2026-09'
            assert release['usage'] == 'disabled'
            assert release['display_allowed'] is False
            assert release['display'] is None
    assert [{k: v for k, v in r.items() if k != 'release_series'} for r in before] == [
        {k: v for k, v in r.items() if k != 'release_series'} for r in after]
    assert apply_series_releases(after) == after


def test_audited_matches_are_exact_and_research_families_stay_unmatched():
    entries = {e['id']: e for e in json.loads((ROOT / 'data/official/xiaomi-release-dictionary.json').read_text())['entries']}
    samples = json.loads((DOC / 'sample-30.json').read_text())
    assert len(samples) == len({s['id'] for s in samples}) == 30
    for sample in samples:
        assert sample['dictionary_entry_id'] in entries
    before = json.loads(gzip.decompress((DOC / 'baseline.json.gz').read_bytes()))
    byid = {r['id']: r for r in apply_series_releases(before)}
    new = json.loads((DOC / 'new-memberships.json').read_text())
    assert len(new) == 7
    for item in new:
        row = byid[item['id']]
        assert row['release_series']['date'] == item['date']
        assert row['release_series']['crosscheck_status'] == 'official'
        assert row['release_series']['display_allowed'] is True
    assert 'release_series' not in byid['CN:mi_cn:product:23676'] # Later 至尊版 isn't base TV.
