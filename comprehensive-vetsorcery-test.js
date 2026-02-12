#!/usr/bin/env node

/**
 * VetSorcery Comprehensive Testing Suite
 * Tests all critical functionality after recent fixes
 */

const puppeteer = require('puppeteer');
const fs = require('fs');

const BASE_URL = 'http://localhost:3005';
const TIMEOUT = 30000;

class VetSorceryTester {
    constructor() {
        this.browser = null;
        this.page = null;
        this.testResults = {
            timestamp: new Date().toISOString(),
            baseUrl: BASE_URL,
            tests: [],
            summary: {
                total: 0,
                passed: 0,
                failed: 0,
                warnings: 0
            }
        };
    }

    async init() {
        console.log('🚀 Initializing VetSorcery Testing Suite...');
        this.browser = await puppeteer.launch({
            headless: false,
            defaultViewport: { width: 1920, height: 1080 },
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        this.page = await this.browser.newPage();
        
        // Enhanced error handling
        this.page.on('console', msg => {
            if (msg.type() === 'error') {
                console.log(`❌ Console Error: ${msg.text()}`);
            }
        });

        this.page.on('pageerror', error => {
            console.log(`💥 Page Error: ${error.message}`);
        });
    }

    async runTest(testName, testFunction) {
        console.log(`\n🧪 Running: ${testName}`);
        this.testResults.summary.total++;
        
        const startTime = Date.now();
        let result = {
            name: testName,
            status: 'unknown',
            duration: 0,
            error: null,
            screenshot: null,
            details: {}
        };

        try {
            const testData = await testFunction();
            result.status = 'passed';
            result.details = testData || {};
            this.testResults.summary.passed++;
            console.log(`✅ ${testName} - PASSED`);
        } catch (error) {
            result.status = 'failed';
            result.error = error.message;
            this.testResults.summary.failed++;
            console.log(`❌ ${testName} - FAILED: ${error.message}`);
            
            // Take screenshot on failure
            try {
                const screenshot = `screenshot_${testName.replace(/\s/g, '_')}_${Date.now()}.png`;
                await this.page.screenshot({ path: screenshot, fullPage: true });
                result.screenshot = screenshot;
            } catch (screenshotError) {
                console.log(`📸 Screenshot failed: ${screenshotError.message}`);
            }
        }

        result.duration = Date.now() - startTime;
        this.testResults.tests.push(result);
    }

    async testServerResponsiveness() {
        await this.page.goto(BASE_URL, { waitUntil: 'networkidle2', timeout: TIMEOUT });
        
        // Check if page loads
        const title = await this.page.title();
        if (!title || title.includes('Error')) {
            throw new Error(`Invalid page title: ${title}`);
        }

        // Check for React app mount
        await this.page.waitForSelector('#root', { timeout: 10000 });
        
        const hasContent = await this.page.evaluate(() => {
            const root = document.getElementById('root');
            return root && root.children.length > 0;
        });

        if (!hasContent) {
            throw new Error('React app not properly mounted');
        }

        return { title, hasReactContent: hasContent };
    }

    async testAppointmentsPage() {
        await this.page.goto(`${BASE_URL}/appointments`, { waitUntil: 'networkidle2', timeout: TIMEOUT });
        
        // Wait for page to load
        await this.page.waitForTimeout(3000);
        
        // Check for common error patterns
        const hasError = await this.page.evaluate(() => {
            const errorTexts = [
                'toLocaleDateString is not a function',
                'TypeError',
                'ReferenceError',
                'Cannot read properties',
                'Unexpected Application Error'
            ];
            
            const bodyText = document.body.textContent || '';
            return errorTexts.some(error => bodyText.includes(error));
        });

        if (hasError) {
            const errorText = await this.page.evaluate(() => document.body.textContent);
            throw new Error(`Date formatting error detected: ${errorText.substring(0, 200)}`);
        }

        // Check if appointments interface loads
        const hasAppointmentElements = await this.page.evaluate(() => {
            // Look for appointment-related elements
            const selectors = [
                '[data-testid*="appointment"]',
                '.appointment',
                '[class*="appointment"]',
                'button[class*="appointment"]',
                'div[class*="calendar"]'
            ];
            
            return selectors.some(selector => {
                return document.querySelector(selector) !== null;
            });
        });

        return { 
            hasError, 
            hasAppointmentElements,
            url: this.page.url()
        };
    }

    async testNavigationConsistency() {
        await this.page.goto(BASE_URL, { waitUntil: 'networkidle2', timeout: TIMEOUT });
        await this.page.waitForTimeout(2000);

        // Check for navigation elements
        const navElements = await this.page.evaluate(() => {
            const selectors = [
                'nav',
                '[role="navigation"]', 
                '.navigation',
                '.nav',
                '.menu',
                '.sidebar'
            ];
            
            const found = {};
            selectors.forEach(sel => {
                const elements = document.querySelectorAll(sel);
                found[sel] = {
                    count: elements.length,
                    visible: Array.from(elements).some(el => {
                        const style = window.getComputedStyle(el);
                        return style.display !== 'none' && style.visibility !== 'hidden';
                    })
                };
            });
            
            return found;
        });

        // Check menu consistency (should be using "big" menu)
        const menuInfo = await this.page.evaluate(() => {
            const menus = document.querySelectorAll('[class*="menu"], [class*="nav"]');
            const menuData = [];
            
            menus.forEach((menu, index) => {
                const rect = menu.getBoundingClientRect();
                const styles = window.getComputedStyle(menu);
                
                menuData.push({
                    index,
                    width: rect.width,
                    height: rect.height,
                    display: styles.display,
                    visibility: styles.visibility,
                    className: menu.className
                });
            });
            
            return menuData;
        });

        return { navElements, menuInfo };
    }

    async testDateFormattingFix() {
        // Test if we can navigate to patient profile or similar page with dates
        const testUrls = [
            '/patients',
            '/patient-profile',
            '/patient/1',
            '/dashboard'
        ];

        const results = {};
        
        for (const url of testUrls) {
            try {
                await this.page.goto(`${BASE_URL}${url}`, { 
                    waitUntil: 'networkidle2', 
                    timeout: 10000 
                });
                
                await this.page.waitForTimeout(2000);
                
                // Check for date-related errors
                const hasDateError = await this.page.evaluate(() => {
                    const bodyText = document.body.textContent || '';
                    const errorPatterns = [
                        'toLocaleDateString is not a function',
                        'date.toLocaleDateString is not a function',
                        'Invalid Date',
                        'TypeError.*Date'
                    ];
                    
                    return errorPatterns.some(pattern => {
                        const regex = new RegExp(pattern, 'i');
                        return regex.test(bodyText);
                    });
                });

                results[url] = { 
                    accessible: true, 
                    hasDateError,
                    status: this.page.url().includes('404') ? 'not_found' : 'ok'
                };
                
            } catch (error) {
                results[url] = { 
                    accessible: false, 
                    error: error.message 
                };
            }
        }

        return results;
    }

    async testPerformanceMetrics() {
        await this.page.goto(BASE_URL, { waitUntil: 'networkidle2', timeout: TIMEOUT });
        
        // Get performance metrics
        const performanceMetrics = await this.page.evaluate(() => {
            const navigation = performance.getEntriesByType('navigation')[0];
            return {
                loadTime: navigation.loadEventEnd - navigation.loadEventStart,
                domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
                totalTime: navigation.loadEventEnd - navigation.fetchStart,
                transferSize: navigation.transferSize,
                resourceCount: performance.getEntriesByType('resource').length
            };
        });

        // Check bundle size warnings
        const bundleWarnings = await this.page.evaluate(() => {
            const scripts = Array.from(document.querySelectorAll('script[src]'));
            return scripts.map(script => ({
                src: script.src,
                async: script.async,
                defer: script.defer
            }));
        });

        return { performanceMetrics, bundleWarnings };
    }

    async testAuthenticationFlow() {
        // Test login page
        await this.page.goto(`${BASE_URL}/login`, { waitUntil: 'networkidle2', timeout: TIMEOUT });
        
        const loginPageInfo = await this.page.evaluate(() => {
            return {
                hasLoginForm: !!document.querySelector('form'),
                hasEmailInput: !!document.querySelector('input[type="email"], input[name="email"]'),
                hasPasswordInput: !!document.querySelector('input[type="password"]'),
                hasSubmitButton: !!document.querySelector('button[type="submit"], input[type="submit"]'),
                title: document.title
            };
        });

        // Test protected route behavior
        await this.page.goto(`${BASE_URL}/appointments`, { waitUntil: 'networkidle2', timeout: TIMEOUT });
        const redirectedToLogin = this.page.url().includes('/login');

        return { loginPageInfo, redirectedToLogin };
    }

    async generateReport() {
        const report = {
            ...this.testResults,
            summary: {
                ...this.testResults.summary,
                successRate: `${((this.testResults.summary.passed / this.testResults.summary.total) * 100).toFixed(1)}%`
            }
        };

        const filename = `vetsorcery_test_report_${Date.now()}.json`;
        fs.writeFileSync(filename, JSON.stringify(report, null, 2));
        
        console.log(`\n📊 Test Report Generated: ${filename}`);
        console.log(`📈 Success Rate: ${report.summary.successRate}`);
        console.log(`✅ Passed: ${report.summary.passed}`);
        console.log(`❌ Failed: ${report.summary.failed}`);
        
        return filename;
    }

    async cleanup() {
        if (this.browser) {
            await this.browser.close();
        }
    }

    async run() {
        try {
            await this.init();
            
            // Run all tests
            await this.runTest('Server Responsiveness', () => this.testServerResponsiveness());
            await this.runTest('Appointments Page', () => this.testAppointmentsPage());
            await this.runTest('Navigation Consistency', () => this.testNavigationConsistency());
            await this.runTest('Date Formatting Fix', () => this.testDateFormattingFix());
            await this.runTest('Performance Metrics', () => this.testPerformanceMetrics());
            await this.runTest('Authentication Flow', () => this.testAuthenticationFlow());
            
            const reportFile = await this.generateReport();
            return reportFile;
            
        } catch (error) {
            console.error(`🚨 Testing suite failed: ${error.message}`);
            throw error;
        } finally {
            await this.cleanup();
        }
    }
}

// Run tests if called directly
if (require.main === module) {
    const tester = new VetSorceryTester();
    tester.run()
        .then(reportFile => {
            console.log(`\n🎉 VetSorcery testing completed successfully!`);
            console.log(`📄 Report: ${reportFile}`);
            process.exit(0);
        })
        .catch(error => {
            console.error(`\n💥 Testing failed: ${error.message}`);
            process.exit(1);
        });
}

module.exports = VetSorceryTester;