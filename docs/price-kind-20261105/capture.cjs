const fs=require('node:fs');const path=require('node:path');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE || '/tmp/seo-html-browser/node_modules/playwright');
(async()=>{const browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'/opt/google/chrome/chrome',headless:true,args:['--no-sandbox']});
try{const context=await browser.newContext({viewport:{width:430,height:932}});const page=await context.newPage();
const rows=JSON.parse(fs.readFileSync(path.join(__dirname,'low-input.json')));const results=[];
for(const sid of [...new Set(rows.map(r=>r.spu_id))]){
 const url=`https://h5mall.yaduo.com/subpacks/mall/goodsDetail/goodsDetail?id=${sid}`;
 await page.goto(url,{waitUntil:'domcontentloaded',timeout:60000});
 await page.waitForFunction(()=>document.body.innerText.includes('已选'),null,{timeout:60000});
 await page.waitForTimeout(2500);
 const text=await page.locator('body').innerText();
 fs.writeFileSync(path.join(__dirname,`evidence/${sid}-page.txt`),text);
 await page.screenshot({path:path.join(__dirname,`evidence/${sid}-page.png`)});
 const business=await page.evaluate(async sid=>{window.webpackJsonp.push([[991244],{},r=>window.atourPriceRequire=r]);const api=window.atourPriceRequire(5251);const panel=await api.JV({spuId:sid});await new Promise(r=>setTimeout(r,2200));const detail=await api.Ec({spuId:sid});return {panel,detail};},sid);
 fs.writeFileSync(path.join(__dirname,`evidence/${sid}-business.json`),JSON.stringify(business,null,2));
 await page.getByText('加入购物车',{exact:true}).click();await page.waitForTimeout(8500);
 const selections=[];
 if(sid===1984)rows.push({spu_id:1984,sku_no:'0105100044-2.0-JD28'});
 for(const row of rows.filter(r=>r.spu_id===sid)){
  const sku=business.panel.skuVOS.find(s=>s.skuNo===row.sku_no);
  const ids=String(sku.skuValIds).split(',');
  const config=JSON.parse(business.panel.skuConfigJson);
  let blocked=false;
  for(const group of config){
   const val=group.skuVals.find(v=>ids.includes(String(v.skuValId)));if(!val)continue;
   const option=page.locator('.cart-sku-popup .sku > .normal').filter({hasText:val.skuValName});
   const cls=await option.getAttribute('class');
   if(cls.includes('not-optional')){blocked=true;break;}
   if(!cls.includes('active')){await option.click();await page.waitForTimeout(1000);}
  }
  const selection={blocked,sku_no:row.sku_no,at:new Date().toISOString(),text:await page.locator('.cart-sku-popup').innerText(),selected:await page.locator('.cart-sku-popup .sku > .normal.active').allTextContents(),disabled:await page.locator('.cart-sku-popup .sku > .not-optional').allTextContents()};
  fs.writeFileSync(path.join(__dirname,`evidence/sku-${row.sku_no}.txt`),selection.text);
  await page.screenshot({path:path.join(__dirname,`evidence/sku-${row.sku_no}.png`)});selections.push(selection);
 }
 const panelText=await page.locator('body').innerText();
 fs.writeFileSync(path.join(__dirname,`evidence/${sid}-panel.txt`),panelText);
 await page.screenshot({path:path.join(__dirname,`evidence/${sid}-panel.png`)});
 results.push({sid,url,selections,at:new Date().toISOString(),text,panelText,skus:business.panel.skuVOS.map(s=>({skuNo:s.skuNo,skuName:s.skuName,salesPrice:s.salesPrice,activityPrice:s.activityPrice,spuStatus:s.spuStatus}))});
 fs.writeFileSync(path.join(__dirname,'evidence/pages.json'),JSON.stringify(results,null,2));console.log(sid,text.slice(0,130).replaceAll('\n',' / '));
}
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1;});
