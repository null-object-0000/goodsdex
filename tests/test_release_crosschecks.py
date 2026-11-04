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
    assert r['crosscheck_status'] == ('corroborated' if delta <= 14 else 'unverified')
    assert r['checks'][-1]['verdict'] == ('corroborated' if delta <= 14 else 'disagreement' if delta <= 45 else 'conflict')
    assert r['source'] == 'third_party'
    if delta > 45:
        assert r['date'] == a and not r['manual_review_required']
    if delta > 14:
        assert r['display_allowed'] is False and r['display'] is None


def test_official_keeps_value_and_records_both_sources_and_delta():
    r = reconcile(dict(source='official', date='2023-05'), [dict(source='llm', date='2024-01')])
    assert r['date'] == '2023-05' and r['source'] == 'official'
    assert r['checks'][-1]['delta_days'] == 240
    assert r['checks'][-1]['verdict'] == 'conflict'
    assert r['checks'][-1]['compared_to'] == dict(source='official', date='2023-05')


def test_official_upgrade_with_two_model_observations_replays_without_reverse_pairs():
    base = dict(source='official', date='2021-10')
    observations = [dict(source='llm', date='2021-10', family='old-estimate'),
                    dict(source='llm', date='2021-10-20', independent=True)]
    first = reconcile(base, observations)
    assert first['source'] == 'official' and first['date'] == '2021-10'
    assert len(first['checks']) == 4  # original, two primary checks, one model pair
    replay = reconcile(base, observations, first['checks'])
    assert replay == first
    assert reconcile(base, observations, replay['checks']) == first


def test_unsupported_llm_pairs_cannot_erase_primary():
    base = dict(source='third_party', date='2023-05')
    r = reconcile(base, [dict(source='llm', date='2023-04', independent=True),
                         dict(source='llm', date='2023-06', independent=True)])
    assert r['date'] == '2023-05' and not r['manual_review_required']
    assert any(c['delta_days'] == 60 and c['compared_to']['source'] == 'llm' for c in r['checks'])


def test_unsupported_history_is_retained_but_cannot_veto_later_agreement():
    base = dict(source='llm', date='2023-05')
    old = reconcile(base, [dict(source='llm', date='2023-08', independent=True)])
    new = reconcile(base, [dict(source='llm', date='2023-05', independent=True)], old['checks'])
    assert new['date'] == '2023-05' and new['corroborated']
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
    assert out[0]['release']['date'] == c['release']['date']
    assert out[0]['release']['display_allowed'] is False
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


def evidence(**extra):
    return dict(url='https://example.com/launch', quote='Launch report',
                sha256='a'*64, captured_at='2026-11-03', **extra)


def test_cited_conflict_keeps_date_without_two_verified_sources():
    base = dict(source='third_party', date='2023-05', evidence=evidence())
    obs = dict(source='llm', date='2023-08', evidence=evidence(), independent=True)
    r = reconcile(base, [obs])
    assert r['crosscheck_status'] == 'conflict'
    assert r['date'] == '2023-05' and not r['manual_review_required']
    assert r['internal_only'] and not r['display_allowed']


def test_two_hard_sources_require_manual_review_and_preserve_evidence():
    base = dict(source='third_party', date='2023-05', evidence=evidence())
    obs = dict(source='llm', date='2023-08', evidence=evidence(verified=True), independent=True)
    r = reconcile(base, [obs])
    assert r['date'] is None and r['manual_review_required']
    assert r['evidence'] == base['evidence']
    assert r['checks'][-1]['evidence'] == obs['evidence']
    # A later match must not erase a verified historical contradiction.
    new = reconcile(base, [dict(source='llm', date='2023-05', independent=True)], r['checks'])
    assert new['date'] is None and new['manual_review_required']


def test_contemporary_report_outranks_unverified_model_citation():
    base = dict(source='third_party', date='2023-05', confidence='high',
                evidence=evidence(published_at='2023-05-27'))
    obs = dict(source='llm', date='2023-08', evidence=dict(quote='a recalled quotation'))
    r = reconcile(base, [obs])
    assert r['date'] == '2023-05' and r['confidence'] == 'high'
    assert r['checks'][-1]['decision_reason'] == 'contemporary_report_precedes_model_memory'
    assert r['crosscheck_status'] == 'unverified'


def test_unsupported_dissent_cannot_subtract_agreement_or_confidence():
    base = dict(source='third_party', date='2023-05', confidence='high', display_allowed=True,
                display='2023 年 5 月', usage='fact', evidence=evidence())
    agree = dict(source='llm', date='2023-05', independent=True)
    a = reconcile(base, [agree])
    b = reconcile(base, [agree, dict(source='llm', date='2023-08', reason='I remember it')])
    assert {k:v for k,v in a.items() if k != 'checks'} == {k:v for k,v in b.items() if k != 'checks'}
    assert b['checks'][-1]['effective_verdict'] == 'unverified'


def test_assembly_retains_model_citation(tmp_path):
    import hashlib
    from crosscheck_release_dates import assemble
    identity = dict(family='check-0000', brand='小米', category='吹风机', model='H501', market='CN', event='availability')
    (tmp_path/'identities.json').write_text(json.dumps([identity]))
    (tmp_path/'baseline-dates.json').write_text(json.dumps([dict(key='check-0000', family='H501', release={})]))
    (tmp_path/'responses').mkdir()
    key = hashlib.sha256(b'check-0000').hexdigest()[:24]
    value = dict(date='2023-08', market='CN', event='availability', evidence=evidence(verified=True))
    (tmp_path/'responses'/f'{key}.json').write_text(json.dumps(dict(response=dict(choices=[dict(message=dict(content=json.dumps(value)))]))))
    assemble(tmp_path)
    assert json.loads((tmp_path/'checks.json').read_text())['checks']['H501']['evidence'] == {k: value['evidence'][k] for k in ('url', 'quote')}


def test_rebuild_restores_old_null_outside_managed_candidates(tmp_path):
    p, checks = tmp_path/'dates.json', tmp_path/'checks.json'
    p.write_text(json.dumps(dict(schema=1, candidates=[])))
    original = candidate(1, 'third_party')['release']
    check = dict(source='llm', date='2023-08', independent=True, original_sha256=digest(original))
    checks.write_text(json.dumps(dict(schema=1, checks={'id-1':check})))
    old = dict(original, date=None, manual_review_required=True, display_allowed=False, checks=[
        dict(source='third_party', date=original['date'], verdict='original', delta_days=0),
        dict(check, verdict='conflict', delta_days=90, compared_to=dict(source='third_party', date=original['date']))])
    out = apply_release_dates([dict(id='id-1', release=old)], p, crosscheck_path=checks)
    assert out[0]['release']['date'] == original['date']
    assert out[0]['release']['evidence'] == original['evidence']
    assert not out[0]['release']['manual_review_required']
    assert apply_release_dates(out, p, crosscheck_path=checks) == out


def test_models_agreeing_with_each_other_cannot_corroborate_a_different_primary_date():
    base = dict(source='third_party', date='2023-05')
    r = reconcile(base, [dict(source='llm', date='2023-08-01', independent=True, model='a'),
                         dict(source='llm', date='2023-08-02', independent=True, model='b')])
    assert any(c['verdict'] == 'corroborated' and c['compared_to']['source'] == 'llm' for c in r['checks'])
    assert r['date'] == '2023-05' and not r['corroborated']
    assert r['crosscheck_status'] == 'unverified' and not r['display_allowed']
