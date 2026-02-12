#!/usr/bin/env node

/**
 * Hardcard Launch Readiness Tester
 * Comprehensive testing suite for all Hardcard applications
 */

const fs = require('fs');
const path = require('path');
const { execSync, spawn } = require('child_process');
const puppeteer = require('puppeteer');

class HardcardLaunchTester {
    constructor() {
        this.results = {
            timestamp: new Date().toISOString(),
            applications: {},
            security: {},
            performance: {},
            ux: {},
            privacy: {},
            recommendations: []
        };

        this.applications = [
            { name: 'main_frontend', url: 'http://localhost:3000', path: '/Users/studio/hardcard/frontend' },
            { name: 'api_backend', url: 'http://localhost:8000', path: '/Users/studio/hardcard/backend' },
            { name: 'hardcard_suite', url: 'http://localhost:3001', path: '/Users/studio/hardcard/hardcard-suite' },
            { name: 'vetsorcery', url: 'http://localhost:3005', path: '/Users/studio/hardcard/hardcard-suite/apps/vetsorcery' },
            { name: 'governance_dashboard', url: 'http://localhost:8080', path: '/Users/studio/hardcard/hardcard-governance/web' }
        ];

        this.testRoutes = [
            '/',
            '/dashboard',
            '/admin',
            '/login',
            '/register',
            '/profile',
            '/products',
            '/cart',
            '/checkout',
            '/analytics',
            '/settings',
            '/help'
        ];
    }

    async init() {
        console.log('🚀 Initializing Hardcard Launch Readiness Tester...');
        this.browser = await puppeteer.launch({ 
            headless: false,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        this.page = await this.browser.newPage();
        await this.page.setViewport({ width: 1920, height: 1080 });
    }

    async testApplication(app) {
        console.log(`\n🔍 Testing ${app.name} at ${app.url}...`);
        
        const appResults = {
            name: app.name,
            url: app.url,
            status: 'unknown',
            pages: {},
            security: {},
            performance: {},
            ux: {},
            errors: []
        };

        try {
            // Test if application is running
            await this.page.goto(app.url, { 
                waitUntil: 'networkidle2',
                timeout: 10000 
            });
            
            appResults.status = 'running';
            console.log(`✅ ${app.name} is running`);

            // Test each route
            for (const route of this.testRoutes) {
                await this.testRoute(app, route, appResults);
            }

            // Performance testing
            await this.testPerformance(app, appResults);

            // Security testing
            await this.testSecurity(app, appResults);

            // UX/UI testing
            await this.testUX(app, appResults);

        } catch (error) {
            appResults.status = 'error';
            appResults.errors.push(`Failed to load ${app.url}: ${error.message}`);
            console.log(`❌ ${app.name} failed to load: ${error.message}`);
        }

        return appResults;
    }

    async testRoute(app, route, appResults) {
        const fullUrl = `${app.url}${route}`;
        console.log(`  📄 Testing route: ${route}`);

        try {
            const startTime = Date.now();
            
            await this.page.goto(fullUrl, { 
                waitUntil: 'networkidle2',
                timeout: 15000 
            });

            const loadTime = Date.now() - startTime;

            // Check for errors in console
            const logs = await this.page.evaluate(() => {
                return window.console._logs || [];
            });

            // Check page content
            const title = await this.page.title();
            const bodyText = await this.page.evaluate(() => document.body.innerText);
            const hasContent = bodyText.length > 100;

            // Check for React/Vue errors
            const hasJSErrors = logs.some(log => 
                log.level === 'error' || 
                log.text.includes('Error') || 
                log.text.includes('Failed')
            );

            // Check accessibility
            const accessibilityScore = await this.checkAccessibility();

            // Take screenshot
            const screenshotPath = `screenshots/launch_test_${app.name}_${route.replace(/\//g, '_')}_${Date.now()}.png`;
            await this.page.screenshot({ 
                path: screenshotPath,
                fullPage: true 
            });

            appResults.pages[route] = {
                status: 'success',
                loadTime,
                title,
                hasContent,
                hasJSErrors,
                accessibilityScore,
                screenshot: screenshotPath,
                contentLength: bodyText.length
            };

            console.log(`    ✅ ${route} loaded in ${loadTime}ms`);

        } catch (error) {
            appResults.pages[route] = {
                status: 'error',
                error: error.message
            };
            console.log(`    ❌ ${route} failed: ${error.message}`);
        }
    }

    async testPerformance(app, appResults) {
        console.log(`  ⚡ Testing performance for ${app.name}...`);

        try {
            // Enable performance monitoring
            await this.page.goto(app.url);
            
            const performanceMetrics = await this.page.evaluate(() => {
                const perfData = performance.getEntriesByType('navigation')[0];
                return {
                    domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
                    loadComplete: perfData.loadEventEnd - perfData.loadEventStart,
                    firstPaint: performance.getEntriesByType('paint')[0]?.startTime || 0,
                    firstContentfulPaint: performance.getEntriesByType('paint')[1]?.startTime || 0
                };
            });

            // Memory usage
            const memoryInfo = await this.page.evaluate(() => {
                return performance.memory ? {
                    usedJSHeapSize: performance.memory.usedJSHeapSize,
                    totalJSHeapSize: performance.memory.totalJSHeapSize,
                    jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
                } : null;
            });

            // Network requests audit
            const networkRequests = await this.page.evaluate(() => {
                return performance.getEntriesByType('resource').map(resource => ({
                    name: resource.name,
                    duration: resource.duration,
                    size: resource.transferSize || resource.encodedBodySize || 0
                }));
            });

            appResults.performance = {
                metrics: performanceMetrics,
                memory: memoryInfo,
                networkRequests: networkRequests.length,
                totalTransferSize: networkRequests.reduce((sum, req) => sum + req.size, 0),
                slowRequests: networkRequests.filter(req => req.duration > 1000)
            };

        } catch (error) {
            appResults.performance.error = error.message;
        }
    }

    async testSecurity(app, appResults) {
        console.log(`  🔒 Testing security for ${app.name}...`);

        try {
            await this.page.goto(app.url);

            // Check HTTPS
            const isHTTPS = app.url.startsWith('https://');

            // Check for common security headers
            const response = await this.page.goto(app.url);
            const headers = response.headers();

            const securityHeaders = {
                'content-security-policy': headers['content-security-policy'],
                'x-frame-options': headers['x-frame-options'],
                'x-content-type-options': headers['x-content-type-options'],
                'strict-transport-security': headers['strict-transport-security'],
                'x-xss-protection': headers['x-xss-protection']
            };

            // Check for sensitive data exposure
            const pageContent = await this.page.content();
            const hasSensitiveData = [
                'password',
                'api_key',
                'secret',
                'token',
                'private_key'
            ].some(term => pageContent.toLowerCase().includes(term));

            // Check for XSS vulnerabilities (basic)
            const xssTest = await this.page.evaluate(() => {
                try {
                    const testScript = '<script>alert("xss")</script>';
                    const div = document.createElement('div');
                    div.innerHTML = testScript;
                    return div.innerHTML.includes('<script>');
                } catch (e) {
                    return false;
                }
            });

            appResults.security = {
                isHTTPS,
                securityHeaders,
                hasSensitiveData,
                xssVulnerable: xssTest,
                score: this.calculateSecurityScore({ isHTTPS, securityHeaders, hasSensitiveData, xssTest })
            };

        } catch (error) {
            appResults.security.error = error.message;
        }
    }

    async testUX(app, appResults) {
        console.log(`  🎨 Testing UX/UI for ${app.name}...`);

        try {
            await this.page.goto(app.url);

            // Check responsive design
            const responsiveTest = await this.testResponsiveness();

            // Check loading states
            const hasLoadingStates = await this.page.evaluate(() => {
                const elements = document.querySelectorAll('[class*="loading"], [class*="spinner"], [class*="skeleton"]');
                return elements.length > 0;
            });

            // Check error states
            const hasErrorStates = await this.page.evaluate(() => {
                const elements = document.querySelectorAll('[class*="error"], [class*="alert"], [class*="warning"]');
                return elements.length > 0;
            });

            // Check navigation
            const navigationElements = await this.page.evaluate(() => {
                const navs = document.querySelectorAll('nav, [role="navigation"], .navigation, .navbar');
                return Array.from(navs).map(nav => ({
                    tagName: nav.tagName,
                    className: nav.className,
                    linksCount: nav.querySelectorAll('a').length
                }));
            });

            // Check forms
            const formAnalysis = await this.page.evaluate(() => {
                const forms = document.querySelectorAll('form');
                return Array.from(forms).map(form => ({
                    action: form.action,
                    method: form.method,
                    inputCount: form.querySelectorAll('input').length,
                    hasValidation: form.querySelectorAll('[required], [pattern]').length > 0
                }));
            });

            // Check color contrast (basic)
            const contrastIssues = await this.checkColorContrast();

            appResults.ux = {
                responsive: responsiveTest,
                hasLoadingStates,
                hasErrorStates,
                navigation: navigationElements,
                forms: formAnalysis,
                contrastIssues,
                score: this.calculateUXScore({ 
                    responsive: responsiveTest, 
                    hasLoadingStates, 
                    hasErrorStates, 
                    navigationElements,
                    contrastIssues 
                })
            };

        } catch (error) {
            appResults.ux.error = error.message;
        }
    }

    async testResponsiveness() {
        const viewports = [
            { width: 375, height: 667, name: 'Mobile' },
            { width: 768, height: 1024, name: 'Tablet' },
            { width: 1200, height: 800, name: 'Desktop' },
            { width: 1920, height: 1080, name: 'Large Desktop' }
        ];

        const results = {};

        for (const viewport of viewports) {
            await this.page.setViewport({ width: viewport.width, height: viewport.height });
            await this.page.waitForTimeout(1000);

            const hasHorizontalScroll = await this.page.evaluate(() => {
                return document.body.scrollWidth > window.innerWidth;
            });

            const hasOverflowingElements = await this.page.evaluate(() => {
                const elements = document.querySelectorAll('*');
                return Array.from(elements).some(el => {
                    const rect = el.getBoundingClientRect();
                    return rect.right > window.innerWidth;
                });
            });

            results[viewport.name] = {
                width: viewport.width,
                height: viewport.height,
                hasHorizontalScroll,
                hasOverflowingElements,
                isResponsive: !hasHorizontalScroll && !hasOverflowingElements
            };
        }

        return results;
    }

    async checkAccessibility() {
        return await this.page.evaluate(() => {
            let score = 100;
            let issues = [];

            // Check for alt attributes on images
            const images = document.querySelectorAll('img');
            const imagesWithoutAlt = Array.from(images).filter(img => !img.alt);
            if (imagesWithoutAlt.length > 0) {
                score -= imagesWithoutAlt.length * 5;
                issues.push(`${imagesWithoutAlt.length} images missing alt attributes`);
            }

            // Check for proper heading hierarchy
            const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
            if (headings.length === 0) {
                score -= 20;
                issues.push('No headings found');
            }

            // Check for form labels
            const inputs = document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"], textarea');
            const inputsWithoutLabels = Array.from(inputs).filter(input => {
                const label = document.querySelector(`label[for="${input.id}"]`);
                const ariaLabel = input.getAttribute('aria-label');
                return !label && !ariaLabel;
            });
            if (inputsWithoutLabels.length > 0) {
                score -= inputsWithoutLabels.length * 10;
                issues.push(`${inputsWithoutLabels.length} form inputs missing labels`);
            }

            // Check for focus indicators
            const focusableElements = document.querySelectorAll('a, button, input, select, textarea, [tabindex]');
            // This is a simplified check - in reality you'd need to check computed styles

            return Math.max(0, score);
        });
    }

    async checkColorContrast() {
        return await this.page.evaluate(() => {
            const issues = [];
            
            // Basic color contrast check (simplified)
            const textElements = document.querySelectorAll('p, span, div, a, button, h1, h2, h3, h4, h5, h6');
            
            for (const element of textElements) {
                const styles = window.getComputedStyle(element);
                const color = styles.color;
                const backgroundColor = styles.backgroundColor;
                
                // This is a very basic check - real contrast checking requires color parsing
                if (color === backgroundColor) {
                    issues.push(`Element with identical text and background color: ${element.tagName}`);
                }
            }

            return issues;
        });
    }

    calculateSecurityScore({ isHTTPS, securityHeaders, hasSensitiveData, xssTest }) {
        let score = 0;
        
        if (isHTTPS) score += 20;
        if (securityHeaders['content-security-policy']) score += 20;
        if (securityHeaders['x-frame-options']) score += 15;
        if (securityHeaders['x-content-type-options']) score += 15;
        if (securityHeaders['strict-transport-security']) score += 15;
        if (!hasSensitiveData) score += 10;
        if (!xssTest) score += 5;

        return Math.min(100, score);
    }

    calculateUXScore({ responsive, hasLoadingStates, hasErrorStates, navigationElements, contrastIssues }) {
        let score = 100;
        
        // Check responsive design
        const responsiveDevices = Object.values(responsive);
        const responsiveScore = responsiveDevices.filter(device => device.isResponsive).length;
        score = (responsiveScore / responsiveDevices.length) * 25;

        // Add points for good UX elements
        if (hasLoadingStates) score += 15;
        if (hasErrorStates) score += 15;
        if (navigationElements.length > 0) score += 20;

        // Subtract for contrast issues
        score -= contrastIssues.length * 5;

        return Math.max(0, Math.min(100, score));
    }

    async generateReport() {
        console.log('\n📊 Generating comprehensive launch readiness report...');

        // Test all applications
        for (const app of this.applications) {
            this.results.applications[app.name] = await this.testApplication(app);
        }

        // Generate recommendations
        this.generateRecommendations();

        // Save results
        const reportPath = `launch_readiness_report_${Date.now()}.json`;
        fs.writeFileSync(reportPath, JSON.stringify(this.results, null, 2));

        // Generate markdown report
        const markdownReport = this.generateMarkdownReport();
        const markdownPath = `LAUNCH_READINESS_REPORT_${Date.now()}.md`;
        fs.writeFileSync(markdownPath, markdownReport);

        console.log(`\n✅ Reports generated:`);
        console.log(`📄 JSON: ${reportPath}`);
        console.log(`📝 Markdown: ${markdownPath}`);

        return this.results;
    }

    generateRecommendations() {
        const recommendations = [];

        Object.values(this.results.applications).forEach(app => {
            // Performance recommendations
            if (app.performance?.metrics?.domContentLoaded > 3000) {
                recommendations.push({
                    type: 'performance',
                    severity: 'high',
                    app: app.name,
                    issue: 'Slow DOM content loading',
                    recommendation: 'Optimize JavaScript bundles and reduce blocking resources'
                });
            }

            // Security recommendations
            if (app.security?.score < 70) {
                recommendations.push({
                    type: 'security',
                    severity: 'high',
                    app: app.name,
                    issue: 'Low security score',
                    recommendation: 'Implement missing security headers and enable HTTPS'
                });
            }

            // UX recommendations
            if (app.ux?.score < 70) {
                recommendations.push({
                    type: 'ux',
                    severity: 'medium',
                    app: app.name,
                    issue: 'Poor UX score',
                    recommendation: 'Improve responsive design and accessibility'
                });
            }

            // Error handling
            if (app.status === 'error') {
                recommendations.push({
                    type: 'critical',
                    severity: 'critical',
                    app: app.name,
                    issue: 'Application not running',
                    recommendation: 'Fix application startup issues before launch'
                });
            }
        });

        this.results.recommendations = recommendations;
    }

    generateMarkdownReport() {
        let markdown = `# Hardcard Launch Readiness Report\n\n`;
        markdown += `**Generated:** ${this.results.timestamp}\n\n`;

        // Executive Summary
        markdown += `## Executive Summary\n\n`;
        const totalApps = Object.keys(this.results.applications).length;
        const runningApps = Object.values(this.results.applications).filter(app => app.status === 'running').length;
        const criticalIssues = this.results.recommendations.filter(r => r.severity === 'critical').length;

        markdown += `- **Applications Tested:** ${totalApps}\n`;
        markdown += `- **Applications Running:** ${runningApps}/${totalApps}\n`;
        markdown += `- **Critical Issues:** ${criticalIssues}\n`;
        markdown += `- **Launch Ready:** ${criticalIssues === 0 && runningApps === totalApps ? '✅ YES' : '❌ NO'}\n\n`;

        // Application Status
        markdown += `## Application Status\n\n`;
        Object.values(this.results.applications).forEach(app => {
            const statusEmoji = app.status === 'running' ? '✅' : '❌';
            markdown += `### ${statusEmoji} ${app.name}\n\n`;
            markdown += `- **URL:** ${app.url}\n`;
            markdown += `- **Status:** ${app.status}\n`;

            if (app.performance?.metrics) {
                markdown += `- **Load Time:** ${app.performance.metrics.domContentLoaded}ms\n`;
            }

            if (app.security?.score) {
                markdown += `- **Security Score:** ${app.security.score}/100\n`;
            }

            if (app.ux?.score) {
                markdown += `- **UX Score:** ${app.ux.score}/100\n`;
            }

            markdown += `\n`;
        });

        // Recommendations
        if (this.results.recommendations.length > 0) {
            markdown += `## Recommendations\n\n`;
            this.results.recommendations.forEach((rec, index) => {
                const severityEmoji = {
                    'critical': '🚨',
                    'high': '⚠️',
                    'medium': '💡',
                    'low': 'ℹ️'
                };

                markdown += `### ${severityEmoji[rec.severity]} ${rec.app} - ${rec.issue}\n\n`;
                markdown += `**Type:** ${rec.type}\n`;
                markdown += `**Severity:** ${rec.severity}\n`;
                markdown += `**Recommendation:** ${rec.recommendation}\n\n`;
            });
        }

        return markdown;
    }

    async cleanup() {
        if (this.browser) {
            await this.browser.close();
        }
    }
}

// Main execution
async function main() {
    const tester = new HardcardLaunchTester();
    
    try {
        await tester.init();
        const results = await tester.generateReport();
        
        // Summary
        console.log('\n🎯 LAUNCH READINESS SUMMARY');
        console.log('================================');
        
        const totalApps = Object.keys(results.applications).length;
        const runningApps = Object.values(results.applications).filter(app => app.status === 'running').length;
        const criticalIssues = results.recommendations.filter(r => r.severity === 'critical').length;
        
        console.log(`Applications: ${runningApps}/${totalApps} running`);
        console.log(`Critical Issues: ${criticalIssues}`);
        console.log(`Launch Ready: ${criticalIssues === 0 && runningApps === totalApps ? '✅ YES' : '❌ NO'}`);
        
    } catch (error) {
        console.error('Testing failed:', error);
    } finally {
        await tester.cleanup();
    }
}

if (require.main === module) {
    main();
}

module.exports = HardcardLaunchTester;