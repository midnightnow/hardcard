#!/usr/bin/env node

/**
 * Enhanced Vision Testing Protocol with Browser Automation
 * Uses Playwright for interactive testing and visual validation
 */

const fs = require('fs');
const path = require('path');

// Configuration
const CONFIG = {
    apps: [
        {
            name: 'main_frontend',
            url: 'http://localhost:5173',
            expected_title: 'HardCard Suite',
            critical_elements: ['#root', '[role="main"]', 'nav'],
            user_flows: [
                { action: 'navigation', target: '/', expected: 'dashboard' },
                { action: 'click', target: 'button', expected: 'response' }
            ]
        },
        {
            name: 'api_backend', 
            url: 'http://localhost:3001',
            expected_title: 'Databutton',
            critical_elements: ['body', '#root'],
            api_endpoints: ['/health', '/api/status']
        },
        {
            name: 'hardcard_suite',
            url: 'http://localhost:3002', 
            expected_title: 'HARDCARD Suite',
            critical_elements: ['header', 'main', 'nav'],
            user_flows: [
                { action: 'load', expected: 'dashboard_visible' },
                { action: 'navigation', target: '/admin', expected: 'admin_panel' }
            ]
        }
    ],
    output_dir: '/Users/studio/hardcard/screenshots',
    report_file: '/Users/studio/hardcard/enhanced_test_report.json'
};

// Simple HTTP testing without external dependencies
async function testHttpEndpoint(url, name) {
    return new Promise((resolve) => {
        const http = require('http');
        const urlObj = new URL(url);
        
        const options = {
            hostname: urlObj.hostname,
            port: urlObj.port,
            path: urlObj.pathname,
            method: 'GET',
            timeout: 10000
        };

        const startTime = Date.now();
        
        const req = http.request(options, (res) => {
            const responseTime = Date.now() - startTime;
            let data = '';
            
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                // Extract title
                const titleMatch = data.match(/<title[^>]*>([^<]+)<\/title>/i);
                const title = titleMatch ? titleMatch[1].trim() : 'No title found';
                
                resolve({
                    name,
                    url,
                    status: 'online',
                    http_status: res.statusCode,
                    response_time: responseTime,
                    title,
                    content_length: data.length,
                    has_content: data.length > 100,
                    timestamp: new Date().toISOString()
                });
            });
        });

        req.on('error', (error) => {
            resolve({
                name,
                url,
                status: 'offline',
                error: error.message,
                timestamp: new Date().toISOString()
            });
        });

        req.on('timeout', () => {
            req.destroy();
            resolve({
                name,
                url,
                status: 'timeout',
                error: 'Request timeout',
                timestamp: new Date().toISOString()
            });
        });

        req.end();
    });
}

// Enhanced testing with Playwright (if available)
async function testWithPlaywright(appConfig) {
    try {
        // Check if Playwright is available
        let playwright;
        try {
            playwright = require('playwright');
        } catch (e) {
            console.log(`Playwright not available for ${appConfig.name}, using basic HTTP testing`);
            return await testHttpEndpoint(appConfig.url, appConfig.name);
        }

        const browser = await playwright.chromium.launch({ headless: true });
        const context = await browser.newContext({
            viewport: { width: 1920, height: 1080 }
        });
        const page = await context.newPage();

        const results = {
            name: appConfig.name,
            url: appConfig.url,
            timestamp: new Date().toISOString(),
            status: 'unknown',
            tests: {}
        };

        try {
            // Navigate to page
            const startTime = Date.now();
            await page.goto(appConfig.url, { waitUntil: 'networkidle', timeout: 30000 });
            const loadTime = Date.now() - startTime;

            results.status = 'online';
            results.load_time = loadTime;
            results.title = await page.title();

            // Take screenshot
            const screenshotPath = path.join(CONFIG.output_dir, `${appConfig.name}_${Date.now()}.png`);
            await page.screenshot({ path: screenshotPath, fullPage: true });
            results.screenshot = screenshotPath;

            // Test critical elements
            results.tests.critical_elements = {};
            for (const selector of appConfig.critical_elements || []) {
                try {
                    const element = await page.$(selector);
                    results.tests.critical_elements[selector] = element ? 'found' : 'missing';
                } catch (e) {
                    results.tests.critical_elements[selector] = 'error';
                }
            }

            // Test user flows
            if (appConfig.user_flows) {
                results.tests.user_flows = [];
                for (const flow of appConfig.user_flows) {
                    try {
                        const flowResult = await executeUserFlow(page, flow);
                        results.tests.user_flows.push(flowResult);
                    } catch (e) {
                        results.tests.user_flows.push({
                            flow: flow.action,
                            status: 'failed',
                            error: e.message
                        });
                    }
                }
            }

            // Performance metrics
            const metrics = await page.evaluate(() => {
                if (typeof window !== 'undefined' && window.performance) {
                    const navigation = performance.getEntriesByType('navigation')[0];
                    return {
                        dom_content_loaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
                        load_complete: navigation.loadEventEnd - navigation.loadEventStart,
                        first_paint: performance.getEntriesByName('first-paint')[0]?.startTime || null,
                        first_contentful_paint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || null
                    };
                }
                return null;
            });
            results.performance = metrics;

            // Accessibility checks
            results.tests.accessibility = await performAccessibilityChecks(page);

        } catch (error) {
            results.status = 'error';
            results.error = error.message;
        } finally {
            await browser.close();
        }

        return results;

    } catch (error) {
        // Fallback to HTTP testing
        console.log(`Playwright testing failed for ${appConfig.name}, falling back to HTTP: ${error.message}`);
        return await testHttpEndpoint(appConfig.url, appConfig.name);
    }
}

async function executeUserFlow(page, flow) {
    const result = { flow: flow.action, status: 'pending' };
    
    switch (flow.action) {
        case 'navigation':
            await page.goto(flow.target);
            result.status = 'completed';
            break;
        case 'click':
            await page.click(flow.target);
            await page.waitForTimeout(1000);
            result.status = 'completed';
            break;
        case 'load':
            await page.waitForLoadState('networkidle');
            result.status = 'completed';
            break;
        default:
            result.status = 'skipped';
            result.reason = 'Unknown action';
    }
    
    return result;
}

async function performAccessibilityChecks(page) {
    try {
        // Basic accessibility checks
        const checks = {
            has_title: await page.title() !== '',
            has_lang: await page.getAttribute('html', 'lang') !== null,
            has_headings: await page.$$('h1, h2, h3, h4, h5, h6').then(h => h.length > 0),
            has_main_landmark: await page.$('main, [role="main"]') !== null,
            has_nav_landmark: await page.$('nav, [role="navigation"]') !== null,
            images_have_alt: await page.$$eval('img', imgs => 
                imgs.every(img => img.hasAttribute('alt'))
            ).catch(() => false)
        };
        
        return checks;
    } catch (error) {
        return { error: error.message };
    }
}

// Main execution function
async function runEnhancedVisionTest() {
    console.log('🚀 Starting Enhanced Vision Testing Protocol');
    console.log('====================================================');
    
    // Ensure output directory exists
    if (!fs.existsSync(CONFIG.output_dir)) {
        fs.mkdirSync(CONFIG.output_dir, { recursive: true });
    }

    const results = {
        test_run_id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        config: CONFIG,
        applications: {},
        summary: {
            total: CONFIG.apps.length,
            online: 0,
            offline: 0,
            errors: 0
        },
        recommendations: []
    };

    // Test each application
    for (const appConfig of CONFIG.apps) {
        console.log(`\\n🔍 Testing ${appConfig.name} (${appConfig.url})`);
        
        const appResult = await testWithPlaywright(appConfig);
        results.applications[appConfig.name] = appResult;
        
        // Update summary
        if (appResult.status === 'online') {
            results.summary.online++;
            console.log(`  ✅ ${appConfig.name}: ONLINE (${appResult.response_time || appResult.load_time}ms)`);
        } else if (appResult.status === 'offline') {
            results.summary.offline++;
            console.log(`  ❌ ${appConfig.name}: OFFLINE`);
        } else {
            results.summary.errors++;
            console.log(`  ⚠️  ${appConfig.name}: ERROR - ${appResult.error}`);
        }
    }

    // Generate recommendations
    generateRecommendations(results);

    // Save results
    fs.writeFileSync(CONFIG.report_file, JSON.stringify(results, null, 2));
    
    console.log('\\n📊 SUMMARY');
    console.log('============');
    console.log(`Total Applications: ${results.summary.total}`);
    console.log(`Online: ${results.summary.online}`);
    console.log(`Offline: ${results.summary.offline}`);  
    console.log(`Errors: ${results.summary.errors}`);
    
    console.log('\\n💡 RECOMMENDATIONS');
    console.log('==================');
    results.recommendations.forEach(rec => console.log(`${rec.priority} ${rec.message}`));
    
    console.log(`\\n📋 Full report saved to: ${CONFIG.report_file}`);
    console.log(`📸 Screenshots saved to: ${CONFIG.output_dir}`);
    
    return results;
}

function generateRecommendations(results) {
    const recommendations = [];
    
    // Check overall health
    if (results.summary.offline === results.summary.total) {
        recommendations.push({
            priority: '🔴 CRITICAL:',
            message: 'All applications are offline - check development environment'
        });
    } else if (results.summary.offline > 0) {
        recommendations.push({
            priority: '⚠️  WARNING:',
            message: `${results.summary.offline} of ${results.summary.total} applications are offline`
        });
    }

    // Check specific applications
    Object.entries(results.applications).forEach(([name, data]) => {
        if (data.status === 'offline') {
            recommendations.push({
                priority: '🔴 HIGH:',
                message: `Restore ${name} - check service dependencies and startup scripts`
            });
        }
        
        if (data.title && !data.title.toLowerCase().includes('hardcard')) {
            recommendations.push({
                priority: '🟡 MEDIUM:',
                message: `Update ${name} branding - title shows "${data.title}" instead of HardCard Suite`
            });
        }
        
        if (data.load_time > 3000) {
            recommendations.push({
                priority: '🟡 MEDIUM:',
                message: `Optimize ${name} performance - load time is ${data.load_time}ms`
            });
        }
    });

    // Add Playwright recommendation if not available
    try {
        require('playwright');
    } catch (e) {
        recommendations.push({
            priority: '🔵 INFO:',
            message: 'Install Playwright for enhanced testing: npm install playwright'
        });
    }

    results.recommendations = recommendations;
}

// Install Playwright if not available
async function ensurePlaylrightInstalled() {
    try {
        require('playwright');
        console.log('✅ Playwright is available');
        return true;
    } catch (e) {
        console.log('📦 Playwright not found. Installing...');
        const { execSync } = require('child_process');
        try {
            execSync('npm list playwright', { stdio: 'ignore' });
        } catch (e) {
            console.log('Installing Playwright...');
            execSync('npm install playwright', { stdio: 'inherit' });
            execSync('npx playwright install', { stdio: 'inherit' });
            console.log('✅ Playwright installed successfully');
            return true;
        }
    }
}

// Run the test if called directly
if (require.main === module) {
    runEnhancedVisionTest().catch(console.error);
}

module.exports = { runEnhancedVisionTest, CONFIG };