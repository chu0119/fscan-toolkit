"""Take detailed screenshots of both tools for the README."""
import asyncio
from playwright.async_api import async_playwright
import os

BASE = r'D:\fscan'
OUT = os.path.join(BASE, 'screenshots')

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()

        # ── Builder screenshots ──

        # 1. Initial state - default fscan
        page = await browser.new_page(viewport={'width': 1440, 'height': 900})
        await page.goto(f'file:///{BASE}/fscan-command-builder.html', wait_until='networkidle')
        await page.wait_for_timeout(1500)
        await page.screenshot(path=os.path.join(OUT, 'builder-01-default.png'), full_page=False)
        print('✓ builder-01-default.png')

        # 2. Fill in a typical scanning scenario
        await page.evaluate("""
            const vals = {
                target: '192.168.1.0/24',
                ports: '80,443,8080,8443,3306,1433,6379',
                threads: '600',
                username: 'admin',
                password: 'admin123',
                outputFile: 'scan-2026-08-10.txt',
                outputFormat: 'json'
            };
            for (const [k, v] of Object.entries(vals)) {
                const el = document.getElementById('f-' + k);
                if (el) { el.value = v; onCh(k, v); }
            }
        """)
        await page.wait_for_timeout(1000)
        await page.screenshot(path=os.path.join(OUT, 'builder-02-filled.png'), full_page=False)
        print('✓ builder-02-filled.png')

        # 3. Switch to pscan to show param name mapping
        await page.evaluate("document.getElementById('tsel').value = 'pscan'; onToolSwitch()")
        await page.wait_for_timeout(1500)
        await page.screenshot(path=os.path.join(OUT, 'builder-03-pscan.png'), full_page=False)
        print('✓ builder-03-pscan.png')

        # 4. Switch to fscan-web
        await page.evaluate("document.getElementById('tsel').value = 'web'; onToolSwitch()")
        await page.wait_for_timeout(1000)
        await page.screenshot(path=os.path.join(OUT, 'builder-04-web.png'), full_page=False)
        print('✓ builder-04-web.png')

        # 5. Back to fscan, show settings modal
        await page.evaluate("document.getElementById('tsel').value = 'fscan'; onToolSwitch()")
        await page.wait_for_timeout(1000)
        await page.evaluate("showCfg()")
        await page.wait_for_timeout(800)
        await page.screenshot(path=os.path.join(OUT, 'builder-05-settings.png'), full_page=False)
        print('✓ builder-05-settings.png')

        # ── Report Generator screenshots ──

        # 6. Initial empty state
        page2 = await browser.new_page(viewport={'width': 1440, 'height': 900})
        await page2.goto(f'file:///{BASE}/fscan-report-generator.html', wait_until='networkidle')
        await page2.wait_for_timeout(1500)
        await page2.screenshot(path=os.path.join(OUT, 'report-01-empty.png'), full_page=False)
        print('✓ report-01-empty.png')

        # 7. Load sample data
        await page2.evaluate("loadSample('sample')")
        await page2.wait_for_timeout(2000)
        await page2.screenshot(path=os.path.join(OUT, 'report-02-sample.png'), full_page=False)
        print('✓ report-02-sample.png')

        await browser.close()

asyncio.run(main())
