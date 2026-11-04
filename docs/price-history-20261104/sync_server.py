"""Import published OSS snapshots with the deployed importer, then refresh catalog."""
from pathlib import Path
import json
import shlex
import subprocess

OUT = Path(__file__).resolve().parent
CODE = r'''
import {loadConfig} from './src/config.mjs';
import {openStore} from './src/store.mjs';
import {syncHistory,queryHistory} from './src/price-history.mjs';
import {createSync} from './src/sync.mjs';
const config=loadConfig();
const source=config.dataSources[0];
const indexRes=await fetch(`${source}/price-history/index.json`,{headers:{'cache-control':'no-cache'}});
if(!indexRes.ok) throw Error(`index HTTP ${indexRes.status}`);
const index=await indexRes.json();
const state={history:{months:Object.fromEntries(index.files.map(f=>[f.month,{validators:{}}]))}};
const db=openStore(config.dbPath);
try {
 await syncHistory({config,db,state,fetchImpl:fetch,now:()=>Date.now()});
 console.log(JSON.stringify({history:state.history,revision:index.revision,retentionEnabled:config.historyRetentionEnabled}));
 if(Object.values(state.history.months).some(m=>m.lastError)) throw Error('History import failed');
} finally {db.close();}
const catalog=await createSync({config}).primeCatalog();
console.log(JSON.stringify({ok:catalog.ok,count:catalog.state?.count,errors:catalog.errors}));
if(!catalog.ok)process.exitCode=1;
'''

if __name__ == '__main__':
    command = 'docker exec spendgood-api node --input-type=module -e ' + shlex.quote(CODE)
    result = subprocess.run(['workbench', 'exec', '--instance-id', 'i-uf6cdkz0c5rl80iaws7h',
                             '--timeout', '180', '--command', command], text=True, capture_output=True)
    (OUT / 'api-sync.log').write_text(result.stdout + result.stderr)
    print(result.stdout + result.stderr, end='')
    raise SystemExit(result.returncode)
