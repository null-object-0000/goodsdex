from copy import deepcopy
import json
import random

import pytest

from goodsdex.release_dates import apply_release_dates, coverage, digest, llm_gate, validate


def candidate(i, source='llm'):
    return dict(family=f'model-{i:02}', ids=[f'id-{i}'], release=dict(
        date='2023-05', granularity='month', source=source, confidence='medium',
        event='availability', model='fixture-model', market='CN', evidence=dict(
            url='https://www.mi.com/launch', quote='本机型于2023年5月发售',
            locator='article/body', sha256='a'*64, captured_at='2026-11-03T00:00:00Z',
            source_type='third_party' if source == 'third_party' else 'official')))


def review(cs, correct=30):
    chosen = random.Random(42).sample(sorted(c['family'] for c in cs), 30)
    by_family = {c['family']:c for c in cs}
    return dict(seed=42, universe_sha256=digest(cs), samples=[dict(
        family=f, candidate_sha256=digest(by_family[f]), correct=i < correct,
        correct_date='2023-05' if i < correct else '2023-06',
        verification_url='https://example.com/launch', verification_quote='逐条核对原文',
        checked_at='2026-11-03T00:00:00Z') for i, f in enumerate(chosen)])


@pytest.mark.parametrize('correct,usage', [(26,'disabled'), (27,'reference'), (29,'reference'), (30,'fact')])
def test_rollout_thresholds_are_bound_to_random_distinct_model_families(correct, usage):
    cs = [candidate(i) for i in range(40)]
    r = review(cs, correct)
    assert llm_gate(cs,r)['usage'] == usage
    cs[0]['release']['date'] = '2023-06'
    with pytest.raises(ValueError, match='universe'):
        llm_gate(cs,r)


def test_repeated_variants_or_unchecked_samples_cannot_unlock_rollout():
    cs = [candidate(i) for i in range(40)]
    r = review(cs)
    r['samples'][1] = deepcopy(r['samples'][0])
    with pytest.raises(ValueError, match='distinct'):
        llm_gate(cs,r)
    r = review(cs)
    r['samples'][0].pop('checked_at')
    with pytest.raises(ValueError, match='Incomplete'):
        llm_gate(cs,r)


@pytest.mark.parametrize('field,value', [('date','2023'), ('date','2023-13'), ('date','2023-05-01'),
    ('source','memory'), ('confidence',.99), ('granularity','day'), ('event','unknown'),
    ('evidence',{}), ('model','')])
def test_rejects_fake_precision_or_missing_provenance(field,value):
    c = candidate(1)
    c['release'][field] = value
    with pytest.raises(ValueError):
        validate(c)


def test_apply_keeps_unknown_empty_never_exports_inference_as_plain_params(tmp_path):
    cs = [candidate(i) for i in range(40)] + [candidate(50,'official')]
    path = tmp_path/'dates.json'
    path.write_text(json.dumps(dict(schema=1,candidates=cs,review=review(cs[:-1],29))))
    rows = [dict(id='id-0',brand='Apple',params={}), dict(id='unknown',name='2025款'), dict(id='id-50')]
    before = deepcopy(rows)
    out = apply_release_dates(rows,path)
    assert rows == before
    assert out[0]['params'] == {}
    assert out[0]['release']['source'] == 'llm'
    assert out[0]['release']['usage'] == 'reference'
    assert out[0]['release']['display'] == '约 2023 年 5 月（推断）'
    assert 'release' not in out[1]
    assert out[2]['release']['source'] == 'official'
    assert apply_release_dates(out,path) == out
    assert coverage(out)['covered'] == 2
    bundle = json.loads(path.read_text());bundle['review'] = review(cs[:-1],26)
    path.write_text(json.dumps(bundle))
    assert 'release' not in apply_release_dates(out,path)[0]


def test_missing_review_input_fails_closed(tmp_path):
    with pytest.raises(ValueError, match='Missing'):
        apply_release_dates([],tmp_path/'missing.json')


def test_unsampled_model_date_cannot_bypass_gate_via_existing_row(tmp_path):
    path = tmp_path/'dates.json'
    path.write_text(json.dumps(dict(schema=1,candidates=[])))
    row = dict(id='unreviewed',release=candidate(0)['release'])
    with pytest.raises(ValueError,match='Unreviewed LLM'):
        apply_release_dates([row],path)


def test_future_official_schedule_is_reference_and_labelled_as_planned(tmp_path):
    c = candidate(1,'official')
    c['release']['event'] = 'planned_availability'
    path = tmp_path/'dates.json'
    path.write_text(json.dumps(dict(schema=1,candidates=[c])))
    r = apply_release_dates([dict(id='id-1')],path)[0]['release']
    assert r['usage'] == 'reference'
    assert r['label'] == '预计发售'
    assert r['display'] == '预计 2023 年 5 月（官方计划）'


def test_committed_evidence_and_sampling_manifest_are_valid():
    from goodsdex.release_dates import DEFAULT_INPUT
    b = json.loads(DEFAULT_INPUT.read_text())
    for c in b['candidates']:
        validate(c)
    gate = llm_gate(b['candidates'],b['review'])
    assert gate['sample_size'] == 30
    ids = [key for c in b['candidates'] for key in c['ids']]
    assert len(set(ids)) == len(ids)
