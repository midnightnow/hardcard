#!/usr/bin/env node

/**
 * Simple VetSorcery API Testing Suite
 * Tests server responses without browser automation
 */

const http = require('http');
const https = require('https');
const fs = require('fs');

const BASE_URL = 'http://localhost:3005';
const TEST_ENDPOINTS = [
    '/',
    '/appointments', 
    '/login',
    '/dashboard',
    '/patients',
    '/patient-profile'
];

class SimpleVetSorceryTester {
    constructor() {
        this.results = {
            timestamp: new Date().toISOString(),
            baseUrl: BASE_URL,
            tests: [],
            summary: { total: 0, passed: 0, failed: 0 }
        };
    }

    async makeRequest(path) {
        return new Promise((resolve, reject) => {
            const url = BASE_URL + path;
            const timeout = 10000;
            
            const req = http.get(url, { timeout }, (res) => {
                let data = '';
                
                res.on('data', chunk => data += chunk);
                res.on('end', () => {
                    resolve({
                        statusCode: res.statusCode,
                        headers: res.headers,
                        body: data,
                        size: data.length
                    });
                });
            });
            
            req.on('error', reject);
            req.on('timeout', () => {
                req.destroy();
                reject(new Error('Request timeout'));
            });
        });
    }

    async testEndpoint(path) {
        console.log(`🧪 Testing ${path}...`);
        this.results.summary.total++;
        
        const startTime = Date.now();
        const result = {
            endpoint: path,
            status: 'unknown',
            duration: 0,
            details: {}
        };

        try {
            const response = await this.makeRequest(path);
            const duration = Date.now() - startTime;
            
            // Analyze response
            const isSuccessful = response.statusCode >= 200 && response.statusCode < 400;
            const hasContent = response.body.length > 0;
            const isHTML = response.headers['content-type']?.includes('text/html');
            const hasReactMount = response.body.includes('id="root"');
            const hasViteScript = response.body.includes('/@vite/client');
            
            // Check for specific errors
            const hasDateError = response.body.includes('toLocaleDateString is not a function');
            const hasJSError = response.body.includes('TypeError') || 
                              response.body.includes('ReferenceError') ||
                              response.body.includes('Unexpected Application Error');
            
            result.status = isSuccessful && !hasDateError && !hasJSError ? 'passed' : 'failed';
            result.duration = duration;
            result.details = {
                statusCode: response.statusCode,
                responseSize: response.size,
                isHTML,
                hasReactMount,
                hasViteScript,
                hasDateError,
                hasJSError,
                contentType: response.headers['content-type']
            };

            if (result.status === 'passed') {
                this.results.summary.passed++;
                console.log(`✅ ${path} - OK (${duration}ms)`);
            } else {
                this.results.summary.failed++;
                console.log(`❌ ${path} - FAILED (${duration}ms)`);
                if (hasDateError) console.log(`   📅 Date formatting error detected`);
                if (hasJSError) console.log(`   🔴 JavaScript error detected`);
            }

        } catch (error) {
            result.status = 'failed';
            result.duration = Date.now() - startTime;
            result.details = { error: error.message };
            this.results.summary.failed++;
            console.log(`❌ ${path} - ERROR: ${error.message}`);
        }

        this.results.tests.push(result);
        return result;
    }

    async testServerHealth() {
        console.log(`🏥 Testing server health...`);
        
        try {
            const response = await this.makeRequest('/');
            const isHealthy = response.statusCode === 200 && 
                            response.body.includes('id="root"') &&
                            response.body.length > 100;
            
            console.log(`🩺 Server Health: ${isHealthy ? 'HEALTHY' : 'UNHEALTHY'}`);
            console.log(`   📊 Status Code: ${response.statusCode}`);
            console.log(`   📦 Response Size: ${response.body.length} bytes`);
            console.log(`   🏷️  Has Root Element: ${response.body.includes('id="root"')}`);
            
            return { healthy: isHealthy, details: response };
        } catch (error) {
            console.log(`💔 Server Health: DOWN - ${error.message}`);
            return { healthy: false, error: error.message };
        }
    }

    async analyzeVetSorcerySpecifics() {
        console.log(`🐾 Analyzing VetSorcery-specific functionality...`);
        
        try {
            const response = await this.makeRequest('/');
            const body = response.body;
            
            const analysis = {
                hasVetSorceryBranding: body.includes('VetSorcery') || body.includes('Vet Sorcery'),
                hasFirebaseConfig: body.includes('firebase') || body.includes('Firebase'),
                hasReactRouter: body.includes('react-router') || body.includes('router'),
                hasAuthSystem: body.includes('auth') || body.includes('Auth'),
                hasModernFramework: body.includes('vite') || body.includes('react'),
                bundleSize: body.length,
                hasSourceMaps: body.includes('sourcemap'),
                isProduction: !body.includes('development')
            };
            
            console.log(`📊 VetSorcery Analysis:`);
            console.log(`   📱 Has VetSorcery Branding: ${analysis.hasVetSorceryBranding}`);
            console.log(`   🔥 Firebase Integration: ${analysis.hasFirebaseConfig}`);
            console.log(`   🛣️  React Router: ${analysis.hasReactRouter}`);
            console.log(`   🔐 Auth System: ${analysis.hasAuthSystem}`);
            console.log(`   ⚡ Modern Framework: ${analysis.hasModernFramework}`);
            console.log(`   📦 Bundle Size: ${(analysis.bundleSize / 1024).toFixed(1)}KB`);
            
            return analysis;
            
        } catch (error) {
            console.log(`❌ VetSorcery Analysis Failed: ${error.message}`);
            return { error: error.message };
        }
    }

    generateReport() {
        const successRate = ((this.results.summary.passed / this.results.summary.total) * 100).toFixed(1);
        
        console.log(`\n📊 === TEST SUMMARY ===`);
        console.log(`📈 Success Rate: ${successRate}%`);
        console.log(`✅ Passed: ${this.results.summary.passed}`);
        console.log(`❌ Failed: ${this.results.summary.failed}`);
        console.log(`📝 Total Tests: ${this.results.summary.total}`);
        
        const reportData = {
            ...this.results,
            summary: {
                ...this.results.summary,
                successRate: `${successRate}%`
            }
        };
        
        const filename = `vetsorcery_simple_test_${Date.now()}.json`;
        fs.writeFileSync(filename, JSON.stringify(reportData, null, 2));
        
        console.log(`\n💾 Report saved: ${filename}`);
        return filename;
    }

    async run() {
        console.log(`🚀 Starting Simple VetSorcery Testing Suite`);
        console.log(`🎯 Target: ${BASE_URL}`);
        console.log(`⏰ Started: ${new Date().toLocaleString()}\n`);
        
        // Test server health first
        const healthResult = await this.testServerHealth();
        if (!healthResult.healthy) {
            console.log(`\n🚨 Server is not healthy, stopping tests.`);
            return this.generateReport();
        }
        
        // Analyze VetSorcery specifics
        await this.analyzeVetSorcerySpecifics();
        
        console.log(`\n🧪 Running endpoint tests...\n`);
        
        // Test all endpoints
        for (const endpoint of TEST_ENDPOINTS) {
            await this.testEndpoint(endpoint);
            await new Promise(resolve => setTimeout(resolve, 500)); // Small delay
        }
        
        return this.generateReport();
    }
}

// Run if called directly
if (require.main === module) {
    const tester = new SimpleVetSorceryTester();
    tester.run()
        .then(reportFile => {
            console.log(`\n🎉 Testing completed!`);
            console.log(`📄 Report: ${reportFile}`);
            process.exit(0);
        })
        .catch(error => {
            console.error(`\n💥 Testing failed: ${error.message}`);
            process.exit(1);
        });
}

module.exports = SimpleVetSorceryTester;