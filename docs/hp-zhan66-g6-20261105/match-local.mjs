import {mkdtemp,readFile,writeFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const [apiRoot,goodsPath]=process.argv.slice(2);
const {createApp}=await import(pathToFileURL(path.resolve(apiRoot,'src/app.mjs')));
const dir=await mkdtemp(path.join(tmpdir(),'hp-full-match-'));
const goods=await readFile(goodsPath);
await writeFile(path.join(dir,'goods.json'),goods);
const app=createApp({config:{dataDir:dir},repo:{reconciliationCandidates:()=>[]},jdBrowser:{close:async()=>{}}});
await new Promise(r=>app.listen(0,'127.0.0.1',r));
try {
 const url=`http://127.0.0.1:${app.address().port}/api/goods/match?`+new URLSearchParams({name:'惠普（HP）战66 六代酷睿 15.6 英寸 i7-13代 32G 1T 2.5K 120Hz'});
 const response=await fetch(url);if(response.status!==200)throw Error('HTTP '+response.status);
 const result=await response.json();
 await writeFile(new URL('./match-after-local.json',import.meta.url),JSON.stringify(result,null,1)+'\n');
 if(result.match!==null||result.candidates.length!==2||result.candidates[1].part_number!=='7P2D5PC')throw Error('Unexpected HP match result');
 console.log(JSON.stringify(result,null,1));
} finally {await new Promise(r=>app.close(r));await rm(dir,{recursive:true,force:true});}
