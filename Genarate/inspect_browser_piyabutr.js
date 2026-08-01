const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  const filePath = 'file:///' + path.resolve('website_constitution.html').replace(/\\/g, '/');
  console.log(`Navigating to ${filePath}...`);
  await page.goto(filePath);

  // 1. Check pms-tab
  console.log('\n--- CHECKING PMS TAB ---');
  await page.click("button:has-text('ทำเนียบนายกรัฐมนตรี')");
  await page.waitForTimeout(1000);
  
  const piyaPmsCard = page.locator("div.tri-profile-card:has-text('ปิยบุตร')");
  if (await piyaPmsCard.count() > 0) {
    console.log('Found Piyabutr in pms-tab!');
    const imgSrc = await piyaPmsCard.locator('img').getAttribute('src');
    const cardText = await piyaPmsCard.innerText();
    console.log(`  Img SRC: ${imgSrc}`);
    console.log(`  Card Text:\n${cardText}`);
  } else {
    console.log('Piyabutr card NOT found in pms-tab!');
  }

  // 2. Check orange-party-tab
  console.log('\n--- CHECKING ORANGE PARTY TAB ---');
  await page.click("button:has-text('พรรคสีส้ม')");
  await page.waitForTimeout(1000);

  const piyaOrangeCard = page.locator("div:has-text('ศ.ดร.ปิยบุตร แสงกนกกุล')").first();
  if (await piyaOrangeCard.count() > 0) {
    console.log('Found Piyabutr in orange-party-tab!');
    const orangeText = await page.locator("div:has-text('นายกรัฐมนตรีคนที่ ๒๙: ศ.ดร.ปิยบุตร แสงกนกกุล')").innerText();
    console.log(`  Card Text snippet:\n${orangeText.slice(0, 300)}`);
  } else {
    console.log('Piyabutr NOT found in orange-party-tab!');
  }

  // 3. Check parties-tab for Move Forward Party or Independent Party
  console.log('\n--- CHECKING PARTIES TAB ---');
  await page.click("button:has-text('พรรคการเมือง')");
  await page.waitForTimeout(1000);

  const partyCards = page.locator('.party-card');
  const count = await partyCards.count();
  console.log(`Total Party Cards: ${count}`);
  for (let i = 0; i < count; i++) {
    const text = await partyCards.nth(i).innerText();
    if (text.includes('ก้าวไกล') || text.includes('อิสระ') || text.includes('ปิยบุตร')) {
      console.log(`\nCard #${i+1}:\n${text}`);
    }
  }

  // 4. Check if there are any broken img elements on the page!
  console.log('\n--- CHECKING FOR BROKEN IMAGES ---');
  const images = await page.locator('img').all();
  let brokenCount = 0;
  for (const img of images) {
    const src = await img.getAttribute('src');
    const naturalWidth = await img.evaluate(node => node.naturalWidth);
    if (naturalWidth === 0) {
      brokenCount++;
      const alt = await img.getAttribute('alt');
      console.log(`⚠️ BROKEN IMAGE: src="${src}", alt="${alt}"`);
    }
  }
  console.log(`Total Broken Images found on page: ${brokenCount}`);

  await browser.close();
})();
