const { chromium } = require('playwright');
const path = require('path');

(async () => {
    console.log("Launching Chromium browser for interactive live test...");
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

    const htmlPath = 'file:///' + path.resolve(__dirname, '../website_constitution.html').replace(/\\/g, '/');
    console.log("Navigating to:", htmlPath);
    await page.goto(htmlPath, { waitUntil: 'load' });

    console.log("\n=== STARTING INTERACTIVE MOUSE MOVEMENT & TAB CLICK SIMULATION ===");

    // Move mouse across navbar
    await page.mouse.move(200, 200);
    await page.mouse.move(500, 200);
    await page.mouse.move(800, 200);

    const tabIds = [
        'history-tab', 'referendum-tab', 'constitutions-tab', 'early-const-tab',
        'rama7-tab', 'rama9-tab', 'chakri-tab', 'siripanya-tab',
        'judiciary-tab', 'legislative-tab', 'hierarchy-laws-tab', 'parties-tab', 'orange-party-tab',
        'independent-organs-tab', 'local-govt-tab', 'ministries-tab', 'khonlalike-tab',
        'bancc-tab', 'flag-tab', 'national-songs-tab', 'thai-canal-tab',
        'paradox-ai-tab', 'pms-tab', 'goc-tab', 'geopolitics-tab', 'superpower-matrix-tab',
        'world-economy-tab', 'laos-kingdom-tab', 'alliances-disputes-tab', 'international-missions-tab',
        'tsl-dashboard-tab', 'the-plague-series-tab', 'dexibola-virus-tab', 'thai-nobel-tab',
        'figures-tab', 'villains-tab'
    ];

    let passed = 0;
    let failed = 0;

    for (let i = 0; i < tabIds.length; i++) {
        const tid = tabIds[i];
        const btnSelector = `button[onclick*="'${tid}'"]`;
        const btn = await page.$(btnSelector);

        if (!btn) {
            console.log(`❌ Button for tab '${tid}' NOT FOUND!`);
            failed++;
            continue;
        }

        // Hover mouse over button
        const box = await btn.boundingBox();
        if (box) {
            await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
        }

        // Click button
        await btn.click();
        await page.waitForTimeout(50);

        // Audit visibility of all tabs in DOM using offsetHeight > 0
        const visibilityReport = await page.evaluate((targetId) => {
            const tabs = Array.from(document.querySelectorAll('.db-tab-content'));
            let visibleCount = 0;
            let visibleIds = [];

            tabs.forEach(t => {
                const style = window.getComputedStyle(t);
                const isVis = style.display !== 'none' && style.visibility !== 'hidden' && t.offsetHeight > 0;
                if (isVis) {
                    visibleCount++;
                    visibleIds.push(t.id);
                }
            });

            const target = document.getElementById(targetId);
            const targetStyle = target ? window.getComputedStyle(target) : null;
            const targetVisible = targetStyle && targetStyle.display !== 'none' && target.offsetHeight > 0;

            return {
                visibleCount,
                visibleIds,
                targetVisible
            };
        }, tid);

        if (visibilityReport.visibleCount === 1 && visibilityReport.visibleIds[0] === tid && visibilityReport.targetVisible) {
            console.log(`✅ Tab #${(i+1).toString().padStart(2, ' ')} (${tid.padEnd(28, ' ')}): ONLY target tab is visible! Zero leakage.`);
            passed++;
        } else {
            console.log(`❌ Tab #${(i+1).toString().padStart(2, ' ')} (${tid.padEnd(28, ' ')}): FAILED! Visible tabs: [${visibilityReport.visibleIds.join(', ')}]`);
            failed++;
        }
    }

    console.log(`\n=== AUTOMATED BROWSER TEST RESULTS ===`);
    console.log(`Total Tabs Tested: ${tabIds.length}`);
    console.log(`Passed: ${passed}`);
    console.log(`Failed: ${failed}`);

    await browser.close();
})();
