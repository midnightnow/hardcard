#!/bin/bash
# Real-Time Test Execution Monitor
# Live monitoring of test runs with instant feedback

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${PURPLE}⚡ Real-Time Test Monitor${NC}"
echo "=========================="
echo ""

# Create real-time monitoring directories
mkdir -p realtime/{streams,sessions,reports}

echo -e "${BLUE}Creating real-time test runner...${NC}"

# Real-time test execution monitor
cat > realtime/test-runner-monitor.js << 'EOF'
#!/usr/bin/env node

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const WebSocket = require('ws');
const http = require('http');

class RealTimeTestMonitor {
  constructor() {
    this.sessions = new Map();
    this.metrics = {
      totalTests: 0,
      passedTests: 0,
      failedTests: 0,
      skippedTests: 0,
      testDurations: [],
      slowTests: [],
      flakyTests: new Map(),
      currentSuite: null
    };
    
    this.server = null;
    this.wss = null;
    this.dashboardPort = 3333;
  }

  async start() {
    console.log('🚀 Starting Real-Time Test Monitor...');
    
    // Start WebSocket server for live updates
    this.startWebSocketServer();
    
    // Start HTTP server for dashboard
    this.startDashboardServer();
    
    console.log(`✅ Monitor running at http://localhost:${this.dashboardPort}`);
  }

  startWebSocketServer() {
    this.wss = new WebSocket.Server({ port: 3334 });
    
    this.wss.on('connection', (ws) => {
      console.log('📡 Dashboard connected');
      
      // Send initial state
      ws.send(JSON.stringify({
        type: 'init',
        data: this.getMetricsSummary()
      }));
      
      ws.on('message', (message) => {
        const msg = JSON.parse(message);
        if (msg.type === 'run-test') {
          this.runTestWithMonitoring(msg.command, ws);
        }
      });
    });
  }

  startDashboardServer() {
    this.server = http.createServer((req, res) => {
      if (req.url === '/') {
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.end(this.getDashboardHTML());
      } else if (req.url === '/metrics') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(this.getMetricsSummary()));
      }
    });
    
    this.server.listen(this.dashboardPort);
  }

  runTestWithMonitoring(command = 'npm test', ws) {
    const sessionId = Date.now().toString();
    const session = {
      id: sessionId,
      command,
      startTime: Date.now(),
      output: [],
      tests: [],
      status: 'running'
    };
    
    this.sessions.set(sessionId, session);
    
    console.log(`🧪 Starting test session: ${sessionId}`);
    
    const testProcess = spawn(command, { 
      shell: true,
      env: { ...process.env, FORCE_COLOR: '1' }
    });
    
    // Real-time output processing
    testProcess.stdout.on('data', (data) => {
      const output = data.toString();
      session.output.push(output);
      
      // Parse test output in real-time
      this.parseTestOutput(output, session, ws);
      
      // Send live output to dashboard
      this.broadcast({
        type: 'output',
        sessionId,
        data: output
      });
    });
    
    testProcess.stderr.on('data', (data) => {
      const output = data.toString();
      session.output.push(output);
      
      this.broadcast({
        type: 'error',
        sessionId,
        data: output
      });
    });
    
    testProcess.on('close', (code) => {
      session.endTime = Date.now();
      session.duration = session.endTime - session.startTime;
      session.status = code === 0 ? 'passed' : 'failed';
      
      // Generate session report
      this.generateSessionReport(session);
      
      this.broadcast({
        type: 'complete',
        sessionId,
        data: {
          status: session.status,
          duration: session.duration,
          summary: this.getSessionSummary(session)
        }
      });
      
      console.log(`✅ Test session ${sessionId} completed in ${session.duration}ms`);
    });
  }

  parseTestOutput(output, session, ws) {
    // Parse Jest/Mocha/other test runner output
    const patterns = {
      // Jest patterns
      testPass: /✓\s+(.+)\s+\((\d+)\s*ms\)/g,
      testFail: /✕\s+(.+)\s+\((\d+)\s*ms\)/g,
      testSkip: /○\s+(.+)/g,
      suiteName: /^\s*(describe|test suite|context)\s+(.+)/i,
      
      // Mocha patterns
      mochaPass: /\s+✓\s+(.+)\s*\((\d+)ms\)/g,
      mochaFail: /\s+\d+\)\s+(.+)/g,
      
      // Summary patterns
      summary: /Tests:\s+(\d+)\s+passed,\s+(\d+)\s+failed/,
      coverage: /Statements\s*:\s*([\d.]+)%/
    };
    
    // Track individual test results
    let match;
    
    // Passing tests
    while ((match = patterns.testPass.exec(output)) !== null) {
      const test = {
        name: match[1],
        duration: parseInt(match[2]),
        status: 'passed',
        timestamp: Date.now()
      };
      
      session.tests.push(test);
      this.metrics.totalTests++;
      this.metrics.passedTests++;
      this.metrics.testDurations.push(test.duration);
      
      // Check for slow tests
      if (test.duration > 1000) {
        this.metrics.slowTests.push(test);
        this.broadcast({
          type: 'slow-test',
          data: test
        });
      }
      
      this.broadcast({
        type: 'test-result',
        sessionId: session.id,
        data: test
      });
    }
    
    // Failing tests
    while ((match = patterns.testFail.exec(output)) !== null) {
      const test = {
        name: match[1],
        duration: parseInt(match[2]),
        status: 'failed',
        timestamp: Date.now()
      };
      
      session.tests.push(test);
      this.metrics.totalTests++;
      this.metrics.failedTests++;
      
      // Track flaky tests
      this.trackFlakyTest(test.name);
      
      this.broadcast({
        type: 'test-result',
        sessionId: session.id,
        data: test
      });
    }
    
    // Suite detection
    if ((match = patterns.suiteName.exec(output)) !== null) {
      this.metrics.currentSuite = match[2];
      this.broadcast({
        type: 'suite-start',
        data: { name: match[2] }
      });
    }
    
    // Coverage detection
    if ((match = patterns.coverage.exec(output)) !== null) {
      this.broadcast({
        type: 'coverage-update',
        data: { statements: parseFloat(match[1]) }
      });
    }
  }

  trackFlakyTest(testName) {
    if (!this.metrics.flakyTests.has(testName)) {
      this.metrics.flakyTests.set(testName, {
        failures: 0,
        passes: 0,
        flakiness: 0
      });
    }
    
    const stats = this.metrics.flakyTests.get(testName);
    stats.failures++;
    stats.flakiness = stats.failures / (stats.failures + stats.passes);
    
    if (stats.flakiness > 0.1 && stats.failures + stats.passes > 5) {
      this.broadcast({
        type: 'flaky-test-detected',
        data: {
          name: testName,
          stats
        }
      });
    }
  }

  generateSessionReport(session) {
    const report = {
      id: session.id,
      command: session.command,
      duration: session.duration,
      status: session.status,
      summary: {
        total: session.tests.length,
        passed: session.tests.filter(t => t.status === 'passed').length,
        failed: session.tests.filter(t => t.status === 'failed').length,
        skipped: session.tests.filter(t => t.status === 'skipped').length
      },
      slowTests: session.tests.filter(t => t.duration > 1000),
      failedTests: session.tests.filter(t => t.status === 'failed'),
      timestamp: new Date().toISOString()
    };
    
    // Save report
    fs.writeFileSync(
      `realtime/sessions/session-${session.id}.json`,
      JSON.stringify(report, null, 2)
    );
    
    return report;
  }

  getSessionSummary(session) {
    const tests = session.tests;
    return {
      total: tests.length,
      passed: tests.filter(t => t.status === 'passed').length,
      failed: tests.filter(t => t.status === 'failed').length,
      duration: session.duration,
      avgDuration: tests.length > 0 ? 
        Math.round(tests.reduce((sum, t) => sum + t.duration, 0) / tests.length) : 0
    };
  }

  getMetricsSummary() {
    return {
      totalTests: this.metrics.totalTests,
      passedTests: this.metrics.passedTests,
      failedTests: this.metrics.failedTests,
      skippedTests: this.metrics.skippedTests,
      passRate: this.metrics.totalTests > 0 ? 
        Math.round((this.metrics.passedTests / this.metrics.totalTests) * 100) : 0,
      avgDuration: this.metrics.testDurations.length > 0 ?
        Math.round(this.metrics.testDurations.reduce((a, b) => a + b, 0) / this.metrics.testDurations.length) : 0,
      slowTests: this.metrics.slowTests.length,
      flakyTests: Array.from(this.metrics.flakyTests.entries())
        .filter(([, stats]) => stats.flakiness > 0.1)
        .map(([name, stats]) => ({ name, ...stats })),
      activeSessions: this.sessions.size
    };
  }

  broadcast(message) {
    if (this.wss) {
      this.wss.clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
          client.send(JSON.stringify(message));
        }
      });
    }
  }

  getDashboardHTML() {
    return `
<!DOCTYPE html>
<html>
<head>
    <title>Real-Time Test Monitor</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #0d1117;
            color: #c9d1d9;
            padding: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 2.5rem;
            background: linear-gradient(45deg, #58a6ff, #56d364);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-card {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }
        .metric-value {
            font-size: 2.5rem;
            font-weight: bold;
            margin: 10px 0;
        }
        .metric-label {
            color: #8b949e;
            font-size: 0.9rem;
        }
        .success { color: #56d364; }
        .error { color: #f85149; }
        .warning { color: #f0883e; }
        .console {
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 20px;
            height: 400px;
            overflow-y: auto;
            font-family: 'Monaco', 'Consolas', monospace;
            font-size: 0.9rem;
        }
        .console-line {
            margin: 2px 0;
            white-space: pre-wrap;
        }
        .test-pass { color: #56d364; }
        .test-fail { color: #f85149; }
        .test-skip { color: #8b949e; }
        .controls {
            margin-bottom: 20px;
            text-align: center;
        }
        button {
            background: #238636;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            font-size: 1rem;
            cursor: pointer;
            margin: 0 5px;
        }
        button:hover {
            background: #2ea043;
        }
        .flaky-tests {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
        }
        .flaky-test {
            display: flex;
            justify-content: space-between;
            padding: 10px;
            border-bottom: 1px solid #30363d;
        }
        .progress-bar {
            width: 100%;
            height: 4px;
            background: #30363d;
            border-radius: 2px;
            overflow: hidden;
            margin: 20px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #56d364, #58a6ff);
            transition: width 0.3s ease;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>⚡ Real-Time Test Monitor</h1>
        <p>Live test execution tracking and analysis</p>
    </div>
    
    <div class="container">
        <div class="controls">
            <button onclick="runTests()">▶️ Run All Tests</button>
            <button onclick="runTests('npm test -- --watch')">🔄 Watch Mode</button>
            <button onclick="clearConsole()">🗑️ Clear Console</button>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" id="progress" style="width: 0%"></div>
        </div>
        
        <div class="grid">
            <div class="metric-card">
                <div class="metric-label">Total Tests</div>
                <div class="metric-value" id="totalTests">0</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Passed</div>
                <div class="metric-value success" id="passedTests">0</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Failed</div>
                <div class="metric-value error" id="failedTests">0</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Pass Rate</div>
                <div class="metric-value" id="passRate">0%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Avg Duration</div>
                <div class="metric-value" id="avgDuration">0ms</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Slow Tests</div>
                <div class="metric-value warning" id="slowTests">0</div>
            </div>
        </div>
        
        <div class="console" id="console">
            <div class="console-line">Waiting for test execution...</div>
        </div>
        
        <div class="flaky-tests" id="flakyTests" style="display: none;">
            <h3>🎲 Flaky Tests Detected</h3>
            <div id="flakyTestsList"></div>
        </div>
    </div>
    
    <script>
        const ws = new WebSocket('ws://localhost:3334');
        let currentSession = null;
        
        ws.onopen = () => {
            console.log('Connected to test monitor');
            addConsoleMessage('✅ Connected to test monitor', 'success');
        };
        
        ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            handleMessage(message);
        };
        
        function handleMessage(message) {
            switch (message.type) {
                case 'init':
                    updateMetrics(message.data);
                    break;
                case 'output':
                    addConsoleMessage(message.data);
                    break;
                case 'error':
                    addConsoleMessage(message.data, 'error');
                    break;
                case 'test-result':
                    handleTestResult(message.data);
                    break;
                case 'complete':
                    handleComplete(message.data);
                    break;
                case 'slow-test':
                    addConsoleMessage(\`⚠️  Slow test: \${message.data.name} (\${message.data.duration}ms)\`, 'warning');
                    break;
                case 'flaky-test-detected':
                    addFlakyTest(message.data);
                    break;
            }
        }
        
        function updateMetrics(data) {
            document.getElementById('totalTests').textContent = data.totalTests;
            document.getElementById('passedTests').textContent = data.passedTests;
            document.getElementById('failedTests').textContent = data.failedTests;
            document.getElementById('passRate').textContent = data.passRate + '%';
            document.getElementById('avgDuration').textContent = data.avgDuration + 'ms';
            document.getElementById('slowTests').textContent = data.slowTests;
            
            // Update progress bar
            if (data.totalTests > 0) {
                const progress = (data.passedTests + data.failedTests) / data.totalTests * 100;
                document.getElementById('progress').style.width = progress + '%';
            }
            
            // Update pass rate color
            const passRateEl = document.getElementById('passRate');
            passRateEl.className = 'metric-value';
            if (data.passRate >= 90) passRateEl.classList.add('success');
            else if (data.passRate >= 70) passRateEl.classList.add('warning');
            else passRateEl.classList.add('error');
        }
        
        function handleTestResult(test) {
            const icon = test.status === 'passed' ? '✓' : '✕';
            const className = test.status === 'passed' ? 'test-pass' : 'test-fail';
            addConsoleMessage(\`\${icon} \${test.name} (\${test.duration}ms)\`, className);
            
            // Update metrics in real-time
            const totalEl = document.getElementById('totalTests');
            totalEl.textContent = parseInt(totalEl.textContent) + 1;
            
            if (test.status === 'passed') {
                const passedEl = document.getElementById('passedTests');
                passedEl.textContent = parseInt(passedEl.textContent) + 1;
            } else {
                const failedEl = document.getElementById('failedTests');
                failedEl.textContent = parseInt(failedEl.textContent) + 1;
            }
            
            updatePassRate();
        }
        
        function updatePassRate() {
            const total = parseInt(document.getElementById('totalTests').textContent);
            const passed = parseInt(document.getElementById('passedTests').textContent);
            if (total > 0) {
                const rate = Math.round((passed / total) * 100);
                document.getElementById('passRate').textContent = rate + '%';
            }
        }
        
        function handleComplete(data) {
            addConsoleMessage(\`\\n✅ Tests completed in \${data.duration}ms\`, 'success');
            addConsoleMessage(\`Summary: \${data.summary.passed} passed, \${data.summary.failed} failed\`);
        }
        
        function addConsoleMessage(message, className = '') {
            const console = document.getElementById('console');
            const line = document.createElement('div');
            line.className = 'console-line ' + className;
            line.textContent = message;
            console.appendChild(line);
            console.scrollTop = console.scrollHeight;
        }
        
        function addFlakyTest(data) {
            const container = document.getElementById('flakyTests');
            container.style.display = 'block';
            
            const list = document.getElementById('flakyTestsList');
            const item = document.createElement('div');
            item.className = 'flaky-test';
            item.innerHTML = \`
                <span>\${data.name}</span>
                <span>Flakiness: \${Math.round(data.stats.flakiness * 100)}%</span>
            \`;
            list.appendChild(item);
        }
        
        function runTests(command = 'npm test') {
            clearConsole();
            addConsoleMessage(\`🚀 Running: \${command}\`);
            ws.send(JSON.stringify({ type: 'run-test', command }));
        }
        
        function clearConsole() {
            document.getElementById('console').innerHTML = '';
        }
    </script>
</body>
</html>`;
  }
}

// Run if called directly
if (require.main === module) {
  const monitor = new RealTimeTestMonitor();
  monitor.start().catch(console.error);
}

module.exports = RealTimeTestMonitor;
EOF

chmod +x realtime/test-runner-monitor.js

echo -e "${BLUE}Creating test execution wrapper...${NC}"

# Test execution wrapper
cat > realtime/smart-test-runner.sh << 'EOF'
#!/bin/bash
# Smart test runner with real-time monitoring

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🧪 Smart Test Runner${NC}"
echo "===================="

# Parse arguments
COMMAND="npm test"
WATCH_MODE=false
COVERAGE=false
SPECIFIC_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -w|--watch)
            WATCH_MODE=true
            shift
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -f|--file)
            SPECIFIC_FILE="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

# Build command
if [ "$WATCH_MODE" = true ]; then
    COMMAND="$COMMAND -- --watch"
fi

if [ "$COVERAGE" = true ]; then
    COMMAND="$COMMAND -- --coverage"
fi

if [ -n "$SPECIFIC_FILE" ]; then
    COMMAND="$COMMAND $SPECIFIC_FILE"
fi

echo -e "${YELLOW}Command: $COMMAND${NC}"

# Start real-time monitor in background
if ! pgrep -f "test-runner-monitor.js" > /dev/null; then
    echo -e "${BLUE}Starting real-time monitor...${NC}"
    node realtime/test-runner-monitor.js &
    MONITOR_PID=$!
    sleep 2
fi

# Open dashboard
if command -v open >/dev/null 2>&1; then
    open http://localhost:3333
elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open http://localhost:3333
fi

echo -e "${GREEN}✅ Dashboard: http://localhost:3333${NC}"
echo ""

# Run tests through monitor
curl -X POST http://localhost:3333/run-test \
    -H "Content-Type: application/json" \
    -d "{\"command\": \"$COMMAND\"}" \
    2>/dev/null || true

# Keep running
echo "Press Ctrl+C to stop monitoring"
wait
EOF

chmod +x realtime/smart-test-runner.sh

echo -e "${BLUE}Creating package.json for real-time monitor...${NC}"

# Package.json
cat > realtime/package.json << 'EOF'
{
  "name": "real-time-test-monitor",
  "version": "1.0.0",
  "description": "Real-time test execution monitoring",
  "main": "test-runner-monitor.js",
  "scripts": {
    "start": "node test-runner-monitor.js",
    "test": "./smart-test-runner.sh",
    "test:watch": "./smart-test-runner.sh --watch",
    "test:coverage": "./smart-test-runner.sh --coverage"
  },
  "dependencies": {
    "ws": "^8.13.0"
  }
}
EOF

echo ""
echo -e "${GREEN}✅ Real-Time Test Monitor setup complete!${NC}"
echo ""
echo -e "${YELLOW}To use:${NC}"
echo "1. cd realtime && npm install"
echo "2. npm start (starts monitor)"
echo "3. Open http://localhost:3333"
echo ""
echo -e "${BLUE}Or use smart runner:${NC}"
echo "  ./realtime/smart-test-runner.sh"
echo "  ./realtime/smart-test-runner.sh --watch"
echo "  ./realtime/smart-test-runner.sh --coverage"