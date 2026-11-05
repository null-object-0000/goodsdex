// Anonymous official H5 adapter. No account, login state, or private endpoints.
const fs = require('node:fs');
const {chromium} = require(process.env.ATOUR_PLAYWRIGHT_MODULE || 'playwright');
(async()=> {
 const browser=await chromium.launch({executablePath:process.env.ATOUR_CHROMIUM_PATH || '/opt/google/chrome/chrome',headless:true,args:['--no-sandbox']});
 try {
  const page=await browser.newPage(); const responses=[];
  page.on('response',r=>{if(r.url().includes('api-shoppingmall.yaduo.com/goods/'))responses.push({url:r.url(),status:r.status()});});
  await page.goto('https://h5mall.yaduo.com/',{waitUntil:'networkidle',timeout:60000});
  const data=await page.evaluate(async()=>{
   window.webpackJsonp.push([[991237],{},r=>window.releaseRequire=r]);
   const api=window.releaseRequire(5251);const pages=[];let last=1;
   for(let pageNo=1;pageNo<=last;pageNo++){const p=await api.pg({pageNo,pageSize:20});pages.push(p);last=p.pageInfo.totalPage;if(last>20)throw Error('Unexpected catalogue pagination');}
   const products=pages.flatMap(p=>p.data).filter(p=>p.spuName.startsWith('亚朵星球 '));
   const details=[];
   for(const p of products){try{details.push({spuId:p.id,detail:await api.Ec({spuId:p.id})});}catch(e){details.push({spuId:p.id,error:String(e)});}}
   return {pages,details};
  });
  fs.writeFileSync(process.argv[2],JSON.stringify({captured_at:new Date().toISOString(),source_url:'https://h5mall.yaduo.com/',responses,...data},null,2));
  console.log(JSON.stringify({spus:data.details.length,errors:data.details.filter(x=>x.error).length}));
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
