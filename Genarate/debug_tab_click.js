const { chromium } = require('playwright');
const path = require('path');

(async () => {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

    const htmlPath = 'file:///' + path.resolve(__dirname, '../website_constitution.html').replace(/\\/g, '/');
    await page.goto(htmlPath, { waitUntil: 'load' });

    const btn = await page.$("button[onclick*=\"'superpower-matrix-tab'\"]");
    console.log("Button Found:", !!btn);

    if (btn) {
        await btn.click();
        await page.waitForTimeout(300);

        const state = await page.evaluate(() => {
            const el = document.getElementById('superpower-matrix-tab');
            if (!el) return { exists: false };
            const style = window.getComputedStyle(el);
            return {
                exists: true,
                display: style.display,
                visibility: style.visibility,
                height: style.height,
                offsetHeight: el.offsetHeight,
                classList: Array.from(el.classList)
            };
        });
        console.log("Superpower Matrix Tab Computed Style:", state);
    }

    await browser.close();
})();
