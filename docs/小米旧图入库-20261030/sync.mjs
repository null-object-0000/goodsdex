import {loadConfig} from '/app/src/config.mjs';
import {createSync} from '/app/src/sync.mjs';
const result=await createSync({config:loadConfig(),log:()=>{}}).primeCatalog();
console.log(JSON.stringify({ok:result.ok,count:result.state?.count,errors:result.errors}));
if(!result.ok)process.exit(1);
