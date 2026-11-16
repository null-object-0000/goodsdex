"""Restore only evidence files from a validated successful collection, never product rows."""
import argparse
import os
from pathlib import Path
import re
import shutil
from generate_sources_status import GitHub


def validate_run(run_id, api, workflow='release-dates-daily.yml'):
    if not re.fullmatch(r'[0-9]+', str(run_id)):
        raise ValueError('Invalid collection run id')
    run = api.get(f'actions/runs/{run_id}')
    if (run.get('path', '').split('@')[0] != '.github/workflows/' + workflow
            or run.get('head_branch') != 'main'
            or run.get('event') not in ('schedule', 'workflow_dispatch')):
        raise ValueError('Evidence must originate from the main date collection workflow')
    jobs = api.get(f'actions/runs/{run_id}/jobs?per_page=100')['jobs']
    if not any(j['name'] == 'collect' and j['conclusion'] == 'success' for j in jobs):
        raise ValueError('Original date collection did not succeed')


def restore(source, root):
    source = Path(source).resolve(); root = Path(root).resolve(); planned = []
    for path in source.rglob('*'):
        if path.is_symlink():
            raise ValueError('Evidence links are not allowed')
        if not path.is_file():
            continue
        rel = path.relative_to(source); name = rel.as_posix()
        allowed = (name.startswith('docs/release-coverage/')
                   or (name.startswith('data/official/') and (rel.name.endswith('release-evidence.json') or rel.name == 'third_party_index.json'))
                   or (name.startswith('data/third-party/') and rel.name.startswith(('l5', 'l6'))))
        if not allowed:
            raise ValueError('Unexpected evidence path: ' + name)
        planned.append((path, root / rel))
    if not planned:
        raise ValueError('Empty evidence artifact')
    for path, target in planned:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    return len(planned)


if __name__ == '__main__':
    p = argparse.ArgumentParser(); mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--validate-run'); mode.add_argument('--from-directory', type=Path)
    p.add_argument('--workflow', choices=('release-dates-daily.yml','refresh-mihome-catalog.yml'), default='release-dates-daily.yml')
    args = p.parse_args()
    if args.validate_run:
        validate_run(args.validate_run, GitHub(os.environ['GITHUB_REPOSITORY'], os.environ['GITHUB_TOKEN']), args.workflow)
        print('Validated original successful collection')
    else:
        print('Restored', restore(args.from_directory, Path('.')), 'evidence files; product rows unchanged')
