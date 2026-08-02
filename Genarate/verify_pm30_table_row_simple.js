const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
  const filePath = 'file:///' + path.resolve('website_constitution.html').replace(/\\/g, '/');
  await page.goto(filePath);

  await page.click("button:has-text('ทำเนียบนายกรัฐมนตรี')");
  await page.waitForTimeout(500);

  const pm30Info = await page.evaluate(() => {
    const table = document.querySelector('#pms-tab table.styled-table');
    if (!table) return 'Table not found';
    const rows = Array.from(table.querySelectorAll('tbody tr'));
    const pm30 = rows[rows.length - 1];
    return {
      totalRows: rows.length,
      lastRowText: pm30 ? pm30.innerText : 'None'
    };
  });

  console.log('PM 30 Table Row Result:', JSON.stringify(pm30Info, null, 2));

  await browser.close();
})();
