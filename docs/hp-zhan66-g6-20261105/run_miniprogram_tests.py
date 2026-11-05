"""Run every mini-program test file in a separate process to bound browser memory."""
import argparse,json,re,subprocess,time
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('project',type=Path);ap.add_argument('--node',default='node');ap.add_argument('--out',type=Path,default=Path(__file__).parent/'mini-test-files');args=ap.parse_args();root=args.project.resolve();args.out.mkdir(parents=True,exist_ok=True);results=[]
for file in sorted((root/'tests').glob('*.test.js')):
 start=time.time()
 try:
  r=subprocess.run([args.node,'--test',str(file)],cwd=root,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=150);code=r.returncode;body=r.stdout
 except subprocess.TimeoutExpired as e:code=124;body=e.stdout or b''
 (args.out/(file.name+'.log')).write_bytes(body)
 row=dict(file=file.name,exit_code=code,seconds=round(time.time()-start,2),counts={k:int(v) for k,v in re.findall(r'ℹ (tests|pass|fail|cancelled|skipped) (\d+)',body.decode(errors='replace'))})
 results.append(row);(args.out/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=1));print(json.dumps(row),flush=True)
raise SystemExit(any(r['exit_code'] for r in results))
