from copy import deepcopy
import json

import pytest

from goodsdex.release_crosschecks import delta_days, reconcile
from goodsdex.release_dates import apply_release_dates, digest
from test_release_dates import candidate


@pytest.mark.parametrize('a,b,delta', [
    ('2023-05', '2023-05-27', 0), ('2023-05', '2023-06', 30),
    ('2023-12', '2024-01-01', 30), ('2024-02', '2024-04', 60),
    ('2024-02-28', '2024-03-13', 14), ('2024-02-28', '2024-03-14', 15),
    ('2024-01-01', '2024-02-15', 45), ('2024-01-01', '2024-02-16', 46)])
def test_precision_and_threshold_boundaries(a, b, delta):
    assert delta_days(a, b) == delta_days(b, a) == delta
    base = dict(source='third_party', date=a)
    r = reconcile(base, [dict(source='llm', date=b, independent=True)])
    assert r['crosscheck_status'] == ('corroborated' if delta <= 14 else 'disagreement' if delta <= 45 else 'conflict')
    assert r['source'] == 'third_party'
    if delta > 45:
        assert r['date'] is None and r['manual_review_required']
    if delta > 14:
        assert r['display_allowed'] is False and r['display'] is None


def test_official_keeps_value_and_records_both_sources_and_delta():
    r = reconcile(dict(source='official', date='2023-05'), [dict(source='llm', date='2024-01')])
    assert r['date'] == '2023-05' and r['source'] == 'official'
    assert r['checks'][-1]['delta_days'] == 240
    assert r['checks'][-1]['verdict'] == 'conflict'
    assert r['checks'][-1]['compared_to'] == dict(source='official', date='2023-05')


def test_llm_llm_pairwise_conflict_even_when_each_is_near_primary():
    base = dict(source='third_party', date='2023-05')
    r = reconcile(base, [dict(source='llm', date='2023-04', independent=True),
                         dict(source='llm', date='2023-06', independent=True)])
    assert r['date'] is None
    assert any(c['delta_days'] == 60 and c['compared_to']['source'] == 'llm' for c in r['checks'])


def test_history_cannot_be_erased_by_later_agreement():
    base = dict(source='llm', date='2023-05')
    old = reconcile(base, [dict(source='llm', date='2023-08', independent=True)])
    new = reconcile(base, [dict(source='llm', date='2023-05', independent=True)], old['checks'])
    assert new['date'] is None
    assert any(c['verdict'] == 'conflict' for c in new['checks'])


def test_absent_or_abstaining_check_never_unlocks_third_party():
    for obs in ([], [dict(source='llm', date=None, independent=True)]):
        r = reconcile(dict(source='third_party', date='2023-05'), obs)
        assert r['crosscheck_status'] == 'unverified'
        assert r['display_allowed'] is False and r['corroborated'] is False


def test_replay_binds_to_original_and_is_idempotent(tmp_path):
    c = candidate(1, 'third_party')
    p, checks = tmp_path/'dates.json', tmp_path/'checks.json'
    p.write_text(json.dumps(dict(schema=1, candidates=[c])))
    doc = dict(schema=1, checks={c['family']: dict(source='llm', date='2023-08', independent=True,
                                                 original_sha256=digest(c['release']))})
    checks.write_text(json.dumps(doc))
    out = apply_release_dates([dict(id='id-1')], p, crosscheck_path=checks)
    assert out[0]['release']['date'] is None
    assert apply_release_dates(out, p, crosscheck_path=checks) == out
    c['release']['date'] = '2023-06'
    p.write_text(json.dumps(dict(schema=1, candidates=[c])))
    with pytest.raises(ValueError, match='Stale'):
        apply_release_dates(out, p, crosscheck_path=checks)


def test_existing_official_overrides_third_party_with_audit(tmp_path):
    c = candidate(1, 'third_party')
    p = tmp_path/'dates.json'
    p.write_text(json.dumps(dict(schema=1, candidates=[c])))
    official = deepcopy(c['release']); official.update(source='official', date='2022-01')
    r = apply_release_dates([dict(id='id-1', release=official)], p)[0]['release']
    assert r['date'] == '2022-01' and r['source'] == 'official'
    assert any(check['source'] == 'third_party' and check['verdict'] == 'conflict' for check in r['checks'])


def test_blind_prompt_cannot_include_prior_values_or_sources():
    from crosscheck_release_dates import prompt
    identity = dict(family='private-key', brand='小米', category='电脑', model='Book Pro 14',
                    market='CN', event='announcement', date='2099-11',
                    evidence='SECRET_SOURCE', release={'date': '2099-11'})
    result = prompt(identity)
    assert '2099-11' not in result and 'SECRET_SOURCE' not in result and 'private-key' not in result
    assert 'Book Pro 14' in result and 'announcement' in result


def test_existing_third_party_outside_candidates_replays_without_anchoring(tmp_path):
    p, checks = tmp_path/'dates.json', tmp_path/'checks.json'
    p.write_text(json.dumps(dict(schema=1, candidates=[])))
    release = candidate(1, 'third_party')['release']
    checks.write_text(json.dumps(dict(schema=1, checks={'id-1': dict(source='llm', date='2023-05-27',
        independent=True, original_sha256=digest(release))})))
    out = apply_release_dates([dict(id='id-1', release=release)], p, crosscheck_path=checks)
    assert out[0]['release']['corroborated']
    assert apply_release_dates(out, p, crosscheck_path=checks) == out
