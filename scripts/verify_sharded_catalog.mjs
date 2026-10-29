// node scripts/verify_sharded_catalog.mjs OLD_GOODS_MODULE NEW_GOODS_MODULE BEFORE_DIR AFTER_DIR OUTPUT
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {performance} from 'node:perf_hooks';
const [oldModule,newModule,beforeDir,afterDir,output]=process.argv.slice(2);
const old=create(await import(oldModule),beforeDir),fresh=create(await import(newModule),afterDir);
function create(module,dir){return module.createGoodsIndex(dir);}
const a=await old.load(),b=await fresh.load();
assert.deepEqual([...b.byId.keys()],[...a.byId.keys()]);
for(const [id,text] of a.text)assert.equal(b.text.get(id),text,`search text ${id}`);
assert.deepEqual([...b.presentations],[...a.presentations]);
const params=new URLSearchParams({limit:'20',group_products:'1'});
const before=await old.query(params),after=await fresh.query(params);
delete after.cursor;delete before.cursor;assert.deepEqual(after,before);
for(const category of before.facets.categories.map(c=>c.value)){
 const q=new URLSearchParams({category,group_products:'1',limit:'50'});
 const x=await old.query(q),y=await fresh.query(q);delete x.cursor;delete y.cursor;assert.deepEqual(y,x,category);
}
for(const q of ['小米','苹果','大疆','富士','256GB','Wi-Fi','净水','汉','2025','扫地机器人']){
 const p=new URLSearchParams({q,group_products:'1',limit:'50'}),x=await old.query(p),y=await fresh.query(p);delete x.cursor;delete y.cursor;assert.deepEqual(y,x,q);
}
// Deterministic stratified sample: all brands, references, conflicting IDs and then evenly spaced IDs.
const ids=[...new Set([...new Set(a.rows.map(r=>r.brand))].flatMap(brand=>a.rows.filter(r=>r.brand===brand).slice(0,2).map(r=>r.id)).concat(a.rows.filter(r=>r.record_level).slice(0,2).map(r=>r.id),a.rows.filter((_,i)=>i%191===0).map(r=>r.id)))].slice(0,20);
for(const id of a.byId.keys())assert.deepEqual(await fresh.detail(id),await old.detail(id),`full-catalog detail ${id}`);
const sample=[];
for(const id of ids){
 const x=await old.detail(id),y=await fresh.detail(id);assert.deepEqual(y,x,`detail ${id}`);
 const p=new URLSearchParams({ids:id});assert.deepEqual(await fresh.query(p),await old.query(p));
 const family=x.product_id||id;
 const xp=await old.query(new URLSearchParams({product_ids:family})),yp=await fresh.query(new URLSearchParams({product_ids:family}));assert.deepEqual(yp,xp,`family ${family}`);
 sample.push({id,fields:['display_name','price_from','list_facts','image','category','categories'],detail:'all fields equal',presentation:a.presentations.get(family)||null});
}
fs.writeFileSync(output,JSON.stringify({verified_at:new Date().toISOString(),total:before.total,facets:before.facets,sample,indexBytes:fs.readdirSync(afterDir+'/index').reduce((n,f)=>n+fs.statSync(afterDir+'/index/'+f).size,0),allDetailsEqual:true,allSearchTextEqual:true,allPresentationsEqual:true,allCategoryQueriesEqual:true},null,2));
console.log('verified',ids.length,'details, all presentations, all search text, all categories');
