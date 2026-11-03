"""Staging-only full catalog experiment; production writers are never called."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
import re
import signal
import sys

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
sys.path[:0] = [str(REPO / 'src'), str(REPO / 'scripts')]
import release_family_llm as runner
BRANDS = ('小米', '大疆', '惠普', '富士', 'Apple', '比亚迪', '小米汽车')
write = runner.write

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def freeze():
    assert not (ROOT / 'families.json').exists(), 'Plan already frozen'
    rows = json.loads((ROOT / 'baseline-goods.json').read_text())
    by = {r['id']: r for r in rows}
    families = {}
    for r in rows:
        brand = r.get('brand') or ('小米' if r['id'].startswith('CN:mi_cn:') else 'UNKNOWN')
        assert brand in BRANDS, (r['id'], brand)
        model = runner.family_model(r, by)
        category = r.get('category') or '未分类'
        key = brand + '|' + category + '|' + re.sub(r'\s+', '', model).lower()
        f = families.setdefault(key, dict(family=key, brand=brand, category=category, model=model, variants=[]))
        f['variants'].append(dict(id=r['id'], name=r['name']))
    all_fs = sorted(families.values(), key=lambda f:f['family'])
    skipped, pending = [], []
    for f in all_fs:
        official = [v['id'] for v in f['variants'] if by[v['id']].get('release', {}).get('source') == 'official' and by[v['id']]['release'].get('date')]
        if official:
            skipped.append({**f, 'official_ids': official, 'status': 'skipped_official'})
        else:
            pending.append(f)
    protected = [REPO/'public/goods.json', REPO/'_data/public/goods.json', *[REPO/p for p in ['data/official/release-dates.json','data/llm/release-dates.json','data/llm/release-crosschecks.json']]]
    write(ROOT/'protected-before.json', {str(p.relative_to(REPO)):sha(p) for p in protected})
    plan = dict(schema=1, created_at=runner.now(), rows=len(rows), total_families=len(all_fs), skipped_official=len(skipped), run_families=len(pending), initial_requests=len(pending), maximum_requests_with_retries=len(pending)*5, concurrency=6, qps=4, consecutive_429=3, retries=4, max_tokens=4096, estimated_wall_seconds=len(pending)*38.327/100, baseline_date_rows=sum(bool(r.get('release',{}).get('date')) for r in rows), baseline_sha256=sha(ROOT/'baseline-goods.json'), baseline_origin='Read-only apply_release_dates(_data/public/goods.json) with current committed official/LLM/crosscheck inputs; API fetch attempted separately. No production files written.', grouping='Existing family_model over ALL rows, seven brands, brand/category/normalized model key; any member with an official date skips the whole family. HP CPU/GPU retained. body_id inherited. Existing third_party and llm dates do not skip.', brands={b:dict(total=sum(f['brand']==b for f in all_fs),official=sum(f['brand']==b for f in skipped),run=sum(f['brand']==b for f in pending)) for b in BRANDS})
    write(ROOT/'all-families.json',all_fs);write(ROOT/'official-skipped.json',skipped);write(ROOT/'families.json',pending);write(ROOT/'plan.json',plan)
    print(json.dumps(plan,ensure_ascii=False,indent=2))

def assemble():
    fs=json.loads((ROOT/'families.json').read_text());rows=json.loads((ROOT/'baseline-goods.json').read_text());plan=json.loads((ROOT/'plan.json').read_text())
    outcomes=[];cost=Counter();models=Counter();new_ids=set()
    for f in fs:
        key=hashlib.sha256(f['family'].encode()).hexdigest()[:24];p=ROOT/'responses'/f'{key}.json'
        o=json.loads(p.read_text()) if p.exists() else {};response=o.get('response') or {};attempts=o.get('attempts',[])
        cost['requests']+=len(attempts);cost['http_429']+=sum(a.get('http_status')==429 for a in attempts)
        cost['backoff_scheduled_seconds']+=sum(a.get('backoff_seconds',0) for a in attempts)
        cost['backoff_elapsed_seconds']+=sum(a.get('backoff_elapsed_seconds',0) for a in attempts)
        for a in attempts:
            for k in ['prompt_tokens','completion_tokens','total_tokens']:
                cost[k]+=(a.get('usage') or {}).get(k,0)
        out={**f,'requested':bool(attempts),'response_file':str(p.relative_to(ROOT)),'result':'pending','success_return':False,'actual_model':response.get('model')}
        if attempts and not response:
            state_path=ROOT/'states'/f'{key}.json'
            state=json.loads(state_path.read_text()) if state_path.exists() else {}
            out['result']='request_failed' if state.get('status')=='failed' else 'in_flight'
        if response:
            model=response.get('model');models[str(model)]+=1
            try:
                content=response['choices'][0]['message']['content'];out['success_return']=bool(content)
                content=re.sub(r'^```(?:json)?\s*|\s*```$','',content.strip())
                value=json.loads(content);assert isinstance(value,dict)
                out['proposal']=value
                assert 'date' in value, 'missing date key'
                if value['date'] is None:
                    out['result']='abstention'
                elif isinstance(value['date'],str) and re.fullmatch(r'(?:19|20)\d{2}-(?:0[1-9]|1[0-2])',value['date']):
                    out['result']='date';e=value.get('evidence');out['has_evidence']=isinstance(e,dict) and bool(e.get('url') or e.get('quote'))
                    new_ids.update(v['id'] for v in f['variants'])
                else:out['result']='invalid_format'
            except Exception as exc:out.update(result='invalid_format',parse_error=str(exc))
        outcomes.append(out)
    before={r['id'] for r in rows if r.get('release',{}).get('date')}
    baseline_count=sum(bool(r.get('release',{}).get('date')) for r in rows)
    hypothetical_count=sum(bool(r.get('release',{}).get('date')) or r['id'] in new_ids for r in rows)
    sessions=[json.loads(p.read_text()) for p in (ROOT/'sessions').glob('*.json')]
    sessions=[s for s in sessions if any(r != 'already_sent' for r in s.get('results',[]))]
    summary=dict(total_families=plan['total_families'],skipped_official=plan['skipped_official'],planned_run_families=len(fs),actually_requested=sum(o['requested'] for o in outcomes),successful_returns=sum(o['success_return'] for o in outcomes),results=dict(Counter(o['result'] for o in outcomes)),actual_response_models=dict(models),cost=dict(cost),wall_seconds=(max(runner.datetime.fromisoformat(s['finished_at']).timestamp() for s in sessions)-min(runner.datetime.fromisoformat(s['started_at']).timestamp() for s in sessions)) if sessions else 0,active_session_seconds=sum(s['elapsed_seconds'] for s in sessions),sessions=len(sessions),circuit_events=len(list((ROOT/'circuit-history').glob('*.json')))+int((ROOT/'circuit.json').exists()),baseline_rows=baseline_count,total_rows=len(rows),candidate_new_rows=hypothetical_count-baseline_count,hypothetical_date_rows=hypothetical_count,brands={b:dict(total=plan['brands'][b]['total'],official=plan['brands'][b]['official'],planned=plan['brands'][b]['run'],requested=sum(o['brand']==b and o['requested'] for o in outcomes),success=sum(o['brand']==b and o['success_return'] for o in outcomes),**dict(Counter(o['result'] for o in outcomes if o['brand']==b))) for b in BRANDS})
    summary['date_without_evidence']=dict(Counter(o['brand'] for o in outcomes if o['result']=='date' and not o['has_evidence']))
    summary['date_with_abstention_reason']=dict(Counter(o['brand'] for o in outcomes if o['result']=='date' and o.get('proposal',{}).get('abstention_reason')))
    write(ROOT/'outcomes.json',outcomes);write(ROOT/'summary.json',summary)
    queue=json.loads((ROOT/'review-queue.json').read_text()) if (ROOT/'review-queue.json').exists() else {}
    for b in BRANDS:
        if b in queue or any(o['result'] in ('pending','in_flight') for o in outcomes if o['brand']==b):
            continue
        candidates=[o for o in outcomes if o['brand']==b and o['result']=='date']
        chosen=random.Random(20261103).sample(candidates,min(10,len(candidates)))
        rest=[o for o in outcomes if o['brand']==b and o not in chosen]
        if len(chosen)<10:chosen+=random.Random(20261103).sample(rest,min(10-len(chosen),len(rest)))
        queue[b]=chosen
    write(ROOT/'review-queue.json',queue)
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['freeze','run','assemble']);ap.add_argument('--resume-after-circuit',action='store_true');args=ap.parse_args()
    if args.action=='freeze':freeze()
    elif args.action=='assemble':assemble()
    else:
        signal.signal(signal.SIGINT,lambda *_:runner.STOP.set());signal.signal(signal.SIGTERM,lambda *_:runner.STOP.set())
        fs=json.loads((ROOT/'families.json').read_text())
        assert len(fs)==json.loads((ROOT/'plan.json').read_text())['run_families']
        runner.run_batch(fs,ROOT,runner.Config(),args.resume_after_circuit)
