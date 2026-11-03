"""Verify the real workflow outcomes and the published status manifest (read-only)."""
from pathlib import Path
import argparse, hashlib, json, subprocess
from urllib.request import urlopen
parser=argparse.ArgumentParser()
parser.add_argument('--previous-goods', type=Path)
args=parser.parse_args()
ROOT=Path(__file__).resolve().parent
REPO='null-object-0000/goodsdex'
def gh(*args): return subprocess.check_output(['gh',*args])
runs={}
for name,run_id in [('cars',41658518208),('hp',41655447640)]:
    d=json.loads(gh('run','view',str(run_id),'--json','databaseId,status,conclusion,headSha,url,jobs'))
    assert d['status']=='completed' and d['conclusion']=='success',d
    assert all(j['conclusion']=='success' for j in d['jobs']),d
    runs[name]=d
    (ROOT/f'{name}-run.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
ref=json.loads(gh('api',f'repos/{REPO}/git/ref/heads/data'))['object']['sha']
def content(name):
    return gh('api',f'repos/{REPO}/contents/public/{name}?ref={ref}','-H','Accept: application/vnd.github.raw+json')
raw=content('sources-status.json');status=json.loads(raw);meta=json.loads(content('meta.json'))
oss_url='https://spend-good.oss-cn-shanghai.aliyuncs.com/data/public/sources-status.json'
with urlopen(oss_url,timeout=40) as r: oss=r.read();assert r.status==200
assert raw==oss,'OSS status differs from pinned data branch'
descriptor=meta['files']['sources-status.json']
assert descriptor['sha256']==hashlib.sha256(raw).hexdigest()
assert descriptor['bytes']==len(raw)
for name in ['hp','cars']:
    row=next(r for r in status['sources'] if r['sourceId']=='refresh-'+name)
    assert row['conclusion']=='success' and row['error'] is None,row
    assert row['runUrl']==runs[name]['url'],row
    assert row['lastSuccessAt'],row
(ROOT/'sources-status.json').write_bytes(raw)
(ROOT/'oss-sources-status.json').write_bytes(oss)
cars=json.loads((ROOT/'cars-final-audit.json').read_text())
hp=json.loads((ROOT/'hp-final-audit.json').read_text())
assert cars['count'] > 0 and cars['count'] + len(cars['skipped']) == 43
assert hp['count']==209 and hp['error_count']==0 and hp['with_image']==hp['with_price']==209
probes=json.loads((ROOT/'actions-probes.json').read_text())
for mode in ['browser-ua','delay-10s','serial-concurrency-1']:
    results=[r for r in probes if r['mode']==mode]
    assert len(results)==3 and all(r['status']==200 for r in results)
report=dict(dataCommit=ref,ossUrl=oss_url,statusSha256=descriptor['sha256'],
            workflows={k:v['databaseId'] for k,v in runs.items()},carsCount=cars['count'],
            hpCount=hp['count'],hpSourceConclusion='success',hpSourceError=None,
            hpProbeStatuses=[r['status'] for r in probes if r['mode']!='alternative'])
if args.previous_goods:
    from sys import path
    path.insert(0, str(ROOT.parents[1] / 'src'))
    from goodsdex.car_structure import expand_sources
    from goodsdex.cars import is_car
    before=json.loads(args.previous_goods.read_text())
    with urlopen(oss_url.replace('sources-status.json','goods.json'),timeout=40) as response:
        current=json.loads(response.read())
    assert [r for r in before if not is_car(r)] == [r for r in current if not is_car(r)]
    old={r['id']:r for r in expand_sources(before)}
    new={r['id']:r for r in expand_sources(current)}
    for skip in cars['skipped']:
        assert old[skip['id']]==new[skip['id']],skip
    report.update(nonCarObjectsUnchanged=True, skippedCarObjectsPreserved=True,
                  publicCount=len(current), hpRecordsRetained=sum(r.get('source')=='hp_cn' for r in current),
                  baselineSha256=hashlib.sha256(args.previous_goods.read_bytes()).hexdigest())
(ROOT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
