#!/bin/bash
# Test Flakiness Detector
# Identifies unreliable tests by running them multiple times

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${PURPLE}🎲 Test Flakiness Detector${NC}"
echo "=========================="
echo ""

# Create flakiness detection directories
mkdir -p flakiness/{results,reports,data}

echo -e "${BLUE}Creating flakiness detection engine...${NC}"

# Flakiness detection engine
cat > flakiness/flakiness-detector.js << 'EOF'
#!/usr/bin/env node

const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

class FlakinessDetector {
  constructor() {
    this.config = {
      runs: 10, // Number of times to run each test
      parallel: 3, // Number of parallel test runs
      threshold: 0.1, // 10% failure rate = flaky
      timeout: 30000, // 30 seconds per test
      retryFailed: true,
      patterns: {
        testFiles: ['**/*.test.*', '**/*.spec.*'],
        ignore: ['node_modules', 'coverage', 'dist']
      }
    };
    
    this.results = {
      timestamp: new Date().toISOString(),
      totalTests: 0,
      flakyTests: [],
      reliableTests: [],
      alwaysFailingTests: [],
      statistics: {}
    };
  }

  async detectFlakiness(options = {}) {
    console.log('🔍 Starting flakiness detection...');
    
    // Merge options
    this.config = { ...this.config, ...options };
    
    try {
      // Step 1: Discover all tests
      const tests = await this.discoverTests();
      console.log(`Found ${tests.length} test files`);
      
      // Step 2: Run each test multiple times
      const testResults = await this.runTestsMultipleTimes(tests);
      
      // Step 3: Analyze results
      this.analyzeResults(testResults);
      
      // Step 4: Generate report
      await this.generateReport();
      
      console.log('✅ Flakiness detection complete');
      
    } catch (error) {
      console.error('❌ Flakiness detection failed:', error.message);
      process.exit(1);
    }
  }

  async discoverTests() {
    console.log('🔎 Discovering test files...');
    
    const testFiles = [];
    const { execSync } = require('child_process');
    
    this.config.patterns.testFiles.forEach(pattern => {
      try {
        const files = execSync(
          `find . -name "${pattern}" -type f | grep -v node_modules | grep -v coverage`,
          { encoding: 'utf8' }
        ).trim().split('\n').filter(Boolean);
        
        testFiles.push(...files);
      } catch (error) {
        // Pattern didn't match any files
      }
    });
    
    // Get individual test names from each file
    const tests = [];
    for (const file of testFiles) {
      const fileTests = await this.extractTestsFromFile(file);
      tests.push(...fileTests);
    }
    
    return tests;
  }

  async extractTestsFromFile(filePath) {
    const content = fs.readFileSync(filePath, 'utf8');
    const tests = [];
    
    // Extract test names using regex
    const patterns = [
      /(?:it|test)\s*\(\s*['"\`]([^'"\`]+)['"\`]/g,
      /(?:it|test)\.(?:only|skip)?\s*\(\s*['"\`]([^'"\`]+)['"\`]/g
    ];
    
    patterns.forEach(pattern => {
      let match;
      while ((match = pattern.exec(content)) !== null) {
        tests.push({
          file: filePath,
          name: match[1],
          fullName: `${filePath} - ${match[1]}`
        });
      }
    });
    
    // If no individual tests found, use the whole file
    if (tests.length === 0) {
      tests.push({
        file: filePath,
        name: 'All tests',
        fullName: filePath
      });
    }
    
    return tests;
  }

  async runTestsMultipleTimes(tests) {
    console.log(`🏃 Running ${tests.length} tests ${this.config.runs} times each...`);
    
    const results = new Map();
    
    // Initialize results map
    tests.forEach(test => {
      results.set(test.fullName, {
        test,
        runs: [],
        passes: 0,
        failures: 0,
        durations: [],
        errors: []
      });
    });
    
    // Run tests in batches
    const batches = this.createBatches(tests, this.config.parallel);
    let completedTests = 0;
    
    for (const batch of batches) {
      await Promise.all(batch.map(async (test) => {
        const result = results.get(test.fullName);
        
        for (let run = 0; run < this.config.runs; run++) {
          const runResult = await this.runSingleTest(test, run);
          result.runs.push(runResult);
          
          if (runResult.passed) {
            result.passes++;
          } else {
            result.failures++;
            result.errors.push(runResult.error);
          }
          
          if (runResult.duration) {
            result.durations.push(runResult.duration);
          }
          
          // Progress update
          completedTests++;
          const progress = Math.round((completedTests / (tests.length * this.config.runs)) * 100);
          process.stdout.write(`\rProgress: ${progress}% (${completedTests}/${tests.length * this.config.runs})`);
        }
      }));
    }
    
    console.log('\n');
    return results;
  }

  async runSingleTest(test, runNumber) {
    const startTime = Date.now();
    
    return new Promise((resolve) => {
      const timeout = setTimeout(() => {
        resolve({
          passed: false,
          duration: this.config.timeout,
          error: 'Test timeout',
          runNumber
        });
      }, this.config.timeout);
      
      // Run test with specific test name filter
      const command = `npm test -- "${test.file}" -t "${test.name}" --no-coverage --silent`;
      
      exec(command, (error, stdout, stderr) => {
        clearTimeout(timeout);
        const duration = Date.now() - startTime;
        
        resolve({
          passed: !error,
          duration,
          error: error ? (stderr || stdout || error.message) : null,
          runNumber,
          output: stdout
        });
      });
    });
  }

  createBatches(items, batchSize) {
    const batches = [];
    for (let i = 0; i < items.length; i += batchSize) {
      batches.push(items.slice(i, i + batchSize));
    }
    return batches;
  }

  analyzeResults(testResults) {
    console.log('📊 Analyzing test results...');
    
    this.results.totalTests = testResults.size;
    
    testResults.forEach((result, testName) => {
      const failureRate = result.failures / this.config.runs;
      const avgDuration = result.durations.length > 0 ?
        result.durations.reduce((a, b) => a + b, 0) / result.durations.length : 0;
      
      const analysis = {
        testName,
        file: result.test.file,
        runs: this.config.runs,
        passes: result.passes,
        failures: result.failures,
        failureRate,
        avgDuration: Math.round(avgDuration),
        maxDuration: Math.max(...result.durations),
        minDuration: Math.min(...result.durations),
        durationVariance: this.calculateVariance(result.durations),
        errors: this.summarizeErrors(result.errors),
        status: this.categorizeTest(failureRate)
      };
      
      // Categorize test
      switch (analysis.status) {
        case 'flaky':
          this.results.flakyTests.push(analysis);
          break;
        case 'failing':
          this.results.alwaysFailingTests.push(analysis);
          break;
        case 'reliable':
          this.results.reliableTests.push(analysis);
          break;
      }
    });
    
    // Calculate statistics
    this.results.statistics = {
      totalTests: this.results.totalTests,
      reliableTests: this.results.reliableTests.length,
      flakyTests: this.results.flakyTests.length,
      failingTests: this.results.alwaysFailingTests.length,
      flakinessRate: (this.results.flakyTests.length / this.results.totalTests * 100).toFixed(2),
      avgTestDuration: this.calculateAvgDuration()
    };
  }

  categorizeTest(failureRate) {
    if (failureRate === 0) return 'reliable';
    if (failureRate === 1) return 'failing';
    if (failureRate > this.config.threshold) return 'flaky';
    return 'reliable'; // Low failure rate, probably not flaky
  }

  calculateVariance(numbers) {
    if (numbers.length === 0) return 0;
    const mean = numbers.reduce((a, b) => a + b, 0) / numbers.length;
    const variance = numbers.reduce((sum, num) => sum + Math.pow(num - mean, 2), 0) / numbers.length;
    return Math.sqrt(variance);
  }

  summarizeErrors(errors) {
    const errorCounts = {};
    
    errors.forEach(error => {
      // Extract key error patterns
      const patterns = [
        /timeout/i,
        /network/i,
        /connection/i,
        /async/i,
        /promise/i,
        /undefined/i,
        /null/i
      ];
      
      let matched = false;
      for (const pattern of patterns) {
        if (pattern.test(error)) {
          const key = pattern.source;
          errorCounts[key] = (errorCounts[key] || 0) + 1;
          matched = true;
          break;
        }
      }
      
      if (!matched) {
        errorCounts['other'] = (errorCounts['other'] || 0) + 1;
      }
    });
    
    return errorCounts;
  }

  calculateAvgDuration() {
    const allDurations = [];
    [...this.results.reliableTests, ...this.results.flakyTests].forEach(test => {
      allDurations.push(test.avgDuration);
    });
    
    return allDurations.length > 0 ?
      Math.round(allDurations.reduce((a, b) => a + b, 0) / allDurations.length) : 0;
  }

  async generateReport() {
    console.log('📝 Generating flakiness report...');
    
    const report = {
      ...this.results,
      recommendations: this.generateRecommendations()
    };
    
    // Save JSON report
    const jsonPath = `flakiness/reports/flakiness-${Date.now()}.json`;
    fs.writeFileSync(jsonPath, JSON.stringify(report, null, 2));
    
    // Generate HTML report
    const htmlPath = `flakiness/reports/flakiness-report.html`;
    fs.writeFileSync(htmlPath, this.generateHTMLReport(report));
    
    // Generate summary
    this.printSummary(report);
    
    console.log(`\n📄 Reports saved:`);
    console.log(`   JSON: ${jsonPath}`);
    console.log(`   HTML: ${htmlPath}`);
  }

  generateRecommendations() {
    const recommendations = [];
    
    if (this.results.flakyTests.length > 0) {
      recommendations.push({
        type: 'flaky',
        message: `Found ${this.results.flakyTests.length} flaky tests that need attention`,
        tests: this.results.flakyTests.slice(0, 5).map(t => t.testName)
      });
    }
    
    // Analyze common error patterns
    const allErrors = {};
    this.results.flakyTests.forEach(test => {
      Object.entries(test.errors).forEach(([error, count]) => {
        allErrors[error] = (allErrors[error] || 0) + count;
      });
    });
    
    const topErrors = Object.entries(allErrors)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3);
    
    if (topErrors.length > 0) {
      recommendations.push({
        type: 'errors',
        message: 'Common failure patterns detected',
        patterns: topErrors.map(([pattern, count]) => ({
          pattern: pattern.replace(/[/\\]/g, ''),
          count
        }))
      });
    }
    
    // Timing-related recommendations
    const timingFlaky = this.results.flakyTests.filter(t => 
      t.durationVariance > t.avgDuration * 0.5
    );
    
    if (timingFlaky.length > 0) {
      recommendations.push({
        type: 'timing',
        message: `${timingFlaky.length} tests have high timing variance, suggesting race conditions`,
        tests: timingFlaky.slice(0, 3).map(t => t.testName)
      });
    }
    
    return recommendations;
  }

  generateHTMLReport(report) {
    return `
<!DOCTYPE html>
<html>
<head>
    <title>Test Flakiness Report</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }
        .header {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        h1 { color: #333; margin: 0; }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .stat {
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            margin: 5px 0;
        }
        .stat-label { color: #666; }
        .flaky { color: #ff9800; }
        .failing { color: #f44336; }
        .reliable { color: #4caf50; }
        .test-list {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 20px 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        th { background: #f5f5f5; }
        .failure-rate {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.9em;
        }
        .recommendations {
            background: #fff3cd;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #ffc107;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎲 Test Flakiness Report</h1>
        <p>Generated: ${new Date(report.timestamp).toLocaleString()}</p>
    </div>
    
    <div class="summary">
        <div class="stat">
            <div class="stat-label">Total Tests</div>
            <div class="stat-value">${report.statistics.totalTests}</div>
        </div>
        <div class="stat">
            <div class="stat-label">Reliable Tests</div>
            <div class="stat-value reliable">${report.statistics.reliableTests}</div>
        </div>
        <div class="stat">
            <div class="stat-label">Flaky Tests</div>
            <div class="stat-value flaky">${report.statistics.flakyTests}</div>
        </div>
        <div class="stat">
            <div class="stat-label">Always Failing</div>
            <div class="stat-value failing">${report.statistics.failingTests}</div>
        </div>
        <div class="stat">
            <div class="stat-label">Flakiness Rate</div>
            <div class="stat-value">${report.statistics.flakinessRate}%</div>
        </div>
    </div>
    
    ${report.flakyTests.length > 0 ? `
    <div class="test-list">
        <h2>🎲 Flaky Tests</h2>
        <table>
            <tr>
                <th>Test Name</th>
                <th>File</th>
                <th>Failure Rate</th>
                <th>Avg Duration</th>
                <th>Variance</th>
            </tr>
            ${report.flakyTests.map(test => `
            <tr>
                <td>${test.testName}</td>
                <td>${test.file}</td>
                <td><span class="failure-rate flaky">${(test.failureRate * 100).toFixed(0)}%</span></td>
                <td>${test.avgDuration}ms</td>
                <td>${test.durationVariance.toFixed(0)}ms</td>
            </tr>
            `).join('')}
        </table>
    </div>
    ` : ''}
    
    ${report.recommendations.length > 0 ? `
    <div class="recommendations">
        <h2>💡 Recommendations</h2>
        ${report.recommendations.map(rec => `
        <div style="margin: 15px 0;">
            <strong>${rec.message}</strong>
            ${rec.tests ? `<ul>${rec.tests.map(t => `<li>${t}</li>`).join('')}</ul>` : ''}
            ${rec.patterns ? `<ul>${rec.patterns.map(p => `<li>${p.pattern}: ${p.count} occurrences</li>`).join('')}</ul>` : ''}
        </div>
        `).join('')}
    </div>
    ` : ''}
</body>
</html>`;
  }

  printSummary(report) {
    console.log('\n📊 Flakiness Detection Summary');
    console.log('=============================');
    console.log(`Total tests analyzed: ${report.statistics.totalTests}`);
    console.log(`✅ Reliable tests: ${report.statistics.reliableTests}`);
    console.log(`🎲 Flaky tests: ${report.statistics.flakyTests}`);
    console.log(`❌ Always failing: ${report.statistics.failingTests}`);
    console.log(`📈 Flakiness rate: ${report.statistics.flakinessRate}%`);
    
    if (report.flakyTests.length > 0) {
      console.log('\n🎲 Top Flaky Tests:');
      report.flakyTests.slice(0, 5).forEach(test => {
        console.log(`   - ${test.testName} (${(test.failureRate * 100).toFixed(0)}% failure rate)`);
      });
    }
    
    if (report.recommendations.length > 0) {
      console.log('\n💡 Recommendations:');
      report.recommendations.forEach(rec => {
        console.log(`   - ${rec.message}`);
      });
    }
  }
}

// Run if called directly
if (require.main === module) {
  const detector = new FlakinessDetector();
  
  // Parse command line arguments
  const args = process.argv.slice(2);
  const options = {};
  
  for (let i = 0; i < args.length; i += 2) {
    const key = args[i].replace('--', '');
    const value = args[i + 1];
    
    if (key === 'runs') options.runs = parseInt(value);
    if (key === 'threshold') options.threshold = parseFloat(value);
    if (key === 'parallel') options.parallel = parseInt(value);
  }
  
  detector.detectFlakiness(options).catch(console.error);
}

module.exports = FlakinessDetector;
EOF

chmod +x flakiness/flakiness-detector.js

echo -e "${BLUE}Creating flakiness CLI tool...${NC}"

# Flakiness CLI
cat > flakiness/detect-flaky-tests.sh << 'EOF'
#!/bin/bash
# Flaky test detection CLI

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🎲 Flaky Test Detection${NC}"
echo "======================="
echo ""

# Default values
RUNS=10
THRESHOLD=0.1
PARALLEL=3

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--runs)
            RUNS="$2"
            shift 2
            ;;
        -t|--threshold)
            THRESHOLD="$2"
            shift 2
            ;;
        -p|--parallel)
            PARALLEL="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  -r, --runs NUM       Number of times to run each test (default: 10)"
            echo "  -t, --threshold NUM  Failure rate threshold for flaky detection (default: 0.1)"
            echo "  -p, --parallel NUM   Number of parallel test runs (default: 3)"
            echo "  -h, --help          Show this help message"
            exit 0
            ;;
        *)
            shift
            ;;
    esac
done

echo -e "${YELLOW}Configuration:${NC}"
echo "  Runs per test: $RUNS"
echo "  Flakiness threshold: $THRESHOLD"
echo "  Parallel execution: $PARALLEL"
echo ""

# Run flakiness detection
node flakiness/flakiness-detector.js \
    --runs "$RUNS" \
    --threshold "$THRESHOLD" \
    --parallel "$PARALLEL"

# Open HTML report if available
if [ -f "flakiness/reports/flakiness-report.html" ]; then
    echo ""
    echo -e "${GREEN}✅ Report generated${NC}"
    
    if command -v open >/dev/null 2>&1; then
        open flakiness/reports/flakiness-report.html
    elif command -v xdg-open >/dev/null 2>&1; then
        xdg-open flakiness/reports/flakiness-report.html
    else
        echo "View report at: flakiness/reports/flakiness-report.html"
    fi
fi
EOF

chmod +x flakiness/detect-flaky-tests.sh

echo -e "${BLUE}Creating scheduled flakiness checks...${NC}"

# Scheduled flakiness check
cat > flakiness/schedule-checks.sh << 'EOF'
#!/bin/bash
# Schedule regular flakiness checks

CRON_SCHEDULE="0 2 * * *"  # Daily at 2 AM

# Add to crontab
(crontab -l 2>/dev/null || true; echo "$CRON_SCHEDULE cd $(pwd) && ./flakiness/detect-flaky-tests.sh --runs 5 > flakiness/logs/cron.log 2>&1") | crontab -

echo "✅ Scheduled daily flakiness checks at 2 AM"
echo "View crontab: crontab -l"
echo "Remove schedule: crontab -e (then delete the line)"
EOF

chmod +x flakiness/schedule-checks.sh

echo ""
echo -e "${GREEN}✅ Test Flakiness Detector setup complete!${NC}"
echo ""
echo -e "${YELLOW}To detect flaky tests:${NC}"
echo "  ./flakiness/detect-flaky-tests.sh"
echo ""
echo -e "${YELLOW}Options:${NC}"
echo "  --runs 20      # Run each test 20 times"
echo "  --threshold 0.05  # 5% failure = flaky"
echo "  --parallel 5   # Run 5 tests in parallel"
echo ""
echo -e "${BLUE}Schedule regular checks:${NC}"
echo "  ./flakiness/schedule-checks.sh"