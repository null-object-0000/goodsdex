// Read-only acceptance against the deployed server's index implementation.
// node scripts/verify_category_queries.mjs /path/to/goods.mjs BEFORE_PUBLIC AFTER_PUBLIC
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
const [modulePath, beforeDir, afterDir] = process.argv.slice(2);
const {createGoodsIndex} = await import(pathToFileURL(modulePath));
const before = createGoodsIndex(beforeDir), after = createGoodsIndex(afterDir);
const left = await before.query(new URLSearchParams()), right = await after.query(new URLSearchParams());
const counts = result => Object.fromEntries(result.facets.categories.map(c=>[c.value,c.count]).sort(([a],[b])=>a.localeCompare(b)));
assert.deepEqual(counts(left),counts(right));
const categories = ['服饰','摄影器材配件','宠物饮水机','烟灶','麦克风配件'];
const queries = [];
for (const category of categories) {
  const a = await before.query(new URLSearchParams({category}));
  const b = await after.query(new URLSearchParams({category}));
  assert.equal(a.total,b.total);
  queries.push({category,before:a.total,after:b.total});
}
console.log(JSON.stringify({facets_before:counts(left),facets_after:counts(right),queries},null,2));
