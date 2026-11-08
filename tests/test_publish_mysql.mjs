import test from 'node:test';
import assert from 'node:assert/strict';
import {plan,hash,publishHistory,publish} from '../scripts/publish_mysql.mjs';
import {mkdtemp,writeFile,rm,mkdir} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
test('No-op publications transmit zero product records; canonical key order is stable',()=>{
  const row={id:'CN:mi_cn:1',name:'小米音箱',params:{颜色:'白色'}};
  assert.equal(hash(row),hash({params:{颜色:'白色'},name:'小米音箱',id:row.id}));
  assert.deepEqual(plan([row],{rows:[{id:row.id,sha256:hash(row),identity:{name:row.name}}]}),[]);
});
test('Preflight rejects contaminated identities before uploading any batches',()=>{
  const row={id:'CN:mi_cn:1',name:'太阳能摄像机'};
  assert.throws(()=>plan([row],{rows:[{id:row.id,sha256:'old',identity:{name:'小米音箱'}}]}),/Source identity changed/);
});

test('Image uploads start only after verified shards pass the source identity guard',async t=>{
  const root=await mkdtemp(path.join(tmpdir(),'mysql-images-'));t.after(()=>rm(root,{recursive:true,force:true}));await mkdir(path.join(root,'detail'));
  const row={id:'CN:mi_cn:1',name:'太阳能摄像机',image:'https://cdn.cnbj1.fds.api.mi-img.com/new.png'};
  const bytes=Buffer.from(JSON.stringify({[row.id]:row}));await writeFile(path.join(root,'detail/00.json'),bytes);
  await writeFile(path.join(root,'meta.json'),JSON.stringify({files:{'detail/00.json':{sha256:createHash('sha256').update(bytes).digest('hex'),bytes:bytes.length}}}));
  let images=0;const fetchImpl=async()=>({ok:true,json:async()=>({rows:[{id:row.id,sha256:'old',identity:{name:'小米音箱'}}]})});
  await assert.rejects(publish({root,baseUrl:'https://api.example.test',token:'a'.repeat(64),fetchImpl,mirrorImages:async()=>images++}),/Source identity changed/);
  assert.equal(images,0);
});
test('Additions and price updates produce deltas, absent source IDs are retained',()=>{
  const row={id:'CN:mi_cn:1',name:'小米音箱',price:199};
  assert.deepEqual(plan([row],{rows:[{id:row.id,sha256:'old',identity:{name:row.name}},{id:'retained',sha256:'old'}]}),[row]);
});
test('Price history sends stable compressed chunks and only the appended tail on the next run',async t=>{
  const root=await mkdtemp(path.join(tmpdir(),'mysql-history-'));t.after(()=>rm(root,{recursive:true,force:true}));
  await mkdir(path.join(root,'price-history'));const name='price-history/2026-11.jsonl.gz';
  const rows=Array.from({length:2001},(_,i)=>JSON.stringify({gid:'CN:mi_cn:1',at:new Date(Date.UTC(2026,10,8,0,0,i)).toISOString(),price:100+i,currency:'CNY',price_type:'price'}));
  const save=async()=>{const wire=gzipSync(rows.join('\n')+'\n');await writeFile(path.join(root,name),wire);return {price_history:{files:{[name]:{sha256:createHash('sha256').update(wire).digest('hex'),bytes:wire.length}}}};};
  const baseline={historyFiles:[]},requests=[];
  const request=async(kind,body)=>{assert.equal(kind,'history');requests.push(body);baseline.historyFiles.push(body.sha256);return {ok:true};};
  let meta=await save();assert.equal((await publishHistory({root,meta,baseline,request,dryRun:false})).chunks,2);
  assert.equal((await publishHistory({root,meta,baseline,request,dryRun:false})).chunks,0);
  rows.push(JSON.stringify({gid:'CN:mi_cn:1',at:'2026-11-08T02:00:00Z',price:20,currency:'CNY',price_type:'price'}));meta=await save();
  assert.equal((await publishHistory({root,meta,baseline,request,dryRun:false})).chunks,1);
  assert.equal(requests.at(-1).jsonl.trim().split('\n').length,2);
});
