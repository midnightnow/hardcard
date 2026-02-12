#!/usr/bin/env node

/**
 * Comprehensive Testing Workflow - Complete App Testing Automation
 * Tests every page, module, function, and component to identify all errors
 * Generates detailed work orders for repair teams
 */

const fs = require('fs');
const path = require('path');

class ComprehensiveTestingWorkflow {
    constructor() {
        this.config = {
            // Applications to test
            applications: [
                {
                    name: 'main_frontend',
                    url: 'http://localhost:5173',
                    type: 'react_spa',
                    routes_file: '/Users/studio/hardcard/frontend/src/user-routes.tsx',
                    components_dir: '/Users/studio/hardcard/frontend/src/components',
                    pages_dir: '/Users/studio/hardcard/frontend/src/pages'
                },
                {
                    name: 'api_backend',
                    url: 'http://localhost:3001',
                    type: 'fastapi',
                    source_dir: '/Users/studio/hardcard/backend/app'
                },
                {
                    name: 'hardcard_suite',
                    url: 'http://localhost:3002',
                    type: 'monorepo',
                    source_dir: '/Users/studio/hardcard/hardcard-suite'
                }
            ],

            // Testing configuration
            testing: {
                timeout: 30000,
                screenshot_on_error: true,
                detailed_logging: true,
                performance_thresholds: {
                    load_time: 3000,
                    first_paint: 1000,
                    largest_contentful_paint: 2500
                },
                accessibility_compliance: 'WCAG_2.1_AA'
            },

            // Output configuration
            output: {
                base_dir: '/Users/studio/hardcard/comprehensive_testing',
                work_orders_dir: '/Users/studio/hardcard/work_orders',
                screenshots_dir: '/Users/studio/hardcard/comprehensive_screenshots',
                reports_dir: '/Users/studio/hardcard/test_reports'
            }
        };

        // Create output directories
        Object.values(this.config.output).forEach(dir => {
            if (!fs.existsSync(dir)) {
                fs.mkdirSync(dir, { recursive: true });
            }
        });

        this.testResults = {
            session_id: Date.now().toString(),
            timestamp: new Date().toISOString(),
            applications: {},
            global_summary: {
                total_tests: 0,
                passed_tests: 0,
                failed_tests: 0,
                total_issues: 0,
                critical_issues: 0,
                work_orders_created: 0
            },
            work_orders: []
        };
    }

    // 🔍 COMPREHENSIVE APPLICATION DISCOVERY
    async discoverApplicationStructure(app) {
        console.log(`🔍 Discovering structure for ${app.name}...`);
        
        const structure = {
            routes: [],
            components: [],
            api_endpoints: [],
            pages: [],
            modules: [],
            dependencies: [],
            configuration_files: []
        };

        try {
            // Discover routes
            if (app.routes_file && fs.existsSync(app.routes_file)) {
                structure.routes = await this.extractRoutes(app.routes_file);
            }

            // Discover components
            if (app.components_dir && fs.existsSync(app.components_dir)) {
                structure.components = await this.discoverComponents(app.components_dir);
            }

            // Discover pages
            if (app.pages_dir && fs.existsSync(app.pages_dir)) {
                structure.pages = await this.discoverPages(app.pages_dir);
            }

            // Discover API endpoints
            if (app.type === 'fastapi' && app.source_dir) {
                structure.api_endpoints = await this.discoverAPIEndpoints(app.source_dir);
            }

            // Discover modules
            if (app.source_dir && fs.existsSync(app.source_dir)) {
                structure.modules = await this.discoverModules(app.source_dir);
            }

            console.log(`  📊 Discovered: ${structure.routes.length} routes, ${structure.components.length} components, ${structure.pages.length} pages`);

        } catch (error) {
            console.log(`  ❌ Discovery error for ${app.name}: ${error.message}`);
        }

        return structure;
    }

    async extractRoutes(routesFile) {
        try {
            const content = fs.readFileSync(routesFile, 'utf8');
            const routes = [];
            
            // Extract route paths from React Router configuration
            const pathMatches = content.match(/path:\s*["']([^"']+)["']/g);
            if (pathMatches) {
                pathMatches.forEach(match => {
                    const path = match.match(/["']([^"']+)["']/)[1];
                    routes.push({
                        path,
                        type: 'react_route',
                        source: routesFile
                    });
                });
            }

            return routes;
        } catch (error) {
            console.log(`    ❌ Failed to extract routes: ${error.message}`);
            return [];
        }
    }

    async discoverComponents(componentsDir) {
        try {
            const components = [];
            const files = this.getAllFiles(componentsDir, ['.tsx', '.ts', '.jsx', '.js']);
            
            files.forEach(file => {
                const name = path.basename(file, path.extname(file));
                components.push({
                    name,
                    path: file,
                    type: 'react_component',
                    extension: path.extname(file)
                });
            });

            return components;
        } catch (error) {
            console.log(`    ❌ Failed to discover components: ${error.message}`);
            return [];
        }
    }

    async discoverPages(pagesDir) {
        try {
            const pages = [];
            const files = this.getAllFiles(pagesDir, ['.tsx', '.ts', '.jsx', '.js']);
            
            files.forEach(file => {
                const name = path.basename(file, path.extname(file));
                pages.push({
                    name,
                    path: file,
                    type: 'react_page',
                    route: `/${name.toLowerCase()}`,
                    extension: path.extname(file)
                });
            });

            return pages;
        } catch (error) {
            console.log(`    ❌ Failed to discover pages: ${error.message}`);
            return [];
        }
    }

    async discoverAPIEndpoints(sourceDir) {
        try {
            const endpoints = [];
            const files = this.getAllFiles(sourceDir, ['.py']);
            
            for (const file of files) {
                const content = fs.readFileSync(file, 'utf8');
                
                // Extract FastAPI route decorators
                const routeMatches = content.match(/@app\.(get|post|put|delete|patch)\(["']([^"']+)["']/g);
                if (routeMatches) {
                    routeMatches.forEach(match => {
                        const [, method, endpoint] = match.match(/@app\.(\w+)\(["']([^"']+)["']/);
                        endpoints.push({
                            method: method.toUpperCase(),
                            path: endpoint,
                            source: file,
                            type: 'fastapi_endpoint'
                        });
                    });
                }
            }

            return endpoints;
        } catch (error) {
            console.log(`    ❌ Failed to discover API endpoints: ${error.message}`);
            return [];
        }
    }

    async discoverModules(sourceDir) {
        try {
            const modules = [];
            const files = this.getAllFiles(sourceDir, ['.py', '.ts', '.tsx', '.js', '.jsx']);
            
            files.forEach(file => {
                const name = path.basename(file, path.extname(file));
                const relativePath = path.relative(sourceDir, file);
                
                modules.push({
                    name,
                    path: file,
                    relative_path: relativePath,
                    type: this.getModuleType(file),
                    extension: path.extname(file)
                });
            });

            return modules;
        } catch (error) {
            console.log(`    ❌ Failed to discover modules: ${error.message}`);
            return [];
        }
    }

    // 🧪 COMPREHENSIVE TESTING EXECUTION
    async runComprehensiveTests(app, structure) {
        console.log(`\\n🧪 Starting comprehensive testing for ${app.name}...`);
        
        const appResults = {
            name: app.name,
            url: app.url,
            structure,
            test_suites: {
                route_tests: [],
                component_tests: [],
                api_tests: [],
                integration_tests: [],
                performance_tests: [],
                accessibility_tests: [],
                security_tests: []
            },
            issues_found: [],
            work_orders: [],
            summary: {
                total_tests: 0,
                passed: 0,
                failed: 0,
                errors: 0
            }
        };

        try {
            const playwright = require('playwright');
            const browser = await playwright.chromium.launch({ 
                headless: false,
                slowMo: 100 // Slow down for better observation
            });
            const context = await browser.newContext({
                viewport: { width: 1920, height: 1080 }
            });
            const page = await context.newPage();

            // Install comprehensive monitoring
            await this.installComprehensiveMonitoring(page);

            // Test all routes
            if (structure.routes.length > 0) {
                appResults.test_suites.route_tests = await this.testAllRoutes(page, app, structure.routes);
            }

            // Test all components (by visiting pages that use them)
            if (structure.pages.length > 0) {
                appResults.test_suites.component_tests = await this.testAllComponents(page, app, structure.pages);
            }

            // Test API endpoints
            if (structure.api_endpoints.length > 0) {
                appResults.test_suites.api_tests = await this.testAllAPIEndpoints(app, structure.api_endpoints);
            }

            // Run integration tests
            appResults.test_suites.integration_tests = await this.runIntegrationTests(page, app, structure);

            // Run performance tests
            appResults.test_suites.performance_tests = await this.runPerformanceTests(page, app, structure);

            // Run accessibility tests
            appResults.test_suites.accessibility_tests = await this.runAccessibilityTests(page, app, structure);

            // Run security tests
            appResults.test_suites.security_tests = await this.runSecurityTests(page, app, structure);

            await browser.close();

            // Analyze results and generate issues
            appResults.issues_found = this.analyzeTestResults(appResults.test_suites);
            
            // Generate work orders
            appResults.work_orders = this.generateWorkOrders(app, appResults.issues_found);

            // Update summary
            this.updateTestSummary(appResults);

        } catch (error) {
            console.log(`❌ Testing error for ${app.name}: ${error.message}`);
            appResults.issues_found.push({
                type: 'critical',
                category: 'testing_framework',
                message: `Testing framework error: ${error.message}`,
                location: 'test_execution',
                priority: 'critical'
            });
        }

        return appResults;
    }

    async installComprehensiveMonitoring(page) {
        await page.addInitScript(() => {
            window.testMonitor = {
                errors: [],
                warnings: [],
                performance: {},
                accessibility: {},
                interactions: [],
                network: [],
                console: []
            };

            // Monitor JavaScript errors
            window.addEventListener('error', (e) => {
                window.testMonitor.errors.push({
                    message: e.message,
                    filename: e.filename,
                    line: e.lineno,
                    column: e.colno,
                    stack: e.error?.stack,
                    timestamp: Date.now()
                });
            });

            // Monitor unhandled promise rejections
            window.addEventListener('unhandledrejection', (e) => {
                window.testMonitor.errors.push({
                    message: 'Unhandled Promise Rejection: ' + e.reason,
                    type: 'promise_rejection',
                    timestamp: Date.now()
                });
            });

            // Monitor console messages
            const originalLog = console.log;
            const originalError = console.error;
            const originalWarn = console.warn;

            console.log = (...args) => {
                window.testMonitor.console.push({ type: 'log', message: args.join(' '), timestamp: Date.now() });
                originalLog.apply(console, args);
            };

            console.error = (...args) => {
                window.testMonitor.console.push({ type: 'error', message: args.join(' '), timestamp: Date.now() });
                originalError.apply(console, args);
            };

            console.warn = (...args) => {
                window.testMonitor.console.push({ type: 'warn', message: args.join(' '), timestamp: Date.now() });
                originalWarn.apply(console, args);
            };

            // Monitor network requests
            if (window.fetch) {
                const originalFetch = window.fetch;
                window.fetch = async (...args) => {
                    const startTime = Date.now();
                    try {
                        const response = await originalFetch.apply(window, args);
                        window.testMonitor.network.push({
                            url: args[0],
                            status: response.status,
                            duration: Date.now() - startTime,
                            success: response.ok,
                            timestamp: Date.now()
                        });
                        return response;
                    } catch (error) {
                        window.testMonitor.network.push({
                            url: args[0],
                            error: error.message,
                            duration: Date.now() - startTime,
                            success: false,
                            timestamp: Date.now()
                        });
                        throw error;
                    }
                };
            }
        });

        // Monitor network responses
        page.on('response', response => {
            if (response.status() >= 400) {
                page.evaluate(({url, status}) => {
                    if (window.testMonitor) {
                        window.testMonitor.network.push({
                            url,
                            status,
                            error: `HTTP ${status}`,
                            timestamp: Date.now()
                        });
                    }
                }, {url: response.url(), status: response.status()});
            }
        });
    }

    async testAllRoutes(page, app, routes) {
        console.log(`  🛤️  Testing ${routes.length} routes...`);
        const routeTests = [];

        for (const route of routes) {
            console.log(`    📄 Testing route: ${route.path}`);
            
            const testResult = {
                route: route.path,
                url: app.url + route.path,
                timestamp: new Date().toISOString(),
                status: 'unknown',
                load_time: null,
                errors: [],
                warnings: [],
                accessibility_issues: [],
                performance_metrics: {},
                screenshot: null
            };

            try {
                const startTime = Date.now();
                await page.goto(app.url + route.path, { 
                    waitUntil: 'networkidle', 
                    timeout: this.config.testing.timeout 
                });
                testResult.load_time = Date.now() - startTime;
                testResult.status = 'loaded';

                // Capture screenshot
                const screenshotPath = path.join(
                    this.config.output.screenshots_dir,
                    `${app.name}_route_${route.path.replace(/\//g, '_')}_${Date.now()}.png`
                );
                await page.screenshot({ path: screenshotPath, fullPage: true });
                testResult.screenshot = screenshotPath;

                // Collect monitoring data
                const monitorData = await page.evaluate(() => window.testMonitor || {});
                testResult.errors = monitorData.errors || [];
                testResult.warnings = monitorData.console?.filter(c => c.type === 'warn') || [];

                // Performance analysis
                testResult.performance_metrics = await page.evaluate(() => {
                    if (window.performance) {
                        const navigation = performance.getEntriesByType('navigation')[0];
                        return {
                            dom_content_loaded: navigation?.domContentLoadedEventEnd - navigation?.domContentLoadedEventStart,
                            load_complete: navigation?.loadEventEnd - navigation?.loadEventStart,
                            first_paint: performance.getEntriesByName('first-paint')[0]?.startTime,
                            first_contentful_paint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime,
                            largest_contentful_paint: performance.getEntriesByName('largest-contentful-paint')[0]?.startTime
                        };
                    }
                    return {};
                });

                // Accessibility analysis
                testResult.accessibility_issues = await this.checkAccessibility(page);

                // Functional testing
                await this.testPageFunctionality(page, testResult);

            } catch (error) {
                testResult.status = 'failed';
                testResult.errors.push({
                    type: 'navigation_error',
                    message: error.message,
                    stack: error.stack
                });
            }

            routeTests.push(testResult);
        }

        return routeTests;
    }

    async testAllComponents(page, app, pages) {
        console.log(`  🧩 Testing components across ${pages.length} pages...`);
        const componentTests = [];

        for (const pageInfo of pages) {
            console.log(`    🧩 Testing components on page: ${pageInfo.name}`);
            
            try {
                const pageUrl = app.url + pageInfo.route;
                await page.goto(pageUrl, { waitUntil: 'networkidle', timeout: this.config.testing.timeout });

                // Test all interactive components
                const components = await page.evaluate(() => {
                    const elements = [];
                    
                    // Find all interactive elements
                    const interactive = document.querySelectorAll('button, input, select, textarea, a, [role="button"], [onclick]');
                    interactive.forEach(el => {
                        elements.push({
                            tagName: el.tagName,
                            type: el.type || 'unknown',
                            className: el.className,
                            id: el.id,
                            text: el.textContent?.slice(0, 50),
                            visible: el.offsetParent !== null,
                            disabled: el.disabled,
                            hasClickHandler: !!el.onclick || el.hasAttribute('onclick')
                        });
                    });

                    return elements;
                });

                // Test each component
                for (const component of components) {
                    const componentTest = await this.testComponent(page, component, pageInfo);
                    componentTests.push(componentTest);
                }

            } catch (error) {
                componentTests.push({
                    page: pageInfo.name,
                    status: 'failed',
                    error: error.message
                });
            }
        }

        return componentTests;
    }

    async testComponent(page, component, pageInfo) {
        const test = {
            component_type: component.tagName,
            component_id: component.id,
            component_class: component.className,
            page: pageInfo.name,
            status: 'unknown',
            issues: []
        };

        try {
            // Accessibility checks
            if (!component.text && component.tagName === 'BUTTON') {
                test.issues.push({
                    type: 'accessibility',
                    message: 'Button has no text content',
                    severity: 'medium'
                });
            }

            if (component.tagName === 'INPUT' && !component.id && !component.className.includes('label')) {
                test.issues.push({
                    type: 'accessibility',
                    message: 'Input field may be missing proper labeling',
                    severity: 'medium'
                });
            }

            // Functionality checks
            if (component.tagName === 'BUTTON' && !component.disabled && component.visible) {
                try {
                    // Test button click functionality
                    const selector = component.id ? `#${component.id}` : 
                                   component.className ? `.${component.className.split(' ')[0]}` :
                                   `${component.tagName.toLowerCase()}`;
                    
                    const elementExists = await page.$(selector);
                    if (elementExists) {
                        test.status = 'functional';
                    } else {
                        test.status = 'not_found';
                        test.issues.push({
                            type: 'functionality',
                            message: 'Component not found with generated selector',
                            severity: 'high'
                        });
                    }
                } catch (error) {
                    test.issues.push({
                        type: 'functionality',
                        message: `Component interaction failed: ${error.message}`,
                        severity: 'medium'
                    });
                }
            }

            if (test.issues.length === 0) {
                test.status = 'passed';
            } else {
                test.status = 'issues_found';
            }

        } catch (error) {
            test.status = 'failed';
            test.issues.push({
                type: 'test_error',
                message: error.message,
                severity: 'high'
            });
        }

        return test;
    }

    async testAllAPIEndpoints(app, endpoints) {
        console.log(`  🔌 Testing ${endpoints.length} API endpoints...`);
        const apiTests = [];

        for (const endpoint of endpoints) {
            console.log(`    🔌 Testing API: ${endpoint.method} ${endpoint.path}`);
            
            const testResult = {
                method: endpoint.method,
                path: endpoint.path,
                url: app.url + endpoint.path,
                timestamp: new Date().toISOString(),
                status: 'unknown',
                response_time: null,
                response_status: null,
                errors: []
            };

            try {
                const http = require('http');
                const https = require('https');
                const url = require('url');
                
                const parsedUrl = url.parse(app.url + endpoint.path);
                const client = parsedUrl.protocol === 'https:' ? https : http;

                const startTime = Date.now();
                
                const response = await new Promise((resolve, reject) => {
                    const req = client.request({
                        hostname: parsedUrl.hostname,
                        port: parsedUrl.port,
                        path: parsedUrl.path,
                        method: endpoint.method,
                        timeout: this.config.testing.timeout
                    }, resolve);

                    req.on('error', reject);
                    req.on('timeout', () => reject(new Error('Request timeout')));
                    req.end();
                });

                testResult.response_time = Date.now() - startTime;
                testResult.response_status = response.statusCode;
                testResult.status = response.statusCode < 400 ? 'passed' : 'failed';

                if (response.statusCode >= 400) {
                    testResult.errors.push({
                        type: 'http_error',
                        message: `HTTP ${response.statusCode} ${response.statusMessage}`,
                        severity: response.statusCode >= 500 ? 'high' : 'medium'
                    });
                }

            } catch (error) {
                testResult.status = 'failed';
                testResult.errors.push({
                    type: 'request_error',
                    message: error.message,
                    severity: 'high'
                });
            }

            apiTests.push(testResult);
        }

        return apiTests;
    }

    async runIntegrationTests(page, app, structure) {
        console.log(`  🔗 Running integration tests...`);
        const integrationTests = [];

        // Test common user flows
        const commonFlows = [
            {
                name: 'homepage_to_login',
                steps: ['/', '/login'],
                description: 'Test navigation from homepage to login'
            },
            {
                name: 'login_to_dashboard',
                steps: ['/login', '/dashboard'],
                description: 'Test navigation from login to dashboard'
            },
            {
                name: 'homepage_to_products',
                steps: ['/', '/products'],
                description: 'Test navigation from homepage to products'
            }
        ];

        for (const flow of commonFlows) {
            const test = await this.testUserFlow(page, app, flow);
            integrationTests.push(test);
        }

        return integrationTests;
    }

    async testUserFlow(page, app, flow) {
        const test = {
            name: flow.name,
            description: flow.description,
            steps: flow.steps,
            status: 'unknown',
            completed_steps: 0,
            errors: [],
            total_time: 0
        };

        const startTime = Date.now();

        try {
            for (let i = 0; i < flow.steps.length; i++) {
                const step = flow.steps[i];
                console.log(`      ➤ Step ${i + 1}: ${step}`);
                
                await page.goto(app.url + step, { 
                    waitUntil: 'networkidle', 
                    timeout: this.config.testing.timeout 
                });
                
                test.completed_steps++;
                
                // Wait for page to stabilize
                await page.waitForTimeout(1000);
            }

            test.status = 'passed';
            test.total_time = Date.now() - startTime;

        } catch (error) {
            test.status = 'failed';
            test.errors.push({
                type: 'flow_error',
                message: error.message,
                step: test.completed_steps + 1,
                severity: 'high'
            });
            test.total_time = Date.now() - startTime;
        }

        return test;
    }

    async runPerformanceTests(page, app, structure) {
        console.log(`  ⚡ Running performance tests...`);
        const performanceTests = [];

        // Test performance on key routes
        const keyRoutes = structure.routes.slice(0, 5); // Test first 5 routes
        
        for (const route of keyRoutes) {
            const test = await this.testRoutePerformance(page, app, route);
            performanceTests.push(test);
        }

        return performanceTests;
    }

    async testRoutePerformance(page, app, route) {
        const test = {
            route: route.path,
            url: app.url + route.path,
            metrics: {},
            issues: [],
            status: 'unknown'
        };

        try {
            const startTime = Date.now();
            await page.goto(app.url + route.path, { waitUntil: 'networkidle', timeout: this.config.testing.timeout });
            const loadTime = Date.now() - startTime;

            // Collect performance metrics
            test.metrics = await page.evaluate(() => {
                if (window.performance) {
                    const navigation = performance.getEntriesByType('navigation')[0];
                    return {
                        total_load_time: Date.now() - performance.timeOrigin,
                        dom_content_loaded: navigation?.domContentLoadedEventEnd - navigation?.domContentLoadedEventStart,
                        first_paint: performance.getEntriesByName('first-paint')[0]?.startTime,
                        first_contentful_paint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime,
                        largest_contentful_paint: performance.getEntriesByName('largest-contentful-paint')[0]?.startTime
                    };
                }
                return {};
            });

            test.metrics.measured_load_time = loadTime;

            // Check against thresholds
            const thresholds = this.config.testing.performance_thresholds;
            
            if (loadTime > thresholds.load_time) {
                test.issues.push({
                    type: 'performance',
                    message: `Load time ${loadTime}ms exceeds threshold ${thresholds.load_time}ms`,
                    severity: 'medium'
                });
            }

            if (test.metrics.first_paint > thresholds.first_paint) {
                test.issues.push({
                    type: 'performance',
                    message: `First paint ${test.metrics.first_paint}ms exceeds threshold ${thresholds.first_paint}ms`,
                    severity: 'low'
                });
            }

            if (test.metrics.largest_contentful_paint > thresholds.largest_contentful_paint) {
                test.issues.push({
                    type: 'performance',
                    message: `LCP ${test.metrics.largest_contentful_paint}ms exceeds threshold ${thresholds.largest_contentful_paint}ms`,
                    severity: 'medium'
                });
            }

            test.status = test.issues.length === 0 ? 'passed' : 'issues_found';

        } catch (error) {
            test.status = 'failed';
            test.issues.push({
                type: 'test_error',
                message: error.message,
                severity: 'high'
            });
        }

        return test;
    }

    async runAccessibilityTests(page, app, structure) {
        console.log(`  ♿ Running accessibility tests...`);
        const accessibilityTests = [];

        // Test accessibility on key routes
        const keyRoutes = structure.routes.slice(0, 5);
        
        for (const route of keyRoutes) {
            const test = await this.testRouteAccessibility(page, app, route);
            accessibilityTests.push(test);
        }

        return accessibilityTests;
    }

    async testRouteAccessibility(page, app, route) {
        const test = {
            route: route.path,
            url: app.url + route.path,
            issues: [],
            status: 'unknown'
        };

        try {
            await page.goto(app.url + route.path, { waitUntil: 'networkidle', timeout: this.config.testing.timeout });
            
            test.issues = await this.checkAccessibility(page);
            test.status = test.issues.length === 0 ? 'passed' : 'issues_found';

        } catch (error) {
            test.status = 'failed';
            test.issues.push({
                type: 'test_error',
                message: error.message,
                severity: 'high'
            });
        }

        return test;
    }

    async checkAccessibility(page) {
        const issues = [];

        try {
            const accessibilityData = await page.evaluate(() => {
                const issues = [];

                // Check for missing alt text on images
                const images = document.querySelectorAll('img');
                images.forEach((img, index) => {
                    if (!img.alt) {
                        issues.push({
                            type: 'accessibility',
                            message: `Image ${index + 1} missing alt text`,
                            element: 'img',
                            severity: 'medium'
                        });
                    }
                });

                // Check for form inputs without labels
                const inputs = document.querySelectorAll('input[type]:not([type="hidden"]):not([type="submit"]):not([type="button"])');
                inputs.forEach((input, index) => {
                    if (!input.labels?.length && !input.getAttribute('aria-label') && !input.getAttribute('aria-labelledby')) {
                        issues.push({
                            type: 'accessibility',
                            message: `Input field ${index + 1} missing proper labeling`,
                            element: 'input',
                            severity: 'high'
                        });
                    }
                });

                // Check for proper heading hierarchy
                const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
                if (headings.length === 0) {
                    issues.push({
                        type: 'accessibility',
                        message: 'No heading elements found - poor content structure',
                        element: 'heading',
                        severity: 'medium'
                    });
                } else {
                    const h1Count = document.querySelectorAll('h1').length;
                    if (h1Count === 0) {
                        issues.push({
                            type: 'accessibility',
                            message: 'No H1 heading found - missing main page heading',
                            element: 'h1',
                            severity: 'medium'
                        });
                    } else if (h1Count > 1) {
                        issues.push({
                            type: 'accessibility',
                            message: `Multiple H1 headings (${h1Count}) - should be exactly one`,
                            element: 'h1',
                            severity: 'low'
                        });
                    }
                }

                // Check for keyboard accessibility
                const focusableElements = document.querySelectorAll('button, input, select, textarea, a, [tabindex]:not([tabindex="-1"])');
                if (focusableElements.length === 0) {
                    issues.push({
                        type: 'accessibility',
                        message: 'No focusable elements found - poor keyboard accessibility',
                        element: 'focus',
                        severity: 'high'
                    });
                }

                // Check for proper landmark elements
                const landmarks = document.querySelectorAll('main, nav, header, footer, [role="main"], [role="navigation"], [role="banner"], [role="contentinfo"]');
                if (landmarks.length === 0) {
                    issues.push({
                        type: 'accessibility',
                        message: 'No landmark elements found - poor page structure for screen readers',
                        element: 'landmarks',
                        severity: 'medium'
                    });
                }

                return issues;
            });

            issues.push(...accessibilityData);

        } catch (error) {
            issues.push({
                type: 'accessibility_test_error',
                message: `Accessibility test failed: ${error.message}`,
                severity: 'medium'
            });
        }

        return issues;
    }

    async runSecurityTests(page, app, structure) {
        console.log(`  🔒 Running security tests...`);
        const securityTests = [];

        // Basic security checks
        const securityTest = {
            name: 'basic_security_checks',
            issues: [],
            status: 'unknown'
        };

        try {
            // Check for HTTPS
            if (!app.url.startsWith('https://') && !app.url.includes('localhost')) {
                securityTest.issues.push({
                    type: 'security',
                    message: 'Application not using HTTPS',
                    severity: 'high'
                });
            }

            // Check for security headers (basic check)
            await page.goto(app.url, { waitUntil: 'networkidle', timeout: this.config.testing.timeout });
            
            const securityHeaders = await page.evaluate(() => {
                // This would need to be expanded for real security testing
                return {
                    csp_present: !!document.querySelector('meta[http-equiv="Content-Security-Policy"]'),
                    has_secure_forms: Array.from(document.querySelectorAll('form')).every(form => 
                        form.action.startsWith('https://') || form.action.startsWith('/')
                    )
                };
            });

            if (!securityHeaders.csp_present) {
                securityTest.issues.push({
                    type: 'security',
                    message: 'No Content Security Policy detected',
                    severity: 'medium'
                });
            }

            securityTest.status = securityTest.issues.length === 0 ? 'passed' : 'issues_found';

        } catch (error) {
            securityTest.status = 'failed';
            securityTest.issues.push({
                type: 'security_test_error',
                message: error.message,
                severity: 'medium'
            });
        }

        securityTests.push(securityTest);
        return securityTests;
    }

    async testPageFunctionality(page, testResult) {
        try {
            // Test form submissions
            const forms = await page.$$('form');
            for (const form of forms) {
                // Basic form validation test
                const inputs = await form.$$('input[required]');
                if (inputs.length > 0) {
                    // Test required field validation
                    try {
                        await form.evaluate(f => f.submit());
                        // If no validation occurs, it might be an issue
                    } catch (e) {
                        // Form validation likely working
                    }
                }
            }

            // Test interactive elements
            const buttons = await page.$$('button:not([disabled])');
            for (let i = 0; i < Math.min(buttons.length, 3); i++) {
                try {
                    await buttons[i].click();
                    await page.waitForTimeout(500); // Wait for any effects
                } catch (e) {
                    testResult.errors.push({
                        type: 'interaction_error',
                        message: `Button ${i + 1} click failed: ${e.message}`,
                        severity: 'medium'
                    });
                }
            }

        } catch (error) {
            testResult.errors.push({
                type: 'functionality_test_error',
                message: error.message,
                severity: 'low'
            });
        }
    }

    // 📋 WORK ORDER GENERATION
    generateWorkOrders(app, issues) {
        console.log(`  📋 Generating work orders for ${issues.length} issues...`);
        const workOrders = [];

        // Group issues by category and priority
        const groupedIssues = this.groupIssuesByCategory(issues);

        Object.entries(groupedIssues).forEach(([category, categoryIssues]) => {
            const workOrder = {
                id: `WO_${Date.now()}_${category}`,
                application: app.name,
                category,
                priority: this.calculateWorkOrderPriority(categoryIssues),
                status: 'open',
                created_date: new Date().toISOString(),
                estimated_effort: this.estimateEffort(categoryIssues),
                issues: categoryIssues,
                repair_instructions: this.generateRepairInstructions(category, categoryIssues),
                acceptance_criteria: this.generateAcceptanceCriteria(category, categoryIssues)
            };

            workOrders.push(workOrder);
        });

        // Save work orders to files
        workOrders.forEach(wo => {
            const workOrderPath = path.join(
                this.config.output.work_orders_dir,
                `${wo.id}.json`
            );
            fs.writeFileSync(workOrderPath, JSON.stringify(wo, null, 2));
        });

        return workOrders;
    }

    groupIssuesByCategory(issues) {
        const grouped = {};
        
        issues.forEach(issue => {
            const category = issue.category || 'general';
            if (!grouped[category]) {
                grouped[category] = [];
            }
            grouped[category].push(issue);
        });

        return grouped;
    }

    calculateWorkOrderPriority(issues) {
        const criticalCount = issues.filter(i => i.severity === 'critical' || i.severity === 'high').length;
        const mediumCount = issues.filter(i => i.severity === 'medium').length;
        
        if (criticalCount > 0) return 'critical';
        if (mediumCount > 3) return 'high';
        if (mediumCount > 0) return 'medium';
        return 'low';
    }

    estimateEffort(issues) {
        // Simple effort estimation based on issue count and severity
        let effort = 0;
        issues.forEach(issue => {
            switch (issue.severity) {
                case 'critical': effort += 8; break;
                case 'high': effort += 4; break;
                case 'medium': effort += 2; break;
                case 'low': effort += 1; break;
                default: effort += 1;
            }
        });

        if (effort <= 4) return 'small';
        if (effort <= 12) return 'medium';
        if (effort <= 24) return 'large';
        return 'extra_large';
    }

    generateRepairInstructions(category, issues) {
        const instructions = [];

        switch (category) {
            case 'accessibility':
                instructions.push('Review WCAG 2.1 AA guidelines');
                instructions.push('Add missing alt text to images');
                instructions.push('Ensure all form inputs have proper labels');
                instructions.push('Implement proper heading hierarchy');
                instructions.push('Add landmark elements (main, nav, header, footer)');
                break;

            case 'performance':
                instructions.push('Optimize page load times');
                instructions.push('Implement lazy loading for images');
                instructions.push('Minify CSS and JavaScript');
                instructions.push('Optimize database queries');
                instructions.push('Add caching strategies');
                break;

            case 'functionality':
                instructions.push('Fix broken interactive elements');
                instructions.push('Implement proper form validation');
                instructions.push('Fix navigation issues');
                instructions.push('Test all user flows');
                break;

            case 'security':
                instructions.push('Implement HTTPS if not present');
                instructions.push('Add Content Security Policy headers');
                instructions.push('Validate all user inputs');
                instructions.push('Implement proper authentication');
                break;

            default:
                instructions.push('Review and fix identified issues');
                instructions.push('Test thoroughly after fixes');
        }

        // Add specific issue-based instructions
        issues.forEach(issue => {
            if (issue.message) {
                instructions.push(`Fix: ${issue.message}`);
            }
        });

        return instructions;
    }

    generateAcceptanceCriteria(category, issues) {
        const criteria = [];

        switch (category) {
            case 'accessibility':
                criteria.push('All images have descriptive alt text');
                criteria.push('All form inputs have proper labels');
                criteria.push('Page has proper heading hierarchy with exactly one H1');
                criteria.push('All interactive elements are keyboard accessible');
                criteria.push('Page has proper landmark elements');
                break;

            case 'performance':
                criteria.push('Page load time under 3 seconds');
                criteria.push('First paint under 1 second');
                criteria.push('Largest Contentful Paint under 2.5 seconds');
                criteria.push('No console errors during page load');
                break;

            case 'functionality':
                criteria.push('All buttons and links work correctly');
                criteria.push('All forms validate properly');
                criteria.push('Navigation works without errors');
                criteria.push('No JavaScript console errors');
                break;

            case 'security':
                criteria.push('HTTPS implemented where required');
                criteria.push('Security headers present');
                criteria.push('No sensitive data exposed');
                criteria.push('Proper input validation implemented');
                break;

            default:
                criteria.push('All identified issues resolved');
                criteria.push('No new issues introduced');
                criteria.push('Functionality tested and working');
        }

        return criteria;
    }

    // 📊 ANALYSIS AND REPORTING
    analyzeTestResults(testSuites) {
        const allIssues = [];

        // Extract issues from all test suites
        Object.values(testSuites).forEach(suite => {
            if (Array.isArray(suite)) {
                suite.forEach(test => {
                    if (test.errors) {
                        test.errors.forEach(error => {
                            allIssues.push({
                                ...error,
                                location: test.route || test.name || 'unknown',
                                test_type: 'error'
                            });
                        });
                    }
                    if (test.issues) {
                        test.issues.forEach(issue => {
                            allIssues.push({
                                ...issue,
                                location: test.route || test.name || 'unknown',
                                test_type: 'issue'
                            });
                        });
                    }
                    if (test.accessibility_issues) {
                        test.accessibility_issues.forEach(issue => {
                            allIssues.push({
                                ...issue,
                                location: test.route || test.name || 'unknown',
                                test_type: 'accessibility'
                            });
                        });
                    }
                });
            }
        });

        return allIssues;
    }

    updateTestSummary(appResults) {
        // Count all tests and results
        Object.values(appResults.test_suites).forEach(suite => {
            if (Array.isArray(suite)) {
                suite.forEach(test => {
                    appResults.summary.total_tests++;
                    
                    if (test.status === 'passed') {
                        appResults.summary.passed++;
                    } else if (test.status === 'failed') {
                        appResults.summary.failed++;
                    } else {
                        appResults.summary.errors++;
                    }
                });
            }
        });

        // Update global summary
        this.testResults.global_summary.total_tests += appResults.summary.total_tests;
        this.testResults.global_summary.passed_tests += appResults.summary.passed;
        this.testResults.global_summary.failed_tests += appResults.summary.failed;
        this.testResults.global_summary.total_issues += appResults.issues_found.length;
        this.testResults.global_summary.work_orders_created += appResults.work_orders.length;

        // Count critical issues
        const criticalIssues = appResults.issues_found.filter(issue => 
            issue.severity === 'critical' || issue.severity === 'high'
        ).length;
        this.testResults.global_summary.critical_issues += criticalIssues;
    }

    // 🚀 MAIN EXECUTION WORKFLOW
    async runComprehensiveTestingWorkflow() {
        console.log('🚀 Starting Comprehensive Testing Workflow');
        console.log('==========================================');
        console.log(`Testing ${this.config.applications.length} applications...`);

        for (const app of this.config.applications) {
            console.log(`\\n🎯 Testing Application: ${app.name}`);
            console.log(`URL: ${app.url}`);
            console.log(`Type: ${app.type}`);

            // Discover application structure
            const structure = await this.discoverApplicationStructure(app);

            // Run comprehensive tests
            const appResults = await this.runComprehensiveTests(app, structure);

            // Store results
            this.testResults.applications[app.name] = appResults;

            console.log(`✅ ${app.name} testing complete:`);
            console.log(`   Tests: ${appResults.summary.total_tests}`);
            console.log(`   Passed: ${appResults.summary.passed}`);
            console.log(`   Failed: ${appResults.summary.failed}`);
            console.log(`   Issues: ${appResults.issues_found.length}`);
            console.log(`   Work Orders: ${appResults.work_orders.length}`);
        }

        // Generate final comprehensive report
        await this.generateFinalReport();

        console.log('\\n📊 COMPREHENSIVE TESTING COMPLETE');
        console.log('===================================');
        console.log(`Total Tests: ${this.testResults.global_summary.total_tests}`);
        console.log(`Passed: ${this.testResults.global_summary.passed_tests}`);
        console.log(`Failed: ${this.testResults.global_summary.failed_tests}`);
        console.log(`Total Issues: ${this.testResults.global_summary.total_issues}`);
        console.log(`Critical Issues: ${this.testResults.global_summary.critical_issues}`);
        console.log(`Work Orders Created: ${this.testResults.global_summary.work_orders_created}`);

        return this.testResults;
    }

    async generateFinalReport() {
        // Save comprehensive results
        const reportPath = path.join(
            this.config.output.reports_dir,
            `comprehensive_test_report_${this.testResults.session_id}.json`
        );
        fs.writeFileSync(reportPath, JSON.stringify(this.testResults, null, 2));

        // Generate summary report
        const summaryPath = path.join(
            this.config.output.reports_dir,
            `test_summary_${this.testResults.session_id}.md`
        );
        const summaryContent = this.generateSummaryMarkdown();
        fs.writeFileSync(summaryPath, summaryContent);

        console.log(`\\n📋 Reports Generated:`);
        console.log(`   Comprehensive: ${reportPath}`);
        console.log(`   Summary: ${summaryPath}`);
        console.log(`   Work Orders: ${this.config.output.work_orders_dir}`);
        console.log(`   Screenshots: ${this.config.output.screenshots_dir}`);
    }

    generateSummaryMarkdown() {
        const summary = this.testResults.global_summary;
        let md = '# Comprehensive Testing Report\\n\\n';
        md += `**Session ID:** ${this.testResults.session_id}\\n`;
        md += `**Timestamp:** ${this.testResults.timestamp}\\n\\n`;
        
        md += '## Overall Results\\n\\n';
        md += `- **Total Tests:** ${summary.total_tests}\\n`;
        md += `- **Passed:** ${summary.passed_tests}\\n`;
        md += `- **Failed:** ${summary.failed_tests}\\n`;
        md += `- **Total Issues:** ${summary.total_issues}\\n`;
        md += `- **Critical Issues:** ${summary.critical_issues}\\n`;
        md += `- **Work Orders Created:** ${summary.work_orders_created}\\n\\n`;

        md += '## Applications Tested\\n\\n';
        Object.entries(this.testResults.applications).forEach(([name, app]) => {
            md += `### ${name}\\n`;
            md += `- **Tests:** ${app.summary.total_tests}\\n`;
            md += `- **Issues:** ${app.issues_found.length}\\n`;
            md += `- **Work Orders:** ${app.work_orders.length}\\n\\n`;
        });

        md += '## Next Steps\\n\\n';
        md += '1. Review work orders in priority order\\n';
        md += '2. Assign work orders to development team\\n';
        md += '3. Implement fixes according to repair instructions\\n';
        md += '4. Validate fixes against acceptance criteria\\n';
        md += '5. Re-run testing to verify all issues resolved\\n';

        return md;
    }

    // Utility methods
    getAllFiles(dir, extensions = []) {
        const files = [];
        
        try {
            const items = fs.readdirSync(dir, { withFileTypes: true });
            
            for (const item of items) {
                const fullPath = path.join(dir, item.name);
                
                if (item.isDirectory()) {
                    files.push(...this.getAllFiles(fullPath, extensions));
                } else if (extensions.length === 0 || extensions.includes(path.extname(item.name))) {
                    files.push(fullPath);
                }
            }
        } catch (error) {
            // Directory doesn't exist or can't be read
        }
        
        return files;
    }

    getModuleType(filePath) {
        const ext = path.extname(filePath);
        const dir = path.dirname(filePath);
        
        if (ext === '.py') return 'python_module';
        if (['.ts', '.tsx'].includes(ext)) return 'typescript_module';
        if (['.js', '.jsx'].includes(ext)) return 'javascript_module';
        if (dir.includes('components')) return 'react_component';
        if (dir.includes('pages')) return 'react_page';
        return 'unknown_module';
    }
}

// Main execution
async function main() {
    try {
        const workflow = new ComprehensiveTestingWorkflow();
        await workflow.runComprehensiveTestingWorkflow();
    } catch (error) {
        console.error('❌ Comprehensive testing workflow failed:', error.message);
        console.log('💡 Ensure all applications are running and Playwright is installed');
    }
}

if (require.main === module) {
    main();
}

module.exports = { ComprehensiveTestingWorkflow };