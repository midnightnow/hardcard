#!/usr/bin/env node

/**
 * Page-by-Page Tester - Following frontend menu navigation to test each page
 */

const playwright = require('playwright');

class PageByPageTester {
    constructor() {
        this.results = {
            tested_pages: [],
            working_pages: [],
            blank_pages: [],
            broken_pages: [],
            functional_issues: []
        };
    }

    async testSpecificPages() {
        console.log('🧪 TESTING SPECIFIC PAGES FOLLOWING FRONTEND MENUS');
        console.log('=================================================');

        const browser = await playwright.chromium.launch({ headless: false });
        const page = await browser.newPage();

        // Monitor console for errors
        const consoleMessages = [];
        page.on('console', msg => {
            consoleMessages.push(`${msg.type()}: ${msg.text()}`);
        });

        // Test the specific pages mentioned and key navigation pages
        const testPages = [
            'http://localhost:3002/familial-trust-model',
            'http://localhost:3002/bitcoin-wallet', 
            'http://localhost:3002/vault',
            'http://localhost:3002/alexandria',
            'http://localhost:3002/hardcard-creator',
            'http://localhost:3002/music-library',
            'http://localhost:3002/family-profiles',
            'http://localhost:3002/trust-dashboard-page',
            'http://localhost:3002/investment-simulator',
            'http://localhost:3002/portfolio-diversification',
            'http://localhost:3002/security-dashboard',
            'http://localhost:3002/admin-page'
        ];

        for (const testUrl of testPages) {
            await this.testSinglePage(page, testUrl, consoleMessages);
        }

        await browser.close();
        this.generateReport();
        return this.results;
    }

    async testSinglePage(page, url, consoleMessages) {
        const pageName = url.split('/').pop();
        console.log(`\n🔍 Testing: ${pageName}`);
        console.log(`   URL: ${url}`);

        const result = {
            url,
            pageName,
            status: 'unknown',
            hasContent: false,
            contentLength: 0,
            hasElements: false,
            elementCount: 0,
            errors: [],
            load_time: 0
        };

        try {
            const startTime = Date.now();
            
            // Clear previous console messages
            consoleMessages.length = 0;
            
            await page.goto(url, { waitUntil: 'networkidle', timeout: 15000 });
            result.load_time = Date.now() - startTime;

            // Wait a bit for React to render
            await page.waitForTimeout(2000);

            // Analyze page content
            const analysis = await page.evaluate(() => {
                const body = document.body;
                const root = document.querySelector('#root');
                
                return {
                    title: document.title,
                    bodyText: body.textContent.trim(),
                    bodyTextLength: body.textContent.trim().length,
                    elementCount: document.querySelectorAll('*').length,
                    rootHtml: root ? root.innerHTML.substring(0, 300) : 'NO ROOT',
                    hasMain: !!document.querySelector('main'),
                    hasNav: !!document.querySelector('nav'),
                    hasHeader: !!document.querySelector('header'),
                    hasButtons: document.querySelectorAll('button').length,
                    hasInputs: document.querySelectorAll('input').length,
                    hasLinks: document.querySelectorAll('a').length
                };
            });

            result.hasContent = analysis.bodyTextLength > 100;
            result.contentLength = analysis.bodyTextLength;
            result.hasElements = analysis.elementCount > 20;
            result.elementCount = analysis.elementCount;

            // Check for errors in console
            const errors = consoleMessages.filter(msg => msg.startsWith('error:'));
            result.errors = errors;

            // Determine status
            if (errors.length > 0) {
                result.status = 'broken';
                this.results.broken_pages.push(result);
                console.log(`   ❌ BROKEN: ${errors.length} errors found`);
            } else if (!result.hasContent || result.contentLength < 50) {
                result.status = 'blank';
                this.results.blank_pages.push(result);
                console.log(`   ⚪ BLANK: Only ${result.contentLength} characters`);
            } else if (result.hasContent && result.hasElements) {
                result.status = 'working';
                this.results.working_pages.push(result);
                console.log(`   ✅ WORKING: ${result.contentLength} chars, ${result.elementCount} elements`);
            } else {
                result.status = 'partial';
                this.results.functional_issues.push(result);
                console.log(`   🟡 PARTIAL: Has content but may have issues`);
            }

            // Show detailed analysis for problematic pages
            if (result.status !== 'working') {
                console.log(`   📊 Analysis:`, {
                    content: result.contentLength + ' chars',
                    elements: result.elementCount,
                    buttons: analysis.hasButtons,
                    inputs: analysis.hasInputs,
                    links: analysis.hasLinks
                });
                console.log(`   🔍 Root HTML: ${analysis.rootHtml.substring(0, 100)}...`);
                if (errors.length > 0) {
                    console.log(`   🚨 Errors:`, errors.slice(0, 3));
                }
            }

        } catch (error) {
            result.status = 'error';
            result.errors = [error.message];
            this.results.broken_pages.push(result);
            console.log(`   💥 ERROR: ${error.message}`);
        }

        this.results.tested_pages.push(result);
    }

    generateReport() {
        console.log('\n📊 PAGE-BY-PAGE TESTING SUMMARY');
        console.log('===============================');
        console.log(`Total Pages Tested: ${this.results.tested_pages.length}`);
        console.log(`✅ Working Pages: ${this.results.working_pages.length}`);
        console.log(`⚪ Blank Pages: ${this.results.blank_pages.length}`);
        console.log(`❌ Broken Pages: ${this.results.broken_pages.length}`);
        console.log(`🟡 Partial/Issues: ${this.results.functional_issues.length}`);

        if (this.results.blank_pages.length > 0) {
            console.log('\n⚪ BLANK PAGES NEEDING FIXES:');
            this.results.blank_pages.forEach(page => {
                console.log(`   - ${page.pageName}: ${page.contentLength} chars`);
            });
        }

        if (this.results.broken_pages.length > 0) {
            console.log('\n❌ BROKEN PAGES WITH ERRORS:');
            this.results.broken_pages.forEach(page => {
                console.log(`   - ${page.pageName}: ${page.errors.length} errors`);
            });
        }

        // Save detailed report
        const fs = require('fs');
        const reportPath = '/Users/studio/hardcard/PAGE_BY_PAGE_TEST_RESULTS.json';
        fs.writeFileSync(reportPath, JSON.stringify(this.results, null, 2));
        console.log(`\n📋 Detailed results saved to: ${reportPath}`);
    }
}

async function main() {
    const tester = new PageByPageTester();
    await tester.testSpecificPages();
}

if (require.main === module) {
    main().catch(console.error);
}

module.exports = { PageByPageTester };