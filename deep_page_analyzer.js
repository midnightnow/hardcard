#!/usr/bin/env node

/**
 * Deep Page-by-Page Analysis Tool
 * Comprehensive testing of all routes and functionality across applications
 */

const fs = require('fs');
const path = require('path');

const CONFIG = {
    apps: [
        {
            name: 'main_frontend',
            url: 'http://localhost:5173',
            expected_title: 'HardCard Suite',
            routes: [
                '/',
                '/admin',
                '/dashboard',
                '/products',
                '/product-catalog',
                '/cart',
                '/profile',
                '/login',
                '/science',
                '/wiki',
                '/education',
                '/maintenance',
                '/crm',
                '/inventory',
                '/analytics',
                '/settings'
            ]
        },
        {
            name: 'api_backend',
            url: 'http://localhost:3001',
            expected_title: 'Databutton',
            routes: [
                '/',
                '/admin',
                '/dashboard',
                '/health',
                '/api/status',
                '/docs'
            ]
        },
        {
            name: 'hardcard_suite',
            url: 'http://localhost:3002',
            expected_title: 'HARDCARD Suite',
            routes: [
                '/',
                '/admin',
                '/dashboard'
            ]
        }
    ],
    output_dir: '/Users/studio/hardcard/deep_analysis',
    report_file: '/Users/studio/hardcard/deep_analysis_report.json',
    timeout: 15000,
    screenshot_all_pages: true
};

// Ensure output directory exists
if (!fs.existsSync(CONFIG.output_dir)) {
    fs.mkdirSync(CONFIG.output_dir, { recursive: true });
}

async function testPageWithPlaywright(app, route) {
    try {
        const playwright = require('playwright');
        const browser = await playwright.chromium.launch({ headless: true });
        const context = await browser.newContext({
            viewport: { width: 1920, height: 1080 }
        });
        const page = await context.newPage();

        const fullUrl = app.url + route;
        const results = {
            app: app.name,
            route,
            url: fullUrl,
            timestamp: new Date().toISOString(),
            status: 'unknown',
            issues: [],
            warnings: [],
            recommendations: []
        };

        try {
            console.log(`    📄 Testing ${route}`);
            
            // Navigate with error handling
            const startTime = Date.now();
            
            // Set up console error capture
            const consoleErrors = [];
            page.on('console', msg => {
                if (msg.type() === 'error') {
                    consoleErrors.push(msg.text());
                }
            });

            // Set up network error capture
            const networkErrors = [];
            page.on('response', response => {
                if (response.status() >= 400) {
                    networkErrors.push({
                        url: response.url(),
                        status: response.status(),
                        statusText: response.statusText()
                    });
                }
            });

            await page.goto(fullUrl, { 
                waitUntil: 'networkidle', 
                timeout: CONFIG.timeout 
            });
            
            const loadTime = Date.now() - startTime;
            results.load_time = loadTime;
            results.status = 'loaded';

            // Get basic page info
            results.title = await page.title();
            results.url_final = page.url(); // Check for redirects

            // Take screenshot
            if (CONFIG.screenshot_all_pages) {
                const screenshotPath = path.join(
                    CONFIG.output_dir, 
                    `${app.name}_${route.replace(/\//g, '_')}_${Date.now()}.png`
                );
                await page.screenshot({ path: screenshotPath, fullPage: true });
                results.screenshot = screenshotPath;
            }

            // Comprehensive page analysis
            const analysis = await page.evaluate(() => {
                const analysis = {
                    content_analysis: {},
                    ui_elements: {},
                    functionality: {},
                    errors: {},
                    performance: {},
                    accessibility: {},
                    seo: {}
                };

                // Content Analysis
                analysis.content_analysis = {
                    total_elements: document.querySelectorAll('*').length,
                    text_content_length: document.body?.textContent?.length || 0,
                    images: document.querySelectorAll('img').length,
                    links: document.querySelectorAll('a').length,
                    forms: document.querySelectorAll('form').length,
                    buttons: document.querySelectorAll('button').length,
                    inputs: document.querySelectorAll('input').length,
                    has_main_content: document.body?.textContent?.length > 100,
                    is_blank_page: document.body?.textContent?.trim().length < 50
                };

                // UI Elements Check
                analysis.ui_elements = {
                    has_header: !!document.querySelector('header, .header, [role="banner"]'),
                    has_navigation: !!document.querySelector('nav, .nav, [role="navigation"]'),
                    has_main: !!document.querySelector('main, .main, [role="main"]'),
                    has_footer: !!document.querySelector('footer, .footer, [role="contentinfo"]'),
                    has_sidebar: !!document.querySelector('.sidebar, .side-nav, aside'),
                    has_breadcrumbs: !!document.querySelector('.breadcrumb, nav[aria-label*="breadcrumb"]'),
                    has_search: !!document.querySelector('input[type="search"], .search-input, [placeholder*="search" i]'),
                    has_logo: !!document.querySelector('.logo, .brand, [alt*="logo" i]')
                };

                // Functionality Check
                analysis.functionality = {
                    clickable_elements: document.querySelectorAll('button, a, [onclick], [role="button"]').length,
                    interactive_forms: document.querySelectorAll('form').length,
                    dropdown_menus: document.querySelectorAll('select, .dropdown, [role="menu"]').length,
                    modals_dialogs: document.querySelectorAll('.modal, .dialog, [role="dialog"]').length,
                    tooltips: document.querySelectorAll('[title], .tooltip, [aria-describedby]').length,
                    ajax_indicators: document.querySelectorAll('.loading, .spinner, .loader').length
                };

                // Error Detection
                analysis.errors = {
                    broken_images: Array.from(document.querySelectorAll('img')).filter(img => 
                        !img.complete || img.naturalWidth === 0
                    ).length,
                    missing_alt_text: Array.from(document.querySelectorAll('img')).filter(img => 
                        !img.hasAttribute('alt') || img.alt.trim() === ''
                    ).length,
                    empty_links: Array.from(document.querySelectorAll('a')).filter(a => 
                        !a.textContent.trim() && !a.querySelector('img')
                    ).length,
                    missing_form_labels: Array.from(document.querySelectorAll('input[type]:not([type="hidden"]):not([type="submit"]):not([type="button"])')).filter(input => 
                        !input.labels?.length && !input.getAttribute('aria-label')
                    ).length
                };

                // Performance Indicators
                if (window.performance) {
                    const navigation = performance.getEntriesByType('navigation')[0];
                    analysis.performance = {
                        dom_content_loaded: navigation?.domContentLoadedEventEnd - navigation?.domContentLoadedEventStart,
                        load_complete: navigation?.loadEventEnd - navigation?.loadEventStart,
                        first_paint: performance.getEntriesByName('first-paint')[0]?.startTime,
                        first_contentful_paint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime,
                        largest_contentful_paint: performance.getEntriesByName('largest-contentful-paint')[0]?.startTime
                    };
                }

                // Accessibility Analysis
                analysis.accessibility = {
                    has_skip_links: !!document.querySelector('a[href*="#main"], .skip-link'),
                    proper_heading_structure: (() => {
                        const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6'));
                        return headings.length > 0 && document.querySelector('h1');
                    })(),
                    focus_management: document.querySelectorAll('[tabindex]').length,
                    aria_labels: document.querySelectorAll('[aria-label], [aria-labelledby]').length,
                    landmark_elements: document.querySelectorAll('[role="main"], [role="navigation"], [role="banner"], [role="contentinfo"]').length
                };

                // SEO Basics
                analysis.seo = {
                    has_title: !!document.title && document.title.trim().length > 0,
                    title_length: document.title?.length || 0,
                    has_meta_description: !!document.querySelector('meta[name="description"]'),
                    has_h1: !!document.querySelector('h1'),
                    h1_count: document.querySelectorAll('h1').length,
                    has_canonical: !!document.querySelector('link[rel="canonical"]')
                };

                return analysis;
            });

            results.analysis = analysis;

            // Add captured console and network errors
            results.console_errors = consoleErrors;
            results.network_errors = networkErrors;

            // Generate issues based on analysis
            generateIssuesForPage(results);

            // Check for route-specific functionality
            await checkRouteSpecificFunctionality(page, route, results);

        } catch (error) {
            results.status = 'error';
            results.error = error.message;
            
            if (error.message.includes('ERR_CONNECTION_REFUSED')) {
                results.issues.push({
                    type: 'critical',
                    category: 'connectivity',
                    message: 'Page failed to load - connection refused',
                    fix: 'Check if the service is running and accessible'
                });
            } else if (error.message.includes('timeout')) {
                results.issues.push({
                    type: 'critical',
                    category: 'performance',
                    message: 'Page load timeout',
                    fix: 'Optimize page load performance or increase timeout'
                });
            } else if (error.message.includes('net::ERR_NAME_NOT_RESOLVED')) {
                results.issues.push({
                    type: 'critical',
                    category: 'connectivity',
                    message: 'DNS resolution failed',
                    fix: 'Check the URL and network configuration'
                });
            } else {
                results.issues.push({
                    type: 'error',
                    category: 'unknown',
                    message: `Page analysis failed: ${error.message}`,
                    fix: 'Investigate the specific error and resolve underlying issues'
                });
            }
        } finally {
            await browser.close();
        }

        return results;

    } catch (error) {
        // Playwright not available, return basic error result
        return {
            app: app.name,
            route,
            url: app.url + route,
            status: 'error',
            error: 'Playwright not available for deep analysis',
            issues: [{
                type: 'warning',
                category: 'tool',
                message: 'Deep analysis requires Playwright',
                fix: 'Install Playwright for comprehensive page testing'
            }]
        };
    }
}

function generateIssuesForPage(results) {
    const analysis = results.analysis;
    if (!analysis) return;

    // Critical Issues
    if (analysis.content_analysis.is_blank_page) {
        results.issues.push({
            type: 'critical',
            category: 'content',
            message: 'Page appears to be blank or has minimal content',
            fix: 'Ensure page content is loading properly and displaying correctly'
        });
    }

    if (analysis.errors.broken_images > 0) {
        results.issues.push({
            type: 'high',
            category: 'content',
            message: `${analysis.errors.broken_images} broken image(s) detected`,
            fix: 'Fix broken image URLs and ensure all images load correctly'
        });
    }

    // Accessibility Issues
    if (analysis.errors.missing_alt_text > 0) {
        results.issues.push({
            type: 'medium',
            category: 'accessibility',
            message: `${analysis.errors.missing_alt_text} image(s) missing alt text`,
            fix: 'Add descriptive alt text to all images for screen reader accessibility'
        });
    }

    if (!analysis.accessibility.proper_heading_structure) {
        results.issues.push({
            type: 'medium',
            category: 'accessibility',
            message: 'Missing or improper heading structure (no H1 or invalid hierarchy)',
            fix: 'Add proper H1 heading and maintain logical heading hierarchy'
        });
    }

    if (analysis.errors.missing_form_labels > 0) {
        results.issues.push({
            type: 'medium',
            category: 'accessibility',
            message: `${analysis.errors.missing_form_labels} form input(s) missing labels`,
            fix: 'Add proper labels or aria-label attributes to all form inputs'
        });
    }

    // UI/UX Issues
    if (!analysis.ui_elements.has_navigation && results.route === '/') {
        results.warnings.push({
            type: 'warning',
            category: 'ux',
            message: 'Main page missing navigation menu',
            fix: 'Consider adding navigation menu for better user experience'
        });
    }

    if (!analysis.ui_elements.has_header && results.route === '/') {
        results.warnings.push({
            type: 'warning',
            category: 'ux',
            message: 'Main page missing header section',
            fix: 'Consider adding header with branding and navigation'
        });
    }

    // Performance Issues
    if (results.load_time > 3000) {
        results.issues.push({
            type: 'medium',
            category: 'performance',
            message: `Slow page load time: ${results.load_time}ms`,
            fix: 'Optimize page performance - target under 2 seconds'
        });
    }

    // SEO Issues
    if (!analysis.seo.has_title || analysis.seo.title_length < 10) {
        results.issues.push({
            type: 'medium',
            category: 'seo',
            message: 'Missing or too short page title',
            fix: 'Add descriptive page title (30-60 characters recommended)'
        });
    }

    if (analysis.seo.h1_count !== 1) {
        results.issues.push({
            type: 'low',
            category: 'seo',
            message: `Incorrect H1 count: ${analysis.seo.h1_count} (should be exactly 1)`,
            fix: 'Ensure each page has exactly one H1 heading'
        });
    }

    // Console/Network Errors
    if (results.console_errors && results.console_errors.length > 0) {
        results.issues.push({
            type: 'high',
            category: 'javascript',
            message: `${results.console_errors.length} JavaScript console error(s)`,
            fix: 'Fix JavaScript errors logged to browser console',
            details: results.console_errors.slice(0, 3) // Include first 3 errors
        });
    }

    if (results.network_errors && results.network_errors.length > 0) {
        results.issues.push({
            type: 'high',
            category: 'network',
            message: `${results.network_errors.length} network error(s)`,
            fix: 'Fix failed network requests and API calls',
            details: results.network_errors.slice(0, 3)
        });
    }
}

async function checkRouteSpecificFunctionality(page, route, results) {
    try {
        // Route-specific tests
        switch (route) {
            case '/':
                // Homepage specific tests
                const hasCallToAction = await page.$('button[type="submit"], .cta-button, .btn-primary, [class*="cta"]');
                if (!hasCallToAction) {
                    results.recommendations.push({
                        type: 'suggestion',
                        category: 'ux',
                        message: 'Homepage missing clear call-to-action button',
                        fix: 'Add prominent call-to-action to guide user journey'
                    });
                }
                break;

            case '/login':
                // Login page specific tests
                const loginForm = await page.$('form[action*="login"], form input[type="password"]');
                if (!loginForm) {
                    results.issues.push({
                        type: 'high',
                        category: 'functionality',
                        message: 'Login page missing login form',
                        fix: 'Implement proper login form with username/email and password fields'
                    });
                }
                break;

            case '/cart':
                // Shopping cart specific tests
                const cartItems = await page.$('.cart-item, .product-item, [class*="cart"]');
                const checkoutButton = await page.$('button[type="submit"], .checkout-btn, [class*="checkout"]');
                
                if (!cartItems && !checkoutButton) {
                    results.warnings.push({
                        type: 'warning',
                        category: 'functionality',
                        message: 'Cart page may not be fully implemented',
                        fix: 'Verify cart functionality and item display'
                    });
                }
                break;

            case '/admin':
                // Admin page specific tests
                const adminPanels = await page.$('.admin-panel, .dashboard, [class*="admin"]');
                if (!adminPanels) {
                    results.warnings.push({
                        type: 'warning',
                        category: 'functionality',
                        message: 'Admin page missing admin interface elements',
                        fix: 'Implement admin dashboard with proper controls'
                    });
                }
                break;
        }
    } catch (error) {
        // Route-specific tests failed, but don't break the main analysis
        results.warnings.push({
            type: 'warning',
            category: 'testing',
            message: `Route-specific functionality test failed: ${error.message}`,
            fix: 'Manual testing may be required for this route'
        });
    }
}

async function runDeepPageAnalysis() {
    console.log('🔍 Starting Deep Page-by-Page Analysis');
    console.log('=====================================');
    
    const results = {
        analysis_id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        config: CONFIG,
        applications: {},
        summary: {
            total_pages: 0,
            successful_pages: 0,
            failed_pages: 0,
            total_issues: 0,
            critical_issues: 0,
            high_issues: 0,
            medium_issues: 0,
            low_issues: 0
        },
        overall_recommendations: []
    };

    // Test each application
    for (const app of CONFIG.apps) {
        console.log(`\\n🔍 Analyzing ${app.name} (${app.url})`);
        console.log(`Routes to test: ${app.routes.length}`);
        
        const appResults = {
            name: app.name,
            url: app.url,
            routes_tested: 0,
            routes_successful: 0,
            routes_failed: 0,
            pages: {},
            app_summary: {
                total_issues: 0,
                critical_issues: 0,
                high_issues: 0,
                medium_issues: 0,
                low_issues: 0
            }
        };

        // Test each route in the application
        for (const route of app.routes) {
            const pageResult = await testPageWithPlaywright(app, route);
            appResults.pages[route] = pageResult;
            appResults.routes_tested++;
            
            if (pageResult.status === 'loaded') {
                appResults.routes_successful++;
                results.summary.successful_pages++;
            } else {
                appResults.routes_failed++;
                results.summary.failed_pages++;
            }
            
            // Count issues
            const issues = pageResult.issues || [];
            issues.forEach(issue => {
                appResults.app_summary.total_issues++;
                appResults.app_summary[issue.type + '_issues']++;
                results.summary.total_issues++;
                results.summary[issue.type + '_issues']++;
            });
            
            results.summary.total_pages++;
        }

        results.applications[app.name] = appResults;
        
        console.log(`  ✅ Completed: ${appResults.routes_successful}/${appResults.routes_tested} routes successful`);
        console.log(`  📊 Issues found: ${appResults.app_summary.total_issues} total`);
    }

    // Generate overall recommendations
    generateOverallRecommendations(results);

    // Save comprehensive results
    fs.writeFileSync(CONFIG.report_file, JSON.stringify(results, null, 2));
    
    console.log('\\n📊 DEEP ANALYSIS SUMMARY');
    console.log('=========================');
    console.log(`Total Pages Analyzed: ${results.summary.total_pages}`);
    console.log(`Successful: ${results.summary.successful_pages}`);
    console.log(`Failed: ${results.summary.failed_pages}`);
    console.log(`Total Issues Found: ${results.summary.total_issues}`);
    console.log(`  🔴 Critical: ${results.summary.critical_issues}`);
    console.log(`  🟠 High: ${results.summary.high_issues}`);
    console.log(`  🟡 Medium: ${results.summary.medium_issues}`);
    console.log(`  🔵 Low: ${results.summary.low_issues}`);
    
    console.log('\\n💡 TOP RECOMMENDATIONS');
    console.log('======================');
    results.overall_recommendations.slice(0, 5).forEach((rec, index) => {
        console.log(`${index + 1}. ${rec.priority} ${rec.message}`);
    });
    
    console.log(`\\n📋 Full report saved to: ${CONFIG.report_file}`);
    console.log(`📸 Screenshots saved to: ${CONFIG.output_dir}`);
    
    return results;
}

function generateOverallRecommendations(results) {
    const recommendations = [];
    
    // High-level analysis
    const totalApps = Object.keys(results.applications).length;
    const appsWithCriticalIssues = Object.values(results.applications).filter(app => 
        app.app_summary.critical_issues > 0
    ).length;
    
    if (appsWithCriticalIssues > 0) {
        recommendations.push({
            priority: '🔴 URGENT:',
            message: `${appsWithCriticalIssues}/${totalApps} applications have critical issues requiring immediate attention`,
            category: 'critical'
        });
    }

    // Performance analysis
    const slowPages = [];
    Object.values(results.applications).forEach(app => {
        Object.entries(app.pages).forEach(([route, page]) => {
            if (page.load_time > 2000) {
                slowPages.push(`${app.name}${route}`);
            }
        });
    });
    
    if (slowPages.length > 0) {
        recommendations.push({
            priority: '🟠 HIGH:',
            message: `${slowPages.length} pages have slow load times (>2s) affecting user experience`,
            category: 'performance'
        });
    }

    // Accessibility analysis
    const accessibilityIssues = results.summary.medium_issues + results.summary.low_issues;
    if (accessibilityIssues > 5) {
        recommendations.push({
            priority: '🟡 MEDIUM:',
            message: `${accessibilityIssues} accessibility issues found - consider comprehensive accessibility audit`,
            category: 'accessibility'
        });
    }

    // Content analysis
    const blankPages = [];
    Object.values(results.applications).forEach(app => {
        Object.entries(app.pages).forEach(([route, page]) => {
            if (page.analysis && page.analysis.content_analysis.is_blank_page) {
                blankPages.push(`${app.name}${route}`);
            }
        });
    });
    
    if (blankPages.length > 0) {
        recommendations.push({
            priority: '🔴 CRITICAL:',
            message: `${blankPages.length} pages appear blank or have minimal content`,
            category: 'content'
        });
    }

    results.overall_recommendations = recommendations;
}

// Run the analysis if called directly
if (require.main === module) {
    runDeepPageAnalysis().catch(console.error);
}

module.exports = { runDeepPageAnalysis, CONFIG };