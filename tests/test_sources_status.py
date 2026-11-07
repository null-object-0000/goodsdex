"""Actions liveness must never invent success; publication shares one manifest."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from generate_sources_status import SOURCES, generate, mark_stale, write_status
from goodsdex.shards import build_shards

NOW = datetime(2026, 11, 3, 20, tzinfo=timezone.utc)


def run(id=100, status='completed', result='success', at='2026-11-03T19:00:00Z'):
    return dict(id=id, status=status, conclusion=result, created_at=at,
                run_started_at=at, updated_at=at, html_url=f'https://github.com/o/r/actions/runs/{id}')


class API:
    def __init__(self, latest=None, successful=None):
        self.latest = latest or run()
        self.successful = successful or run(id=99)
        self.calls = []

    def get(self, path, raw=False):
        self.calls.append(path)
        if '/logs' in path:
            return b'2026-11-03T19:00:00Z ##[error]first failure\n##[error]later error'
        if 'annotations?' in path:
            return [dict(annotation_level='failure', message='annotation failure')]
        return {'workflow_runs': [self.successful if 'status=success' in path else self.latest]}

    def pages(self, path, key):
        return iter([dict(id=10, name='collect', status='completed', conclusion='failure',
                          check_run_url='https://api.github.com/repos/o/r/check-runs/10')])


def test_without_token_is_explicit_unknown_for_all_sources():
    api = API()
    payload = generate('o/r', '', NOW, api)
    assert len(payload['sources']) == len(SOURCES)
    assert [s['sourceId'] for s in payload['sources']] == [s[0] for s in SOURCES]
    assert all(s['conclusion'] == 'unknown' and s['error'] == '缺少 GITHUB_TOKEN'
               and s['lastSuccessAt'] is None for s in payload['sources'])
    assert not api.calls


def test_latest_failure_retains_real_previous_success_and_first_error():
    api = API(run(result='failure'), run(id=98, at='2026-11-03T15:00:00Z'))
    rows = generate('o/r', 'test-token', NOW, api)['sources']
    row = rows[0]
    assert row['conclusion'] == 'failure'
    assert row['lastAttemptAt'] == '2026-11-03T19:00:00Z'
    assert row['lastSuccessAt'] == '2026-11-03T15:00:00Z'
    assert row['runUrl'].endswith('/100')
    assert row['error'] == 'first failure'
    assert row['stale'] is True
    assert row['staleReason'] == '已 5.0 小时无成功运行（预期每 60 分钟）'
    assert rows[3]['stale'] is False  # daily cars, not hourly
    assert rows[-1]['expectedIntervalMinutes'] is None


@pytest.mark.parametrize('status,result,expected', [
    ('in_progress', None, 'in_progress'), ('queued', None, 'in_progress'),
    ('completed', 'cancelled', 'cancelled'), ('completed', 'timed_out', 'failure'),
    ('completed', 'skipped', 'unknown'), ('completed', 'success', 'success')])
def test_conclusions(status, result, expected):
    row = generate('o/r', 't', NOW, API(run(status=status, result=result)))['sources'][0]
    assert row['conclusion'] == expected
    assert row['lastSuccessAt'] == '2026-11-03T19:00:00Z'


def test_stale_threshold_is_strict_and_missing_success_explained():
    for at, expected in [('2026-11-03T18:00:00Z', False), ('2026-11-03T17:59:59Z', True), (None, True)]:
        row = dict(expectedIntervalMinutes=60, lastSuccessAt=at, stale=False, staleReason=None)
        mark_stale(row, NOW)
        assert row['stale'] is expected
        assert bool(row['staleReason']) is expected


def test_api_permission_failure_does_not_claim_success_or_leak_exception():
    class Denied(API):
        def get(self, path, raw=False):
            raise RuntimeError('GitHub API HTTP 403')
    rows = generate('o/r', 't', NOW, Denied())['sources']
    assert all(r['conclusion'] == 'unknown' and '403' in r['error'] for r in rows)


def test_missing_runs_and_missing_success():
    class Empty(API):
        def get(self, path, raw=False):
            return {'workflow_runs': []}
        def pages(self, path, key):
            return iter([])
    rows = generate('o/r', 't', NOW, Empty())['sources']
    assert all(r['conclusion'] == 'unknown' and r['lastSuccessAt'] is None for r in rows)
    assert rows[0]['stale']


def test_annotation_fallback_truncates_and_redacts_token():
    class Fallback(API):
        def get(self, path, raw=False):
            if '/logs' in path:
                raise RuntimeError('GitHub API HTTP 403')
            if 'annotations?' in path:
                return [dict(annotation_level='failure', message='test-token ' + '错' * 300)]
            return super().get(path, raw)
    row = generate('o/r', 'test-token', NOW, Fallback(run(result='failure')))['sources'][0]
    assert len(row['error']) == 200
    assert 'test-token' not in row['error']
    assert row['error'].startswith('[REDACTED]')


def test_reusable_publish_uses_actual_job_and_skips_skipped_callers():
    class Reusable(API):
        def get(self, path, raw=False):
            if 'publish-release.yml/runs?' in path:
                return {'workflow_runs': []}
            return super().get(path, raw)
        def pages(self, path, key):
            if key == 'workflow_runs':
                return iter([dict(run(id=i), referenced_workflows=[dict(path='o/r/.github/workflows/publish-release.yml@main')]) for i in [100, 99]])
            skipped = '/100/' in path
            return iter([dict(id=20, name='publish / publish', status='completed',
                             conclusion='skipped' if skipped else 'success',
                             started_at='2026-11-03T18:00:00Z', completed_at='2026-11-03T18:05:00Z')])
    row = generate('o/r', 't', NOW, Reusable())['sources'][-1]
    assert row['conclusion'] == 'success'
    assert row['lastSuccessAt'] == '2026-11-03T18:05:00Z'
    assert row['lastAttemptAt'] == '2026-11-03T18:00:00Z'
    assert row['runUrl'].endswith('/99')


def test_status_descriptor_survives_finalize_and_preserves_goods_meta(tmp_path):
    goods = b'[]\n'
    (tmp_path / 'goods.json').write_bytes(goods)
    old_meta = build_shards(tmp_path)
    payload = generate('o/r', '', NOW)
    write_status(tmp_path, payload)
    meta = json.loads((tmp_path / 'meta.json').read_bytes())
    assert {k: v for k, v in meta.items() if k != 'files'} == {k: v for k, v in old_meta.items() if k != 'files'}
    assert all(meta['files'][k] == v for k, v in old_meta['files'].items())
    raw = (tmp_path / 'sources-status.json').read_bytes()
    descriptor = dict(sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw), count=len(SOURCES))
    assert meta['files']['sources-status.json'] == descriptor
    assert build_shards(tmp_path)['files']['sources-status.json'] == descriptor
    assert (tmp_path / 'goods.json').read_bytes() == goods


def test_failure_conclusion_survives_unavailable_job_logs():
    class Unavailable(API):
        def pages(self, path, key):
            raise RuntimeError('GitHub API HTTP 403')
    row = generate('o/r', 't', NOW, Unavailable(run(result='failure')))['sources'][0]
    assert row['conclusion'] == 'failure'
    assert row['error'] == '无法读取失败日志/注解，请查看 runUrl'


def test_failure_with_no_success_does_not_reuse_attempt_timestamp():
    class NoSuccess(API):
        def get(self, path, raw=False):
            if 'status=success' in path:
                return {'workflow_runs': []}
            return super().get(path, raw)
    row = generate('o/r', 't', NOW, NoSuccess(run(result='failure')))['sources'][0]
    assert row['lastAttemptAt'] is not None
    assert row['lastSuccessAt'] is None
    assert row['stale'] is True


def test_hp_degraded_is_not_a_successful_observation():
    class HP(API):
        def pages(self, path, key):
            if key == 'workflow_runs':
                return iter([run(id=100), run(id=98, at='2026-10-30T23:23:00Z')])
            return iter([dict(id=100 if '/100/' in path else 98, name='collect')])
        def get(self, path, raw=False):
            if '/logs' in path:
                status = 'degraded' if '/100/' in path else 'success'
                return ('timestamp GOODSDEX_SOURCE_STATUS=' + json.dumps(dict(conclusion=status, error='blocked: 403 from hpstore.cn' if status == 'degraded' else None))).encode()
            return super().get(path, raw)
    row = generate('o/r', 'test-token', NOW, HP())['sources'][2]
    assert row['conclusion'] == 'degraded'
    assert row['error'] == 'blocked: 403 from hpstore.cn'
    assert row['lastSuccessAt'] == '2026-10-30T23:23:00Z'
    assert row['expectedIntervalMinutes'] == 1440
    assert row['stale']


def test_first_error_reports_exception_and_step_not_exit_code():
    """面板不该只说 exit code 1：要报失败步骤 + 真异常。"""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
    from generate_sources_status import first_error

    log = "\n".join([
        "2026-11-07T11:08:20Z ValueError: Concurrent change at data/archive/x.json.updated_at",
        "##[error]Process completed with exit code 1.",
    ])

    class Api:
        def get(self, path, raw=False):
            if path.startswith('actions/jobs/') and path.endswith('/logs'):
                return log.encode()
            raise AssertionError(path)

    job = dict(id=1, status='completed', conclusion='failure', check_run_url='x/1',
               steps=[dict(number=10, name='Merge candidate onto latest release', conclusion='failure')])
    out = first_error(Api(), dict(id=9), [job])
    assert 'Merge candidate onto latest release' in out
    assert 'Concurrent change at data/archive/x.json.updated_at' in out
    assert 'exit code' not in out
