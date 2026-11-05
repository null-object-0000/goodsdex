// Local QA server: uses actual API catalog + built React application against a full source snapshot.
import {mkdtemp,copyFile,writeFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {readFile} from 'node:fs/promises';
const repo=process.env.SPENDGOOD_REPO || '/home/nichangen/代码/self-code/spend-good';
const {createApp}=await import(repo+'/services/api/src/app.mjs');
const {createGoodsIndex}=await import(repo+'/services/api/src/goods.mjs');
const {openStore,createRepository}=await import(repo+'/services/api/src/store.mjs');
const {loadConfig}=await import(repo+'/services/api/src/config.mjs');
const source=process.argv[2]; if(!source)throw Error('Full goods.json snapshot argument required');
const dir=await mkdtemp(path.join(tmpdir(),'release-dashboard-'));
const rows=JSON.parse(await readFile(source));await copyFile(source,path.join(dir,'goods.json'));
await writeFile(path.join(dir,'meta.json'),JSON.stringify({count:rows.length}));
const db=openStore(path.join(dir,'test.db')),repoDb=createRepository(db);
const config=loadConfig({DATA_DIR:dir,ADMIN_PASSWORD_LOGIN:'1',ADMIN_TOKEN:'local-release-evidence',ADMIN_INSECURE_LOCAL:'1',ADMIN_DIST:repo+'/services/admin-pro/dist'});
const app=createApp({config,repo:repoDb,goodsIndex:createGoodsIndex(dir,[]),sync:{readState:async()=>({generatedAt:new Date().toISOString(),files:{'goods.json':{fetchedAt:Date.now()}}})},now:Date.now});
app.listen(18136,'127.0.0.1',()=>console.log('Local release QA ready on 18136; snapshot rows='+rows.length));
