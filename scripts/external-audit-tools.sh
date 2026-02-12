#!/bin/bash
# External Audit Tools Setup
# Integrates third-party tools to validate test quality

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${PURPLE}🔍 External Audit Tools Setup${NC}"
echo "==============================="
echo ""

# Create audit tools directory
mkdir -p audit-tools/{reports,config,scripts}

echo -e "${BLUE}Setting up ESLint testing plugin...${NC}"

# ESLint config for test quality
cat > audit-tools/config/eslint-test-quality.js << 'EOF'
module.exports = {
  extends: [
    'eslint:recommended',
    'plugin:jest/recommended'
  ],
  plugins: ['jest'],
  env: {
    jest: true,
    node: true
  },
  rules: {
    // Test-specific rules
    'jest/expect-expect': 'error',
    'jest/no-disabled-tests': 'warn',
    'jest/no-focused-tests': 'error',
    'jest/no-identical-title': 'error',
    'jest/prefer-to-have-length': 'error',
    'jest/valid-expect': 'error',
    
    // Custom rules for test quality
    'no-empty-function': 'error',
    'no-unused-vars': 'error',
    
    // Prevent weak assertions
    'jest/prefer-strict-equal': 'error',
    'jest/prefer-to-be': 'error',
    'jest/prefer-to-contain': 'error'
  },
  overrides: [
    {
      files: ['**/*.test.*', '**/*.spec.*'],
      rules: {
        // Stricter rules for test files
        'max-lines': ['error', { max: 300 }],
        'max-len': ['error', { code: 120 }],
        'complexity': ['error', { max: 10 }]
      }
    }
  ]
};
EOF

echo -e "${BLUE}Setting up SonarQube test quality scanner...${NC}"

# SonarQube properties for test quality
cat > audit-tools/config/sonar-project.properties << 'EOF'
sonar.projectKey=hardcard-test-quality
sonar.projectName=HardCard Test Quality
sonar.projectVersion=1.0

# Source and test directories
sonar.sources=.
sonar.tests=.
sonar.test.inclusions=**/*.test.*,**/*.spec.*
sonar.exclusions=**/node_modules/**,**/coverage/**,**/dist/**

# Test coverage
sonar.javascript.lcov.reportPaths=coverage/lcov.info
sonar.coverage.exclusions=**/*.test.*,**/*.spec.*

# Test quality metrics
sonar.testExecutionReportPaths=test-results/sonar-report.xml

# Quality gates for tests
sonar.qualitygate.wait=true

# Language settings
sonar.sourceEncoding=UTF-8
EOF

echo -e "${BLUE}Creating test coverage analyzer...${NC}"

# Test coverage quality script
cat > audit-tools/scripts/coverage-analyzer.js << 'EOF'
#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

class CoverageAnalyzer {
  constructor() {
    this.coverageDir = './coverage';
    this.reportFile = './audit-tools/reports/coverage-analysis.json';
  }

  analyzeCoverage() {
    try {
      // Read Istanbul/NYC coverage report
      const coverageFile = path.join(this.coverageDir, 'coverage-summary.json');
      
      if (!fs.existsSync(coverageFile)) {
        throw new Error('Coverage report not found. Run tests with coverage first.');
      }

      const coverage = JSON.parse(fs.readFileSync(coverageFile, 'utf8'));
      
      const analysis = {
        timestamp: new Date().toISOString(),
        overall: this.analyzeSummary(coverage.total),
        files: {},
        recommendations: [],
        qualityScore: 0
      };

      // Analyze per-file coverage
      Object.keys(coverage).forEach(file => {
        if (file !== 'total') {
          analysis.files[file] = this.analyzeSummary(coverage[file]);
        }
      });

      // Generate recommendations
      analysis.recommendations = this.generateRecommendations(analysis);
      analysis.qualityScore = this.calculateQualityScore(analysis);

      // Save analysis
      fs.writeFileSync(this.reportFile, JSON.stringify(analysis, null, 2));
      
      this.printReport(analysis);
      return analysis;

    } catch (error) {
      console.error('Coverage analysis failed:', error.message);
      process.exit(1);
    }
  }

  analyzeSummary(summary) {
    return {
      statements: {
        pct: summary.statements.pct,
        covered: summary.statements.covered,
        total: summary.statements.total,
        quality: this.getQualityLevel(summary.statements.pct)
      },
      branches: {
        pct: summary.branches.pct,
        covered: summary.branches.covered,
        total: summary.branches.total,
        quality: this.getQualityLevel(summary.branches.pct)
      },
      functions: {
        pct: summary.functions.pct,
        covered: summary.functions.covered,
        total: summary.functions.total,
        quality: this.getQualityLevel(summary.functions.pct)
      },
      lines: {
        pct: summary.lines.pct,
        covered: summary.lines.covered,
        total: summary.lines.total,
        quality: this.getQualityLevel(summary.lines.pct)
      }
    };
  }

  getQualityLevel(percentage) {
    if (percentage >= 90) return 'excellent';
    if (percentage >= 80) return 'good';
    if (percentage >= 70) return 'fair';
    if (percentage >= 50) return 'poor';
    return 'critical';
  }

  generateRecommendations(analysis) {
    const recommendations = [];
    const overall = analysis.overall;

    if (overall.statements.pct < 80) {
      recommendations.push({
        type: 'coverage',
        priority: 'high',
        message: `Statement coverage is ${overall.statements.pct}%. Target: 80%+`,
        action: 'Add tests for uncovered statements'
      });
    }

    if (overall.branches.pct < 75) {
      recommendations.push({
        type: 'coverage',
        priority: 'high',
        message: `Branch coverage is ${overall.branches.pct}%. Target: 75%+`,
        action: 'Add tests for edge cases and conditional logic'
      });
    }

    if (overall.functions.pct < 85) {
      recommendations.push({
        type: 'coverage',
        priority: 'medium',
        message: `Function coverage is ${overall.functions.pct}%. Target: 85%+`,
        action: 'Add tests for untested functions'
      });
    }

    // Find files with poor coverage
    Object.keys(analysis.files).forEach(file => {
      const fileCoverage = analysis.files[file];
      if (fileCoverage.statements.pct < 60) {
        recommendations.push({
          type: 'file',
          priority: 'high',
          message: `File ${file} has low coverage: ${fileCoverage.statements.pct}%`,
          action: `Focus testing efforts on ${file}`
        });
      }
    });

    return recommendations;
  }

  calculateQualityScore(analysis) {
    const weights = {
      statements: 0.3,
      branches: 0.3,
      functions: 0.2,
      lines: 0.2
    };

    const overall = analysis.overall;
    return Math.round(
      overall.statements.pct * weights.statements +
      overall.branches.pct * weights.branches +
      overall.functions.pct * weights.functions +
      overall.lines.pct * weights.lines
    );
  }

  printReport(analysis) {
    console.log('\n📊 Test Coverage Analysis Report');
    console.log('================================');
    
    const overall = analysis.overall;
    console.log(`\n📈 Overall Quality Score: ${analysis.qualityScore}/100`);
    console.log(`📋 Statements: ${overall.statements.pct}% (${overall.statements.quality})`);
    console.log(`🌳 Branches: ${overall.branches.pct}% (${overall.branches.quality})`);
    console.log(`⚙️  Functions: ${overall.functions.pct}% (${overall.functions.quality})`);
    console.log(`📄 Lines: ${overall.lines.pct}% (${overall.lines.quality})`);

    if (analysis.recommendations.length > 0) {
      console.log('\n🎯 Recommendations:');
      analysis.recommendations.forEach((rec, index) => {
        const priority = rec.priority === 'high' ? '🔴' : '🟡';
        console.log(`${priority} ${index + 1}. ${rec.message}`);
        console.log(`   Action: ${rec.action}`);
      });
    }

    console.log(`\n📄 Full report: ${this.reportFile}`);
  }
}

// Run if called directly
if (require.main === module) {
  const analyzer = new CoverageAnalyzer();
  analyzer.analyzeCoverage();
}

module.exports = CoverageAnalyzer;
EOF

chmod +x audit-tools/scripts/coverage-analyzer.js

echo -e "${BLUE}Setting up Lighthouse CI for performance testing...${NC}"

# Lighthouse CI configuration
cat > audit-tools/config/lighthouse-ci.json << 'EOF'
{
  "ci": {
    "collect": {
      "startServerCommand": "npm start",
      "url": [
        "http://localhost:3005",
        "http://localhost:3005/appointments",
        "http://localhost:3005/login",
        "http://localhost:3005/dashboard"
      ],
      "numberOfRuns": 3,
      "settings": {
        "preset": "desktop",
        "chromeFlags": "--no-sandbox"
      }
    },
    "assert": {
      "assertions": {
        "categories:performance": ["error", {"minScore": 0.8}],
        "categories:accessibility": ["error", {"minScore": 0.9}],
        "categories:best-practices": ["error", {"minScore": 0.8}],
        "categories:seo": ["error", {"minScore": 0.8}]
      }
    },
    "upload": {
      "target": "temporary-public-storage"
    }
  }
}
EOF

echo -e "${BLUE}Creating unified audit runner...${NC}"

# Main audit script
cat > audit-tools/run-audits.sh << 'EOF'
#!/bin/bash
# Unified Test Quality Audit Runner

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${PURPLE}🔍 Running External Test Audits${NC}"
echo "================================="
echo ""

# Create reports directory
mkdir -p audit-tools/reports

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to run audit with error handling
run_audit() {
    local name="$1"
    local command="$2"
    local optional="$3"
    
    echo -e "${BLUE}Running $name...${NC}"
    
    if eval "$command"; then
        echo -e "${GREEN}✅ $name completed successfully${NC}"
    else
        if [ "$optional" = "optional" ]; then
            echo -e "${YELLOW}⚠️  $name failed (optional)${NC}"
        else
            echo -e "${RED}❌ $name failed${NC}"
            return 1
        fi
    fi
    echo ""
}

# 1. ESLint Test Quality Check
if command_exists eslint; then
    run_audit "ESLint Test Quality" \
        "eslint **/*.test.* **/*.spec.* --config audit-tools/config/eslint-test-quality.js --format json --output-file audit-tools/reports/eslint-tests.json || true"
else
    echo -e "${YELLOW}⚠️  ESLint not found, skipping...${NC}"
fi

# 2. Test Coverage Analysis
if [ -d "coverage" ]; then
    run_audit "Coverage Analysis" \
        "node audit-tools/scripts/coverage-analyzer.js"
else
    echo -e "${YELLOW}⚠️  No coverage data found. Run tests with coverage first:${NC}"
    echo "  npm test -- --coverage"
fi

# 3. Test Sanity Check
if [ -f "scripts/test-sanity-checker.sh" ]; then
    run_audit "Test Sanity Check" \
        "./scripts/test-sanity-checker.sh > audit-tools/reports/sanity-check.log 2>&1 || true"
fi

# 4. Mutation Testing (optional - can be slow)
read -p "Run mutation testing? (slow) [y/N]: " run_mutation
if [[ $run_mutation =~ ^[Yy]$ ]] && [ -f "scripts/mutation-tester.sh" ]; then
    run_audit "Mutation Testing" \
        "./scripts/mutation-tester.sh > audit-tools/reports/mutation-testing.log 2>&1 || true" \
        "optional"
fi

# 5. Lighthouse CI (if server can be started)
if command_exists lhci && command_exists npm; then
    read -p "Run Lighthouse performance audit? [y/N]: " run_lighthouse
    if [[ $run_lighthouse =~ ^[Yy]$ ]]; then
        run_audit "Lighthouse CI" \
            "cd audit-tools && lhci autorun --config config/lighthouse-ci.json" \
            "optional"
    fi
fi

# 6. Bundle Analyzer (if webpack/vite)
if [ -f "package.json" ]; then
    if grep -q "webpack-bundle-analyzer\|vite-bundle-analyzer" package.json; then
        run_audit "Bundle Analysis" \
            "npm run analyze > audit-tools/reports/bundle-analysis.log 2>&1 || echo 'No analyze script found'" \
            "optional"
    fi
fi

# Generate consolidated report
echo -e "${BLUE}Generating consolidated report...${NC}"

cat > audit-tools/reports/audit-summary.md << EOF
# 🔍 Test Quality Audit Summary

Generated: $(date)

## Audits Performed

### ✅ Completed Audits
EOF

# Add completed audits to report
if [ -f "audit-tools/reports/eslint-tests.json" ]; then
    echo "- ESLint Test Quality Check" >> audit-tools/reports/audit-summary.md
fi

if [ -f "audit-tools/reports/coverage-analysis.json" ]; then
    echo "- Test Coverage Analysis" >> audit-tools/reports/audit-summary.md
fi

if [ -f "audit-tools/reports/sanity-check.log" ]; then
    echo "- Test Sanity Check" >> audit-tools/reports/audit-summary.md
fi

cat >> audit-tools/reports/audit-summary.md << EOF

## Key Findings

### Coverage Analysis
EOF

if [ -f "audit-tools/reports/coverage-analysis.json" ]; then
    node -e "
    const data = JSON.parse(require('fs').readFileSync('audit-tools/reports/coverage-analysis.json'));
    console.log(\`- Quality Score: \${data.qualityScore}/100\`);
    console.log(\`- Statements: \${data.overall.statements.pct}%\`);
    console.log(\`- Branches: \${data.overall.branches.pct}%\`);
    console.log(\`- Functions: \${data.overall.functions.pct}%\`);
    if (data.recommendations.length > 0) {
        console.log('');
        console.log('### Recommendations');
        data.recommendations.forEach((rec, i) => {
            console.log(\`\${i+1}. \${rec.message}\`);
        });
    }
    " >> audit-tools/reports/audit-summary.md
fi

cat >> audit-tools/reports/audit-summary.md << EOF

### Test Sanity Issues
EOF

if [ -f "test-sanity-results/$(ls -t test-sanity-results | head -1)/SANITY_REPORT.md" ]; then
    echo "See: test-sanity-results/latest/SANITY_REPORT.md" >> audit-tools/reports/audit-summary.md
fi

cat >> audit-tools/reports/audit-summary.md << EOF

## Next Steps

1. Review individual audit reports in audit-tools/reports/
2. Address high-priority issues first
3. Set up CI/CD integration for continuous monitoring
4. Run audits before each release

## Files Generated

EOF

ls -la audit-tools/reports/ | grep -v "^d" | awk '{print "- " $9}' >> audit-tools/reports/audit-summary.md

echo ""
echo -e "${GREEN}🎉 Audit complete!${NC}"
echo -e "${BLUE}📄 Summary report: audit-tools/reports/audit-summary.md${NC}"
echo ""

# Suggest next steps based on findings
if [ -f "audit-tools/reports/coverage-analysis.json" ]; then
    quality_score=$(node -e "console.log(JSON.parse(require('fs').readFileSync('audit-tools/reports/coverage-analysis.json')).qualityScore)")
    if [ "$quality_score" -lt 80 ]; then
        echo -e "${YELLOW}⚠️  Quality score below 80. Consider:${NC}"
        echo "1. Adding more comprehensive tests"
        echo "2. Reviewing the improved test examples"
        echo "3. Running mutation testing to find weak tests"
    fi
fi

chmod +x audit-tools/run-audits.sh

echo -e "${BLUE}Creating CI/CD integration...${NC}"

# GitHub Actions for audit integration
cat > .github/workflows/test-quality-audit.yml << 'EOF'
name: Test Quality Audit

on:
  pull_request:
    branches: [ main, master ]
  schedule:
    # Run weekly on Sundays
    - cron: '0 0 * * 0'

jobs:
  audit:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run tests with coverage
      run: npm test -- --coverage
    
    - name: Install audit tools
      run: |
        npm install -g eslint @lighthouse-ci/cli
        npm install eslint-plugin-jest
    
    - name: Run quality audits
      run: ./audit-tools/run-audits.sh
      env:
        CI: true
    
    - name: Upload audit reports
      uses: actions/upload-artifact@v4
      with:
        name: audit-reports
        path: audit-tools/reports/
        retention-days: 30
    
    - name: Comment PR with results
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v7
      with:
        script: |
          const fs = require('fs');
          if (fs.existsSync('audit-tools/reports/audit-summary.md')) {
            const summary = fs.readFileSync('audit-tools/reports/audit-summary.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '## 🔍 Test Quality Audit Results\n\n' + summary
            });
          }
EOF

echo -e "${BLUE}Creating package.json for audit tools...${NC}"

# Package.json for audit dependencies
cat > audit-tools/package.json << 'EOF'
{
  "name": "hardcard-audit-tools",
  "version": "1.0.0",
  "description": "External audit tools for test quality",
  "scripts": {
    "audit": "./run-audits.sh",
    "install:tools": "npm install -g eslint @lighthouse-ci/cli && npm install eslint-plugin-jest"
  },
  "devDependencies": {
    "eslint": "^8.0.0",
    "eslint-plugin-jest": "^27.0.0",
    "@lighthouse-ci/cli": "^0.12.0"
  }
}
EOF

echo ""
echo -e "${GREEN}✅ External audit tools setup complete!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. cd audit-tools"
echo "2. npm run install:tools"
echo "3. npm test -- --coverage (in main directory)"
echo "4. ./run-audits.sh"
echo ""
echo -e "${BLUE}📁 Files created:${NC}"
echo "- audit-tools/config/eslint-test-quality.js"
echo "- audit-tools/config/sonar-project.properties"
echo "- audit-tools/config/lighthouse-ci.json"
echo "- audit-tools/scripts/coverage-analyzer.js"
echo "- audit-tools/run-audits.sh"
echo "- .github/workflows/test-quality-audit.yml"