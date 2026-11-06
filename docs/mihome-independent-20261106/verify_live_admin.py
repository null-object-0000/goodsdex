import subprocess,shlex
from pathlib import Path
js='''
import { loadConfig } from './src/config.mjs';
import { createSync } from './src/sync.mjs';
const config=loadConfig();
const sync=createSync({config,log:()=>{}});
const result=await sync.runOnce();
if(!result.ok)throw Error('Catalog sync failed: '+JSON.stringify(result.errors));
const ids=['16735','19555','19700','20558','20559','20760','20958','21002','21108','24141','3488','3807','4802','5005','5008'];
const samples=[];
for(const id of ids){
 const key='CN:mi_cn:product:'+id;
 const response=await fetch('http://127.0.0.1:'+config.port+'/admin/api/goods/'+encodeURIComponent(key)+'/raw',{headers:{'x-admin-token':process.env.ADMIN_TOKEN}});
 if(!response.ok)throw Error(key+' HTTP '+response.status);
 const data=await response.json();const row=data.effective;
 if(!row?.name_mihome || !row?.catalog_display)throw Error(key+' independent source missing');
 const icon=!!row.image_mihome&&!row.image;
 if(icon && (!row.image_mihome.url.startsWith('https://') || row.image_mihome.url.includes('?')))throw Error('Device icon not publicly renderable');
 samples.push({id:key,name:row.name,name_mihome:row.name_mihome,name_source:row.name_source,category:row.category,category_mihome:row.category_mihome,image:row.image,image_mihome:icon?row.image_mihome:null,catalog_display:row.catalog_display});
}
console.log(JSON.stringify({sync_ok:result.ok,samples}));
process.exit(0);
'''
cmd='docker exec spendgood-api node --input-type=module -e '+shlex.quote(js)
r=subprocess.run(['workbench','exec','--instance-id','i-uf6cdkz0c5rl80iaws7h','--timeout','300','--command',cmd],capture_output=True,text=True)
Path('docs/mihome-independent-20261106/live-admin.log').write_text(r.stdout+r.stderr)
print(r.stdout);print('exit',r.returncode)
if r.returncode:raise SystemExit(r.returncode)
