const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
  const filePath = 'file:///' + path.resolve('website_constitution.html').replace(/\\/g, '/');
  await page.goto(filePath);

  // Click Chakri tab
  await page.click("button:has-text('ราชวงศ์จักรี')");
  await page.waitForTimeout(500);

  // Check section
  const sectionText = await page.locator('#chakri-tab').innerText();
  console.log('Chakri tab text snippet contains positions header:');
  console.log(sectionText.includes('👑 ตำแหน่งที่สำคัญของราชวงศ์') ? '✅ Found Header' : '❌ Header Missing');

  // Take screenshot of Royal Positions section
  const section = page.locator('#chakri-tab > div').first();
  await section.screenshot({ path: path.resolve('royal_positions_section.png') });
  console.log('Saved screenshot to royal_positions_section.png!');

  await browser.close();
})();
