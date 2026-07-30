const { test, expect } = require('@playwright/test');
const path = require('path');

test('Verify interactive mouse movement and tab isolation across all 34 tabs', async ({ page }) => {
    const htmlPath = 'file:///' + path.resolve(__dirname, '../website_constitution.html').replace(/\\/g, '/');
    console.log("Loading page:", htmlPath);
    await page.goto(htmlPath, { waitUntil: 'load' });

    // Move mouse interactively across page elements
    await page.mouse.move(100, 100);
    await page.mouse.move(400, 300);
    await page.mouse.move(700, 500);

    const tabIds = [
        'history-tab', 'referendum-tab', 'constitutions-tab', 'early-const-tab',
        'rama7-tab', 'rama9-tab', 'chakri-tab', 'siripanya-tab',
        'judiciary-tab', 'legislative-tab', 'parties-tab', 'orange-party-tab',
        'independent-organs-tab', 'local-govt-tab', 'ministries-tab', 'khonlalike-tab',
        'bancc-tab', 'flag-tab', 'national-songs-tab', 'thai-canal-tab',
        'paradox-ai-tab', 'pms-tab', 'goc-tab', 'geopolitics-tab',
        'world-economy-tab', 'laos-kingdom-tab', 'alliances-disputes-tab', 'international-missions-tab',
        'tsl-dashboard-tab', 'the-plague-series-tab', 'dexibola-virus-tab', 'thai-nobel-tab',
        'figures-tab', 'villains-tab'
    ];

    console.log(`\nStarting Playwright Browser Audit for ${tabIds.length} Tabs...`);

    for (let i = 0; i < tabIds.length; i++) {
        const tid = tabIds[i];
        const btn = page.locator(`button[onclick*="'${tid}'"]`).first();
        
        await expect(btn).toBeVisible();

        // Move mouse over button
        await btn.hover();
        
        // Click button
        await btn.click();
        await page.waitForTimeout(50);

        // Audit visibility of all 34 tab contents in browser DOM
        const visibleTabs = await page.evaluate(() => {
            const tabs = Array.from(document.querySelectorAll('.db-tab-content'));
            return tabs.filter(t => {
                const style = window.getComputedStyle(t);
                return style.display !== 'none' && style.visibility !== 'hidden' && parseInt(style.height) > 0;
            }).map(t => t.id);
        });

        console.log(`Tab #${(i+1).toString().padStart(2, ' ')} (${tid.padEnd(28, ' ')}): Visible tabs in DOM = [${visibleTabs.join(', ')}]`);
        
        expect(visibleTabs.length).toBe(1);
        expect(visibleTabs[0]).toBe(tid);
    }

    console.log("\n✅ ALL 34 TABS PASSED BROWSER ISOLATION TEST!");
});
