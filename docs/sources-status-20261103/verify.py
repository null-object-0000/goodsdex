"""Verify a pinned data snapshot, OSS bytes, manifest and GitHub success timestamps."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
REPO = 'null-object-0000/goodsdex'

def api(path):
    return json.loads(subprocess.check_output(['gh', 'api', f'repos/{REPO}/{path}']))


def content(name, ref):
    result = api(f'contents/public/{name}?ref={ref}')
    return base64.b64decode(result['content'])


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


ref = api('branches/data')['commit']['sha']
data = content('sources-status.json', ref)
meta = json.loads(content('meta.json', ref))
oss_path = ROOT / 'oss-sources-status.json'
http = subprocess.check_output(['curl', '--fail', '--silent', '--show-error',
    '--max-time', '60', '--output', str(oss_path), '--write-out', '%{http_code}',
    'https://spend-good.oss-cn-shanghai.aliyuncs.com/data/public/sources-status.json'], text=True)
assert http == '200', http
oss = oss_path.read_bytes()
assert oss == data, 'OSS/data snapshot differs; rerun after the publication lock is released'
payload = json.loads(data)
assert len(payload['sources']) == 5
assert {r['sourceId'] for r in payload['sources']} == {
    'refresh-prices', 'refresh-apple', 'refresh-hp', 'refresh-cars', 'publish-release'}
assert meta['files']['sources-status.json']['sha256'] == digest(data)
assert meta['files']['sources-status.json']['bytes'] == len(data)
evidence = []
for row in payload['sources']:
    run_id = row['runUrl'].rsplit('/', 1)[-1]
    latest = api(f'actions/runs/{run_id}')
    proof = dict(sourceId=row['sourceId'], lastAttemptRunId=int(run_id),
                 lastAttemptAt=row['lastAttemptAt'], lastSuccessAt=row['lastSuccessAt'],
                 conclusion=row['conclusion'], latestRunUrl=row['runUrl'])
    if row['sourceId'] == 'publish-release':
        jobs = api(f'actions/runs/{run_id}/jobs?filter=latest&per_page=100')['jobs']
        job = next(j for j in jobs if j['name'] == 'publish / publish')
        assert job['started_at'] == row['lastAttemptAt']
        proof.update(publishJobId=job['id'], githubJobConclusion=job['conclusion'],
                     githubJobCompletedAt=job['completed_at'])
        if row['lastSuccessAt']:
            assert job['conclusion'] == 'success'
            assert job['completed_at'] == row['lastSuccessAt']
            proof['lastSuccessRunId'] = int(run_id)
    else:
        assert latest['run_started_at'] == row['lastAttemptAt']
        successes = api(f"actions/workflows/{row['sourceId']}.yml/runs?per_page=100&status=success")['workflow_runs']
        success = next(r for r in successes if r['updated_at'] == row['lastSuccessAt'])
        proof.update(lastSuccessRunId=success['id'], githubUpdatedAt=success['updated_at'],
                     githubConclusion=success['conclusion'], lastSuccessRunUrl=success['html_url'])
        assert success['conclusion'] == 'success'
    evidence.append(proof)
(ROOT / 'sources-status.json').write_bytes(data)
(ROOT / 'github-run-comparison.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')
commit = api(f'commits/{ref}')
changed = [f['filename'] for f in commit['files']]
assert set(changed) == {'public/meta.json', 'public/sources-status.json'}
previous_meta = json.loads(content('meta.json', commit['parents'][0]['sha']))
current_meta = json.loads(json.dumps(meta))
for document in (previous_meta, current_meta):
    document['files'].pop('sources-status.json', None)
assert previous_meta == current_meta
verification = dict(dataCommit=ref, generatedAt=payload['generatedAt'], sourceCount=5,
    ossUrl='https://spend-good.oss-cn-shanghai.aliyuncs.com/data/public/sources-status.json',
    httpStatus=int(http), dataSha256=digest(data), ossSha256=digest(oss),
    manifestSha256=meta['files']['sources-status.json']['sha256'], githubTimestampsMatch=True,
    statusOnlyChangedFiles=changed, otherMetaFieldsUnchanged=True)
(ROOT / 'verification.json').write_text(json.dumps(verification, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(verification, ensure_ascii=False, indent=2))
print(json.dumps(evidence, ensure_ascii=False, indent=2))
