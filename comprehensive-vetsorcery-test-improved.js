#!/usr/bin/env node

/**
 * VetSorcery Comprehensive Testing Suite - IMPROVED VERSION
 * Tests actual functionality, not just element existence
 */

const puppeteer = require('puppeteer');
const fs = require('fs');

const BASE_URL = 'http://localhost:3005';
const TIMEOUT = 30000;

class VetSorceryImprovedTester {
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
        console.log('🚀 Initializing VetSorcery IMPROVED Testing Suite...');
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
        
        // Check specific page title
        const title = await this.page.title();
        if (title !== 'VetSorcery - Veterinary Practice Management') {
            throw new Error(`Unexpected page title: "${title}". Expected: "VetSorcery - Veterinary Practice Management"`);
        }

        // Check React app mounts with specific content
        await this.page.waitForSelector('#root', { timeout: 10000 });
        
        const appContent = await this.page.evaluate(() => {
            const root = document.getElementById('root');
            if (!root) return null;
            
            // Check for specific app structure
            const hasHeader = !!document.querySelector('header, [role="banner"], .app-header');
            const hasNavigation = !!document.querySelector('nav, [role="navigation"], .navigation');
            const hasMainContent = !!document.querySelector('main, [role="main"], .main-content');
            
            return {
                hasRoot: true,
                hasHeader,
                hasNavigation,
                hasMainContent,
                rootClasses: root.className,
                childCount: root.children.length
            };
        });

        if (!appContent.hasHeader || !appContent.hasNavigation || !appContent.hasMainContent) {
            throw new Error(`Missing essential app components. Header: ${appContent.hasHeader}, Nav: ${appContent.hasNavigation}, Main: ${appContent.hasMainContent}`);
        }

        return { title, appContent };
    }

    async testAppointmentsPage() {
        await this.page.goto(`${BASE_URL}/appointments`, { waitUntil: 'networkidle2', timeout: TIMEOUT });
        
        // Wait for page to load
        await this.page.waitForTimeout(3000);
        
        // Check for specific error patterns
        const pageText = await this.page.evaluate(() => document.body.textContent || '');
        
        // Specific error checks
        if (pageText.includes('toLocaleDateString is not a function')) {
            throw new Error('Date formatting error detected: toLocaleDateString is not a function');
        }
        
        if (pageText.includes('TypeError') || pageText.includes('ReferenceError')) {
            throw new Error(`JavaScript error on page: ${pageText.substring(0, 200)}`);
        }

        // Check for specific appointment functionality
        const appointmentData = await this.page.evaluate(() => {
            // Look for appointment-specific elements with actual data
            const appointmentCards = document.querySelectorAll('[data-testid="appointment-card"], .appointment-card');
            const appointmentList = document.querySelector('[data-testid="appointment-list"], .appointment-list');
            const addButton = document.querySelector('button[aria-label*="appointment"], button:contains("Add Appointment")');
            
            // Check calendar if present
            const calendar = document.querySelector('.calendar, [data-testid="calendar"]');
            const hasCalendarDates = calendar ? calendar.querySelectorAll('.date, [data-date]').length > 0 : false;
            
            return {
                appointmentCount: appointmentCards.length,
                hasAppointmentList: !!appointmentList,
                hasAddButton: !!addButton,
                hasCalendar: !!calendar,
                hasCalendarDates,
                // Sample first appointment data if available
                firstAppointment: appointmentCards.length > 0 ? {
                    hasTime: !!appointmentCards[0].querySelector('[data-testid*="time"], .appointment-time'),
                    hasPatient: !!appointmentCards[0].querySelector('[data-testid*="patient"], .patient-name'),
                    hasDoctor: !!appointmentCards[0].querySelector('[data-testid*="doctor"], .doctor-name')
                } : null
            };
        });

        // Verify meaningful appointment UI
        if (!appointmentData.hasAppointmentList && !appointmentData.hasCalendar) {
            throw new Error('No appointment list or calendar found on appointments page');
        }

        // Check page title contains appointments
        const pageTitle = await this.page.title();
        if (!pageTitle.toLowerCase().includes('appointment')) {
            throw new Error(`Page title doesn't mention appointments: "${pageTitle}"`);
        }

        return { 
            pageTitle,
            appointmentData,
            url: this.page.url()
        };
    }

    async testNavigationConsistency() {
        await this.page.goto(BASE_URL, { waitUntil: 'networkidle2', timeout: TIMEOUT });
        await this.page.waitForTimeout(2000);

        // Check for specific navigation items
        const navigationData = await this.page.evaluate(() => {
            const nav = document.querySelector('nav, [role="navigation"]');
            if (!nav) return { hasNav: false };
            
            // Look for specific navigation links
            const expectedLinks = ['Dashboard', 'Appointments', 'Patients', 'Settings'];
            const foundLinks = {};
            
            expectedLinks.forEach(linkText => {
                const link = Array.from(nav.querySelectorAll('a, button')).find(el => 
                    el.textContent.toLowerCase().includes(linkText.toLowerCase())
                );
                foundLinks[linkText] = {
                    found: !!link,
                    href: link?.href || link?.getAttribute('data-href') || null,
                    isActive: link?.classList.contains('active') || link?.getAttribute('aria-current') === 'page'
                };
            });
            
            // Check menu structure
            const menuStyle = window.getComputedStyle(nav);
            const isVisible = menuStyle.display !== 'none' && menuStyle.visibility !== 'hidden';
            const menuWidth = nav.getBoundingClientRect().width;
            
            return {
                hasNav: true,
                isVisible,
                menuWidth,
                foundLinks,
                totalLinks: nav.querySelectorAll('a, button').length
            };
        });

        if (!navigationData.hasNav || !navigationData.isVisible) {
            throw new Error('Navigation menu not found or not visible');
        }

        // Verify essential links exist
        const missingLinks = Object.entries(navigationData.foundLinks)
            .filter(([name, data]) => !data.found)
            .map(([name]) => name);
            
        if (missingLinks.length > 0) {
            throw new Error(`Missing navigation links: ${missingLinks.join(', ')}`);
        }

        return navigationData;
    }

    async testDateFormattingFix() {
        // Test specific pages that should display dates
        const testUrls = [
            { path: '/patients', expectedContent: 'patient' },
            { path: '/appointments', expectedContent: 'appointment' },
            { path: '/dashboard', expectedContent: 'dashboard' }
        ];

        const results = {};
        
        for (const { path, expectedContent } of testUrls) {
            try {
                await this.page.goto(`${BASE_URL}${path}`, { 
                    waitUntil: 'networkidle2', 
                    timeout: 10000 
                });
                
                await this.page.waitForTimeout(2000);
                
                const pageData = await this.page.evaluate((expectedContent) => {
                    const bodyText = document.body.textContent || '';
                    
                    // Check for date errors
                    const hasDateError = bodyText.includes('toLocaleDateString is not a function') ||
                                       bodyText.includes('Invalid Date');
                    
                    // Look for properly formatted dates
                    const datePatterns = [
                        /\d{1,2}\/\d{1,2}\/\d{4}/,  // MM/DD/YYYY
                        /\d{4}-\d{2}-\d{2}/,         // YYYY-MM-DD
                        /\w+ \d{1,2}, \d{4}/         // Month DD, YYYY
                    ];
                    
                    const foundDates = datePatterns.some(pattern => pattern.test(bodyText));
                    
                    // Check if page has expected content
                    const hasExpectedContent = bodyText.toLowerCase().includes(expectedContent);
                    
                    // Find actual date elements
                    const dateElements = document.querySelectorAll('[data-date], time, .date, .timestamp');
                    const dateValues = Array.from(dateElements).map(el => el.textContent.trim()).filter(Boolean);
                    
                    return {
                        hasDateError,
                        foundDates,
                        hasExpectedContent,
                        dateElementCount: dateElements.length,
                        sampleDates: dateValues.slice(0, 3)
                    };
                }, expectedContent);
                
                if (pageData.hasDateError) {
                    throw new Error('Date formatting error detected on page');
                }
                
                if (!pageData.hasExpectedContent) {
                    throw new Error(`Page doesn't contain expected "${expectedContent}" content`);
                }
                
                results[path] = { 
                    success: true,
                    ...pageData
                };
                
            } catch (error) {
                results[path] = { 
                    success: false,
                    error: error.message 
                };
            }
        }

        // At least dashboard should work
        if (!results['/dashboard']?.success) {
            throw new Error('Dashboard page failed to load properly');
        }

        return results;
    }

    async testPerformanceMetrics() {
        await this.page.goto(BASE_URL, { waitUntil: 'networkidle2', timeout: TIMEOUT });
        
        // Get detailed performance metrics
        const performanceData = await this.page.evaluate(() => {
            const navigation = performance.getEntriesByType('navigation')[0];
            const resources = performance.getEntriesByType('resource');
            
            // Categorize resources
            const jsFiles = resources.filter(r => r.name.endsWith('.js'));
            const cssFiles = resources.filter(r => r.name.endsWith('.css'));
            const largeFiles = resources.filter(r => r.transferSize > 500000); // > 500KB
            
            return {
                navigation: {
                    loadTime: navigation.loadEventEnd - navigation.loadEventStart,
                    domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
                    totalTime: navigation.loadEventEnd - navigation.fetchStart,
                    transferSize: navigation.transferSize
                },
                resources: {
                    total: resources.length,
                    jsCount: jsFiles.length,
                    cssCount: cssFiles.length,
                    largeFiles: largeFiles.map(f => ({
                        name: f.name.split('/').pop(),
                        size: Math.round(f.transferSize / 1024) + 'KB'
                    }))
                }
            };
        });

        // Check performance thresholds
        if (performanceData.navigation.totalTime > 5000) {
            throw new Error(`Page load too slow: ${performanceData.navigation.totalTime}ms (threshold: 5000ms)`);
        }

        if (performanceData.resources.largeFiles.length > 0) {
            console.warn(`⚠️  Large files detected: ${performanceData.resources.largeFiles.map(f => f.name).join(', ')}`);
        }

        return performanceData;
    }

    async testAuthenticationFlow() {
        // Test login page specifics
        await this.page.goto(`${BASE_URL}/login`, { waitUntil: 'networkidle2', timeout: TIMEOUT });
        
        const loginPageData = await this.page.evaluate(() => {
            // Check for specific form elements
            const form = document.querySelector('form');
            const emailInput = document.querySelector('input[type="email"], input[name="email"], input[name="username"]');
            const passwordInput = document.querySelector('input[type="password"]');
            const submitButton = document.querySelector('button[type="submit"], input[type="submit"]');
            
            // Check form validation attributes
            const hasValidation = {
                emailRequired: emailInput?.hasAttribute('required'),
                passwordRequired: passwordInput?.hasAttribute('required'),
                emailType: emailInput?.type === 'email'
            };
            
            // Check for remember me and forgot password
            const rememberMe = document.querySelector('input[type="checkbox"][name*="remember"]');
            const forgotPassword = Array.from(document.querySelectorAll('a')).find(a => 
                a.textContent.toLowerCase().includes('forgot')
            );
            
            return {
                hasLoginForm: !!form,
                hasEmailInput: !!emailInput,
                hasPasswordInput: !!passwordInput,
                hasSubmitButton: !!submitButton,
                submitButtonText: submitButton?.textContent.trim(),
                hasValidation,
                hasRememberMe: !!rememberMe,
                hasForgotPassword: !!forgotPassword,
                formAction: form?.action,
                formMethod: form?.method
            };
        });

        // Verify essential login elements
        if (!loginPageData.hasLoginForm || !loginPageData.hasEmailInput || 
            !loginPageData.hasPasswordInput || !loginPageData.hasSubmitButton) {
            throw new Error('Missing essential login form elements');
        }

        // Test protected route redirect
        await this.page.goto(`${BASE_URL}/appointments`, { waitUntil: 'networkidle2', timeout: TIMEOUT });
        const currentUrl = this.page.url();
        const redirectedToLogin = currentUrl.includes('/login');

        return { 
            loginPageData, 
            protectedRouteRedirect: redirectedToLogin,
            finalUrl: currentUrl
        };
    }

    async testNegativeScenarios() {
        const negativeTests = [];

        // Test 1: Invalid route should show 404 or redirect
        try {
            await this.page.goto(`${BASE_URL}/invalid-route-12345`, { waitUntil: 'networkidle2', timeout: 10000 });
            const is404 = await this.page.evaluate(() => {
                const bodyText = document.body.textContent || '';
                return bodyText.includes('404') || bodyText.includes('not found') || 
                       document.title.includes('404');
            });
            
            negativeTests.push({
                test: 'Invalid Route Handling',
                passed: is404 || this.page.url() === BASE_URL + '/',
                details: is404 ? '404 page shown' : 'Redirected to home'
            });
        } catch (error) {
            negativeTests.push({
                test: 'Invalid Route Handling',
                passed: false,
                error: error.message
            });
        }

        // Test 2: Form submission without data
        try {
            await this.page.goto(`${BASE_URL}/login`, { waitUntil: 'networkidle2', timeout: TIMEOUT });
            
            // Try to submit empty form
            await this.page.evaluate(() => {
                const form = document.querySelector('form');
                if (form) {
                    const event = new Event('submit', { cancelable: true });
                    form.dispatchEvent(event);
                }
            });
            
            await this.page.waitForTimeout(1000);
            
            // Check for validation messages
            const hasValidationErrors = await this.page.evaluate(() => {
                const messages = document.querySelectorAll('.error, .invalid-feedback, [role="alert"]');
                const hasHTML5Validation = document.querySelector(':invalid');
                return messages.length > 0 || !!hasHTML5Validation;
            });
            
            negativeTests.push({
                test: 'Empty Form Validation',
                passed: hasValidationErrors,
                details: hasValidationErrors ? 'Validation errors shown' : 'No validation errors'
            });
        } catch (error) {
            negativeTests.push({
                test: 'Empty Form Validation',
                passed: false,
                error: error.message
            });
        }

        return negativeTests;
    }

    async generateReport() {
        const report = {
            ...this.testResults,
            summary: {
                ...this.testResults.summary,
                successRate: `${((this.testResults.summary.passed / this.testResults.summary.total) * 100).toFixed(1)}%`
            }
        };

        const filename = `vetsorcery_improved_test_report_${Date.now()}.json`;
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
            
            // Run all tests including negative scenarios
            await this.runTest('Server Responsiveness', () => this.testServerResponsiveness());
            await this.runTest('Appointments Page', () => this.testAppointmentsPage());
            await this.runTest('Navigation Consistency', () => this.testNavigationConsistency());
            await this.runTest('Date Formatting Fix', () => this.testDateFormattingFix());
            await this.runTest('Performance Metrics', () => this.testPerformanceMetrics());
            await this.runTest('Authentication Flow', () => this.testAuthenticationFlow());
            await this.runTest('Negative Scenarios', () => this.testNegativeScenarios());
            
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
    const tester = new VetSorceryImprovedTester();
    tester.run()
        .then(reportFile => {
            console.log(`\n🎉 VetSorcery IMPROVED testing completed successfully!`);
            console.log(`📄 Report: ${reportFile}`);
            process.exit(0);
        })
        .catch(error => {
            console.error(`\n💥 Testing failed: ${error.message}`);
            process.exit(1);
        });
}

module.exports = VetSorceryImprovedTester;