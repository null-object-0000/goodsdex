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
    assert all(out[0]['release'][k] == v for k, v in official.items())
    assert any(c['source'] == 'llm' for c in out[0]['release']['checks'])
    r = out[1]['release']
    assert r['confidence'] == 'high' and r['usage'] == 'reference'
    assert r['internal_only'] and not r['display_allowed']
    assert r['estimate_notice'] == '按型号世代估算'
    assert apply_release_dates(out, main, sidecar) == out
    b['enabled'] = False
    sidecar.write_text(json.dumps(b))
    rolled = apply_release_dates(out, main, sidecar)
    assert rolled[0] == out[0] and 'release' not in rolled[1]


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


def test_concurrent_batch_is_bounded_and_resume_does_not_resend_ok(tmp_path, monkeypatch):
    import io
    import threading
    import time
    active = peak = calls = 0
    lock = threading.Lock()
    class Backend:
        def open(self, request, timeout):
            nonlocal active, peak, calls
            with lock:
                active += 1
                calls += 1
                peak = max(peak, active)
            time.sleep(.04)
            with lock:
                active -= 1
            return io.StringIO(json.dumps({'model': 'fixture', 'choices': [{'message': {'content': '{}'}}]}))
    monkeypatch.setattr(runner.urllib.request, 'build_opener', lambda *args: Backend())
    monkeypatch.setattr(runner, '_api_key', lambda: 'fixture')
    fs = [dict(family=str(i), brand='小米', category='相机', model=str(i)) for i in range(12)]
    config = runner.Config()
    # Pacing has a separate real-clock test; isolate the worker bound here.
    monkeypatch.setattr(runner.Dispatch, 'acquire', lambda self: not runner.STOP.is_set())
    runner.run_batch(fs, tmp_path, config)
    assert peak == 6 and calls == 12
    runner.run_batch(fs, tmp_path, config)
    assert calls == 12
    assert all(json.loads(p.read_text())['status'] == 'ok' for p in (tmp_path/'states').glob('*.json'))


def test_global_dispatch_pacing_and_sticky_circuit(tmp_path):
    import time
    runner.STOP.clear()
    d = runner.Dispatch(tmp_path, runner.Config())
    starts = []
    for _ in range(3):
        assert d.acquire()
        starts.append(time.monotonic())
    assert all(b-a >= .24 for a,b in zip(starts, starts[1:]))
    for _ in range(3):
        d.completed(429, 'test')
    d.completed(200, 'inflight_success')
    assert runner.STOP.is_set() and not d.acquire()
    assert (tmp_path/'circuit.json').exists()
    runner.STOP.clear()


def test_resume_interrupted_sent_and_429_without_resending_success(tmp_path, monkeypatch):
    import io
    import hashlib
    f = dict(family='interrupted', brand='小米', category='相机', model='test')
    key = hashlib.sha256(f['family'].encode()).hexdigest()[:24]
    runner.write(tmp_path/'sent'/f'{key}.json', {'family': f['family']})
    runner.write(tmp_path/'states'/f'{key}.json', {'status': 'sent'})
    runner.write(tmp_path/'responses'/f'{key}.json', {'attempts': [{'attempt': 1}]})
    class Backend:
        def open(self, request, timeout):
            return io.StringIO(json.dumps({'model': 'fixture', 'choices': [{'message': {'content': '{}'}}]}))
    monkeypatch.setattr(runner.urllib.request, 'build_opener', lambda *args: Backend())
    monkeypatch.setattr(runner, '_api_key', lambda: 'fixture')
    runner.STOP.clear()
    runner.run_batch([f], tmp_path, runner.Config())
    saved = json.loads((tmp_path/'responses'/f'{key}.json').read_text())
    assert saved['attempts'][0]['interrupted_usage_unknown']
    assert len(saved['attempts']) == 2 and saved['captured_at'] and saved['model'] == 'fixture'


def test_parallel_429_stops_queued_work_and_is_explicitly_resumable(tmp_path, monkeypatch):
    from urllib.error import HTTPError
    calls = []
    class Backend:
        def open(self, request, timeout):
            calls.append(1)
            raise HTTPError(request.full_url, 429, 'limited', {}, None)
    monkeypatch.setattr(runner.urllib.request, 'build_opener', lambda *args: Backend())
    monkeypatch.setattr(runner, '_api_key', lambda: 'fixture')
    fs = [dict(family=str(i), brand='小米', category='相机', model=str(i)) for i in range(20)]
    runner.run_batch(fs, tmp_path, runner.Config())
    assert 3 <= len(calls) <= 8  # At most six already in flight when breaker trips.
    assert (tmp_path/'circuit.json').exists()
    with pytest.raises(ValueError, match='Circuit'):
        runner.run_batch(fs, tmp_path, runner.Config())
    assert any(json.loads(p.read_text())['status'] == 'pending' for p in (tmp_path/'states').glob('*.json'))
    runner.STOP.clear()


def test_exponential_backoff_all_four_steps_and_recorded_raw_body(tmp_path, monkeypatch):
    from urllib.error import HTTPError
    import io
    calls, sleeps = [], []
    d = runner.Dispatch(tmp_path, runner.Config())
    class Backend:
        def open(self, request, timeout):
            calls.append(1)
            if len(calls) <= 4:
                # Concurrent healthy completions break a run of consecutive 429s.
                d.completed(200, 'healthy_other_family')
                raise HTTPError(request.full_url, 429, 'limited', {}, io.BytesIO(b'{"error":"rate limit"}'))
            return io.StringIO('{"model":"fixture","choices":[{"message":{"content":"{}"}}]}')
    monkeypatch.setattr(runner.urllib.request, 'build_opener', lambda *args: Backend())
    monkeypatch.setattr(runner, '_api_key', lambda: 'fixture')
    monkeypatch.setattr(d, 'acquire', lambda: True)
    from itertools import count
    times = count(1000, 20)
    monkeypatch.setattr(runner.time, 'time', lambda: next(times))
    monkeypatch.setattr(runner.STOP, 'wait', lambda delay: sleeps.append(delay) or False)
    runner.STOP.clear()
    f = dict(family='retry', brand='小米', category='相机', model='test')
    assert runner.run_one(f, tmp_path, runner.Config(), d) == 'completed'
    assert len(calls) == 5
    # Ignore the extra sub-millisecond retry_at clock checks.
    assert [s for s in sleeps if s >= 1] == [1, 2, 4, 8]
    saved = json.loads(next((tmp_path/'responses').glob('*.json')).read_text())
    assert saved['attempts'][0]['response_body'] == '{"error":"rate limit"}'
    assert saved['raw_response'].startswith('{"model":"fixture"')


def test_budget_and_rate_guards_cannot_disable_circuit():
    for kwargs in ({'consecutive_429': 4}, {'qps': 0}, {'qps': 5}, {'concurrency': 0}, {'concurrency': 7}):
        with pytest.raises(ValueError):
            runner.Config(**kwargs)


def test_resume_429_keeps_cooldown_budget_and_skips_completed_peer(tmp_path, monkeypatch):
    import io
    import hashlib
    calls, delays = [], []
    fs = [dict(family=name, brand='小米', category='相机', model=name) for name in ['limited', 'ok']]
    keys = [hashlib.sha256(f['family'].encode()).hexdigest()[:24] for f in fs]
    runner.write(tmp_path/'states'/f'{keys[0]}.json', dict(status='pending', retry_at=1010))
    runner.write(tmp_path/'responses'/f'{keys[0]}.json', {'attempts': [dict(http_status=429, backoff_seconds=1), dict(http_status=429, backoff_seconds=2)]})
    runner.write(tmp_path/'states'/f'{keys[1]}.json', dict(status='ok'))
    runner.write(tmp_path/'responses'/f'{keys[1]}.json', {'response': {'model': 'saved'}, 'attempts': [{'http_status': 200}]})
    runner.write(tmp_path/'circuit.json', dict(reason='consecutive_429', count=3))
    class Backend:
        def open(self, request, timeout):
            calls.append(json.loads(request.data))
            return io.StringIO('{"model":"fixture","choices":[{"message":{"content":"{}"}}]}')
    monkeypatch.setattr(runner.urllib.request, 'build_opener', lambda *args: Backend())
    monkeypatch.setattr(runner, '_api_key', lambda: 'fixture')
    monkeypatch.setattr(runner.time, 'time', lambda: 1000)
    monkeypatch.setattr(runner.STOP, 'wait', lambda delay: delays.append(delay) or False)
    monkeypatch.setattr(runner.Dispatch, 'acquire', lambda self: True)
    runner.run_batch(fs, tmp_path, runner.Config(), resume_after_circuit=True)
    assert len(calls) == 1 and delays == [10]
    assert len(json.loads((tmp_path/'responses'/f'{keys[0]}.json').read_text())['attempts']) == 3
    assert len(list((tmp_path/'circuit-history').glob('*.json'))) == 1
    assert not (tmp_path/'circuit.json').exists()



def test_consecutive_429_counter_survives_restart(tmp_path):
    runner.STOP.clear()
    first = runner.Dispatch(tmp_path, runner.Config())
    first.completed(429, 'first')
    first.completed(429, 'second')
    assert not runner.STOP.is_set()
    resumed = runner.Dispatch(tmp_path, runner.Config())
    resumed.completed(429, 'third_after_restart')
    assert runner.STOP.is_set()
    assert json.loads((tmp_path/'circuit.json').read_text())['count'] == 3
    runner.STOP.clear()
