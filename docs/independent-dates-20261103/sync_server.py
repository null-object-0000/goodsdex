"""Ask the existing deployed synchronizer to read the published OSS generation."""
from pathlib import Path
import shlex
import subprocess

code = """import {loadConfig} from './src/config.mjs';
import {createSync} from './src/sync.mjs';
const result = await createSync({config:loadConfig()}).primeCatalog();
console.log(JSON.stringify({ok:result.ok,count:result.state?.count,errors:result.errors}));
if(!result.ok)process.exitCode=1;
"""
command = 'docker exec spendgood-api node --input-type=module -e ' + shlex.quote(code)
if __name__=='__main__':
    p=subprocess.run(['workbench','exec','--instance-id','i-uf6cdkz0c5rl80iaws7h','--timeout','180','--command',command],text=True,capture_output=True)
    (Path(__file__).resolve().parent/'api-sync.log').write_text(p.stdout+p.stderr)
    print(p.stdout+p.stderr,end='')
    raise SystemExit(p.returncode)
