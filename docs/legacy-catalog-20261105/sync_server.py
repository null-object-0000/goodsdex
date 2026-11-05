"""Refresh the deployed catalog from the completed, verified OSS release."""
from pathlib import Path
import shlex,subprocess
CODE="""
import {createSync} from './src/sync.mjs';
import {loadConfig} from './src/config.mjs';
const result=await createSync({config:loadConfig()}).primeCatalog();
console.log(JSON.stringify({ok:result.ok,count:result.state?.count,succeeded:result.succeeded,errors:result.errors}));
if(!result.ok)process.exitCode=1;
"""
if __name__=='__main__':
    command='docker exec spendgood-api node --input-type=module -e '+shlex.quote(CODE)
    result=subprocess.run(['workbench','exec','--instance-id','i-uf6cdkz0c5rl80iaws7h','--timeout','180','--command',command],text=True,capture_output=True)
    Path(__file__).with_name('api-sync.log').write_text(result.stdout+result.stderr)
    print(result.stdout+result.stderr,end='')
    raise SystemExit(result.returncode)
