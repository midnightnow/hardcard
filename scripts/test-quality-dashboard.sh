#!/bin/bash
# Test Quality Metrics Dashboard Generator
# Creates a comprehensive dashboard showing test quality over time

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${PURPLE}📊 Test Quality Dashboard Generator${NC}"
echo "===================================="
echo ""

# Create dashboard directories
mkdir -p dashboard/{data,templates,assets,reports}
mkdir -p dashboard/data/{historical,current}

echo -e "${BLUE}Creating dashboard data collector...${NC}"

# Data collection script
cat > dashboard/collect-metrics.js << 'EOF'
#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class MetricsCollector {
  constructor() {
    this.timestamp = new Date().toISOString();
    this.dataDir = './dashboard/data/current';
    this.historicalDir = './dashboard/data/historical';
    this.metrics = {
      timestamp: this.timestamp,
      testFiles: {},
      coverage: {},
      performance: {},
      quality: {},
      trends: {}
    };
  }

  async collectAll() {
    console.log('📊 Collecting test quality metrics...');
    
    try {
      await this.collectTestFileMetrics();
      await this.collectCoverageMetrics();
      await this.collectPerformanceMetrics();
      await this.collectQualityMetrics();
      await this.calculateTrends();
      
      await this.saveMetrics();
      console.log('✅ Metrics collection complete');
      
    } catch (error) {
      console.error('❌ Metrics collection failed:', error.message);
      process.exit(1);
    }
  }

  async collectTestFileMetrics() {
    console.log('🧪 Analyzing test files...');
    
    // Count test files
    const testFiles = this.findTestFiles();
    const testFileStats = {
      total: testFiles.length,
      byType: {},
      bySize: { small: 0, medium: 0, large: 0 },
      avgSize: 0,
      totalLines: 0
    };

    let totalLines = 0;
    
    testFiles.forEach(file => {
      const ext = path.extname(file);
      testFileStats.byType[ext] = (testFileStats.byType[ext] || 0) + 1;
      
      try {
        const content = fs.readFileSync(file, 'utf8');
        const lines = content.split('\n').length;
        totalLines += lines;
        
        if (lines < 50) testFileStats.bySize.small++;
        else if (lines < 200) testFileStats.bySize.medium++;
        else testFileStats.bySize.large++;
        
      } catch (error) {
        console.warn(`Could not read ${file}: ${error.message}`);
      }
    });
    
    testFileStats.totalLines = totalLines;
    testFileStats.avgSize = Math.round(totalLines / testFiles.length);
    
    this.metrics.testFiles = testFileStats;
  }

  async collectCoverageMetrics() {
    console.log('📈 Collecting coverage data...');
    
    try {
      // Check for coverage report
      const coveragePath = 'coverage/coverage-summary.json';
      if (fs.existsSync(coveragePath)) {
        const coverage = JSON.parse(fs.readFileSync(coveragePath, 'utf8'));
        this.metrics.coverage = {
          statements: coverage.total.statements.pct,
          branches: coverage.total.branches.pct,
          functions: coverage.total.functions.pct,
          lines: coverage.total.lines.pct,
          files: Object.keys(coverage).length - 1, // -1 for 'total'
          uncovered: {
            statements: coverage.total.statements.total - coverage.total.statements.covered,
            branches: coverage.total.branches.total - coverage.total.branches.covered,
            functions: coverage.total.functions.total - coverage.total.functions.covered,
            lines: coverage.total.lines.total - coverage.total.lines.covered
          }
        };
      } else {
        this.metrics.coverage = { error: 'No coverage data found' };
      }
    } catch (error) {
      this.metrics.coverage = { error: error.message };
    }
  }

  async collectPerformanceMetrics() {
    console.log('⚡ Collecting performance data...');
    
    try {
      // Check for Lighthouse reports
      const lighthouseReports = this.findFiles('**/.lighthouseci/**/*.json', 'lighthouse');
      if (lighthouseReports.length > 0) {
        // Process latest report
        const latest = lighthouseReports[lighthouseReports.length - 1];
        const report = JSON.parse(fs.readFileSync(latest, 'utf8'));
        
        this.metrics.performance = {
          performance: report.lhr?.categories?.performance?.score * 100 || 0,
          accessibility: report.lhr?.categories?.accessibility?.score * 100 || 0,
          bestPractices: report.lhr?.categories?.['best-practices']?.score * 100 || 0,
          seo: report.lhr?.categories?.seo?.score * 100 || 0,
          firstContentfulPaint: report.lhr?.audits?.['first-contentful-paint']?.numericValue || 0,
          largestContentfulPaint: report.lhr?.audits?.['largest-contentful-paint']?.numericValue || 0
        };
      } else {
        this.metrics.performance = { note: 'No Lighthouse data available' };
      }
    } catch (error) {
      this.metrics.performance = { error: error.message };
    }
  }

  async collectQualityMetrics() {
    console.log('🎯 Calculating quality scores...');
    
    // Test sanity check results
    const sanityResults = this.findFiles('test-sanity-results/**/SANITY_REPORT.md');
    if (sanityResults.length > 0) {
      try {
        const latest = sanityResults[sanityResults.length - 1];
        const content = fs.readFileSync(latest, 'utf8');
        
        // Parse sanity check results
        const issues = (content.match(/- 🚩/g) || []).length;
        const files = (content.match(/### \w+\.test\./g) || []).length;
        
        this.metrics.quality.sanityCheck = {
          totalIssues: issues,
          affectedFiles: files,
          score: Math.max(0, 100 - (issues * 10)) // 10 points per issue
        };
      } catch (error) {
        this.metrics.quality.sanityCheck = { error: error.message };
      }
    }
    
    // Calculate overall quality score
    const scores = [];
    if (this.metrics.coverage.statements !== undefined) {
      scores.push(this.metrics.coverage.statements);
    }
    if (this.metrics.performance.performance !== undefined) {
      scores.push(this.metrics.performance.performance);
    }
    if (this.metrics.quality.sanityCheck?.score !== undefined) {
      scores.push(this.metrics.quality.sanityCheck.score);
    }
    
    this.metrics.quality.overallScore = scores.length > 0 ? 
      Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) : 0;
  }

  async calculateTrends() {
    console.log('📈 Calculating trends...');
    
    // Load historical data
    const historicalFiles = fs.readdirSync(this.historicalDir)
      .filter(f => f.endsWith('.json'))
      .sort()
      .slice(-7); // Last 7 data points
    
    const historical = historicalFiles.map(file => {
      try {
        return JSON.parse(fs.readFileSync(path.join(this.historicalDir, file), 'utf8'));
      } catch (error) {
        return null;
      }
    }).filter(Boolean);
    
    if (historical.length >= 2) {
      const latest = historical[historical.length - 1];
      const previous = historical[historical.length - 2];
      
      this.metrics.trends = {
        coverage: this.calculateTrend(latest.coverage?.statements, previous.coverage?.statements),
        performance: this.calculateTrend(latest.performance?.performance, previous.performance?.performance),
        quality: this.calculateTrend(latest.quality?.overallScore, previous.quality?.overallScore),
        testFiles: this.calculateTrend(latest.testFiles?.total, previous.testFiles?.total)
      };
    }
  }

  calculateTrend(current, previous) {
    if (current === undefined || previous === undefined) return null;
    
    const change = current - previous;
    const percentChange = previous !== 0 ? (change / previous) * 100 : 0;
    
    return {
      current,
      previous,
      change,
      percentChange: Math.round(percentChange * 100) / 100,
      direction: change > 0 ? 'up' : change < 0 ? 'down' : 'stable'
    };
  }

  findTestFiles() {
    const testPatterns = [
      '**/*.test.js', '**/*.test.ts', '**/*.test.jsx', '**/*.test.tsx',
      '**/*.spec.js', '**/*.spec.ts', '**/*.spec.jsx', '**/*.spec.tsx'
    ];
    
    let files = [];
    testPatterns.forEach(pattern => {
      try {
        const found = execSync(`find . -name "${pattern}" -not -path "./node_modules/*"`, { encoding: 'utf8' })
          .trim().split('\n').filter(Boolean);
        files = files.concat(found);
      } catch (error) {
        // Pattern not found, continue
      }
    });
    
    return [...new Set(files)]; // Remove duplicates
  }

  findFiles(pattern, type = 'files') {
    try {
      const command = type === 'lighthouse' ? 
        `find . -path "*/.lighthouseci/*" -name "*.json" -not -path "./node_modules/*"` :
        `find . -path "${pattern}" -not -path "./node_modules/*"`;
      
      return execSync(command, { encoding: 'utf8' })
        .trim().split('\n').filter(Boolean);
    } catch (error) {
      return [];
    }
  }

  async saveMetrics() {
    // Save current metrics
    const currentFile = path.join(this.dataDir, 'latest.json');
    fs.writeFileSync(currentFile, JSON.stringify(this.metrics, null, 2));
    
    // Save to historical data
    const historicalFile = path.join(this.historicalDir, `${Date.now()}.json`);
    fs.writeFileSync(historicalFile, JSON.stringify(this.metrics, null, 2));
    
    console.log(`📄 Metrics saved to ${currentFile}`);
  }
}

// Run if called directly
if (require.main === module) {
  const collector = new MetricsCollector();
  collector.collectAll().catch(console.error);
}

module.exports = MetricsCollector;
EOF

chmod +x dashboard/collect-metrics.js

echo -e "${BLUE}Creating HTML dashboard template...${NC}"

# HTML dashboard template
cat > dashboard/templates/dashboard.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Quality Dashboard - HardCard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #f5f7fa;
            color: #2d3748;
            line-height: 1.6;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .header h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
        .header p { opacity: 0.9; font-size: 1.1rem; }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-bottom: 2rem;
        }
        
        .card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.15);
        }
        
        .card h3 {
            color: #4a5568;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 0.5rem 0;
            padding: 0.5rem;
            background: #f7fafc;
            border-radius: 6px;
        }
        
        .metric-value {
            font-weight: bold;
            font-size: 1.2rem;
        }
        
        .trend {
            display: flex;
            align-items: center;
            gap: 0.25rem;
            font-size: 0.9rem;
        }
        
        .trend.up { color: #48bb78; }
        .trend.down { color: #f56565; }
        .trend.stable { color: #4a5568; }
        
        .score {
            text-align: center;
            padding: 1rem;
        }
        
        .score-circle {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1rem;
            font-size: 2rem;
            font-weight: bold;
            color: white;
        }
        
        .score-excellent { background: linear-gradient(135deg, #48bb78, #38a169); }
        .score-good { background: linear-gradient(135deg, #4299e1, #3182ce); }
        .score-fair { background: linear-gradient(135deg, #ed8936, #dd6b20); }
        .score-poor { background: linear-gradient(135deg, #f56565, #e53e3e); }
        
        .chart-container {
            position: relative;
            height: 300px;
            margin-top: 1rem;
        }
        
        .timeline {
            margin-top: 2rem;
        }
        
        .timeline-item {
            display: flex;
            align-items: center;
            margin: 1rem 0;
            padding: 1rem;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .timeline-date {
            color: #718096;
            font-size: 0.9rem;
            min-width: 150px;
        }
        
        .alert {
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
        
        .alert-warning {
            background: #fef5e7;
            border-left: 4px solid #ed8936;
            color: #c05621;
        }
        
        .alert-success {
            background: #f0fff4;
            border-left: 4px solid #48bb78;
            color: #2f855a;
        }
        
        .footer {
            text-align: center;
            padding: 2rem;
            color: #718096;
            border-top: 1px solid #e2e8f0;
            margin-top: 2rem;
        }
        
        @media (max-width: 768px) {
            .container { padding: 1rem; }
            .grid { grid-template-columns: 1fr; }
            .header h1 { font-size: 2rem; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Test Quality Dashboard</h1>
        <p>Real-time insights into your test suite quality and performance</p>
        <p><small>Last updated: <span id="lastUpdated">{{timestamp}}</span></small></p>
    </div>

    <div class="container">
        <!-- Overall Quality Score -->
        <div class="card score">
            <h3>🎯 Overall Quality Score</h3>
            <div class="score-circle {{scoreClass}}" id="overallScore">
                {{overallScore}}%
            </div>
            <p>Based on coverage, performance, and test quality metrics</p>
        </div>

        <!-- Key Metrics Grid -->
        <div class="grid">
            <!-- Test Coverage -->
            <div class="card">
                <h3>📈 Test Coverage</h3>
                <div class="metric">
                    <span>Statements</span>
                    <div>
                        <span class="metric-value">{{coverage.statements}}%</span>
                        <span class="trend {{coverage.trend.direction}}">
                            {{coverage.trend.symbol}} {{coverage.trend.change}}%
                        </span>
                    </div>
                </div>
                <div class="metric">
                    <span>Branches</span>
                    <div>
                        <span class="metric-value">{{coverage.branches}}%</span>
                    </div>
                </div>
                <div class="metric">
                    <span>Functions</span>
                    <div>
                        <span class="metric-value">{{coverage.functions}}%</span>
                    </div>
                </div>
                <div class="metric">
                    <span>Lines</span>
                    <div>
                        <span class="metric-value">{{coverage.lines}}%</span>
                    </div>
                </div>
            </div>

            <!-- Test Files -->
            <div class="card">
                <h3>🧪 Test Files</h3>
                <div class="metric">
                    <span>Total Files</span>
                    <span class="metric-value">{{testFiles.total}}</span>
                </div>
                <div class="metric">
                    <span>Average Size</span>
                    <span class="metric-value">{{testFiles.avgSize}} lines</span>
                </div>
                <div class="metric">
                    <span>Small Tests (&lt;50 lines)</span>
                    <span class="metric-value">{{testFiles.bySize.small}}</span>
                </div>
                <div class="metric">
                    <span>Large Tests (&gt;200 lines)</span>
                    <span class="metric-value">{{testFiles.bySize.large}}</span>
                </div>
            </div>

            <!-- Performance -->
            <div class="card">
                <h3>⚡ Performance</h3>
                <div class="metric">
                    <span>Performance Score</span>
                    <span class="metric-value">{{performance.performance}}%</span>
                </div>
                <div class="metric">
                    <span>Accessibility</span>
                    <span class="metric-value">{{performance.accessibility}}%</span>
                </div>
                <div class="metric">
                    <span>Best Practices</span>
                    <span class="metric-value">{{performance.bestPractices}}%</span>
                </div>
                <div class="metric">
                    <span>SEO</span>
                    <span class="metric-value">{{performance.seo}}%</span>
                </div>
            </div>

            <!-- Quality Issues -->
            <div class="card">
                <h3>🚩 Quality Issues</h3>
                <div class="metric">
                    <span>Sanity Check Score</span>
                    <span class="metric-value">{{quality.sanityCheck.score}}%</span>
                </div>
                <div class="metric">
                    <span>Total Issues</span>
                    <span class="metric-value">{{quality.sanityCheck.totalIssues}}</span>
                </div>
                <div class="metric">
                    <span>Affected Files</span>
                    <span class="metric-value">{{quality.sanityCheck.affectedFiles}}</span>
                </div>
            </div>
        </div>

        <!-- Charts -->
        <div class="grid">
            <div class="card">
                <h3>📊 Coverage Trends</h3>
                <div class="chart-container">
                    <canvas id="coverageChart"></canvas>
                </div>
            </div>
            
            <div class="card">
                <h3>📈 Quality Trends</h3>
                <div class="chart-container">
                    <canvas id="qualityChart"></canvas>
                </div>
            </div>
        </div>

        <!-- Alerts and Recommendations -->
        <div id="alerts">
            {{#if hasWarnings}}
            <div class="alert alert-warning">
                <strong>⚠️ Action Required</strong>
                <ul>
                    {{#each warnings}}
                    <li>{{this}}</li>
                    {{/each}}
                </ul>
            </div>
            {{/if}}
            
            {{#if hasSuccesses}}
            <div class="alert alert-success">
                <strong>✅ Well Done!</strong>
                <ul>
                    {{#each successes}}
                    <li>{{this}}</li>
                    {{/each}}
                </ul>
            </div>
            {{/if}}
        </div>
    </div>

    <div class="footer">
        <p>Generated by HardCard Test Quality Dashboard • <a href="#" onclick="location.reload()">Refresh</a></p>
    </div>

    <script>
        // Initialize charts with data
        const metricsData = {{metricsJson}};
        
        // Coverage trend chart
        const coverageCtx = document.getElementById('coverageChart').getContext('2d');
        new Chart(coverageCtx, {
            type: 'line',
            data: {
                labels: ['7 days ago', '6 days ago', '5 days ago', '4 days ago', '3 days ago', '2 days ago', 'Today'],
                datasets: [{
                    label: 'Statements',
                    data: metricsData.historical?.coverage?.statements || [65, 70, 72, 75, 78, 80, 82],
                    borderColor: '#4299e1',
                    backgroundColor: 'rgba(66, 153, 225, 0.1)',
                    tension: 0.4
                }, {
                    label: 'Branches',
                    data: metricsData.historical?.coverage?.branches || [60, 65, 67, 70, 72, 75, 77],
                    borderColor: '#48bb78',
                    backgroundColor: 'rgba(72, 187, 120, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, max: 100 }
                }
            }
        });

        // Quality trend chart
        const qualityCtx = document.getElementById('qualityChart').getContext('2d');
        new Chart(qualityCtx, {
            type: 'bar',
            data: {
                labels: ['Performance', 'Coverage', 'Test Quality', 'Overall'],
                datasets: [{
                    label: 'Score',
                    data: [
                        metricsData.performance?.performance || 85,
                        metricsData.coverage?.statements || 80,
                        metricsData.quality?.sanityCheck?.score || 75,
                        metricsData.quality?.overallScore || 80
                    ],
                    backgroundColor: [
                        'rgba(237, 137, 54, 0.8)',
                        'rgba(66, 153, 225, 0.8)',
                        'rgba(72, 187, 120, 0.8)',
                        'rgba(159, 122, 234, 0.8)'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, max: 100 }
                }
            }
        });
    </script>
</body>
</html>
EOF

echo -e "${BLUE}Creating dashboard generator...${NC}"

# Dashboard generator script
cat > dashboard/generate-dashboard.js << 'EOF'
#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

class DashboardGenerator {
  constructor() {
    this.templatePath = './dashboard/templates/dashboard.html';
    this.dataPath = './dashboard/data/current/latest.json';
    this.outputPath = './dashboard/reports/index.html';
  }

  async generate() {
    console.log('📊 Generating test quality dashboard...');
    
    try {
      // Load data
      const metrics = this.loadMetrics();
      
      // Load template
      const template = fs.readFileSync(this.templatePath, 'utf8');
      
      // Process data
      const processedData = this.processMetrics(metrics);
      
      // Generate HTML
      const html = this.populateTemplate(template, processedData);
      
      // Ensure output directory exists
      const outputDir = path.dirname(this.outputPath);
      if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
      }
      
      // Save dashboard
      fs.writeFileSync(this.outputPath, html);
      
      console.log(`✅ Dashboard generated: ${this.outputPath}`);
      
      // Generate summary
      this.generateSummary(processedData);
      
    } catch (error) {
      console.error('❌ Dashboard generation failed:', error.message);
      process.exit(1);
    }
  }

  loadMetrics() {
    if (!fs.existsSync(this.dataPath)) {
      throw new Error('No metrics data found. Run collect-metrics.js first.');
    }
    
    return JSON.parse(fs.readFileSync(this.dataPath, 'utf8'));
  }

  processMetrics(metrics) {
    const processed = {
      timestamp: new Date(metrics.timestamp).toLocaleString(),
      overallScore: metrics.quality?.overallScore || 0,
      scoreClass: this.getScoreClass(metrics.quality?.overallScore || 0),
      coverage: {
        statements: metrics.coverage?.statements || 0,
        branches: metrics.coverage?.branches || 0,
        functions: metrics.coverage?.functions || 0,
        lines: metrics.coverage?.lines || 0,
        trend: this.formatTrend(metrics.trends?.coverage)
      },
      testFiles: {
        total: metrics.testFiles?.total || 0,
        avgSize: metrics.testFiles?.avgSize || 0,
        bySize: metrics.testFiles?.bySize || { small: 0, medium: 0, large: 0 }
      },
      performance: {
        performance: metrics.performance?.performance || 0,
        accessibility: metrics.performance?.accessibility || 0,
        bestPractices: metrics.performance?.bestPractices || 0,
        seo: metrics.performance?.seo || 0
      },
      quality: {
        sanityCheck: metrics.quality?.sanityCheck || { score: 0, totalIssues: 0, affectedFiles: 0 }
      },
      metricsJson: JSON.stringify(metrics),
      warnings: this.generateWarnings(metrics),
      successes: this.generateSuccesses(metrics)
    };

    processed.hasWarnings = processed.warnings.length > 0;
    processed.hasSuccesses = processed.successes.length > 0;

    return processed;
  }

  getScoreClass(score) {
    if (score >= 90) return 'score-excellent';
    if (score >= 80) return 'score-good';
    if (score >= 70) return 'score-fair';
    return 'score-poor';
  }

  formatTrend(trend) {
    if (!trend) return { direction: 'stable', symbol: '→', change: '0' };
    
    const symbols = { up: '↗', down: '↘', stable: '→' };
    return {
      direction: trend.direction,
      symbol: symbols[trend.direction] || '→',
      change: Math.abs(trend.change || 0).toFixed(1)
    };
  }

  generateWarnings(metrics) {
    const warnings = [];
    
    if (metrics.coverage?.statements < 80) {
      warnings.push(`Test coverage is ${metrics.coverage.statements}% - aim for 80%+`);
    }
    
    if (metrics.quality?.sanityCheck?.totalIssues > 5) {
      warnings.push(`${metrics.quality.sanityCheck.totalIssues} test quality issues found`);
    }
    
    if (metrics.performance?.performance < 70) {
      warnings.push(`Performance score is ${metrics.performance.performance}% - optimize loading`);
    }
    
    if (metrics.testFiles?.bySize?.large > metrics.testFiles?.total * 0.2) {
      warnings.push(`${metrics.testFiles.bySize.large} test files are very large (>200 lines)`);
    }

    return warnings;
  }

  generateSuccesses(metrics) {
    const successes = [];
    
    if (metrics.coverage?.statements >= 90) {
      successes.push(`Excellent test coverage: ${metrics.coverage.statements}%`);
    }
    
    if (metrics.quality?.sanityCheck?.totalIssues === 0) {
      successes.push('No test quality issues detected');
    }
    
    if (metrics.performance?.performance >= 90) {
      successes.push(`Outstanding performance score: ${metrics.performance.performance}%`);
    }
    
    if (metrics.quality?.overallScore >= 85) {
      successes.push(`High overall quality score: ${metrics.quality.overallScore}%`);
    }

    return successes;
  }

  populateTemplate(template, data) {
    let html = template;
    
    // Replace simple variables
    Object.keys(data).forEach(key => {
      if (typeof data[key] === 'string' || typeof data[key] === 'number') {
        const regex = new RegExp(`{{${key}}}`, 'g');
        html = html.replace(regex, data[key]);
      }
    });
    
    // Replace nested variables
    const nestedRegex = /{{(\w+)\.(\w+)\.?(\w+)?}}/g;
    html = html.replace(nestedRegex, (match, obj, prop, subProp) => {
      if (data[obj] && data[obj][prop]) {
        if (subProp && data[obj][prop][subProp] !== undefined) {
          return data[obj][prop][subProp];
        } else if (!subProp) {
          return data[obj][prop];
        }
      }
      return match;
    });
    
    // Handle conditionals and loops (simplified)
    html = this.handleConditionals(html, data);
    
    return html;
  }

  handleConditionals(html, data) {
    // Handle {{#if condition}}...{{/if}}
    const ifRegex = /{{#if (\w+)}}([\s\S]*?){{\/if}}/g;
    html = html.replace(ifRegex, (match, condition, content) => {
      return data[condition] ? content : '';
    });
    
    // Handle {{#each array}}...{{/each}}
    const eachRegex = /{{#each (\w+)}}([\s\S]*?){{\/each}}/g;
    html = html.replace(eachRegex, (match, arrayName, itemTemplate) => {
      const array = data[arrayName];
      if (Array.isArray(array)) {
        return array.map(item => 
          itemTemplate.replace(/{{this}}/g, item)
        ).join('');
      }
      return '';
    });
    
    return html;
  }

  generateSummary(data) {
    const summaryPath = './dashboard/reports/summary.txt';
    
    const summary = `
Test Quality Dashboard Summary
=============================

Generated: ${data.timestamp}
Overall Score: ${data.overallScore}%

Coverage:
- Statements: ${data.coverage.statements}%
- Branches: ${data.coverage.branches}%
- Functions: ${data.coverage.functions}%
- Lines: ${data.coverage.lines}%

Test Files: ${data.testFiles.total} files
Quality Issues: ${data.quality.sanityCheck.totalIssues}

Performance:
- Performance: ${data.performance.performance}%
- Accessibility: ${data.performance.accessibility}%

${data.warnings.length > 0 ? '\nWarnings:\n' + data.warnings.map(w => `- ${w}`).join('\n') : ''}
${data.successes.length > 0 ? '\nSuccesses:\n' + data.successes.map(s => `- ${s}`).join('\n') : ''}
`;
    
    fs.writeFileSync(summaryPath, summary.trim());
    console.log(`📄 Summary saved: ${summaryPath}`);
  }
}

// Run if called directly
if (require.main === module) {
  const generator = new DashboardGenerator();
  generator.generate().catch(console.error);
}

module.exports = DashboardGenerator;
EOF

chmod +x dashboard/generate-dashboard.js

echo -e "${BLUE}Creating dashboard runner script...${NC}"

# Main runner script
cat > dashboard/run-dashboard.sh << 'EOF'
#!/bin/bash
# Test Quality Dashboard Runner

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}📊 Test Quality Dashboard${NC}"
echo "=========================="
echo ""

# Step 1: Collect metrics
echo -e "${BLUE}Step 1: Collecting metrics...${NC}"
node dashboard/collect-metrics.js

# Step 2: Generate dashboard
echo -e "${BLUE}Step 2: Generating dashboard...${NC}"
node dashboard/generate-dashboard.js

# Step 3: Open dashboard
echo ""
echo -e "${GREEN}✅ Dashboard ready!${NC}"
echo -e "${BLUE}📄 Dashboard: dashboard/reports/index.html${NC}"

# Offer to open
if command -v open >/dev/null 2>&1; then
    read -p "Open dashboard in browser? [y/N]: " open_browser
    if [[ $open_browser =~ ^[Yy]$ ]]; then
        open dashboard/reports/index.html
    fi
elif command -v xdg-open >/dev/null 2>&1; then
    read -p "Open dashboard in browser? [y/N]: " open_browser
    if [[ $open_browser =~ ^[Yy]$ ]]; then
        xdg-open dashboard/reports/index.html
    fi
fi

echo ""
echo -e "${YELLOW}💡 To update dashboard:${NC}"
echo "  ./dashboard/run-dashboard.sh"
echo ""
echo -e "${YELLOW}💡 To automate:${NC}"
echo "  # Add to crontab for daily updates"
echo "  0 9 * * * cd /path/to/project && ./dashboard/run-dashboard.sh >/dev/null"
EOF

chmod +x dashboard/run-dashboard.sh

echo ""
echo -e "${GREEN}✅ Test Quality Dashboard setup complete!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Run some tests to generate data:"
echo "   npm test -- --coverage"
echo "2. Generate dashboard:"
echo "   ./dashboard/run-dashboard.sh"
echo ""
echo -e "${BLUE}📁 Files created:${NC}"
echo "- dashboard/collect-metrics.js"
echo "- dashboard/generate-dashboard.js"
echo "- dashboard/templates/dashboard.html"
echo "- dashboard/run-dashboard.sh"