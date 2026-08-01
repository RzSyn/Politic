const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  const filePath = 'file:///' + path.resolve('website_constitution.html').replace(/\\/g, '/');
  console.log(`Navigating to ${filePath}...`);
  await page.goto(filePath);

  // Fast single-shot evaluation of all images
  const brokenImages = await page.$$eval('img', imgs => {
    return imgs.map(img => ({
      src: img.getAttribute('src'),
      alt: img.getAttribute('alt'),
      complete: img.complete,
      naturalWidth: img.naturalWidth
    })).filter(img => !img.complete || img.naturalWidth === 0);
  });

  console.log('\n--- BROKEN IMAGE AUDIT RESULTS ---');
  if (brokenImages.length === 0) {
    console.log('✅ 100% PERFECT! ZERO BROKEN IMAGES FOUND!');
  } else {
    console.log(`❌ Found ${brokenImages.length} broken images:`);
    brokenImages.forEach(img => console.log(`   src="${img.src}", alt="${img.alt}"`));
  }

  // Check Piyabutr card in pms-tab
  await page.click("button:has-text('ทำเนียบนายกรัฐมนตรี')");
  await page.waitForTimeout(300);
  const pmsPiyaText = await page.$eval("div.tri-profile-card:has-text('ปิยบุตร')", el => el.innerText);
  console.log('\n--- PMS TAB PIYABUTR CARD ---');
  console.log(pmsPiyaText);

  await browser.close();
})();
