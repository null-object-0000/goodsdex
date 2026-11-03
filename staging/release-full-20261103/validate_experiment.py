"""Read-only validation of experiment accounting, scope and production invariants."""
import hashlib
import json
from pathlib import Path
from collections import Counter
P=Path(__file__).resolve().parent
R=P.parents[1]
def read(name):return json.loads((P/name).read_text())
def key(f):return hashlib.sha256(f['family'].encode()).hexdigest()[:24]
def validate(complete=True):
    plan=read('plan.json');fs=read('families.json');all_fs=read('all-families.json');skip=read('official-skipped.json');rows=read('baseline-goods.json');by={r['id']:r for r in rows}
    assert len(all_fs)==len(fs)+len(skip)==plan['total_families']
    assert not ({f['family'] for f in fs}&{f['family'] for f in skip})
    assert sum(len(f['variants']) for f in all_fs)==len(rows)==3968
    assert len({f['family'] for f in all_fs})==len(all_fs)
    assert hashlib.sha256((P/'baseline-goods.json').read_bytes()).hexdigest()==plan['baseline_sha256']
    for f in fs:
        assert not any(by[v['id']].get('release',{}).get('source')=='official' and by[v['id']]['release'].get('date') for v in f['variants'])
    for f in skip:
        assert f['official_ids'] and not (P/'sent'/f'{key(f)}.json').exists()
    protected=read('protected-before.json')
    after={path:hashlib.sha256((R/path).read_bytes()).hexdigest() for path in protected}
    assert after==protected, 'Protected production input/output changed'
    summary=read('summary.json');outs=read('outcomes.json')
    assert summary['results']==dict(Counter(o['result'] for o in outs))
    assert sum(summary['results'].values())==len(fs)
    assert summary['actually_requested']==sum(o['requested'] for o in outs)
    assert summary['successful_returns']==sum(o['success_return'] for o in outs)
    assert summary['successful_returns']==sum(summary['results'].get(k,0) for k in ['date','abstention','invalid_format'])
    assert summary['baseline_rows']==694
    dates={v['id'] for o in outs if o['result']=='date' for v in o['variants']}
    expected=sum(bool(r.get('release',{}).get('date')) or r['id'] in dates for r in rows)
    assert summary['hypothetical_date_rows']==expected
    assert summary['candidate_new_rows']==expected-694
    attempts=[]
    for f in fs:
        p=P/'responses'/f'{key(f)}.json'
        if not p.exists():continue
        raw=json.loads(p.read_text());attempts+=raw['attempts']
        if raw.get('response'):
            assert raw['captured_at'] and raw['response'].get('model')
            assert raw['model']==raw['response']['model']
            assert raw.get('usage')==raw['response'].get('usage')
            assert json.loads(raw['raw_response'])==raw['response']
    assert len(attempts)==summary['cost']['requests']
    from datetime import datetime
    starts=sorted(datetime.fromisoformat(a['started_at']).timestamp() for a in attempts)
    minimum=min((b-a for a,b in zip(starts,starts[1:])),default=0)
    # Marker is written immediately after global dispatch. fsync jitter permits 20ms tolerance.
    assert minimum>=.23, minimum
    events=[]
    for a in attempts:
        if a.get('elapsed_seconds') is None:continue
        start=datetime.fromisoformat(a['started_at']).timestamp()
        events.extend([(start,1),(start+a['elapsed_seconds'],-1)])
    active=peak=0
    for _,delta in sorted(events):
        active+=delta;peak=max(peak,active)
    assert peak<=6, peak
    if complete:
        assert not any(o['result'] in ('pending','in_flight') for o in outs)
        assert len(fs)==summary['actually_requested']
        assert plan['total_families']==plan['skipped_official']+summary['actually_requested']
        queue=read('review-queue.json');reviews=read('reviews.json');rb={v['family']:v for v in reviews}
        assert set(queue)==set(plan['brands'])
        for brand,items in queue.items():
            assert len(items)==min(10,plan['brands'][brand]['run'])
            assert all(o['family'] in rb for o in items), (brand,'missing reviews')
            for o in items:
                v=rb[o['family']]
                assert v['llm_date']==o.get('proposal',{}).get('date')
                if v['correct'] is not None:
                    assert v['verification_url'] and v['correct_date']
                    assert v['correct']==(v['llm_date']==v['correct_date'])
    result=dict(complete=complete,checks='denominators, official exclusions, production hashes, raw response/model/usage, exact row coverage, global pacing, frozen review completeness',minimum_dispatch_gap_seconds=minimum,observed_max_inflight=peak,production_files_unchanged=True,protected_after=after)
    (P/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':validate()
