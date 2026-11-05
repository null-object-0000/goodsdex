// Optional browser evidence capture: YOUPIN_PLAYWRIGHT_MODULE points to playwright-core.
const fs = require('node:fs');
const {chromium} = require(process.env.YOUPIN_PLAYWRIGHT_MODULE || 'playwright');
(async () => {
 const browser = await chromium.launch({executablePath:process.env.YOUPIN_CHROME_PATH || '/usr/bin/google-chrome',headless:true,args:['--no-sandbox']});
 try {
  const page = await browser.newPage(); const pending=[];
  page.on('response', r => {
   if (!/\/api\/gateway\/detail|\/mtop\/market\/search\/v2\/doSearch/.test(r.url())) return;
   pending.push((async()=>({url:r.url(),method:r.request().method(),headers:await r.request().allHeaders(),body:r.request().postData(),status:r.status(),response:await r.json()}))());
  });
  await page.goto('https://www.xiaomiyoupin.com/detail?gid=156975',{waitUntil:'networkidle',timeout:60000});
  await page.goto('https://www.xiaomiyoupin.com/search?keyword=小米15',{waitUntil:'networkidle',timeout:60000});
  fs.writeFileSync(process.argv[2] || 'youpin-browser.json', JSON.stringify({captured_at:new Date().toISOString(),events:await Promise.all(pending)},null,2));
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
