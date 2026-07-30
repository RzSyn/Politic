const { chromium } = require('playwright');
const path = require('path');

(async () => {
    console.log("Launching Chromium browser for interactive direct evaluation test...");
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

    const htmlPath = 'file:///' + path.resolve(__dirname, '../website_constitution.html').replace(/\\/g, '/');
    await page.goto(htmlPath, { waitUntil: 'load' });

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

    let passed = 0;
    let failed = 0;

    for (let i = 0; i < tabIds.length; i++) {
        const tid = tabIds[i];

        const report = await page.evaluate((targetId) => {
            const btn = document.querySelector(`button[onclick*="'${targetId}'"]`);
            if (btn) {
                switchTab(targetId, btn);
            } else {
                switchTab(targetId);
            }

            const tabs = Array.from(document.querySelectorAll('.db-tab-content'));
            const visibleTabs = tabs.filter(t => {
                const style = window.getComputedStyle(t);
                return style.display !== 'none';
            }).map(t => t.id);

            return {
                visibleCount: visibleTabs.length,
                visibleIds: visibleTabs
            };
        }, tid);

        if (report.visibleCount === 1 && report.visibleIds[0] === tid) {
            console.log(`✅ Tab #${(i+1).toString().padStart(2, ' ')} (${tid.padEnd(28, ' ')}): PERFECT! ONLY target tab '${tid}' is visible in DOM.`);
            passed++;
        } else {
            console.log(`❌ Tab #${(i+1).toString().padStart(2, ' ')} (${tid.padEnd(28, ' ')}): FAILED! Visible tabs: [${report.visibleIds.join(', ')}]`);
            failed++;
        }
    }

    console.log(`\n=== AUTOMATED BROWSER DIRECT TEST RESULTS ===`);
    console.log(`Total Tabs Tested: ${tabIds.length}`);
    console.log(`Passed: ${passed}`);
    console.log(`Failed: ${failed}`);

    await browser.close();
})();
