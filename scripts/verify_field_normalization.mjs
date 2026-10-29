// Verify the existing API query/detail implementation against an independent union oracle.
// node SCRIPT API_MODULE BEFORE_PUBLIC AFTER_PUBLIC EXPECTED_JSON OUTPUT_JSON
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {pathToFileURL} from 'node:url';
const [modulePath,beforeDir,afterDir,expectedPath,outputPath]=process.argv.slice(2);
const {createGoodsIndex}=await import(pathToFileURL(modulePath));
const before=createGoodsIndex(beforeDir),after=createGoodsIndex(afterDir);
const a=await before.query(new URLSearchParams({limit:'1',group_products:'1'}));
const b=await after.query(new URLSearchParams({limit:'1',group_products:'1'}));
const counts=items=>Object.fromEntries(items.map(x=>[x.value,x.count]).sort(([a],[b])=>a.localeCompare(b)));
for(const facet of ['categories','brands'])assert.deepEqual(counts(b.facets[facet]),counts(a.facets[facet]),facet);
assert.equal(b.total,a.total);
const expected=JSON.parse(fs.readFileSync(expectedPath));
assert.equal(expected.length,10);
const sample=[];
for(const {id,params,originalKeys,unionKeys} of expected){
  const detail=await after.detail(id);
  assert.deepEqual(detail.params,params,`detail params ${id}`);
  sample.push({id,originalKeys,unionKeys,returnedKeys:Object.keys(detail.params).length,paramsEqual:true});
}
fs.writeFileSync(outputPath,JSON.stringify({apiModule:modulePath,beforeTotal:a.total,afterTotal:b.total,
  facetsBefore:a.facets,facetsAfter:b.facets,allFacetCountsEqual:true,sample},null,2)+'\n');
console.log('All category/brand facet counts equal; 10 API details equal normalized original union.');
