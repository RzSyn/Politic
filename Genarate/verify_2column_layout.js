const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
  const filePath = 'file:///' + path.resolve('website_constitution.html').replace(/\\/g, '/');
  await page.goto(filePath);

  // Click Orange Party Tab
  await page.click("button:has-text('พรรคสีส้ม')");
  await page.waitForTimeout(500);

  // Measure PM cards 2-column flex alignment
  const cardsInfo = await page.evaluate(() => {
    const orangeTab = document.getElementById('orange-party-tab');
    if (!orangeTab) return [];

    // Find all PM flex card containers inside orange-party-tab
    const containers = Array.from(orangeTab.querySelectorAll('div')).filter(d => {
      const style = window.getComputedStyle(d);
      return style.display === 'flex' && style.gap === '28px';
    });

    return containers.map((card, idx) => {
      const children = Array.from(card.children);
      const leftCol = children[0];
      const rightCol = children[1];
      const leftRect = leftCol ? leftCol.getBoundingClientRect() : null;
      const rightRect = rightCol ? rightCol.getBoundingClientRect() : null;

      return {
        cardIndex: idx + 1,
        childrenCount: children.length,
        isSideBySide: leftRect && rightRect && rightRect.left > leftRect.left + 200,
        leftTop: leftRect ? leftRect.top : null,
        rightTop: rightRect ? rightRect.top : null,
        leftWidth: leftRect ? leftRect.width : null,
        rightWidth: rightRect ? rightRect.width : null,
        rightColTextSnippet: rightCol ? rightCol.innerText.slice(0, 80).replace(/\n/g, ' ') : 'N/A'
      };
    });
  });

  console.log('PM Cards 2-Column Layout Test Results:');
  console.log(JSON.stringify(cardsInfo, null, 2));

  // Take screenshot of Pita's card for verification artifact
  const pitaCard = await page.locator("div:has-text('นายกรัฐมนตรีคนที่ ๑๗: พิธา ลิ้มเจริญรัตน์')").first();
  await pitaCard.screenshot({ path: path.resolve('pitacard_fixed_2col.png') });
  console.log("Saved screenshot to pitacard_fixed_2col.png!");

  await browser.close();
})();
