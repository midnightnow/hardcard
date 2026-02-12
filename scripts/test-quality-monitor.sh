#!/bin/bash
# Automated Test Quality Monitoring System
# Continuously monitors test quality and alerts on degradation

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${PURPLE}🔍 Test Quality Monitor${NC}"
echo "========================"
echo ""

# Create monitoring directories
mkdir -p monitor/{logs,alerts,reports,hooks}

echo -e "${BLUE}Creating continuous monitoring script...${NC}"

# Main monitoring daemon
cat > monitor/quality-monitor.js << 'EOF'
#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const chokidar = require('chokidar');

class TestQualityMonitor {
  constructor() {
    this.config = {
      watchPaths: [
        '**/*.test.*',
        '**/*.spec.*',
        'src/**/*.js',
        'src/**/*.ts',
        'src/**/*.jsx',
        'src/**/*.tsx'
      ],
      ignorePaths: ['node_modules', 'coverage', 'dist', 'build'],
      thresholds: {
        coverage: {
          statements: 80,
          branches: 75,
          functions: 80,
          lines: 80
        },
        performance: {
          testDuration: 300000, // 5 minutes max
          fileSize: 500, // 500 lines max per test file
        },
        quality: {
          maxComplexity: 10,
          maxFileSize: 300,
          minAssertions: 1
        }
      },
      alertChannels: {
        console: true,
        file: true,
        slack: false,
        email: false
      }
    };
    
    this.stats = {
      startTime: Date.now(),
      testsRun: 0,
      failures: 0,
      degradations: 0,
      improvements: 0,
      alerts: []
    };
    
    this.previousMetrics = this.loadPreviousMetrics();
  }

  async start() {
    console.log('🚀 Starting Test Quality Monitor...');
    
    // Initial scan
    await this.runFullScan();
    
    // Set up file watchers
    this.setupWatchers();
    
    // Set up periodic checks
    this.setupPeriodicChecks();
    
    // Set up signal handlers
    this.setupSignalHandlers();
    
    console.log('✅ Monitor running. Press Ctrl+C to stop.');
  }

  setupWatchers() {
    const watcher = chokidar.watch(this.config.watchPaths, {
      ignored: this.config.ignorePaths,
      persistent: true,
      ignoreInitial: true
    });

    watcher
      .on('add', path => this.handleFileChange('added', path))
      .on('change', path => this.handleFileChange('changed', path))
      .on('unlink', path => this.handleFileChange('removed', path));
  }

  async handleFileChange(event, filePath) {
    console.log(`📝 File ${event}: ${filePath}`);
    
    if (filePath.includes('.test.') || filePath.includes('.spec.')) {
      // Test file changed
      await this.analyzeTestFile(filePath);
    } else {
      // Source file changed - check if tests exist
      await this.checkTestCoverage(filePath);
    }
    
    // Run incremental quality check
    await this.runIncrementalCheck(filePath);
  }

  async analyzeTestFile(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const analysis = {
        path: filePath,
        lines: content.split('\n').length,
        hasDescribe: /describe\s*\(/.test(content),
        hasIt: /it\s*\(/.test(content),
        hasExpect: /expect\s*\(/.test(content),
        hasAsync: /async|await|\.then/.test(content),
        assertions: (content.match(/expect\s*\(/g) || []).length,
        skippedTests: (content.match(/\.skip\s*\(/g) || []).length,
        focusedTests: (content.match(/\.only\s*\(/g) || []).length,
        todos: (content.match(/\.todo\s*\(/g) || []).length
      };
      
      // Check for quality issues
      const issues = [];
      
      if (!analysis.hasExpect) {
        issues.push({ type: 'error', message: 'No assertions found' });
      }
      
      if (analysis.assertions < this.config.thresholds.quality.minAssertions) {
        issues.push({ type: 'warning', message: `Only ${analysis.assertions} assertions found` });
      }
      
      if (analysis.lines > this.config.thresholds.performance.fileSize) {
        issues.push({ type: 'warning', message: `Test file too large: ${analysis.lines} lines` });
      }
      
      if (analysis.skippedTests > 0) {
        issues.push({ type: 'info', message: `${analysis.skippedTests} skipped tests` });
      }
      
      if (analysis.focusedTests > 0) {
        issues.push({ type: 'error', message: `${analysis.focusedTests} focused tests (.only)` });
      }
      
      if (issues.length > 0) {
        this.reportIssues(filePath, issues);
      }
      
      return analysis;
    } catch (error) {
      console.error(`Error analyzing ${filePath}:`, error.message);
    }
  }

  async checkTestCoverage(sourcePath) {
    // Check if corresponding test file exists
    const testPaths = [
      sourcePath.replace(/\.(js|ts|jsx|tsx)$/, '.test.$1'),
      sourcePath.replace(/\.(js|ts|jsx|tsx)$/, '.spec.$1'),
      sourcePath.replace(/src\//, 'test/').replace(/\.(js|ts|jsx|tsx)$/, '.test.$1'),
      sourcePath.replace(/src\//, '__tests__/').replace(/\.(js|ts|jsx|tsx)$/, '.test.$1')
    ];
    
    const hasTest = testPaths.some(path => fs.existsSync(path));
    
    if (!hasTest) {
      this.reportIssues(sourcePath, [{
        type: 'warning',
        message: 'No test file found for this source file'
      }]);
    }
  }

  async runIncrementalCheck(changedFile) {
    console.log('🔄 Running incremental quality check...');
    
    try {
      // Run tests for changed file
      const testCommand = this.getTestCommand(changedFile);
      const startTime = Date.now();
      
      exec(testCommand, (error, stdout, stderr) => {
        const duration = Date.now() - startTime;
        this.stats.testsRun++;
        
        if (error) {
          this.stats.failures++;
          this.reportIssues(changedFile, [{
            type: 'error',
            message: `Tests failed: ${error.message}`
          }]);
        } else {
          console.log(`✅ Tests passed in ${duration}ms`);
          
          if (duration > 5000) {
            this.reportIssues(changedFile, [{
              type: 'warning',
              message: `Slow tests: ${duration}ms`
            }]);
          }
        }
        
        // Update metrics
        this.updateMetrics();
      });
    } catch (error) {
      console.error('Incremental check failed:', error.message);
    }
  }

  async runFullScan() {
    console.log('🔍 Running full quality scan...');
    
    const metrics = {
      timestamp: new Date().toISOString(),
      coverage: await this.getCoverageMetrics(),
      testFiles: await this.getTestFileMetrics(),
      quality: await this.getQualityMetrics(),
      performance: await this.getPerformanceMetrics()
    };
    
    // Compare with previous metrics
    const comparison = this.compareMetrics(metrics, this.previousMetrics);
    
    if (comparison.degraded) {
      this.stats.degradations++;
      this.alert('Quality Degradation Detected', comparison.issues);
    } else if (comparison.improved) {
      this.stats.improvements++;
      console.log('📈 Quality improved!');
    }
    
    // Save current metrics
    this.saveMetrics(metrics);
    this.previousMetrics = metrics;
    
    return metrics;
  }

  async getCoverageMetrics() {
    return new Promise((resolve) => {
      exec('npm test -- --coverage --json --outputFile=coverage/test-results.json', (error, stdout) => {
        if (error) {
          resolve({ error: 'Coverage collection failed' });
          return;
        }
        
        try {
          const coveragePath = 'coverage/coverage-summary.json';
          if (fs.existsSync(coveragePath)) {
            const coverage = JSON.parse(fs.readFileSync(coveragePath, 'utf8'));
            resolve(coverage.total);
          } else {
            resolve({ error: 'No coverage data' });
          }
        } catch (err) {
          resolve({ error: err.message });
        }
      });
    });
  }

  async getTestFileMetrics() {
    const testFiles = this.findTestFiles();
    const metrics = {
      total: testFiles.length,
      byType: {},
      largeFiles: [],
      noAssertions: [],
      skippedTests: []
    };
    
    for (const file of testFiles) {
      const analysis = await this.analyzeTestFile(file);
      if (analysis) {
        const ext = path.extname(file);
        metrics.byType[ext] = (metrics.byType[ext] || 0) + 1;
        
        if (analysis.lines > this.config.thresholds.performance.fileSize) {
          metrics.largeFiles.push({ file, lines: analysis.lines });
        }
        
        if (!analysis.hasExpect) {
          metrics.noAssertions.push(file);
        }
        
        if (analysis.skippedTests > 0) {
          metrics.skippedTests.push({ file, count: analysis.skippedTests });
        }
      }
    }
    
    return metrics;
  }

  async getQualityMetrics() {
    // Run quality checks
    const qualityChecks = [];
    
    // ESLint check
    qualityChecks.push(this.runESLintCheck());
    
    // Test sanity check
    qualityChecks.push(this.runSanityCheck());
    
    // Complexity check
    qualityChecks.push(this.runComplexityCheck());
    
    const results = await Promise.all(qualityChecks);
    
    return {
      eslint: results[0],
      sanity: results[1],
      complexity: results[2],
      score: this.calculateQualityScore(results)
    };
  }

  async getPerformanceMetrics() {
    return new Promise((resolve) => {
      const startTime = Date.now();
      
      exec('npm test', (error) => {
        const duration = Date.now() - startTime;
        
        resolve({
          testDuration: duration,
          passed: !error,
          slow: duration > this.config.thresholds.performance.testDuration
        });
      });
    });
  }

  compareMetrics(current, previous) {
    if (!previous) return { degraded: false, improved: false, issues: [] };
    
    const issues = [];
    let degraded = false;
    let improved = false;
    
    // Check coverage degradation
    if (current.coverage && previous.coverage) {
      ['statements', 'branches', 'functions', 'lines'].forEach(type => {
        const curr = current.coverage[type]?.pct || 0;
        const prev = previous.coverage[type]?.pct || 0;
        
        if (curr < prev - 5) {
          degraded = true;
          issues.push(`${type} coverage dropped from ${prev}% to ${curr}%`);
        } else if (curr > prev + 5) {
          improved = true;
        }
      });
    }
    
    // Check test file changes
    if (current.testFiles && previous.testFiles) {
      if (current.testFiles.noAssertions.length > previous.testFiles.noAssertions.length) {
        degraded = true;
        issues.push(`${current.testFiles.noAssertions.length} test files without assertions`);
      }
    }
    
    return { degraded, improved, issues };
  }

  reportIssues(context, issues) {
    const timestamp = new Date().toISOString();
    
    issues.forEach(issue => {
      const alert = {
        timestamp,
        context,
        type: issue.type,
        message: issue.message
      };
      
      this.stats.alerts.push(alert);
      
      // Console output
      if (this.config.alertChannels.console) {
        const icon = issue.type === 'error' ? '❌' : issue.type === 'warning' ? '⚠️' : 'ℹ️';
        console.log(`${icon} [${context}] ${issue.message}`);
      }
      
      // File logging
      if (this.config.alertChannels.file) {
        const logEntry = `${timestamp} [${issue.type.toUpperCase()}] ${context}: ${issue.message}\n`;
        fs.appendFileSync('monitor/logs/quality.log', logEntry);
      }
    });
  }

  alert(title, issues) {
    console.log(`\n🚨 ${title}`);
    issues.forEach(issue => console.log(`   - ${issue}`));
    
    // Save alert
    const alert = {
      timestamp: new Date().toISOString(),
      title,
      issues,
      stats: this.stats
    };
    
    fs.writeFileSync(
      `monitor/alerts/alert-${Date.now()}.json`,
      JSON.stringify(alert, null, 2)
    );
  }

  // Helper methods
  findTestFiles() {
    const patterns = ['**/*.test.*', '**/*.spec.*'];
    const files = [];
    
    patterns.forEach(pattern => {
      const found = this.glob(pattern);
      files.push(...found);
    });
    
    return [...new Set(files)];
  }

  glob(pattern) {
    // Simple glob implementation
    const glob = require('glob');
    return glob.sync(pattern, { 
      ignore: this.config.ignorePaths.map(p => `**/${p}/**`)
    });
  }

  getTestCommand(file) {
    if (file.includes('.test.') || file.includes('.spec.')) {
      return `npm test -- ${file}`;
    }
    return 'npm test';
  }

  runESLintCheck() {
    return new Promise((resolve) => {
      exec('npx eslint **/*.test.* --format json', (error, stdout) => {
        try {
          const results = JSON.parse(stdout);
          const issues = results.reduce((sum, file) => sum + file.errorCount + file.warningCount, 0);
          resolve({ issues, files: results.length });
        } catch (err) {
          resolve({ error: 'ESLint check failed' });
        }
      });
    });
  }

  runSanityCheck() {
    return new Promise((resolve) => {
      if (fs.existsSync('scripts/test-sanity-checker.sh')) {
        exec('./scripts/test-sanity-checker.sh', (error, stdout) => {
          const matches = stdout.match(/Total red flags: (\d+)/);
          const redFlags = matches ? parseInt(matches[1]) : 0;
          resolve({ redFlags });
        });
      } else {
        resolve({ error: 'Sanity checker not found' });
      }
    });
  }

  runComplexityCheck() {
    // Placeholder for complexity analysis
    return Promise.resolve({ averageComplexity: 5 });
  }

  calculateQualityScore(results) {
    let score = 100;
    
    // Deduct points for issues
    if (results[0].issues) score -= Math.min(results[0].issues * 2, 30);
    if (results[1].redFlags) score -= Math.min(results[1].redFlags * 5, 30);
    if (results[2].averageComplexity > 10) score -= 20;
    
    return Math.max(score, 0);
  }

  loadPreviousMetrics() {
    try {
      const metricsPath = 'monitor/reports/latest-metrics.json';
      if (fs.existsSync(metricsPath)) {
        return JSON.parse(fs.readFileSync(metricsPath, 'utf8'));
      }
    } catch (error) {
      console.error('Error loading previous metrics:', error.message);
    }
    return null;
  }

  saveMetrics(metrics) {
    fs.writeFileSync(
      'monitor/reports/latest-metrics.json',
      JSON.stringify(metrics, null, 2)
    );
    
    // Also save timestamped version
    fs.writeFileSync(
      `monitor/reports/metrics-${Date.now()}.json`,
      JSON.stringify(metrics, null, 2)
    );
  }

  updateMetrics() {
    // Update dashboard if it exists
    if (fs.existsSync('dashboard/collect-metrics.js')) {
      exec('node dashboard/collect-metrics.js', (error) => {
        if (!error) {
          console.log('📊 Dashboard metrics updated');
        }
      });
    }
  }

  setupPeriodicChecks() {
    // Run full scan every hour
    setInterval(() => {
      this.runFullScan();
    }, 60 * 60 * 1000);
    
    // Update dashboard every 15 minutes
    setInterval(() => {
      this.updateMetrics();
    }, 15 * 60 * 1000);
    
    // Generate daily report
    setInterval(() => {
      this.generateDailyReport();
    }, 24 * 60 * 60 * 1000);
  }

  generateDailyReport() {
    const report = {
      date: new Date().toISOString().split('T')[0],
      stats: this.stats,
      metrics: this.previousMetrics,
      topIssues: this.getTopIssues(),
      recommendations: this.generateRecommendations()
    };
    
    fs.writeFileSync(
      `monitor/reports/daily-${report.date}.json`,
      JSON.stringify(report, null, 2)
    );
    
    console.log(`📋 Daily report generated: daily-${report.date}.json`);
  }

  getTopIssues() {
    const issueCounts = {};
    
    this.stats.alerts.forEach(alert => {
      const key = `${alert.type}:${alert.message}`;
      issueCounts[key] = (issueCounts[key] || 0) + 1;
    });
    
    return Object.entries(issueCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .map(([issue, count]) => ({ issue, count }));
  }

  generateRecommendations() {
    const recommendations = [];
    
    if (this.stats.failures > this.stats.testsRun * 0.1) {
      recommendations.push('High test failure rate - review test stability');
    }
    
    if (this.stats.degradations > this.stats.improvements) {
      recommendations.push('Quality trending downward - implement stricter checks');
    }
    
    const topIssues = this.getTopIssues();
    if (topIssues.length > 0 && topIssues[0].count > 10) {
      recommendations.push(`Address recurring issue: ${topIssues[0].issue}`);
    }
    
    return recommendations;
  }

  setupSignalHandlers() {
    process.on('SIGINT', () => {
      console.log('\n📊 Generating final report...');
      this.generateDailyReport();
      console.log('👋 Monitor stopped');
      process.exit(0);
    });
  }
}

// Run if called directly
if (require.main === module) {
  const monitor = new TestQualityMonitor();
  monitor.start().catch(console.error);
}

module.exports = TestQualityMonitor;
EOF

chmod +x monitor/quality-monitor.js

echo -e "${BLUE}Creating monitor configuration...${NC}"

# Monitor configuration
cat > monitor/config.json << 'EOF'
{
  "monitor": {
    "enabled": true,
    "mode": "continuous",
    "interval": 300000,
    "paths": {
      "watch": ["src", "test", "tests", "__tests__"],
      "ignore": ["node_modules", "coverage", "dist", "build", ".git"]
    }
  },
  "thresholds": {
    "coverage": {
      "statements": 80,
      "branches": 75,
      "functions": 80,
      "lines": 80
    },
    "performance": {
      "maxTestDuration": 300000,
      "maxFileSize": 500,
      "maxTestFiles": 1000
    },
    "quality": {
      "maxComplexity": 10,
      "minAssertions": 1,
      "maxSkippedTests": 5
    }
  },
  "alerts": {
    "channels": ["console", "file", "dashboard"],
    "rules": [
      {
        "name": "Coverage Drop",
        "condition": "coverage.delta < -5",
        "severity": "high"
      },
      {
        "name": "Slow Tests",
        "condition": "performance.duration > 60000",
        "severity": "medium"
      },
      {
        "name": "No Assertions",
        "condition": "quality.assertions === 0",
        "severity": "high"
      }
    ]
  },
  "reports": {
    "daily": true,
    "weekly": true,
    "onDemand": true
  }
}
EOF

echo -e "${BLUE}Creating Git hooks for quality checks...${NC}"

# Pre-commit hook
cat > monitor/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook for test quality

echo "🔍 Running pre-commit test quality checks..."

# Check for focused tests (.only)
if grep -r "\.only(" --include="*.test.*" --include="*.spec.*" .; then
    echo "❌ Found focused tests (.only). Please remove before committing."
    exit 1
fi

# Check for console.log in tests
if grep -r "console\.log" --include="*.test.*" --include="*.spec.*" . | grep -v "// eslint-disable"; then
    echo "⚠️  Found console.log in tests. Consider removing."
fi

# Run quick sanity check
if [ -f "scripts/test-sanity-checker.sh" ]; then
    ./scripts/test-sanity-checker.sh --quick
fi

echo "✅ Pre-commit checks passed"
EOF

chmod +x monitor/hooks/pre-commit

# Pre-push hook
cat > monitor/hooks/pre-push << 'EOF'
#!/bin/bash
# Pre-push hook for comprehensive quality check

echo "🚀 Running pre-push test quality verification..."

# Run tests
npm test || {
    echo "❌ Tests failed. Push aborted."
    exit 1
}

# Check coverage
npm test -- --coverage --silent
if [ -f "coverage/coverage-summary.json" ]; then
    node -e "
    const coverage = require('./coverage/coverage-summary.json');
    const statements = coverage.total.statements.pct;
    if (statements < 80) {
        console.error('❌ Coverage too low:', statements + '%');
        process.exit(1);
    }
    console.log('✅ Coverage:', statements + '%');
    "
fi

echo "✅ Pre-push verification complete"
EOF

chmod +x monitor/hooks/pre-push

echo -e "${BLUE}Creating monitor CLI...${NC}"

# Monitor CLI script
cat > monitor/monitor-cli.sh << 'EOF'
#!/bin/bash
# Test Quality Monitor CLI

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
NC='\033[0m'

case "$1" in
    start)
        echo -e "${GREEN}Starting test quality monitor...${NC}"
        nohup node monitor/quality-monitor.js > monitor/logs/monitor.log 2>&1 &
        echo $! > monitor/monitor.pid
        echo "Monitor started with PID: $(cat monitor/monitor.pid)"
        ;;
        
    stop)
        if [ -f monitor/monitor.pid ]; then
            PID=$(cat monitor/monitor.pid)
            kill $PID 2>/dev/null || true
            rm monitor/monitor.pid
            echo -e "${YELLOW}Monitor stopped${NC}"
        else
            echo "Monitor not running"
        fi
        ;;
        
    status)
        if [ -f monitor/monitor.pid ] && kill -0 $(cat monitor/monitor.pid) 2>/dev/null; then
            echo -e "${GREEN}Monitor is running${NC}"
            echo "PID: $(cat monitor/monitor.pid)"
            echo ""
            echo "Recent alerts:"
            tail -5 monitor/logs/quality.log 2>/dev/null || echo "No alerts"
        else
            echo -e "${RED}Monitor is not running${NC}"
        fi
        ;;
        
    report)
        echo -e "${BLUE}Generating quality report...${NC}"
        node -e "
        const fs = require('fs');
        const latestMetrics = JSON.parse(fs.readFileSync('monitor/reports/latest-metrics.json', 'utf8'));
        console.log('\\n📊 Test Quality Report');
        console.log('===================');
        console.log('Coverage:', latestMetrics.coverage?.statements?.pct || 'N/A', '%');
        console.log('Test Files:', latestMetrics.testFiles?.total || 0);
        console.log('Quality Score:', latestMetrics.quality?.score || 0);
        console.log('\\nTop Issues:');
        const alerts = fs.readdirSync('monitor/alerts').slice(-5);
        alerts.forEach(file => {
            const alert = JSON.parse(fs.readFileSync('monitor/alerts/' + file));
            console.log('-', alert.title);
        });
        "
        ;;
        
    install-hooks)
        echo -e "${BLUE}Installing Git hooks...${NC}"
        cp monitor/hooks/pre-commit .git/hooks/
        cp monitor/hooks/pre-push .git/hooks/
        echo -e "${GREEN}✅ Hooks installed${NC}"
        ;;
        
    dashboard)
        echo -e "${PURPLE}Opening quality dashboard...${NC}"
        ./dashboard/run-dashboard.sh
        ;;
        
    *)
        echo "Usage: $0 {start|stop|status|report|install-hooks|dashboard}"
        exit 1
        ;;
esac
EOF

chmod +x monitor/monitor-cli.sh

echo -e "${BLUE}Creating package.json for monitor dependencies...${NC}"

# Package.json for monitor
cat > monitor/package.json << 'EOF'
{
  "name": "test-quality-monitor",
  "version": "1.0.0",
  "description": "Automated test quality monitoring",
  "main": "quality-monitor.js",
  "scripts": {
    "start": "./monitor-cli.sh start",
    "stop": "./monitor-cli.sh stop",
    "status": "./monitor-cli.sh status",
    "report": "./monitor-cli.sh report"
  },
  "dependencies": {
    "chokidar": "^3.5.3",
    "glob": "^8.0.3"
  }
}
EOF

echo ""
echo -e "${GREEN}✅ Test Quality Monitor setup complete!${NC}"
echo ""
echo -e "${YELLOW}Commands:${NC}"
echo "  ./monitor/monitor-cli.sh start       # Start monitoring"
echo "  ./monitor/monitor-cli.sh stop        # Stop monitoring"
echo "  ./monitor/monitor-cli.sh status      # Check status"
echo "  ./monitor/monitor-cli.sh report      # Generate report"
echo "  ./monitor/monitor-cli.sh install-hooks # Install Git hooks"
echo ""
echo -e "${BLUE}Features:${NC}"
echo "- Real-time file watching"
echo "- Automatic quality checks"
echo "- Coverage monitoring"
echo "- Performance tracking"
echo "- Git hook integration"
echo "- Alert system"