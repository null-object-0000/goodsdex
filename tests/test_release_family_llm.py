from copy import deepcopy
import json

import pytest

from goodsdex.release_dates import apply_release_dates, brand_llm_gate, brand_sample, digest
from test_release_dates import candidate
from release_family_llm import aggregate
import release_family_llm as runner


def corpus(brand, count=100):
    cs = [candidate(i) for i in range(count)]
    for c in cs:
        c['brand'] = brand
        c['family'] = brand + '|' + c['family']
        c['ids'] = [brand + '|' + c['ids'][0]]
    return cs


def review(cs, correct):
    by = {c['family']: c for c in cs}
    return dict(seed=20261105, universe_sha256=digest(cs), samples=[dict(
        family=f, candidate_sha256=digest(by[f]), correct=i < correct,
        correct_date='2023-05' if i < correct else '2023-06', identity_match=True,
        evidence_supported=True, checked_at='2026-11-03T00:00:00Z',
        verification_url='https://example.com/verified', verification_quote='Checked original',
        verdict_reason='Model and month checked')
        for i, f in enumerate(brand_sample(by, 20261105))])


def test_brand_accuracy_never_unlocks_another_brand():
    good, bad = corpus('富士'), corpus('惠普')
    gates = brand_llm_gate(good + bad, {'富士': review(good, 10), '惠普': review(bad, 8)})
    assert gates['富士']['confidence'] == 'high'
    assert gates['惠普']['usage'] == 'disabled'
    assert brand_llm_gate(good, {'富士': review(good, 9)})['富士']['confidence'] == 'medium'
    r = review(good, 10)
    r['samples'][0]['evidence_supported'] = False
    with pytest.raises(ValueError, match='support'):
        brand_llm_gate(good, {'富士': r})
    good[0]['release']['date'] = '2024-05'
    with pytest.raises(ValueError, match='universe'):
        brand_llm_gate(good, {'富士': r})


def test_sidecar_official_priority_internal_only_and_single_switch_rollback(tmp_path):
    cs = corpus('富士', 40)
    main = tmp_path / 'official.json'
    main.write_text(json.dumps(dict(schema=1, candidates=[])))
    sidecar = tmp_path / 'llm.json'
    b = dict(schema=1, enabled=True, candidates=cs, reviews={'富士': review(cs, 4)},
             managed_ids=[key for c in cs for key in c['ids']])
    sidecar.write_text(json.dumps(b))
    official = deepcopy(candidate(0, 'official')['release'])
    rows = [dict(id=cs[0]['ids'][0], release=official), dict(id=cs[1]['ids'][0])]
    out = apply_release_dates(rows, main, sidecar)
    assert out[0] == rows[0]
    r = out[1]['release']
    assert r['confidence'] == 'high' and r['usage'] == 'reference'
    assert r['internal_only'] and not r['display_allowed']
    assert r['estimate_notice'] == '按型号世代估算'
    assert apply_release_dates(out, main, sidecar) == out
    b['enabled'] = False
    sidecar.write_text(json.dumps(b))
    rolled = apply_release_dates(out, main, sidecar)
    assert rolled[0] == rows[0] and 'release' not in rolled[1]


def test_family_grouping_retains_se_and_platform_but_merges_storage_and_body_kits():
    rows = [dict(id='a', brand='小米', category='扫地机器人', name='H501 8GB+128GB'),
            dict(id='b', brand='小米', category='扫地机器人', name='H501 12GB+256GB'),
            dict(id='c', brand='小米', category='扫地机器人', name='H501 SE'),
            dict(id='body', brand='富士', category='相机', name='FUJIFILM X-T5', release={'source': 'official'}),
            dict(id='kit', brand='富士', category='相机', name='X-T5 1650套机', body_id='body')]
    fs = aggregate(rows)
    assert len(fs) == 3
    assert sorted(len(f['variants']) for f in fs) == [1, 1, 2]
    assert next(f for f in fs if f['brand'] == '富士')['model'] == 'FUJIFILM X-T5'


def test_rate_limit_opens_circuit_without_sending_or_retrying_other_families(tmp_path, monkeypatch):
    from urllib.error import HTTPError
    calls = []

    class Limited:
        def open(self, request, timeout):
            calls.append(request.full_url)
            raise HTTPError(request.full_url, 429, 'Rate limited', {'Retry-After': '60'}, None)

    monkeypatch.setattr(runner.urllib.request, 'build_opener', lambda *args: Limited())
    monkeypatch.setattr(runner, '_api_key', lambda: 'fixture')
    f = dict(family='小米|相机|H501', brand='小米', category='相机', model='H501')
    monkeypatch.setattr(runner, 'CONSECUTIVE_429', 0)
    runner.STOP.clear()
    try:
        assert runner.run_one(f, tmp_path, runner.Config(consecutive_429=1)) == 'failed'
        assert runner.run_one({**f, 'family': '小米|相机|H501 SE'}, tmp_path) == 'circuit_open_not_sent'
        assert len(calls) == 1 and len(list((tmp_path / 'sent').glob('*.json'))) == 1
        failure = json.loads(next((tmp_path / 'responses').glob('*.json')).read_text())
        assert failure['retry_after'] == '60'
        runner.STOP.clear()
        assert runner.run_one(f, tmp_path) == 'already_sent'
        assert len(calls) == 1
    finally:
        runner.STOP.clear()


def test_budget_floor():
    with pytest.raises(ValueError):
        runner.Config(max_tokens=650)


def test_429_backoff_and_resume(tmp_path, monkeypatch):
    from urllib.error import HTTPError
    import io
    calls, sleeps = [], []
    class Backend:
        def open(self, request, timeout):
            body = json.loads(request.data)
            assert body['max_tokens'] >= 4000 and body['enable_thinking'] is False
            calls.append(body)
            if len(calls) < 3:
                raise HTTPError(request.full_url, 429, 'limited', {}, None)
            return io.StringIO(json.dumps({'choices': [{'message': {'content': '{}'}}], 'usage': {'prompt_tokens': 12, 'completion_tokens': 4}}))
    monkeypatch.setattr(runner.urllib.request, 'build_opener', lambda *args: Backend())
    monkeypatch.setattr(runner, '_api_key', lambda: 'fixture')
    monkeypatch.setattr(runner.time, 'sleep', sleeps.append)
    monkeypatch.setattr(runner, 'CONSECUTIVE_429', 0)
    f = dict(family='test', brand='小米', category='相机', model='test')
    runner.STOP.clear()
    assert runner.run_one(f, tmp_path) == 'completed'
    assert sleeps == [1, 2]
    assert runner.run_one(f, tmp_path) == 'already_sent'
    assert len(calls) == 3
    assert json.loads(next((tmp_path/'states').glob('*.json')).read_text())['status'] == 'ok'
