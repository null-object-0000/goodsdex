import test from 'node:test';
import assert from 'node:assert/strict';
import {plan,hash} from '../scripts/publish_mysql.mjs';
test('No-op publications transmit zero product records; canonical key order is stable',()=>{
  const row={id:'CN:mi_cn:1',name:'小米音箱',params:{颜色:'白色'}};
  assert.equal(hash(row),hash({params:{颜色:'白色'},name:'小米音箱',id:row.id}));
  assert.deepEqual(plan([row],{rows:[{id:row.id,sha256:hash(row),identity:{name:row.name}}]}),[]);
});
test('Preflight rejects contaminated identities before uploading any batches',()=>{
  const row={id:'CN:mi_cn:1',name:'太阳能摄像机'};
  assert.throws(()=>plan([row],{rows:[{id:row.id,sha256:'old',identity:{name:'小米音箱'}}]}),/Source identity changed/);
});
test('Additions and price updates produce deltas, absent source IDs are retained',()=>{
  const row={id:'CN:mi_cn:1',name:'小米音箱',price:199};
  assert.deepEqual(plan([row],{rows:[{id:row.id,sha256:'old',identity:{name:row.name}},{id:'retained',sha256:'old'}]}),[row]);
});
