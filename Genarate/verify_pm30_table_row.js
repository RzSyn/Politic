const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
  const filePath = 'file:///' + path.resolve('website_constitution.html').replace(/\\/g, '/');
  await page.goto(filePath);

  // Click PMs tab
  await page.click("button:has-text('ทำเนียบนายกรัฐมนตรี')");
  await page.waitForTimeout(500);

  // Locate PM 30 table row
  const pm30Row = page.locator("tr:has-text('ทักษิณ ชินวัตร (วาระสอง)')").first();
  const rowText = await pm30Row.innerText();
  console.log("PM 30 Table Row Text Snippet:");
  console.log(rowText);

  // Take screenshot of PM 30 table row for visual artifact verification
  await pm30Row.screenshot({ path: path.resolve('pm30_table_row_expanded.png') });
  console.log("Saved screenshot to pm30_table_row_expanded.png!");

  await browser.close();
})();
