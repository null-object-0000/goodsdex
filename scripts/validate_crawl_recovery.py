"""Allow publication recovery only from a successful main-branch crawl's candidate."""
import json
import os
import re
from pathlib import Path

from generate_sources_status import GitHub


def validate(run, jobs, bundle, source_run_id, repository):
    if not re.fullmatch(r'[1-9][0-9]*', source_run_id):
        raise ValueError('Recovery run ID must be numeric')
    if (run.get('id') != int(source_run_id)
            or (run.get('repository') or {}).get('full_name') != repository
            or run.get('head_branch') != 'main'
            or run.get('path', '').split('@')[0] != '.github/workflows/crawl-all.yml'
            or run.get('event') not in ('schedule', 'workflow_dispatch')
            or run.get('status') != 'completed'
            or run.get('conclusion') != 'failure'):
        raise ValueError('Recovery requires a failed main-branch crawl-all run from this repository')
    if not any(j.get('name') == 'crawl' and j.get('status') == 'completed'
               and j.get('conclusion') == 'success' for j in jobs):
        raise ValueError('Recovery source did not complete collection successfully')
    if (bundle.get('schema') != 1 or bundle.get('scope') != 'all'
            or not isinstance(bundle.get('files'), dict)
            or not re.fullmatch(r'[0-9a-f]{40}', str(bundle.get('base', '')))):
        raise ValueError('Recovery artifact is not an all-scope publication candidate')


def main():
    run_id = os.environ['RECOVERY_RUN_ID']
    if not re.fullmatch(r'[1-9][0-9]*', run_id):
        raise ValueError('Recovery run ID must be numeric')
    repository = os.environ['GITHUB_REPOSITORY']
    api = GitHub(repository, os.environ['GITHUB_TOKEN'])
    run = api.get(f'actions/runs/{run_id}')
    jobs = list(api.pages(f'actions/runs/{run_id}/jobs', 'jobs'))
    candidate = Path(os.environ['RUNNER_TEMP']) / 'candidate/candidate.json'
    validate(run, jobs, json.loads(candidate.read_text()), run_id, repository)
    print(f'Validated saved candidate from crawl-all run {run_id}; all publication gates still apply')


if __name__ == '__main__':
    main()
