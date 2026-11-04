/* Anonymous official H5 reader. Never persists headers, cookies, storage or tokens. */
const fs = require('node:fs');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const out = process.argv[2];
if (!out) throw Error('Output JSON required');
function saveBusiness(value) {
 const check=x=>{if(Array.isArray(x))x.forEach(check);else if(x&&typeof x==='object')for(const [k,v] of Object.entries(x)){
  if(/cookie|token|authorization|unionid/i.test(k))throw Error('Credential-bearing payload must not be stored');
  check(v);
 }};
 check(value);fs.writeFileSync(out,JSON.stringify(value,null,2)+'\n');
}
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROME_PATH || undefined,headless:true,args:['--no-sandbox']});
 try {
  const context=await browser.newContext();
  let chain=Promise.resolve(), last=0; const requests=[];
  await context.route('https://api-shoppingmall.yaduo.com/**', async route=>{
   // Only storefront reads used by the official anonymous page are permitted.
   const req=route.request(), u=new URL(req.url());
   if (!['/common/getPublicKey/v1','/index/getConfig','/goods/spu/pageByParam/v1','/goods/spu/getNewDetail/v1','/goods/sku/getGoodsSkuPanel/v1'].includes(u.pathname)) {await route.abort();return;}
   const previous=chain; let done; chain=new Promise(r=>done=r);
   await previous;
   try {
    await new Promise(r=>setTimeout(r,Math.max(0,last+2105-Date.now())));
    last=Date.now();
    const headers={...req.headers()};
    for(const k of Object.keys(headers)) if(/cookie|token|authorization|unionid/i.test(k)) delete headers[k];
    requests.push({url:u.origin+u.pathname,method:req.method(),started_at:new Date(last).toISOString()});
    await route.continue({headers});
   } finally {done();}
  });
  const page=await context.newPage();
  page.on('response', response=>{
   const u=new URL(response.url());
   if(u.hostname==='api-shoppingmall.yaduo.com'){
    const record=requests.find(r=>r.url===u.origin+u.pathname && r.status===undefined);
    if(record)record.status=response.status();
   }
  });
  await page.goto('https://h5mall.yaduo.com/',{waitUntil:'domcontentloaded',timeout:60000});
  // Analytics/images can keep networkidle pending forever; wait for the actual reader.
  await page.waitForFunction(()=>{
   if(!window.webpackJsonp)return false;
   if(!window.atourRequire)window.webpackJsonp.push([[991239],{},r=>window.atourRequire=r]);
   try{window.atourApi=window.atourRequire(5251);return typeof window.atourApi.pg==='function';}catch{return false;}
  },null,{timeout:60000});
  const call=async(method,args)=>page.evaluate(async({method,args})=>await window.atourApi[method](args),{method,args});
  const pages=[];
  const first=await call('pg',{pageNo:1,pageSize:20});pages.push(first);
  for(let n=2;n<=first.pageInfo.totalPage;n++) pages.push(await call('pg',{pageNo:n,pageSize:20}));
  const products=pages.flatMap(p=>p.data).filter(p=>p.spuName.startsWith('亚朵星球 '));
  const entries=[];
  for(const p of products){
   const panel=await call('JV',{spuId:p.id});
   const detail=await call('Ec',{spuId:p.id});
   entries.push({listing:p,panel,detail,captured_at:new Date().toISOString()});
   console.log(p.id,p.spuName,panel.skuVOS.length);
   // Persist business objects only; no request/response envelopes or browser state.
   saveBusiness({complete:false,pages,entries,requests});
  }
  saveBusiness({complete:true,pages,entries,requests,captured_at:new Date().toISOString()});
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
