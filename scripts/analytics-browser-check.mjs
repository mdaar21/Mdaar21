// A fixture tag and collector verify browser/CSP behavior. No Google account or
// real measurement endpoint is contacted, and these checks are not live stats.
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { readFile, mkdtemp, mkdir, rm, writeFile } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';
const root = fileURLToPath(new URL('../', import.meta.url));
const scratch = await mkdtemp(path.join(tmpdir(), 'mdaar-analytics-'));
const id = 'G-TEST123456';
const results = [];
function build(name, measurementId) {
  const out = path.join(scratch, name);
  const run = spawnSync('python3', ['scripts/build-github-pages.py', '--output', out, '--measurement-id', measurementId], { cwd: root, encoding: 'utf8' });
  assert.equal(run.status, 0, run.stderr);
  return out;
}
const enabled = build('enabled', id), disabled = build('disabled', '');
for (const name of ['index.html', 'discover/index.html']) {
  const html = await readFile(path.join(enabled,name),'utf8');
  assert(html.slice(0,1024).includes('<meta charset="utf-8">'));
  assert(html.indexOf('Content-Security-Policy')<html.indexOf('<script'),'CSP precedes scripts');
}
let tree = enabled;
const types = { '.html':'text/html', '.mjs':'text/javascript', '.js':'text/javascript', '.css':'text/css', '.json':'application/json', '.webmanifest':'application/manifest+json', '.svg':'image/svg+xml', '.ttf':'font/ttf', '.png':'image/png', '.webp':'image/webp' };
const server = createServer(async (req, res) => {
  try {
    let name = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
    assert(name.startsWith('/Mdaar21/'));
    name = name.slice('/Mdaar21/'.length);
    if (!name || name.endsWith('/')) name += 'index.html';
    const target = path.resolve(tree, name);
    assert(target.startsWith(tree + path.sep));
    res.setHeader('Content-Type', types[path.extname(target)] || 'application/octet-stream');
    res.end(await readFile(target));
  } catch { res.writeHead(404);res.end(); }
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const base = `http://127.0.0.1:${server.address().port}/Mdaar21/`;
const browser = await chromium.launch({executablePath:process.env.CHROMIUM_PATH || '/usr/bin/chromium',headless:true,args:['--no-sandbox']});
async function run(name, fn) {
  const context = await browser.newContext({viewport:{width:390,height:844}, serviceWorkers:'block'});
  const page = await context.newPage(), errors = [], requests = [], violations = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.addInitScript(() => {
    window.fixtureCsp = [];
    document.addEventListener('securitypolicyviolation', e => window.fixtureCsp.push({blocked:e.blockedURI, directive:e.effectiveDirective}));
    localStorage.setItem('mdaar_t', JSON.stringify({w:98.123,private:'PRIVATE_RECORD_SENTINEL'}));
  });
  // Stop every external request. The tag stub exercises the actual CSP by
  // sending only fixture data to an intercepted Google collector URL.
  await page.route('https://**/*', async route => {
    const url = route.request().url();requests.push(url);
    if (url.startsWith('https://www.googletagmanager.com/gtag/js?')) return route.fulfill({contentType:'text/javascript',body:"window.fixtureTagLoaded=true;fetch('https://region1.google-analytics.com/g/collect',{method:'POST',mode:'no-cors',body:'fixture-only'}).catch(()=>{});"});
    if (url.startsWith('https://region1.google-analytics.com/g/collect')) return route.fulfill({status:204,headers:{'Access-Control-Allow-Origin':'*'}});
    return route.abort();
  });
  try {
    await fn(page, requests);
    violations.push(...await page.evaluate(() => window.fixtureCsp));
    assert.deepEqual(errors, []);assert.deepEqual(violations, []);
    results.push({name,status:'passed'});
  } finally { await context.close(); }
}
const layer = page => page.evaluate(() => (window.dataLayer || []).map(x => Array.from(x)));
try {
  await run('unconfigured builds contact no analytics provider on either surface', async (page, requests) => {
    tree = disabled;
    for (const url of [base,base+'discover/']) {
      await page.goto(url,{waitUntil:'networkidle'});
      assert.equal(await page.locator('meta[name="mdaar-ga4"]').count(),0);
      assert.deepEqual(await layer(page),[]);
    }
    assert.equal(requests.length,0);tree=enabled;
  });
  for (const [area, tail] of [['app',''],['showcase','discover/']]) await run(`${area}: one sanitized page view, campaign attribution and CSP-compatible tag`, async (page, requests) => {
    await page.goto(base+tail+'?email=PRIVATE_EMAIL_SENTINEL&weight=98.123&utm_source=tiktok&utm_medium=social&utm_campaign=launch#PRIVATE_HASH_SENTINEL',{waitUntil:'networkidle'});
    assert(await page.evaluate(() => window.fixtureTagLoaded));
    const data=await layer(page), config=data.find(x=>x[0]==='config'), views=data.filter(x=>x[0]==='event'&&x[1]==='page_view');
    assert.equal(views.length,1);assert.equal(config[1],id);assert.equal(config[2].send_page_view,false);
    assert.equal(config[2].allow_google_signals,false);assert.equal(config[2].allow_ad_personalization_signals,false);
    assert.equal(views[0][2].page_location,base+tail);assert.equal(views[0][2].site_area,area);assert.equal(views[0][2].campaign_source,'tiktok');
    assert(!/PRIVATE_|98\.123|email=/.test(JSON.stringify(data)));
    assert(requests.some(x=>x.includes('region1.google-analytics.com/g/collect')));
    if(area==='app') {
      assert(await page.locator('meta[name="mdaar-service-origin"]').getAttribute('content'));
      await page.locator('#tabs [data-t="calc"]').click();
      await page.locator('#age').fill('25');await page.locator('#w').fill('75');await page.locator('#h').fill('175');
      await page.locator('#f button[type="submit"]').click();assert(await page.locator('#out').isVisible());
      assert.equal((await layer(page)).filter(x=>x[0]==='event').length,1,'no form-value or health events');
    }
  });
  await run('store click records placement once without blocking purchase navigation', async page => {
    await page.goto(base+'discover/',{waitUntil:'networkidle'});
    await page.evaluate(() => document.addEventListener('click', e => {if(e.target.closest?.('a[data-purchase]')){window.fixtureClickWasPrevented=e.defaultPrevented;e.preventDefault();}}));
    await page.locator('.hero-actions [data-purchase]').click();
    const clicks=(await layer(page)).filter(x=>x[0]==='event'&&x[1]==='purchase_click');
    assert.equal(clicks.length,1);assert.equal(clicks[0][2].button_placement,'hero');assert.equal(await page.evaluate(()=>window.fixtureClickWasPrevented),false);
    assert.equal((await layer(page)).filter(x=>x[1]==='purchase').length,0,'a click is not a completed sale');
  });
  for (const flag of ['doNotTrack','globalPrivacyControl']) await run(`${flag}: browser privacy preference prevents analytics`, async (page, requests) => {
    await page.addInitScript(flag => Object.defineProperty(navigator,flag,{value:flag==='doNotTrack'?'1':true,configurable:true}),flag);
    await page.goto(base+'discover/',{waitUntil:'networkidle'});assert.deepEqual(await layer(page),[]);assert.equal(requests.length,0);
  });
  await run('an analytics blocker leaves the application usable', async page => {
    await page.route('https://www.googletagmanager.com/**',route=>route.abort());
    await page.goto(base,{waitUntil:'networkidle'});await page.locator('#tabs [data-t="calc"]').click();assert(await page.locator('#f').isVisible());
  });
  const invalid=spawnSync('python3',['scripts/build-github-pages.py','--output',path.join(scratch,'invalid'),'--measurement-id','https://invalid.example/script.js'],{cwd:root,encoding:'utf8'});
  assert.notEqual(invalid.status,0);results.push({name:'invalid measurement identifiers fail the build',status:'passed'});
  const report={scope:'Local project-prefixed Pages builds; provider and collector intercepted; not proof of live Google property activation',results};
  const reportPath=process.env.MDAAR_TEST_REPORT || path.join(root,'docs/reports/analytics-browser.json');
  await mkdir(path.dirname(reportPath),{recursive:true});await writeFile(reportPath,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
} finally {await browser.close();await new Promise(resolve=>server.close(resolve));await rm(scratch,{recursive:true,force:true});}
