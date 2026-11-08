"""Saved candidates require trusted collection provenance, never an arbitrary artifact."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from validate_crawl_recovery import validate


def source():
    return (dict(id=123, repository={'full_name': 'owner/repo'}, head_branch='main',
                 path='.github/workflows/crawl-all.yml', event='workflow_dispatch',
                 status='completed', conclusion='failure'),
            [dict(name='crawl', status='completed', conclusion='success')],
            dict(schema=1, scope='all', base='a' * 40, files={},collector_mode='discovery'))


def test_saved_successful_collection_can_recover_publication():
    run, jobs, bundle = source()
    validate(run, jobs, bundle, '123', 'owner/repo')


def test_legacy_full_replacement_candidate_cannot_be_replayed():
    run,jobs,bundle=source();bundle.pop('collector_mode')
    with pytest.raises(ValueError,match='recollected'):validate(run,jobs,bundle,'123','owner/repo')
    run['event'] = 'schedule'
    validate(run, jobs, bundle, '123', 'owner/repo')


@pytest.mark.parametrize('change', [
    {'id': 999}, {'repository': {'full_name': 'other/repo'}},
    {'head_branch': 'feature'}, {'event': 'pull_request'},
    {'path': '.github/workflows/refresh-apple.yml'},
    {'status': 'in_progress'}, {'conclusion': 'success'}, {'conclusion': 'cancelled'},
])
def test_untrusted_or_unfinished_source_is_rejected(change):
    run, jobs, bundle = source()
    run.update(change)
    with pytest.raises(ValueError, match='main-branch crawl-all'):
        validate(run, jobs, bundle, '123', 'owner/repo')


@pytest.mark.parametrize('jobs', [[], [dict(name='crawl', status='completed', conclusion='failure')],
                                  [dict(name='recover', status='completed', conclusion='success')]])
def test_failed_or_recursive_collection_reuse_is_rejected(jobs):
    run, _, bundle = source()
    with pytest.raises(ValueError, match='complete collection successfully'):
        validate(run, jobs, bundle, '123', 'owner/repo')


@pytest.mark.parametrize('change', [{'schema': 2}, {'scope': 'apple'}, {'files': []}, {'base': 'invalid'}])
def test_incompatible_artifact_is_rejected(change):
    run, jobs, bundle = source()
    bundle.update(change)
    with pytest.raises(ValueError, match='all-scope publication candidate'):
        validate(run, jobs, bundle, '123', 'owner/repo')


@pytest.mark.parametrize('run_id', ['-1', '0', '123/../jobs', '123; echo unsafe'])
def test_run_id_cannot_inject_an_api_path(run_id):
    with pytest.raises(ValueError, match='numeric'):
        validate(*source(), run_id, 'owner/repo')
