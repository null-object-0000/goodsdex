const fs=require('node:fs');
const {chromium}=require(process.env.ATOUR_PLAYWRIGHT_MODULE || '/home/nichangen/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright-core');
(async()=>{
 const browser=await chromium.launch({executablePath:'/opt/google/chrome/chrome',headless:true,args:['--no-sandbox']});
 try{
 const page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.setViewportSize({width:1440,height:1100});
 await page.goto('http://127.0.0.1:18136/admin/login');
 await page.locator('input[type=password]').fill('local-release-evidence');await page.getByRole('button',{name:'口令登录'}).click();
 await page.getByText('发布日期精度 · 品牌矩阵',{exact:true}).waitFor();
 await page.waitForFunction(()=>document.body.innerText.includes('亚朵星球') && !document.querySelector('.ant-spin-spinning'));
 const result=await page.evaluate(async()=>await(await fetch('/admin/api/catalog')).json());
 fs.writeFileSync(process.argv[2]+'/dashboard-catalog.json',JSON.stringify(result,null,2));
 for(const width of [1440,390]){
  await page.setViewportSize({width,height:1100});
  await page.getByText('发布日期精度 · 品牌矩阵',{exact:true}).scrollIntoViewIfNeeded();await page.waitForTimeout(600);
  await page.screenshot({path:process.argv[2]+`/dashboard-${width}.png`,fullPage:true});
 }
 if(errors.length)throw Error(errors.join('\n'));console.log(JSON.stringify({total:result.releasePrecision.total,errors}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
