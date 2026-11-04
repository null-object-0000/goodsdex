#!/usr/bin/env node
/** Capture public HP Support SKU identities. No serial numbers or account APIs.
 * npm install --prefix <runtime> playwright; set HP_PLAYWRIGHT_MODULE if needed.
 * Usage: node scripts/capture_hp_support.cjs candidates.json evidence-directory
 */
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { chromium } = require(process.env.HP_PLAYWRIGHT_MODULE || 'playwright');
const [input, output] = process.argv.slice(2);
if (!input || !output) throw new Error('Need candidates.json and evidence directory');
const candidates = JSON.parse(fs.readFileSync(input));
fs.mkdirSync(output, { recursive: true });
const endpoint = 'https://support.hp.com/wcc-services/profile/devices/warranty/specs?cache=true';
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
(async () => {
 const options = { headless: true };
 if (process.env.HP_CHROMIUM_PATH) options.executablePath = process.env.HP_CHROMIUM_PATH;
 if (process.env.HP_BROWSER_PROXY) options.proxy = { server: process.env.HP_BROWSER_PROXY };
 const browser = await chromium.launch(options);
 try {
  const page = await browser.newPage();
  // The actual browser network stack handles the public support site's JS/cookies.
  await page.route('**/*', route => ['image', 'font', 'media'].includes(route.request().resourceType()) ? route.abort() : route.continue());
  let ready = false;
  for (let i = 0; i < 4; i++) {
   try { await page.goto('https://support.hp.com/cn-zh/products', { timeout: 25000, waitUntil: 'domcontentloaded' }); ready = true; break; }
   catch (e) { console.log('initialization retry', i + 1, String(e).slice(0, 150)); }
  }
  if (!ready) throw new Error('Cannot initialize official HP support origin');
  let last = 0, success = 0, failed = 0;
  const audit = [];
  for (const item of candidates) {
   const sku = item.part_number;
   if (!/^[A-Z0-9]{5}(?:PC|PA)$/.test(sku)) throw new Error('Not a discovered China SKU: ' + sku);
   const file = path.join(output, sku + '.json');
   if (fs.existsSync(file)) { const prior = JSON.parse(fs.readFileSync(file)); if (prior.validated) { success++; continue; } }
   const payload = { cc: 'cn', lc: 'zh', utcOffset: 'P0800', devices: [{ seriesOid: null, modelOid: null, serialNumber: null, productNumber: sku, displayProductNumber: null, countryOfPurchase: 'cn' }] };
   let valid = false;
   for (let attempt = 0; attempt < 3; attempt++) {
    await pause(Math.max(0, 2150 - (Date.now() - last))); last = Date.now();
    const observed_at = new Date().toISOString();
    let record = { url: endpoint, method: 'POST', payload, observed_at, discovery: item };
    try {
     const response = await page.evaluate(async ({ url, payload }) => {
      const r = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload), signal: AbortSignal.timeout(20000) });
      return { status: r.status, body: await r.text(), final_url: r.url };
     }, { url: endpoint, payload });
     record = { ...record, ...response, sha256: crypto.createHash('sha256').update(response.body).digest('hex') };
     const data = JSON.parse(response.body);
     const specs = data?.data?.devices?.[0]?.productSpecs;
     const product = specs?.data;
     valid = response.status === 200 && data.code === 200 && specs.code === 200 && product?.productNumber === sku && !!product?.productName && ['laptop', 'desktop', 'pc', 'workstation'].includes(product?.prodCategory);
     record.validated = valid;
     if (!valid) record.error = 'No exact public computer SKU match';
    } catch (error) { record.error = String(error); }
    audit.push({ ...record, body: undefined });
    fs.writeFileSync(file, JSON.stringify(record, null, 1) + '\n');
    if (valid) break;
   }
   valid ? success++ : failed++;
   console.log(JSON.stringify({ sku, valid, success, failed, remaining: candidates.length - success - failed }));
   fs.writeFileSync(path.join(output, 'audit.json'), JSON.stringify(audit, null, 1) + '\n');
  }
  console.log(JSON.stringify({ success, failed, total: candidates.length }));
  process.exitCode = failed ? 1 : 0;
 } finally { await browser.close(); }
})();
