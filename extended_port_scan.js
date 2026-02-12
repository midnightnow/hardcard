#!/usr/bin/env node

/**
 * Extended Port Scan Vision Testing - localhost:3001-3009
 * Comprehensive testing across extended port range
 */

const fs = require('fs');
const path = require('path');

// Configuration for extended port range
const CONFIG = {
    base_url: 'http://localhost',
    port_range: { start: 3001, end: 3009 },
    output_dir: '/Users/studio/hardcard/screenshots',
    report_file: '/Users/studio/hardcard/extended_port_scan_report.json',
    timeout: 10000
};

// Generate app configurations for all ports
const generatePortConfigs = () => {
    const configs = [];
    for (let port = CONFIG.port_range.start; port <= CONFIG.port_range.end; port++) {
        configs.push({
            name: `port_${port}`,
            url: `${CONFIG.base_url}:${port}`,
            expected_title: 'Unknown',
            critical_elements: ['body', '#root', 'main', 'nav', 'header'],
            user_flows: [
                { action: 'load', expected: 'page_loaded' }
            ]
        });
    }
    return configs;
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
            timeout: CONFIG.timeout
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
                
                // Analyze content
                const hasReact = data.includes('react') || data.includes('React');
                const hasVue = data.includes('vue') || data.includes('Vue');
                const hasAngular = data.includes('angular') || data.includes('Angular');
                const hasNext = data.includes('next') || data.includes('Next');
                const hasRoot = data.includes('id="root"') || data.includes('id=\'root\'');
                const hasApp = data.includes('id="app"') || data.includes('id=\'app\'');
                
                // Detect framework
                let framework = 'Unknown';
                if (hasReact) framework = 'React';
                else if (hasVue) framework = 'Vue.js';
                else if (hasAngular) framework = 'Angular';
                else if (hasNext) framework = 'Next.js';
                else if (hasRoot || hasApp) framework = 'SPA Framework';
                
                resolve({
                    name,
                    url,
                    status: 'online',
                    http_status: res.statusCode,
                    response_time: responseTime,
                    title,
                    content_length: data.length,
                    has_content: data.length > 100,
                    framework,
                    analysis: {
                        has_react_elements: hasReact,
                        has_spa_structure: hasRoot || hasApp,
                        content_type: res.headers['content-type'] || 'unknown',
                        server: res.headers['server'] || 'unknown'
                    },
                    timestamp: new Date().toISOString()
                });
            });
        });

        req.on('error', (error) => {
            resolve({
                name,
                url,
                status: 'offline',
                error: error.code === 'ECONNREFUSED' ? 'Connection refused - service not running' : error.message,
                timestamp: new Date().toISOString()
            });
        });

        req.on('timeout', () => {
            req.destroy();
            resolve({
                name,
                url,
                status: 'timeout',
                error: 'Request timeout - service not responding',
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

        const browser = await playwright.chromium.launch({ 
            headless: true,
            timeout: CONFIG.timeout 
        });
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
            // Navigate to page with timeout
            const startTime = Date.now();
            await page.goto(appConfig.url, { 
                waitUntil: 'networkidle', 
                timeout: CONFIG.timeout 
            });
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

            // Enhanced analysis
            const analysis = await page.evaluate(() => {
                return {
                    frameworks_detected: {
                        react: !!(window.React || document.querySelector('[data-reactroot]') || document.querySelector('#root')),
                        vue: !!(window.Vue || document.querySelector('[data-v-]')),
                        angular: !!(window.angular || document.querySelector('[ng-app]')),
                        jquery: !!(window.jQuery || window.$)
                    },
                    page_info: {
                        has_spa_elements: !!(document.querySelector('#root') || document.querySelector('#app')),
                        total_elements: document.querySelectorAll('*').length,
                        has_scripts: document.querySelectorAll('script').length,
                        has_stylesheets: document.querySelectorAll('link[rel="stylesheet"]').length
                    }
                };
            });
            results.analysis = analysis;

            // Accessibility checks
            results.tests.accessibility = await performAccessibilityChecks(page);

            // Performance metrics
            const metrics = await page.evaluate(() => {
                if (typeof window !== 'undefined' && window.performance) {
                    const navigation = performance.getEntriesByType('navigation')[0];
                    return {
                        dom_content_loaded: navigation?.domContentLoadedEventEnd - navigation?.domContentLoadedEventStart,
                        load_complete: navigation?.loadEventEnd - navigation?.loadEventStart,
                        first_paint: performance.getEntriesByName('first-paint')[0]?.startTime || null,
                        first_contentful_paint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || null
                    };
                }
                return null;
            });
            results.performance = metrics;

        } catch (error) {
            if (error.message.includes('ERR_CONNECTION_REFUSED')) {
                results.status = 'offline';
                results.error = 'Connection refused - service not running on this port';
            } else if (error.message.includes('timeout')) {
                results.status = 'timeout';
                results.error = 'Request timeout - service not responding';
            } else {
                results.status = 'error';
                results.error = error.message;
            }
        } finally {
            await browser.close();
        }

        return results;

    } catch (error) {
        // Fallback to HTTP testing
        return await testHttpEndpoint(appConfig.url, appConfig.name);
    }
}

async function performAccessibilityChecks(page) {
    try {
        const checks = {
            has_title: await page.title() !== '',
            has_lang: await page.getAttribute('html', 'lang') !== null,
            has_headings: await page.$$('h1, h2, h3, h4, h5, h6').then(h => h.length > 0),
            has_main_landmark: await page.$('main, [role="main"]') !== null,
            has_nav_landmark: await page.$('nav, [role="navigation"]') !== null,
            images_have_alt: await page.$$eval('img', imgs => 
                imgs.length === 0 || imgs.every(img => img.hasAttribute('alt'))
            ).catch(() => false)
        };
        return checks;
    } catch (error) {
        return { error: error.message };
    }
}

// Main execution function
async function runExtendedPortScan() {
    console.log('🔍 Starting Extended Port Scan (3001-3009)');
    console.log('============================================');
    
    // Ensure output directory exists
    if (!fs.existsSync(CONFIG.output_dir)) {
        fs.mkdirSync(CONFIG.output_dir, { recursive: true });
    }

    const appConfigs = generatePortConfigs();
    
    const results = {
        test_run_id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        port_range: CONFIG.port_range,
        config: CONFIG,
        applications: {},
        summary: {
            total: appConfigs.length,
            online: 0,
            offline: 0,
            errors: 0,
            timeouts: 0
        },
        frameworks_found: {},
        recommendations: []
    };

    // Test each port
    for (const appConfig of appConfigs) {
        const port = appConfig.url.split(':')[2];
        console.log(`\\n🔍 Testing ${appConfig.name} (${appConfig.url})`);
        
        const appResult = await testWithPlaywright(appConfig);
        results.applications[appConfig.name] = appResult;
        
        // Update summary
        if (appResult.status === 'online') {
            results.summary.online++;
            console.log(`  ✅ Port ${port}: ONLINE - "${appResult.title}" (${appResult.load_time || appResult.response_time}ms)`);
            
            // Track frameworks
            if (appResult.framework && appResult.framework !== 'Unknown') {
                if (!results.frameworks_found[appResult.framework]) {
                    results.frameworks_found[appResult.framework] = [];
                }
                results.frameworks_found[appResult.framework].push(port);
            }
        } else if (appResult.status === 'offline') {
            results.summary.offline++;
            console.log(`  ❌ Port ${port}: OFFLINE`);
        } else if (appResult.status === 'timeout') {
            results.summary.timeouts++;
            console.log(`  ⏱️  Port ${port}: TIMEOUT`);
        } else {
            results.summary.errors++;
            console.log(`  ⚠️  Port ${port}: ERROR - ${appResult.error}`);
        }
    }

    // Generate recommendations
    generateExtendedRecommendations(results);

    // Save results
    fs.writeFileSync(CONFIG.report_file, JSON.stringify(results, null, 2));
    
    console.log('\\n📊 EXTENDED SCAN SUMMARY');
    console.log('=========================');
    console.log(`Ports Scanned: ${CONFIG.port_range.start}-${CONFIG.port_range.end} (${results.summary.total} total)`);
    console.log(`Online Services: ${results.summary.online}`);
    console.log(`Offline/No Service: ${results.summary.offline}`);  
    console.log(`Timeouts: ${results.summary.timeouts}`);
    console.log(`Errors: ${results.summary.errors}`);
    
    if (Object.keys(results.frameworks_found).length > 0) {
        console.log('\\n🛠️  FRAMEWORKS DETECTED');
        console.log('======================');
        Object.entries(results.frameworks_found).forEach(([framework, ports]) => {
            console.log(`${framework}: Port(s) ${ports.join(', ')}`);
        });
    }
    
    console.log('\\n💡 RECOMMENDATIONS');
    console.log('==================');
    results.recommendations.forEach(rec => console.log(`${rec.priority} ${rec.message}`));
    
    console.log(`\\n📋 Full report saved to: ${CONFIG.report_file}`);
    console.log(`📸 Screenshots saved to: ${CONFIG.output_dir}`);
    
    return results;
}

function generateExtendedRecommendations(results) {
    const recommendations = [];
    
    // Overall health assessment
    if (results.summary.online === 0) {
        recommendations.push({
            priority: '🔴 CRITICAL:',
            message: 'No services found on any ports 3001-3009 - check if services are running'
        });
    } else if (results.summary.online < 3) {
        recommendations.push({
            priority: '🟡 MEDIUM:',
            message: `Only ${results.summary.online} services found - you may have more services to start`
        });
    } else {
        recommendations.push({
            priority: '✅ GOOD:',
            message: `${results.summary.online} services are running and accessible`
        });
    }

    // Framework analysis
    const frameworks = Object.keys(results.frameworks_found);
    if (frameworks.length > 3) {
        recommendations.push({
            priority: '🟡 MEDIUM:',
            message: `Multiple frameworks detected (${frameworks.join(', ')}) - consider standardizing stack`
        });
    }

    // Performance recommendations
    Object.entries(results.applications).forEach(([name, data]) => {
        if (data.status === 'online' && (data.load_time > 2000 || data.response_time > 2000)) {
            const port = data.url.split(':')[2];
            recommendations.push({
                priority: '🟡 MEDIUM:',
                message: `Port ${port} has slow response time - investigate performance`
            });
        }
    });

    results.recommendations = recommendations;
}

// Run the scan if called directly
if (require.main === module) {
    runExtendedPortScan().catch(console.error);
}

module.exports = { runExtendedPortScan, CONFIG };