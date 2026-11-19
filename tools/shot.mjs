// shot.mjs — screenshot an element of website_new.html (or another page) by tab and text.
//   node tools/shot.mjs <tab-id> "<text inside the element>" <out.png> [page=website_new.html] [width=1280]
// Opens page#tab-id, finds the smallest element whose text contains the string and is at least
// 300 px wide, scrolls to it and saves a screenshot of it. Uses the globally installed Playwright.
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
import { resolve } from 'node:path';
const require = createRequire(execSync('npm root -g').toString().trim() + '/');
const { chromium } = require('playwright');
const [tab, text, out, page = 'website_new.html', width = '1280'] = process.argv.slice(2);
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: +width, height: 900 } });
await p.goto('file://' + resolve(page) + '?nc=' + Date.now() + '#' + tab);
await p.waitForTimeout(2500);
const ok = await p.evaluate(({ tab, text }) => {
  const root = document.getElementById(tab) || document;
  let best = null;
  for (const el of root.querySelectorAll('div, tr, section, article, table')) {
    const r = el.getBoundingClientRect();
    if (r.width < 300 || r.height < 20 || !el.textContent.includes(text)) continue;
    if (!best || el.textContent.length < best.textContent.length) best = el;
  }
  if (!best) return false;
  best.setAttribute('data-shot', '1');
  best.scrollIntoView({ block: 'start' });
  return true;
}, { tab, text });
if (!ok) { console.error('not found: ' + text); process.exit(1); }
await p.waitForTimeout(800);
await p.locator('[data-shot="1"]').screenshot({ path: out });
await b.close();
console.log('saved', out);
