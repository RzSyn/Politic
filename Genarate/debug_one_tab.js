const { chromium } = require('playwright');
const path = require('path');

(async () => {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    const htmlPath = 'file:///' + path.resolve(__dirname, '../website_constitution.html').replace(/\\/g, '/');
    await page.goto(htmlPath);

    const result = await page.evaluate(() => {
        const figTab = document.getElementById('figures-tab');
        const figBtn = document.querySelector("button[onclick*='figures-tab']");
        
        const beforeDisplay = figTab ? window.getComputedStyle(figTab).display : 'null';
        
        if (figBtn) switchTab('figures-tab', figBtn);
        
        const afterDisplay = figTab ? window.getComputedStyle(figTab).display : 'null';
        const allVisible = Array.from(document.querySelectorAll('.db-tab-content'))
            .filter(c => window.getComputedStyle(c).display !== 'none')
            .map(c => c.id);

        return {
            figTabExists: !!figTab,
            figBtnExists: !!figBtn,
            beforeDisplay,
            afterDisplay,
            allVisible
        };
    });

    console.log("=== ONE TAB DEBUG RESULT ===");
    console.log(result);

    await browser.close();
})();
