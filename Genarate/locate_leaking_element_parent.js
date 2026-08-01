const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  const filePath = 'file:///' + path.resolve('website_constitution.html').replace(/\\/g, '/');
  await page.goto(filePath);

  const leakedInfo = await page.evaluate(() => {
    const nodes = Array.from(document.querySelectorAll('*'));
    const matches = nodes.filter(n => n.innerText && n.innerText.includes('📌 บทบาทพรรคส่งต่อ & สะพานเชื่อมแห่งนกฟินิกส์'));
    return matches.map(n => {
      const parentTab = n.closest('.db-tab-content');
      const style = window.getComputedStyle(n);
      return {
        tagName: n.tagName,
        id: n.id,
        className: n.className,
        parentTabId: parentTab ? parentTab.id : 'NO PARENT TAB (OUTSIDE ALL TABS)',
        display: style.display,
        visibility: style.visibility,
        top: n.getBoundingClientRect().top
      };
    });
  });

  console.log('Leaked Info:', JSON.stringify(leakedInfo, null, 2));

  await browser.close();
})();
