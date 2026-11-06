"""Offline acceptance against the pinned 4,491-row data-branch publication.

Run from the repository root: PYTHONPATH=src python3 docs/carry-forward-20261106/verify.py
The source-scoped rebuild sample deliberately omits all unsourced rows, rather
than deleting just seven IDs from a source that the sample still covers.
"""
import contextlib
import gzip
import io
import json
import subprocess
from pathlib import Path

from goodsdex.supplements import DEFAULT_SUPPLEMENTS, merge


DATA_COMMIT = '9d7971f5505c3325f5d616199491ed8342cd7f69'
TARGETS = {'CN:mi_cn:product:' + suffix for suffix in
           '19228 19782 20071 20553 20568 24809 25073'.split()}


def run_merge(rebuilt, supplements, previous):
    with contextlib.redirect_stdout(io.StringIO()):
        return merge(rebuilt, supplements, previous)


def verify():
    blob = subprocess.check_output(['git', 'show', DATA_COMMIT + ':public/goods.json.gz'])
    previous = json.loads(gzip.decompress(blob))
    assert len(previous) == 4491
    supplements = json.loads(DEFAULT_SUPPLEMENTS.read_text())
    covered = {'apple_cn', 'apple_support', 'mi_cn'}
    rebuilt = [row for row in previous if row.get('source') in covered]
    assert {row.get('source') for row in rebuilt} == covered
    assert {row.get('source') for row in previous if row['id'] in TARGETS} == {None}
    result, audit = run_merge(rebuilt, supplements, previous)
    assert TARGETS <= set(audit['carried_ids'])
    assert not audit['missing_ids']
    assert not {row['id'] for row in previous} - {row['id'] for row in result}

    # Select an actually covered ID that supplements cannot independently restore.
    extra_ids = {row['id'] for row in supplements}
    lost = next(row['id'] for row in rebuilt
                if row['source'] == 'apple_cn' and row['id'] not in extra_ids)
    broken = [row for row in rebuilt if row['id'] != lost]
    assert {row.get('source') for row in broken} == covered
    try:
        run_merge(broken, supplements, previous)
    except ValueError as error:
        expected = f"Publication would drop 1 IDs: {sorted([lost])}"
        assert str(error) == expected, str(error)
        gate_error = str(error)
    else:
        raise AssertionError('Covered-source loss unexpectedly passed the gate')

    return dict(
        data_commit=DATA_COMMIT,
        sample='Previous rows restricted to apple_cn/apple_support/mi_cn; other sources omitted as whole classes',
        previous_count=len(previous), sample_rebuilt_count=len(rebuilt),
        result_count=len(result), carried_count=len(audit['carried_ids']),
        carried_sources=audit['carried_sources'],
        target_carried_ids=sorted(TARGETS & set(audit['carried_ids'])),
        target_carried_count=len(TARGETS & set(audit['carried_ids'])),
        missing_ids=audit['missing_ids'],
        covered_source_negative=dict(removed_id=lost, missing_count=1, gate_error=gate_error))


if __name__ == '__main__':
    report = verify()
    path = Path(__file__).with_name('acceptance.json')
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(path.read_text())
