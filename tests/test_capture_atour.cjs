const {test} = require('node:test');
const assert = require('node:assert/strict');
const {READ_PATHS, skipResource} = require('../scripts/capture_atour.cjs');

test('current anonymous storefront reads are allowed, account and order writes stay blocked', () => {
 for (const path of ['/goods/spu/pageByParam/v1', '/goods/spu/getNewDetail/v1', '/goods/sku/getGoodsSkuPanel/v1']) {
  assert.ok(READ_PATHS.has(path));
 }
 for (const path of ['/login/loginByWeChatMobile/v1', '/goods/shopping/cart/addShoppingCart', '/qiniu/token/v1']) {
  assert.ok(!READ_PATHS.has(path));
 }
});

test('nonessential synchronous analytics is skipped while official application scripts remain readable', () => {
 assert.ok(skipResource('https://oss-front-code-prod-c.yaduo.com/manual/collect-privity-v5.0.0.js', 'script'));
 assert.ok(!skipResource('https://ack-frontend-oss.yaduo.com/static-all/atour-planet-h5/prod/current/js/app.js', 'script'));
 assert.ok(!skipResource('https://api-shoppingmall.yaduo.com/common/getPublicKey/v1', 'xhr'));
 assert.ok(skipResource('https://xbu-qiniu.yaduo.com/photo.jpg', 'image'));
});
