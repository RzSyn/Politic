const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
  const filePath = 'file:///' + path.resolve('website_constitution.html').replace(/\\/g, '/');
  console.log(`Navigating to ${filePath}...`);
  await page.goto(filePath);

  // 1. Click history-tab
  await page.click("button:has-text('ประวัติศาสตร์')");
  await page.waitForTimeout(500);

  // Check visibility of orange-party-tab and Forward Party card while history-tab is active!
  const orangeTabVisible = await page.evaluate(() => {
    const el = document.getElementById('orange-party-tab');
    if (!el) return { exists: false };
    const style = window.getComputedStyle(el);
    return {
      exists: true,
      display: style.display,
      visibility: style.visibility,
      height: el.offsetHeight,
      clientRect: el.getBoundingClientRect()
    };
  });
  console.log('orange-party-tab while history-tab is active:', JSON.stringify(orangeTabVisible, null, 2));

  // Check if any element containing "พรรคส่งต่อ" is visible on screen!
  const songtorVisibility = await page.evaluate(() => {
    const nodes = Array.from(document.querySelectorAll('div, section, p, span'));
    const songtorNode = nodes.find(n => n.textContent && n.textContent.includes('พรรคส่งต่อ (Forward Party)'));
    if (!songtorNode) return { found: false };
    const rect = songtorNode.getBoundingClientRect();
    const style = window.getComputedStyle(songtorNode);
    return {
      found: true,
      display: style.display,
      visibility: style.visibility,
      top: rect.top,
      bottom: rect.bottom,
      height: rect.height,
      parentTabId: songtorNode.closest('.db-tab-content')?.id
    };
  });
  console.log('Forward Party Card visibility:', JSON.stringify(songtorVisibility, null, 2));

  await browser.close();
})();
