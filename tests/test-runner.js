/**
 * VetSorcery Test Runner
 * 
 * Comprehensive test execution and reporting system for all VetSorcery modules
 * Coordinates unit, integration, E2E, performance, and accessibility tests
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Test configuration
const TEST_CONFIG = {
  baseUrl: process.env.VETSORCERY_URL || 'http://localhost:3000',
  testTimeout: 60000,
  retries: 2,
  parallel: true,
  reporter: 'html',
  outputDir: './test-results',
  coverage: {
    threshold: 90,
    includeUntested: true
  }
};

// Test suites
const TEST_SUITES = {
  unit: {
    name: 'Unit Tests',
    command: 'npm run test:unit',
    files: ['tests/unit/**/*.test.{js,ts,tsx}'],
    timeout: 30000
  },
  integration: {
    name: 'Integration Tests', 
    command: 'npx playwright test tests/integration/',
    files: ['tests/integration/**/*.test.js'],
    timeout: 60000
  },
  e2e: {
    name: 'End-to-End Tests',
    command: 'npx playwright test tests/e2e/',
    files: ['tests/e2e/**/*.spec.js'],
    timeout: 120000
  },
  performance: {
    name: 'Performance Tests',
    command: 'npx playwright test tests/performance/',
    files: ['tests/performance/**/*.js'],
    timeout: 180000
  },
  accessibility: {
    name: 'Accessibility Tests',
    command: 'npx playwright test tests/accessibility/',
    files: ['tests/accessibility/**/*.js'],
    timeout: 90000
  }
};

class TestRunner {
  constructor() {
    this.results = {
      summary: {
        totalSuites: 0,
        passedSuites: 0,
        failedSuites: 0,
        totalTests: 0,
        passedTests: 0,
        failedTests: 0,
        skippedTests: 0,
        duration: 0
      },
      suites: {},
      coverage: {},
      errors: []
    };
    
    this.startTime = Date.now();
  }

  async runAllTests() {
    console.log('🚀 Starting VetSorcery comprehensive test suite...\n');
    
    // Create output directory
    this.ensureOutputDir();
    
    // Check if application is running
    await this.checkApplicationHealth();
    
    // Run all test suites
    for (const [suiteKey, suite] of Object.entries(TEST_SUITES)) {
      await this.runTestSuite(suiteKey, suite);
    }
    
    // Generate final report
    this.generateFinalReport();
    
    // Return results
    return this.results;
  }

  async runTestSuite(suiteKey, suite) {
    console.log(`\n📋 Running ${suite.name}...`);
    console.log(`   Command: ${suite.command}`);
    console.log(`   Timeout: ${suite.timeout}ms`);
    
    const suiteStartTime = Date.now();
    this.results.summary.totalSuites++;
    
    try {
      // Execute test suite
      const output = execSync(suite.command, {
        cwd: process.cwd(),
        timeout: suite.timeout,
        encoding: 'utf8',
        stdio: 'pipe'
      });
      
      const duration = Date.now() - suiteStartTime;
      
      // Parse test results from output
      const suiteResults = this.parseTestOutput(output, suite.name);
      suiteResults.duration = duration;
      suiteResults.status = 'passed';
      
      this.results.suites[suiteKey] = suiteResults;
      this.results.summary.passedSuites++;
      
      console.log(`   ✅ ${suite.name} completed successfully`);
      console.log(`   📊 ${suiteResults.passed}/${suiteResults.total} tests passed`);
      console.log(`   ⏱️  Duration: ${duration}ms`);
      
    } catch (error) {
      const duration = Date.now() - suiteStartTime;
      
      this.results.suites[suiteKey] = {
        name: suite.name,
        status: 'failed',
        duration,
        error: error.message,
        output: error.stdout || '',
        stderr: error.stderr || ''
      };
      
      this.results.summary.failedSuites++;
      this.results.errors.push({
        suite: suite.name,
        error: error.message,
        timestamp: new Date().toISOString()
      });
      
      console.log(`   ❌ ${suite.name} failed`);
      console.log(`   🔍 Error: ${error.message}`);
      console.log(`   ⏱️  Duration: ${duration}ms`);
    }
  }

  parseTestOutput(output, suiteName) {
    // Parse different test output formats
    const results = {
      name: suiteName,
      total: 0,
      passed: 0,
      failed: 0,
      skipped: 0,
      tests: []
    };
    
    // Playwright output parsing
    if (output.includes('passed') || output.includes('failed')) {
      const playwrightMatch = output.match(/(\d+) passed.*?(\d+) failed.*?(\d+) skipped/);
      if (playwrightMatch) {
        results.passed = parseInt(playwrightMatch[1]) || 0;
        results.failed = parseInt(playwrightMatch[2]) || 0;
        results.skipped = parseInt(playwrightMatch[3]) || 0;
        results.total = results.passed + results.failed + results.skipped;
      }
    }
    
    // Jest output parsing
    if (output.includes('Tests:')) {
      const jestMatch = output.match(/Tests:\s+(\d+) passed.*?(\d+) total/);
      if (jestMatch) {
        results.passed = parseInt(jestMatch[1]) || 0;
        results.total = parseInt(jestMatch[2]) || 0;
        results.failed = results.total - results.passed;
      }
    }
    
    // Update summary
    this.results.summary.totalTests += results.total;
    this.results.summary.passedTests += results.passed;
    this.results.summary.failedTests += results.failed;
    this.results.summary.skippedTests += results.skipped;
    
    return results;
  }

  async checkApplicationHealth() {
    console.log('🔍 Checking application health...');
    
    try {
      const { execSync } = require('child_process');
      const healthCheck = execSync(`curl -f ${TEST_CONFIG.baseUrl}/health || curl -f ${TEST_CONFIG.baseUrl}/ || echo "App check failed"`, {
        encoding: 'utf8',
        timeout: 10000
      });
      
      if (healthCheck.includes('App check failed')) {
        console.log('⚠️  Application may not be running. Some tests may fail.');
        console.log(`   Make sure the app is running at ${TEST_CONFIG.baseUrl}`);
      } else {
        console.log('✅ Application is responding');
      }
    } catch (error) {
      console.log('⚠️  Could not verify application status');
      console.log(`   Make sure the app is running at ${TEST_CONFIG.baseUrl}`);
    }
  }

  ensureOutputDir() {
    if (!fs.existsSync(TEST_CONFIG.outputDir)) {
      fs.mkdirSync(TEST_CONFIG.outputDir, { recursive: true });
    }
  }

  generateFinalReport() {
    this.results.summary.duration = Date.now() - this.startTime;
    
    // Generate console report
    this.generateConsoleReport();
    
    // Generate HTML report
    this.generateHtmlReport();
    
    // Generate JSON report
    this.generateJsonReport();
    
    // Generate CI/CD report
    this.generateCiReport();
  }

  generateConsoleReport() {
    const { summary } = this.results;
    
    console.log('\n' + '='.repeat(60));
    console.log('🏁 VetSorcery Test Suite Complete');
    console.log('='.repeat(60));
    
    console.log('\n📊 Summary:');
    console.log(`   Total Test Suites: ${summary.totalSuites}`);
    console.log(`   ✅ Passed Suites: ${summary.passedSuites}`);
    console.log(`   ❌ Failed Suites: ${summary.failedSuites}`);
    console.log(`   Total Tests: ${summary.totalTests}`);
    console.log(`   ✅ Passed Tests: ${summary.passedTests}`);
    console.log(`   ❌ Failed Tests: ${summary.failedTests}`);
    console.log(`   ⏭️  Skipped Tests: ${summary.skippedTests}`);
    console.log(`   ⏱️  Total Duration: ${(summary.duration / 1000).toFixed(2)}s`);
    
    // Success rate
    const successRate = summary.totalTests > 0 ? 
      ((summary.passedTests / summary.totalTests) * 100).toFixed(1) : 0;
    console.log(`   📈 Success Rate: ${successRate}%`);
    
    console.log('\n📋 Suite Details:');
    Object.entries(this.results.suites).forEach(([key, suite]) => {
      const status = suite.status === 'passed' ? '✅' : '❌';
      const duration = (suite.duration / 1000).toFixed(2);
      console.log(`   ${status} ${suite.name}: ${suite.passed || 0}/${suite.total || 0} tests (${duration}s)`);
    });
    
    if (this.results.errors.length > 0) {
      console.log('\n🚨 Errors:');
      this.results.errors.forEach(error => {
        console.log(`   ❌ ${error.suite}: ${error.error}`);
      });
    }
    
    console.log('\n📁 Reports generated in:', TEST_CONFIG.outputDir);
    console.log('='.repeat(60));
  }

  generateHtmlReport() {
    const htmlTemplate = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VetSorcery Test Report</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: white; padding: 30px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .metric { background: white; padding: 20px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .metric-value { font-size: 2em; font-weight: bold; margin-bottom: 5px; }
        .metric-label { color: #666; font-size: 0.9em; }
        .suite { background: white; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .suite-header { padding: 20px; border-bottom: 1px solid #eee; }
        .suite-title { margin: 0; display: flex; align-items: center; gap: 10px; }
        .status-passed { color: #10b981; }
        .status-failed { color: #ef4444; }
        .suite-content { padding: 20px; }
        .error { background: #fef2f2; border: 1px solid #fecaca; padding: 15px; border-radius: 6px; margin-top: 10px; }
        .timestamp { color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏥 VetSorcery Test Report</h1>
            <p class="timestamp">Generated: ${new Date().toLocaleString()}</p>
            <p>Comprehensive test results for all VetSorcery modules</p>
        </div>
        
        <div class="summary">
            <div class="metric">
                <div class="metric-value status-${this.results.summary.failedSuites === 0 ? 'passed' : 'failed'}">${this.results.summary.passedSuites}/${this.results.summary.totalSuites}</div>
                <div class="metric-label">Test Suites Passed</div>
            </div>
            <div class="metric">
                <div class="metric-value status-${this.results.summary.failedTests === 0 ? 'passed' : 'failed'}">${this.results.summary.passedTests}/${this.results.summary.totalTests}</div>
                <div class="metric-label">Tests Passed</div>
            </div>
            <div class="metric">
                <div class="metric-value">${((this.results.summary.passedTests / this.results.summary.totalTests) * 100).toFixed(1)}%</div>
                <div class="metric-label">Success Rate</div>
            </div>
            <div class="metric">
                <div class="metric-value">${(this.results.summary.duration / 1000).toFixed(1)}s</div>
                <div class="metric-label">Total Duration</div>
            </div>
        </div>
        
        <h2>Test Suite Details</h2>
        ${Object.entries(this.results.suites).map(([key, suite]) => `
            <div class="suite">
                <div class="suite-header">
                    <h3 class="suite-title">
                        <span class="status-${suite.status}">${suite.status === 'passed' ? '✅' : '❌'}</span>
                        ${suite.name}
                    </h3>
                </div>
                <div class="suite-content">
                    <p><strong>Duration:</strong> ${(suite.duration / 1000).toFixed(2)}s</p>
                    ${suite.total ? `<p><strong>Tests:</strong> ${suite.passed}/${suite.total} passed</p>` : ''}
                    ${suite.error ? `<div class="error"><strong>Error:</strong> ${suite.error}</div>` : ''}
                </div>
            </div>
        `).join('')}
        
        ${this.results.errors.length > 0 ? `
            <h2>Errors</h2>
            ${this.results.errors.map(error => `
                <div class="error">
                    <strong>${error.suite}:</strong> ${error.error}
                    <br><small>${error.timestamp}</small>
                </div>
            `).join('')}
        ` : ''}
    </div>
</body>
</html>`;
    
    fs.writeFileSync(
      path.join(TEST_CONFIG.outputDir, 'test-report.html'),
      htmlTemplate
    );
  }

  generateJsonReport() {
    fs.writeFileSync(
      path.join(TEST_CONFIG.outputDir, 'test-results.json'),
      JSON.stringify(this.results, null, 2)
    );
  }

  generateCiReport() {
    // Generate JUnit XML for CI/CD systems
    const junitXml = this.generateJUnitXml();
    fs.writeFileSync(
      path.join(TEST_CONFIG.outputDir, 'junit-results.xml'),
      junitXml
    );
    
    // Generate badge data
    const badgeData = {
      schemaVersion: 1,
      label: 'tests',
      message: this.results.summary.failedTests === 0 ? 'passing' : 'failing',
      color: this.results.summary.failedTests === 0 ? 'brightgreen' : 'red',
      passCount: this.results.summary.passedTests,
      totalCount: this.results.summary.totalTests
    };
    
    fs.writeFileSync(
      path.join(TEST_CONFIG.outputDir, 'badge.json'),
      JSON.stringify(badgeData, null, 2)
    );
  }

  generateJUnitXml() {
    const testSuites = Object.entries(this.results.suites).map(([key, suite]) => {
      const tests = suite.tests || [];
      const failures = suite.failed || 0;
      const errors = suite.error ? 1 : 0;
      
      return `
        <testsuite 
          name="${suite.name}"
          tests="${suite.total || 0}"
          failures="${failures}"
          errors="${errors}"
          time="${(suite.duration / 1000).toFixed(3)}"
        >
          ${tests.map(test => `
            <testcase name="${test.name}" time="${test.duration || 0}">
              ${test.status === 'failed' ? `<failure message="${test.error || 'Test failed'}">${test.error || ''}</failure>` : ''}
            </testcase>
          `).join('')}
          ${suite.error ? `<error message="${suite.error}">${suite.error}</error>` : ''}
        </testsuite>
      `;
    }).join('');
    
    return `<?xml version="1.0" encoding="UTF-8"?>
<testsuites>
  ${testSuites}
</testsuites>`;
  }

  // Quick test runner for specific suites
  async runQuickTest(suiteNames = []) {
    console.log('🚀 Running quick test suite...\n');
    
    const suitesToRun = suiteNames.length > 0 ? 
      Object.fromEntries(Object.entries(TEST_SUITES).filter(([key]) => suiteNames.includes(key))) :
      { unit: TEST_SUITES.unit, integration: TEST_SUITES.integration };
    
    for (const [suiteKey, suite] of Object.entries(suitesToRun)) {
      await this.runTestSuite(suiteKey, suite);
    }
    
    this.generateFinalReport();
    return this.results;
  }
}

// CLI interface
if (require.main === module) {
  const args = process.argv.slice(2);
  const testRunner = new TestRunner();
  
  if (args.includes('--quick')) {
    testRunner.runQuickTest(['unit', 'integration']).then(results => {
      process.exit(results.summary.failedSuites > 0 ? 1 : 0);
    });
  } else if (args.includes('--suite')) {
    const suiteIndex = args.indexOf('--suite');
    const suiteName = args[suiteIndex + 1];
    if (suiteName && TEST_SUITES[suiteName]) {
      testRunner.runQuickTest([suiteName]).then(results => {
        process.exit(results.summary.failedSuites > 0 ? 1 : 0);
      });
    } else {
      console.log('Available test suites:', Object.keys(TEST_SUITES).join(', '));
      process.exit(1);
    }
  } else {
    testRunner.runAllTests().then(results => {
      process.exit(results.summary.failedSuites > 0 ? 1 : 0);
    });
  }
}

module.exports = { TestRunner, TEST_CONFIG, TEST_SUITES };