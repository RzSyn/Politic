const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1600, height: 1000 } });
  const filePath = 'file:///' + path.resolve('website_constitution.html').replace(/\\/g, '/');
  console.log(`Navigating to ${filePath}...`);
  await page.goto(filePath);

  // 1. Check all images for broken status (naturalWidth === 0)
  console.log('\n--- AUDITING ALL IMAGES ON THE PAGE ---');
  const images = await page.locator('img').all();
  let brokenCount = 0;
  for (const img of images) {
    const src = await img.getAttribute('src');
    const alt = await img.getAttribute('alt');
    const isLoaded = await img.evaluate(node => node.complete && node.naturalWidth > 0);
    if (!isLoaded) {
      brokenCount++;
      console.log(`❌ BROKEN IMAGE: src="${src}", alt="${alt}"`);
    }
  }
  if (brokenCount === 0) {
    console.log(`✅ ALL ${images.length} IMAGES LOADED PERFECTLY! ZERO BROKEN IMAGES!`);
  } else {
    console.log(`⚠️ Total broken images found: ${brokenCount}`);
  }

  // 2. Audit Piyabutr in pms-tab
  console.log('\n--- PMS-TAB PIYABUTR AUDIT ---');
  await page.click("button:has-text('ทำเนียบนายกรัฐมนตรี')");
  await page.waitForTimeout(500);
  const pmsPiyaCard = page.locator("div.tri-profile-card:has-text('ปิยบุตร')");
  if (await pmsPiyaCard.count() > 0) {
    const text = await pmsPiyaCard.innerText();
    const imgUrl = await pmsPiyaCard.locator('img').getAttribute('src');
    console.log(`✅ Found Piyabutr Card in pms-tab!`);
    console.log(`  Img URL: ${imgUrl}`);
    console.log(`  Party Info:\n${text}`);
  }

  // 3. Audit Piyabutr in orange-party-tab
  console.log('\n--- ORANGE-PARTY-TAB PIYABUTR AUDIT ---');
  await page.click("button:has-text('พรรคสีส้ม')");
  await page.waitForTimeout(500);
  const orangePiyaHeading = page.locator("h2, div").filter({ hasText: 'นายกรัฐมนตรีคนที่ ๒๙: ศ.ดร.ปิยบุตร แสงกนกกุล' }).first();
  if (await orangePiyaHeading.count() > 0) {
    console.log(`✅ Found Piyabutr heading in orange-party-tab!`);
  }

  await browser.close();
})();
