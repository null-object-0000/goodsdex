"""Hourly fallback; query Actions immediately before dispatch, with a local lease."""
import argparse
from datetime import datetime,timezone
import fcntl
import json
from pathlib import Path
import subprocess
from generate_sources_status import stamp

def gh(*args):
    return subprocess.check_output(['gh',*args],text=True)

def check(rows, repo, state, dispatch=True):
    now=datetime.now(timezone.utc);leases=json.loads(state.read_text()) if state.exists() else {}
    for row in rows:
        workflow=row['workflow']
        try:
            runs=json.loads(gh('api',f'repos/{repo}/actions/workflows/{workflow}/runs?per_page=10'))['workflow_runs']
            if any(r['status']!='completed' for r in runs):
                print(workflow,'skip active/queued',flush=True);continue
            last=stamp(runs[0].get('run_started_at') or runs[0]['created_at']) if runs else None
            if last and (now-last).total_seconds()<=row['period_minutes']*90:
                print(workflow,'fresh',flush=True);continue
            if workflow in leases and (now-stamp(leases[workflow])).total_seconds()<3600:
                print(workflow,'skip dispatch lease',flush=True);continue
            print(now.isoformat(),workflow,'dispatch' if dispatch else 'would-dispatch',flush=True)
            if dispatch:
                gh('workflow','run',workflow,'--repo',repo)
                leases[workflow]=now.isoformat();state.write_text(json.dumps(leases))
        except subprocess.CalledProcessError as exc:
            print(workflow,'ERROR',exc.returncode,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--registry',type=Path,required=True);p.add_argument('--repo',default='null-object-0000/goodsdex');p.add_argument('--state',type=Path,required=True);p.add_argument('--dry-run',action='store_true');a=p.parse_args()
    a.state.parent.mkdir(parents=True,exist_ok=True)
    with a.state.with_suffix('.lock').open('w') as lock:
        try: fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError: raise SystemExit('watchdog already running')
        check(json.loads(a.registry.read_text()),a.repo,a.state,not a.dry_run)
