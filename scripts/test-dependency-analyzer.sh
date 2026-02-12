#!/bin/bash
# Test Dependency Analyzer
# Identifies dependencies between tests and recommends isolation improvements

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${PURPLE}🔗 Test Dependency Analyzer${NC}"
echo "============================"
echo ""

# Create dependency analysis directories
mkdir -p dependency/{analysis,graphs,reports}

echo -e "${BLUE}Creating dependency analysis engine...${NC}"

# Main dependency analyzer
cat > dependency/dependency-analyzer.js << 'EOF'
#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class TestDependencyAnalyzer {
  constructor() {
    this.dependencies = {
      sharedState: new Map(),
      fileSystem: new Map(),
      database: new Map(),
      network: new Map(),
      globalVars: new Map(),
      testOrder: new Map(),
      parallelConflicts: []
    };
    
    this.patterns = {
      // Shared state patterns
      sharedState: {
        beforeAll: /beforeAll\s*\(/g,
        beforeEach: /beforeEach\s*\(/g,
        afterAll: /afterAll\s*\(/g,
        afterEach: /afterEach\s*\(/g,
        globalSetup: /globalSetup|globalTeardown/g
      },
      
      // File system patterns
      fileSystem: {
        fsWrite: /fs\.(write|mkdir|rmdir|unlink|rename)/g,
        fileCreate: /createWriteStream|createReadStream/g,
        tempFiles: /tmp|temp|TEMP|\.cache/g,
        fixtures: /fixtures?\/|__fixtures__/g
      },
      
      // Database patterns
      database: {
        dbConnect: /connect\(|createConnection|mongoose\.connect/g,
        dbQuery: /query\(|findOne|findMany|insert|update|delete/g,
        migrations: /migrate|seed|truncate/g,
        transactions: /transaction|beginTransaction|commit|rollback/g
      },
      
      // Network patterns
      network: {
        apiCalls: /fetch\(|axios\.|request\(|http\./g,
        mocking: /mock|stub|spy|nock|jest\.mock/g,
        servers: /listen\(|createServer|app\.listen/g,
        ports: /:(\d{4,5})|PORT\s*=\s*(\d+)/g
      },
      
      // Global state patterns
      globalVars: {
        windowGlobal: /window\.|global\.|process\.env/g,
        moduleState: /module\.exports|exports\./g,
        singletons: /getInstance|singleton/gi,
        staticVars: /static\s+\w+\s*=/g
      },
      
      // Test order dependencies
      testOrder: {
        skip: /\.skip\(|xit\(/g,
        only: /\.only\(|fit\(/g,
        sequential: /describe\.serial|test\.serial/g,
        ordered: /test\.\d+|it\.\d+|step\(/g
      }
    };
  }

  async analyze() {
    console.log('🔍 Analyzing test dependencies...');
    
    try {
      // Step 1: Find all test files
      const testFiles = this.findTestFiles();
      console.log(`Found ${testFiles.length} test files`);
      
      // Step 2: Analyze each file
      for (const file of testFiles) {
        await this.analyzeTestFile(file);
      }
      
      // Step 3: Detect cross-file dependencies
      this.detectCrossFileDependencies();
      
      // Step 4: Identify parallel conflicts
      this.identifyParallelConflicts();
      
      // Step 5: Generate dependency graph
      const graph = this.generateDependencyGraph();
      
      // Step 6: Create recommendations
      const recommendations = this.generateRecommendations();
      
      // Step 7: Generate report
      await this.generateReport(graph, recommendations);
      
      console.log('✅ Dependency analysis complete');
      
    } catch (error) {
      console.error('❌ Analysis failed:', error.message);
      process.exit(1);
    }
  }

  findTestFiles() {
    const patterns = ['**/*.test.*', '**/*.spec.*', '**/test_*.py'];
    const files = [];
    
    patterns.forEach(pattern => {
      try {
        const found = execSync(
          `find . -name "${pattern}" -type f | grep -v node_modules | grep -v coverage | grep -v dist`,
          { encoding: 'utf8' }
        ).trim().split('\n').filter(Boolean);
        files.push(...found);
      } catch (error) {
        // Pattern didn't match any files
      }
    });
    
    return [...new Set(files)];
  }

  async analyzeTestFile(filePath) {
    const content = fs.readFileSync(filePath, 'utf8');
    const analysis = {
      file: filePath,
      dependencies: {
        sharedState: [],
        fileSystem: [],
        database: [],
        network: [],
        globalVars: [],
        testOrder: []
      },
      imports: this.extractImports(content),
      setupTeardown: this.extractSetupTeardown(content)
    };
    
    // Analyze each dependency type
    Object.keys(this.patterns).forEach(type => {
      Object.entries(this.patterns[type]).forEach(([name, pattern]) => {
        const matches = content.match(pattern);
        if (matches && matches.length > 0) {
          analysis.dependencies[type].push({
            pattern: name,
            count: matches.length,
            matches: matches.slice(0, 5) // First 5 matches
          });
        }
      });
    });
    
    // Store analysis
    this.storeAnalysis(filePath, analysis);
  }

  extractImports(content) {
    const imports = [];
    
    // JavaScript/TypeScript imports
    const esImports = content.match(/import\s+.*\s+from\s+['"]([^'"]+)['"]/g) || [];
    const requireImports = content.match(/require\s*\(['"]([^'"]+)['"]\)/g) || [];
    
    // Python imports
    const pythonImports = content.match(/^(import|from)\s+[\w.]+/gm) || [];
    
    imports.push(...esImports, ...requireImports, ...pythonImports);
    
    return imports.map(imp => ({
      statement: imp,
      isLocal: imp.includes('./') || imp.includes('../'),
      isTestUtil: imp.includes('test') || imp.includes('spec') || imp.includes('mock')
    }));
  }

  extractSetupTeardown(content) {
    const setup = {
      hasBeforeAll: /beforeAll|before\(/.test(content),
      hasBeforeEach: /beforeEach/.test(content),
      hasAfterAll: /afterAll|after\(/.test(content),
      hasAfterEach: /afterEach/.test(content),
      hasGlobalSetup: /globalSetup/.test(content),
      usesFixtures: /fixture/.test(content)
    };
    
    return setup;
  }

  storeAnalysis(filePath, analysis) {
    // Store by dependency type
    Object.entries(analysis.dependencies).forEach(([type, deps]) => {
      if (deps.length > 0) {
        this.dependencies[type].set(filePath, deps);
      }
    });
    
    // Store setup/teardown info
    if (Object.values(analysis.setupTeardown).some(v => v)) {
      this.dependencies.sharedState.set(filePath, analysis.setupTeardown);
    }
  }

  detectCrossFileDependencies() {
    console.log('🔄 Detecting cross-file dependencies...');
    
    // Find shared resources
    const sharedResources = {
      databases: new Set(),
      files: new Set(),
      ports: new Set(),
      mockTargets: new Set()
    };
    
    // Analyze database usage
    this.dependencies.database.forEach((deps, file) => {
      deps.forEach(dep => {
        if (dep.pattern === 'dbConnect') {
          sharedResources.databases.add(file);
        }
      });
    });
    
    // Analyze file system usage
    this.dependencies.fileSystem.forEach((deps, file) => {
      deps.forEach(dep => {
        dep.matches.forEach(match => {
          const fileMatch = match.match(/['"]([^'"]+)['"]/);
          if (fileMatch) {
            sharedResources.files.add(fileMatch[1]);
          }
        });
      });
    });
    
    // Analyze network usage
    this.dependencies.network.forEach((deps, file) => {
      deps.forEach(dep => {
        if (dep.pattern === 'ports') {
          dep.matches.forEach(match => {
            const portMatch = match.match(/\d{4,5}/);
            if (portMatch) {
              sharedResources.ports.add(portMatch[0]);
            }
          });
        }
      });
    });
    
    return sharedResources;
  }

  identifyParallelConflicts() {
    console.log('🚨 Identifying parallel execution conflicts...');
    
    const conflicts = [];
    
    // Database conflicts
    const dbTests = Array.from(this.dependencies.database.keys());
    if (dbTests.length > 1) {
      conflicts.push({
        type: 'database',
        severity: 'high',
        files: dbTests,
        reason: 'Multiple tests accessing database without isolation'
      });
    }
    
    // File system conflicts
    const fsTests = Array.from(this.dependencies.fileSystem.keys());
    const sharedFiles = this.findSharedFiles(fsTests);
    if (sharedFiles.length > 0) {
      conflicts.push({
        type: 'filesystem',
        severity: 'medium',
        files: fsTests,
        sharedResources: sharedFiles,
        reason: 'Tests modifying same files'
      });
    }
    
    // Port conflicts
    const networkTests = Array.from(this.dependencies.network.keys());
    const usedPorts = this.findUsedPorts(networkTests);
    const duplicatePorts = this.findDuplicates(usedPorts);
    if (duplicatePorts.length > 0) {
      conflicts.push({
        type: 'network',
        severity: 'high',
        files: networkTests,
        ports: duplicatePorts,
        reason: 'Tests using same network ports'
      });
    }
    
    // Global state conflicts
    const globalTests = Array.from(this.dependencies.globalVars.keys());
    if (globalTests.length > 1) {
      conflicts.push({
        type: 'global',
        severity: 'medium',
        files: globalTests,
        reason: 'Tests modifying global state'
      });
    }
    
    this.dependencies.parallelConflicts = conflicts;
    return conflicts;
  }

  findSharedFiles(testFiles) {
    const fileAccess = new Map();
    
    testFiles.forEach(testFile => {
      const deps = this.dependencies.fileSystem.get(testFile) || [];
      deps.forEach(dep => {
        dep.matches.forEach(match => {
          const fileMatch = match.match(/['"]([^'"]+)['"]/);
          if (fileMatch) {
            const accessedFile = fileMatch[1];
            if (!fileAccess.has(accessedFile)) {
              fileAccess.set(accessedFile, []);
            }
            fileAccess.get(accessedFile).push(testFile);
          }
        });
      });
    });
    
    // Return files accessed by multiple tests
    return Array.from(fileAccess.entries())
      .filter(([file, tests]) => tests.length > 1)
      .map(([file, tests]) => ({ file, tests }));
  }

  findUsedPorts(testFiles) {
    const ports = [];
    
    testFiles.forEach(testFile => {
      const deps = this.dependencies.network.get(testFile) || [];
      deps.forEach(dep => {
        if (dep.pattern === 'ports') {
          dep.matches.forEach(match => {
            const portMatch = match.match(/\d{4,5}/);
            if (portMatch) {
              ports.push({ port: portMatch[0], file: testFile });
            }
          });
        }
      });
    });
    
    return ports;
  }

  findDuplicates(items) {
    const seen = new Set();
    const duplicates = new Set();
    
    items.forEach(item => {
      const key = item.port || item;
      if (seen.has(key)) {
        duplicates.add(key);
      }
      seen.add(key);
    });
    
    return Array.from(duplicates);
  }

  generateDependencyGraph() {
    console.log('📊 Generating dependency graph...');
    
    const nodes = [];
    const edges = [];
    
    // Create nodes for each test file
    const testFiles = new Set();
    Object.values(this.dependencies).forEach(depMap => {
      if (depMap instanceof Map) {
        depMap.forEach((_, file) => testFiles.add(file));
      }
    });
    
    testFiles.forEach(file => {
      nodes.push({
        id: file,
        label: path.basename(file),
        type: 'test',
        dependencies: this.getFileDependencies(file)
      });
    });
    
    // Create edges for dependencies
    this.dependencies.parallelConflicts.forEach(conflict => {
      conflict.files.forEach((file1, i) => {
        conflict.files.slice(i + 1).forEach(file2 => {
          edges.push({
            source: file1,
            target: file2,
            type: conflict.type,
            label: conflict.reason
          });
        });
      });
    });
    
    return { nodes, edges };
  }

  getFileDependencies(file) {
    const deps = {
      sharedState: this.dependencies.sharedState.has(file),
      fileSystem: this.dependencies.fileSystem.has(file),
      database: this.dependencies.database.has(file),
      network: this.dependencies.network.has(file),
      globalVars: this.dependencies.globalVars.has(file)
    };
    
    return Object.entries(deps)
      .filter(([_, hasDep]) => hasDep)
      .map(([type]) => type);
  }

  generateRecommendations() {
    console.log('💡 Generating recommendations...');
    
    const recommendations = [];
    
    // Database isolation
    if (this.dependencies.database.size > 0) {
      recommendations.push({
        category: 'Database Isolation',
        priority: 'high',
        issues: [
          'Tests are sharing database connections',
          'No transaction rollback detected',
          'Missing test database configuration'
        ],
        solutions: [
          'Use transaction rollback in afterEach hooks',
          'Create separate test databases per test suite',
          'Implement database seeding and cleanup utilities',
          'Consider using in-memory databases for unit tests'
        ],
        example: `
// Add to test setup:
beforeEach(async () => {
  await db.beginTransaction();
});

afterEach(async () => {
  await db.rollback();
});`
      });
    }
    
    // File system isolation
    const fsConflicts = this.dependencies.parallelConflicts
      .filter(c => c.type === 'filesystem');
    if (fsConflicts.length > 0) {
      recommendations.push({
        category: 'File System Isolation',
        priority: 'medium',
        issues: [
          'Tests writing to shared directories',
          'No cleanup of temporary files',
          'Hardcoded file paths'
        ],
        solutions: [
          'Use unique temporary directories per test',
          'Implement proper cleanup in afterEach',
          'Use mock file systems for unit tests',
          'Parameterize file paths'
        ],
        example: `
// Use unique temp dirs:
import { mkdtempSync } from 'fs';
import { tmpdir } from 'os';
import { join } from 'path';

beforeEach(() => {
  this.tempDir = mkdtempSync(join(tmpdir(), 'test-'));
});

afterEach(() => {
  fs.rmSync(this.tempDir, { recursive: true });
});`
      });
    }
    
    // Network isolation
    const networkConflicts = this.dependencies.parallelConflicts
      .filter(c => c.type === 'network');
    if (networkConflicts.length > 0) {
      recommendations.push({
        category: 'Network Isolation',
        priority: 'high',
        issues: [
          'Tests using hardcoded ports',
          'No proper server cleanup',
          'Missing network mocks'
        ],
        solutions: [
          'Use dynamic port allocation (port 0)',
          'Properly close servers in afterEach',
          'Mock external API calls',
          'Use test containers for integration tests'
        ],
        example: `
// Dynamic port allocation:
const server = app.listen(0); // OS assigns available port
const port = server.address().port;

afterEach(() => {
  server.close();
});`
      });
    }
    
    // Global state isolation
    if (this.dependencies.globalVars.size > 0) {
      recommendations.push({
        category: 'Global State Isolation',
        priority: 'medium',
        issues: [
          'Tests modifying global variables',
          'Singleton instances shared between tests',
          'Process.env mutations'
        ],
        solutions: [
          'Reset global state in beforeEach',
          'Use dependency injection instead of singletons',
          'Mock process.env instead of modifying',
          'Isolate module state with jest.isolateModules'
        ],
        example: `
// Save and restore global state:
let originalEnv;

beforeEach(() => {
  originalEnv = { ...process.env };
});

afterEach(() => {
  process.env = originalEnv;
});`
      });
    }
    
    // Parallel execution
    const canRunParallel = this.dependencies.parallelConflicts.length === 0;
    recommendations.push({
      category: 'Parallel Execution',
      priority: canRunParallel ? 'low' : 'high',
      status: canRunParallel ? '✅ Tests can run in parallel' : '❌ Parallel execution blocked',
      issues: canRunParallel ? [] : this.dependencies.parallelConflicts.map(c => c.reason),
      solutions: canRunParallel ? ['No changes needed'] : [
        'Fix isolation issues listed above',
        'Use test.concurrent for safe parallel tests',
        'Group conflicting tests in serial suites',
        'Consider test sharding strategies'
      ]
    });
    
    return recommendations;
  }

  async generateReport(graph, recommendations) {
    console.log('📝 Generating dependency report...');
    
    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        totalTests: graph.nodes.length,
        dependencies: {
          sharedState: this.dependencies.sharedState.size,
          fileSystem: this.dependencies.fileSystem.size,
          database: this.dependencies.database.size,
          network: this.dependencies.network.size,
          globalVars: this.dependencies.globalVars.size
        },
        conflicts: this.dependencies.parallelConflicts.length,
        canRunParallel: this.dependencies.parallelConflicts.length === 0
      },
      graph,
      conflicts: this.dependencies.parallelConflicts,
      recommendations
    };
    
    // Save JSON report
    const jsonPath = `dependency/reports/dependency-analysis-${Date.now()}.json`;
    fs.writeFileSync(jsonPath, JSON.stringify(report, null, 2));
    
    // Generate visualization
    const dotPath = 'dependency/graphs/dependencies.dot';
    fs.writeFileSync(dotPath, this.generateDotGraph(graph));
    
    // Generate HTML report
    const htmlPath = 'dependency/reports/dependency-report.html';
    fs.writeFileSync(htmlPath, this.generateHTMLReport(report));
    
    // Print summary
    this.printSummary(report);
    
    console.log(`\n📄 Reports saved:`);
    console.log(`   JSON: ${jsonPath}`);
    console.log(`   Graph: ${dotPath}`);
    console.log(`   HTML: ${htmlPath}`);
  }

  generateDotGraph(graph) {
    let dot = 'digraph TestDependencies {\n';
    dot += '  rankdir=LR;\n';
    dot += '  node [shape=box];\n';
    
    // Add nodes
    graph.nodes.forEach(node => {
      const deps = node.dependencies.join(',');
      dot += `  "${node.id}" [label="${node.label}\\n${deps}"];\n`;
    });
    
    // Add edges
    graph.edges.forEach(edge => {
      const color = {
        database: 'red',
        filesystem: 'orange',
        network: 'blue',
        global: 'purple'
      }[edge.type] || 'black';
      
      dot += `  "${edge.source}" -> "${edge.target}" [label="${edge.type}", color="${color}"];\n`;
    });
    
    dot += '}\n';
    return dot;
  }

  generateHTMLReport(report) {
    return `
<!DOCTYPE html>
<html>
<head>
    <title>Test Dependency Analysis</title>
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
        .good { color: #4caf50; }
        .bad { color: #f44336; }
        .warning { color: #ff9800; }
        .conflicts {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 20px 0;
        }
        .conflict {
            border-left: 4px solid #f44336;
            padding: 10px;
            margin: 10px 0;
            background: #ffebee;
        }
        .recommendations {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 20px 0;
        }
        .recommendation {
            margin: 20px 0;
            padding: 15px;
            border-radius: 8px;
            background: #e3f2fd;
        }
        .recommendation h3 {
            margin-top: 0;
            color: #1976d2;
        }
        pre {
            background: #f5f5f5;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
        }
        .priority-high { border-left: 4px solid #f44336; }
        .priority-medium { border-left: 4px solid #ff9800; }
        .priority-low { border-left: 4px solid #4caf50; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔗 Test Dependency Analysis</h1>
        <p>Generated: ${new Date(report.timestamp).toLocaleString()}</p>
    </div>
    
    <div class="summary">
        <div class="stat">
            <div class="stat-label">Total Tests</div>
            <div class="stat-value">${report.summary.totalTests}</div>
        </div>
        <div class="stat">
            <div class="stat-label">Shared State</div>
            <div class="stat-value ${report.summary.dependencies.sharedState > 0 ? 'warning' : 'good'}">
                ${report.summary.dependencies.sharedState}
            </div>
        </div>
        <div class="stat">
            <div class="stat-label">File System</div>
            <div class="stat-value ${report.summary.dependencies.fileSystem > 0 ? 'warning' : 'good'}">
                ${report.summary.dependencies.fileSystem}
            </div>
        </div>
        <div class="stat">
            <div class="stat-label">Database</div>
            <div class="stat-value ${report.summary.dependencies.database > 0 ? 'warning' : 'good'}">
                ${report.summary.dependencies.database}
            </div>
        </div>
        <div class="stat">
            <div class="stat-label">Network</div>
            <div class="stat-value ${report.summary.dependencies.network > 0 ? 'warning' : 'good'}">
                ${report.summary.dependencies.network}
            </div>
        </div>
        <div class="stat">
            <div class="stat-label">Parallel Safe</div>
            <div class="stat-value ${report.summary.canRunParallel ? 'good' : 'bad'}">
                ${report.summary.canRunParallel ? '✅ Yes' : '❌ No'}
            </div>
        </div>
    </div>
    
    ${report.conflicts.length > 0 ? `
    <div class="conflicts">
        <h2>🚨 Conflicts Detected</h2>
        ${report.conflicts.map(conflict => `
        <div class="conflict">
            <strong>${conflict.type.toUpperCase()}</strong>: ${conflict.reason}
            <br>Files: ${conflict.files.join(', ')}
            ${conflict.ports ? `<br>Ports: ${conflict.ports.join(', ')}` : ''}
            ${conflict.sharedResources ? `<br>Shared: ${conflict.sharedResources.map(r => r.file).join(', ')}` : ''}
        </div>
        `).join('')}
    </div>
    ` : ''}
    
    <div class="recommendations">
        <h2>💡 Recommendations</h2>
        ${report.recommendations.map(rec => `
        <div class="recommendation priority-${rec.priority}">
            <h3>${rec.category}</h3>
            ${rec.status ? `<p><strong>${rec.status}</strong></p>` : ''}
            ${rec.issues.length > 0 ? `
            <p><strong>Issues:</strong></p>
            <ul>${rec.issues.map(issue => `<li>${issue}</li>`).join('')}</ul>
            ` : ''}
            <p><strong>Solutions:</strong></p>
            <ul>${rec.solutions.map(solution => `<li>${solution}</li>`).join('')}</ul>
            ${rec.example ? `<pre><code>${rec.example.trim()}</code></pre>` : ''}
        </div>
        `).join('')}
    </div>
</body>
</html>`;
  }

  printSummary(report) {
    console.log('\n📊 Dependency Analysis Summary');
    console.log('==============================');
    console.log(`Total test files: ${report.summary.totalTests}`);
    console.log('\nDependency Types:');
    Object.entries(report.summary.dependencies).forEach(([type, count]) => {
      const icon = count > 0 ? '⚠️' : '✅';
      console.log(`  ${icon} ${type}: ${count}`);
    });
    
    if (report.summary.canRunParallel) {
      console.log('\n✅ Tests can run in parallel safely');
    } else {
      console.log(`\n❌ ${report.conflicts.length} conflicts prevent parallel execution`);
      report.conflicts.forEach(conflict => {
        console.log(`   - ${conflict.type}: ${conflict.reason}`);
      });
    }
    
    console.log('\n💡 Top Recommendations:');
    report.recommendations.slice(0, 3).forEach(rec => {
      console.log(`   - ${rec.category} (${rec.priority} priority)`);
    });
  }
}

// Run if called directly
if (require.main === module) {
  const analyzer = new TestDependencyAnalyzer();
  analyzer.analyze().catch(console.error);
}

module.exports = TestDependencyAnalyzer;
EOF

chmod +x dependency/dependency-analyzer.js

echo -e "${BLUE}Creating dependency visualization tool...${NC}"

# Visualization generator
cat > dependency/visualize-dependencies.sh << 'EOF'
#!/bin/bash
# Generate visual dependency graphs

set -e

# Check for graphviz
if ! command -v dot >/dev/null 2>&1; then
    echo "⚠️  Graphviz not installed. Install with: brew install graphviz"
    exit 1
fi

# Generate SVG from DOT file
if [ -f "dependency/graphs/dependencies.dot" ]; then
    dot -Tsvg dependency/graphs/dependencies.dot -o dependency/graphs/dependencies.svg
    echo "✅ Generated dependency/graphs/dependencies.svg"
    
    # Generate PNG as well
    dot -Tpng dependency/graphs/dependencies.dot -o dependency/graphs/dependencies.png
    echo "✅ Generated dependency/graphs/dependencies.png"
    
    # Open in browser
    if command -v open >/dev/null 2>&1; then
        open dependency/graphs/dependencies.svg
    fi
else
    echo "❌ No dependency graph found. Run the analyzer first."
fi
EOF

chmod +x dependency/visualize-dependencies.sh

echo -e "${BLUE}Creating parallel test runner...${NC}"

# Parallel test executor based on dependencies
cat > dependency/parallel-test-runner.sh << 'EOF'
#!/bin/bash
# Run tests in parallel based on dependency analysis

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚀 Parallel Test Runner${NC}"
echo "======================="

# Check for dependency analysis
if [ ! -f "dependency/reports/dependency-analysis-*.json" ]; then
    echo "⚠️  No dependency analysis found. Running analyzer first..."
    node dependency/dependency-analyzer.js
fi

# Get latest analysis
LATEST_ANALYSIS=$(ls -t dependency/reports/dependency-analysis-*.json | head -1)

# Extract parallel-safe tests
SAFE_TESTS=$(node -e "
const report = require('./$LATEST_ANALYSIS');
if (report.summary.canRunParallel) {
    console.log('ALL');
} else {
    // Extract tests without conflicts
    const conflictFiles = new Set();
    report.conflicts.forEach(c => c.files.forEach(f => conflictFiles.add(f)));
    const safeTests = report.graph.nodes
        .filter(n => !conflictFiles.has(n.id))
        .map(n => n.id);
    console.log(safeTests.join(' '));
}
")

if [ "$SAFE_TESTS" = "ALL" ]; then
    echo -e "${GREEN}✅ All tests can run in parallel!${NC}"
    npm test -- --parallel
else
    echo -e "${YELLOW}⚠️  Running safe tests in parallel, others sequentially${NC}"
    
    # Run safe tests in parallel
    if [ -n "$SAFE_TESTS" ]; then
        echo "Parallel tests: $SAFE_TESTS"
        npm test -- --parallel $SAFE_TESTS
    fi
    
    # Run conflicting tests sequentially
    echo "Running conflicting tests sequentially..."
    npm test -- --runInBand --testPathPattern="conflict"
fi
EOF

chmod +x dependency/parallel-test-runner.sh

echo -e "${BLUE}Creating package.json for dependency analyzer...${NC}"

# Package.json
cat > dependency/package.json << 'EOF'
{
  "name": "test-dependency-analyzer",
  "version": "1.0.0",
  "description": "Analyze test dependencies and conflicts",
  "main": "dependency-analyzer.js",
  "scripts": {
    "analyze": "node dependency-analyzer.js",
    "visualize": "./visualize-dependencies.sh",
    "parallel": "./parallel-test-runner.sh"
  },
  "dependencies": {}
}
EOF

echo ""
echo -e "${GREEN}✅ Test Dependency Analyzer setup complete!${NC}"
echo ""
echo -e "${YELLOW}To use:${NC}"
echo "  cd dependency && npm install"
echo "  npm run analyze      # Analyze dependencies"
echo "  npm run visualize    # Generate visual graph"
echo "  npm run parallel     # Run tests optimally"
echo ""
echo -e "${BLUE}Features:${NC}"
echo "- Detects shared state between tests"
echo "- Identifies file system conflicts"
echo "- Finds database dependencies"
echo "- Discovers network port conflicts"
echo "- Generates dependency graphs"
echo "- Recommends isolation improvements"
echo "- Optimizes parallel execution"