/* Independent anonymous rendered-H5 acceptance, no credentials/browser state saved. */
const fs=require('node:fs');const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const out=process.argv[2];
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_PATH||undefined,headless:true,args:['--no-sandbox']});
try{const c=await b.newContext({viewport:{width:430,height:1000}});let last=0,chain=Promise.resolve();let categories=[],seconds=[];
await c.route('https://api-shoppingmall.yaduo.com/**',async r=>{const prev=chain;let done;chain=new Promise(x=>done=x);await prev;try{await new Promise(x=>setTimeout(x,Math.max(0,last+2100-Date.now())));last=Date.now();const headers={...r.request().headers()};for(const k in headers)if(/cookie|token|authorization|unionid/i.test(k))delete headers[k];const path=new URL(r.request().url()).pathname;if(!/getPublicKey|getConfig|getFirstClassifyList|getSecondClassifyList|querySearchPageData|pageByParam|getNewDetail|getGoodsSkuPanel/.test(path)){await r.abort();return;}await r.continue({headers})}finally{done()}});
const p=await c.newPage();p.on('response',async r=>{if(r.url().includes('/goods/classify/')){try{const j=await r.json();if(r.url().includes('getFirst'))categories=j.result;else seconds.push(j.result)}catch{}}});
await p.goto('https://h5mall.yaduo.com/pages/category/category',{waitUntil:'networkidle',timeout:120000});const classification=[];
for(const name of ['深睡组合','枕芯系列','被芯系列','深睡睡衣','套件系列','床品配件','床垫系列','专享款']){
 await p.getByText(name,{exact:true}).first().click();await p.waitForTimeout(5000);classification.push({name,body:await p.locator('body').innerText(),groups:seconds.at(-1)});console.log('category',name);
}
fs.writeFileSync(out+'/categories.json',JSON.stringify({categories,classification},null,2)+'\n');
const samples=[];
for(const id of [1987,2044,2048,1977,2006,2099,2113,2034,1965,2049]){
 const url='https://h5mall.yaduo.com/subpacks/mall/goodsDetail/goodsDetail?id='+id;
 await p.goto(url,{waitUntil:'networkidle',timeout:120000});await p.waitForTimeout(3000);
 let body=await p.locator('body').innerText();
 await p.screenshot({path:out+'/h5-'+id+'.png',fullPage:false});
 samples.push({spu_id:id,url,body,captured_at:new Date().toISOString()});
 fs.writeFileSync(out+'/h5-samples.json',JSON.stringify(samples,null,2)+'\n');console.log('sample',id,body.slice(0,650));
}
}finally{await b.close()}})().catch(e=>{console.error(e);process.exitCode=1});
