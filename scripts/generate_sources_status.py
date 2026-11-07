"""Snapshot Actions liveness, independently of goods fetch timestamps (stdlib only)."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import re
from urllib.error import HTTPError
from urllib.request import Request, build_opener, HTTPRedirectHandler, urlopen

SOURCES = [('refresh-prices', 60), ('refresh-apple', 60), ('refresh-hp', 1440), ('refresh-atour', 1440),
           ('refresh-cars', 1440), ('publish-release', None)]


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class GitHub:
    def __init__(self, repository, token):
        self.base = f'https://api.github.com/repos/{repository}/'
        self.token = token

    def get(self, path, raw=False):
        request = Request(self.base + path, headers={
            'Authorization': f'Bearer {self.token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
        })
        try:
            with build_opener(NoRedirect).open(request, timeout=30) as response:
                body = response.read()
        except HTTPError as exc:
            if not raw or exc.code != 302:
                raise RuntimeError(f'GitHub API HTTP {exc.code}') from None
            location = exc.headers['Location']
            if not location.startswith('https://'):
                raise RuntimeError('GitHub 日志重定向不是 HTTPS')
            # Signed log storage URL: never forward the GitHub credential.
            with urlopen(Request(location), timeout=30) as response:
                body = response.read()
        return body if raw else json.loads(body)

    def pages(self, path, key):
        separator = '&' if '?' in path else '?'
        for page in range(1, 11):
            rows = self.get(f'{path}{separator}per_page=100&page={page}')[key]
            yield from rows
            if len(rows) < 100:
                return
        raise RuntimeError('GitHub 查询超过 1000 条，无法确认最近状态')


def stamp(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def conclusion(run):
    if run.get('status') != 'completed':
        return 'in_progress'
    value = run.get('conclusion')
    if value in ('success', 'failure', 'cancelled'):
        return value
    return 'failure' if value in ('timed_out', 'action_required', 'startup_failure') else 'unknown'


def redact(message, token):
    if token:
        message = message.replace(token, '[REDACTED]')
    message = re.sub(r'(?i)\b(?:gh[pousr]_[\w]+|github_pat_[\w]+)\b', '[REDACTED]', message)
    message = re.sub(r'(?i)(authorization\s*[:=]\s*(?:bearer\s+)?|(?:token|password|secret|access_key\w*)\s*[:=]\s*)\S+', r'\1[REDACTED]', message)
    return message.strip()[:200]


EXC_LINE = re.compile(r'((?:\w+Error|\w+Exception|AssertionError):\s+.+)$')


def first_error(api, run, jobs=None):
    jobs = jobs if jobs is not None else list(api.pages(f"actions/runs/{run['id']}/jobs?filter=latest", 'jobs'))
    unavailable = False
    generic = None
    for job in jobs:
        if conclusion(job) != 'failure':
            continue
        step = next((s.get('name') for s in job.get('steps') or []
                     if s.get('conclusion') == 'failure'), None)
        # Log access needs only actions:read. Check annotations are a fallback.
        try:
            log = api.get(f"actions/jobs/{job['id']}/logs", raw=True).decode('utf-8', errors='replace')
            for line in log.splitlines():
                text = line.strip()
                # 真因通常是最后那条 Python 异常，不是 "exit code 1" 这种空话。
                match = EXC_LINE.search(text)
                if match:
                    return f'{step}: {match.group(1)}' if step else match.group(1)
                if '##[error]' in text:
                    message = text.split('##[error]', 1)[1].strip()
                    if 'Process completed with exit code' in message:
                        generic = generic or (f'{step}: {message}' if step else message)
                    else:
                        return f'{step}: {message}' if step else message
        except Exception:
            unavailable = True
        try:
            check_id = job['check_run_url'].rsplit('/', 1)[-1]
            for page in range(1, 11):
                annotations = api.get(f'check-runs/{check_id}/annotations?per_page=100&page={page}')
                for annotation in annotations:
                    if annotation.get('annotation_level') == 'failure':
                        return annotation['message']
                if len(annotations) < 100:
                    break
        except Exception:
            unavailable = True
    if generic:
        return generic
    return '无法读取失败日志/注解，请查看 runUrl' if unavailable else None


def hp_collection_status(api, run):
    """Read the run's explicit collector outcome, not GitHub's exit-zero status."""
    for job in api.pages(f"actions/runs/{run['id']}/jobs?filter=latest", 'jobs'):
        if job['name'] != 'collect':
            continue
        log = api.get(f"actions/jobs/{job['id']}/logs", raw=True).decode('utf-8', errors='replace')
        for line in reversed(log.splitlines()):
            marker = 'GOODSDEX_SOURCE_STATUS='
            if marker in line:
                payload = json.loads(line.split(marker, 1)[1])
                if payload['conclusion'] not in ('success', 'degraded', 'failure'):
                    raise RuntimeError('Invalid HP collector outcome')
                return payload
    return {'conclusion': 'success', 'error': None}  # legacy successful runs


def reusable_publish(api):
    """Reusable workflow runs live under callers; use the actual publish job."""
    for run in api.pages('actions/runs?exclude_pull_requests=true', 'workflow_runs'):
        if not any('/.github/workflows/publish-release.yml@' in w['path']
                   for w in run.get('referenced_workflows', [])):
            continue
        jobs = [j for j in api.pages(f"actions/runs/{run['id']}/jobs?filter=latest", 'jobs')
                if j['name'] == 'publish / publish']
        if jobs and jobs[0].get('conclusion') != 'skipped':
            job = jobs[0]
            return dict(run, status=job['status'], conclusion=job['conclusion'],
                        run_started_at=job.get('started_at'), updated_at=job.get('completed_at')), jobs
    return None, []


def mark_stale(row, now):
    interval = row['expectedIntervalMinutes']
    if interval is None:
        return
    if not row['lastSuccessAt']:
        row.update(stale=True, staleReason=f'无可确认的成功运行（预期每 {interval} 分钟）')
        return
    hours = (now - stamp(row['lastSuccessAt'])).total_seconds() / 3600
    if hours * 60 > interval * 2:
        row.update(stale=True, staleReason=f'已 {hours:.1f} 小时无成功运行（预期每 {interval} 分钟）')


def generate(repository, token, now=None, api=None):
    now = now or datetime.now(timezone.utc)
    api = api or GitHub(repository, token)
    rows = []
    for source, interval in SOURCES:
        row = dict(sourceId=source, workflow=f'.github/workflows/{source}.yml',
                   expectedIntervalMinutes=interval, lastAttemptAt=None, lastSuccessAt=None,
                   conclusion='unknown', runUrl=None, error=None, stale=False, staleReason=None)
        try:
            if not token:
                raise RuntimeError('缺少 GITHUB_TOKEN')
            path = f'actions/workflows/{source}.yml/runs?per_page=1'
            runs = api.get(path)['workflow_runs']
            jobs = None
            latest = runs[0] if runs else None
            if source == 'publish-release' and latest is None:
                latest, jobs = reusable_publish(api)
            if latest:
                row.update(lastAttemptAt=latest.get('run_started_at') or latest['created_at'],
                           conclusion=conclusion(latest), runUrl=latest['html_url'])
                if interval is not None:
                    successful = api.get(path + '&status=success')['workflow_runs']
                    if source == 'refresh-hp':
                        if row['conclusion'] == 'success':
                            outcome = hp_collection_status(api, latest)
                            row.update(conclusion=outcome['conclusion'], error=outcome.get('error'))
                        # An exit-zero degraded run must never advance lastSuccessAt.
                        for candidate in api.pages(f'actions/workflows/{source}.yml/runs?status=success', 'workflow_runs'):
                            if hp_collection_status(api, candidate)['conclusion'] == 'success':
                                row['lastSuccessAt'] = candidate['updated_at']
                                break
                    elif successful:
                        row['lastSuccessAt'] = successful[0]['updated_at']
                elif row['conclusion'] == 'success':
                    row['lastSuccessAt'] = latest['updated_at']
                if row['conclusion'] == 'failure':
                    try:
                        row['error'] = first_error(api, latest, jobs)
                    except Exception:
                        row['error'] = '无法读取失败日志/注解，请查看 runUrl'
            else:
                row['error'] = 'GitHub 未找到运行记录'
        except Exception as exc:
            row.update(conclusion='unknown', error=str(exc) if isinstance(exc, RuntimeError)
                       else f'GitHub 状态读取失败（{type(exc).__name__}）')
        if row['error']:
            row['error'] = redact(row['error'], token)
        mark_stale(row, now)
        rows.append(row)
    return dict(generatedAt=now.isoformat(timespec='seconds').replace('+00:00', 'Z'), sources=rows)


def write_status(public, payload):
    public.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(payload, ensure_ascii=False, indent=2) + '\n').encode()
    (public / 'sources-status.json').write_bytes(raw)
    meta_path = public / 'meta.json'
    # Status-only publication preserves all existing goods/meta semantics and bytes.
    if meta_path.exists():
        meta = json.loads(meta_path.read_bytes())
        meta.setdefault('files', {})['sources-status.json'] = dict(
            sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw), count=len(payload['sources']))
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, separators=(',', ':')) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--public', type=Path, required=True)
    parser.add_argument('--repository', default=os.environ.get('GITHUB_REPOSITORY'))
    args = parser.parse_args()
    token = os.environ.get('GITHUB_TOKEN', '').strip()
    if token and not args.repository:
        parser.error('--repository or GITHUB_REPOSITORY is required with GITHUB_TOKEN')
    write_status(args.public, generate(args.repository or '', token))
