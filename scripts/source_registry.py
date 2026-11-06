"""Runtime registry: Actions outcomes plus immutable per-run collection metrics."""
import argparse
from datetime import datetime, timezone
import io
import json
import os
from pathlib import Path
import zipfile
from generate_sources_status import GitHub, conclusion, first_error, redact, stamp

DEFAULT = Path(__file__).resolve().parents[1]/'data/official/sources-registry.json'


def metrics(before, after):
    from goodsdex.release_coverage import effective
    old = {r['id'] for r in before}
    new = {r['id']:r for r in after if r['id'] not in old}
    dated = sum(bool(effective(r)) for r in new.values())
    return dict(items_found=len({r['id'] for r in after}), items_new=len(new),
                new_with_date=dated, new_date_ratio=dated/len(new) if new else None,
                additions=[dict(id=r['id'], name=r.get('name'), source=r.get('discovered_by') or r.get('source'),
                                has_date=bool(effective(r)), reason=None if effective(r) else
                                r.get('release_missing_reason') or '来源未提供可核验的产品发布日期') for r in new.values()])


def reconcile(row, runs, now):
    row = dict(row)
    if not runs:
        return row
    latest = runs[0]
    row.update(last_run=latest.get('run_started_at') or latest['created_at'],
               run_id=latest['id'], run_url=latest['html_url'], status=conclusion(latest))
    completed = [r for r in runs if r['status']=='completed']
    failures=0
    for r in completed:
        if conclusion(r)=='success': break
        failures+=1
    row['consecutive_failures']=failures
    success=next((r for r in completed if conclusion(r)=='success'),None)
    if success: row['last_success']=success['updated_at']
    row['alert']=failures>=2
    row['stale']=(now-stamp(row['last_run'])).total_seconds()>row['period_minutes']*90
    if row['status']=='success': row['failure_reason']=None
    return row


def refresh(root, api, now=None):
    now=now or datetime.now(timezone.utc)
    target=root/'data/official/sources-registry.json'
    definitions=json.loads(DEFAULT.read_text())
    saved={r['source']:r for r in json.loads(target.read_text())} if target.exists() else {}
    previous=[dict(r,**{k:v for k,v in saved.get(r['source'],{}).items() if k not in ('workflow','schedule','period_minutes','scope','note')}) for r in definitions]
    rows=[]
    for row in previous:
        try:
            runs=api.get(f"actions/workflows/{row['workflow']}/runs?per_page=100")['workflow_runs']
            updated=reconcile(row,runs,now)
            updated.pop('registry_error',None)
            if runs and updated['status']=='failure':
                updated['failure_reason']=redact(first_error(api,runs[0]),api.token)
            if runs and runs[0]['status']=='completed' and row.get('metrics_run_id')!=runs[0]['id']:
                artifacts=api.get(f"actions/runs/{runs[0]['id']}/artifacts")['artifacts']
                artifact=next((a for a in artifacts if a['name']=='source-metrics' and not a['expired']),None)
                if artifact:
                    raw=api.get(f"actions/artifacts/{artifact['id']}/zip",raw=True)
                    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                        result=json.loads(archive.read('source-metrics.json'))
                        # Failed publication candidates are never reported as additions to the library.
                        if updated['status']!='success':
                            result.update(items_new=0,new_with_date=0,new_date_ratio=None,additions=[])
                        updated.update(result)
                        batches=list(row.get('batches',[]))
                        if result.get('items_new') and not any(b['run_id']==runs[0]['id'] for b in batches):
                            batches.insert(0,dict(result,run_id=runs[0]['id'],published_at=runs[0]['updated_at']))
                        updated['batches']=batches[:50]
                    updated['metrics_run_id']=runs[0]['id']
            rows.append(updated)
        except Exception as exc:
            # API errors never overwrite a real collector outcome or reset its streak.
            rows.append(dict(row, registry_error=redact(str(exc),api.token)))
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    public=root/'public';public.mkdir(parents=True,exist_ok=True)
    (public/'sources-registry.json').write_text(target.read_text())
    meta_path=public/'meta.json'
    if meta_path.exists():
        import hashlib
        meta=json.loads(meta_path.read_text());raw=(public/'sources-registry.json').read_bytes()
        meta.setdefault('files',{})['sources-registry.json']=dict(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),count=len(rows))
        meta_path.write_text(json.dumps(meta,ensure_ascii=False,separators=(',',':'))+'\n')
    return rows

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args()
    refresh(a.root,GitHub(os.environ['GITHUB_REPOSITORY'],os.environ['GITHUB_TOKEN']))
