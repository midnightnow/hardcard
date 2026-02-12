#!/usr/bin/env node

/**
 * Generate a visual HTML report from the JSON test results
 */

const fs = require('fs');
const path = require('path');

// Read the latest test results
const reportPath = '/Users/studio/hardcard/enhanced_test_report.json';
const outputPath = '/Users/studio/hardcard/visual_report.html';

const testData = JSON.parse(fs.readFileSync(reportPath, 'utf8'));

const html = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HardCard Suite Vision Testing Report</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 700;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }
        .summary {
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .summary-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .summary-card h3 {
            margin: 0 0 10px 0;
            color: #2c3e50;
        }
        .summary-card .value {
            font-size: 2em;
            font-weight: bold;
            color: #27ae60;
        }
        .apps-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            padding: 30px;
        }
        .app-card {
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            border: 1px solid #e9ecef;
        }
        .app-header {
            padding: 20px;
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            color: white;
        }
        .app-header h3 {
            margin: 0;
            font-size: 1.3em;
        }
        .app-header .url {
            opacity: 0.9;
            font-size: 0.9em;
            margin-top: 5px;
        }
        .status-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            margin-top: 10px;
        }
        .status-online {
            background: #27ae60;
            color: white;
        }
        .status-offline {
            background: #e74c3c;
            color: white;
        }
        .app-details {
            padding: 20px;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #f1f3f4;
        }
        .metric:last-child {
            border-bottom: none;
        }
        .metric-label {
            font-weight: 500;
            color: #555;
        }
        .metric-value {
            color: #2c3e50;
        }
        .check-passed {
            color: #27ae60;
            font-weight: bold;
        }
        .check-failed {
            color: #e74c3c;
            font-weight: bold;
        }
        .recommendations {
            padding: 30px;
            background: #fff3cd;
            border-top: 1px solid #ffeaa7;
        }
        .recommendations h3 {
            margin: 0 0 15px 0;
            color: #d68910;
        }
        .recommendation {
            padding: 10px 15px;
            background: white;
            border-left: 4px solid #f39c12;
            margin-bottom: 10px;
            border-radius: 0 5px 5px 0;
        }
        .screenshot-info {
            background: #e8f5e8;
            padding: 15px;
            border-radius: 10px;
            margin-top: 15px;
            font-size: 0.9em;
            color: #2d5016;
        }
        .timestamp {
            text-align: center;
            padding: 20px;
            color: #6c757d;
            font-size: 0.9em;
            border-top: 1px solid #e9ecef;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 HardCard Suite Vision Testing Report</h1>
            <p>Automated testing with Playwright • ${new Date(testData.timestamp).toLocaleString()}</p>
        </div>

        <div class="summary">
            <h2>📊 Test Summary</h2>
            <div class="summary-grid">
                <div class="summary-card">
                    <h3>Total Applications</h3>
                    <div class="value">${testData.summary.total}</div>
                </div>
                <div class="summary-card">
                    <h3>Online</h3>
                    <div class="value" style="color: #27ae60">${testData.summary.online}</div>
                </div>
                <div class="summary-card">
                    <h3>Offline</h3>
                    <div class="value" style="color: #e74c3c">${testData.summary.offline}</div>
                </div>
                <div class="summary-card">
                    <h3>Errors</h3>
                    <div class="value" style="color: #f39c12">${testData.summary.errors}</div>
                </div>
            </div>
        </div>

        <div class="apps-grid">
            ${Object.entries(testData.applications).map(([name, app]) => `
                <div class="app-card">
                    <div class="app-header">
                        <h3>${app.name.replace(/_/g, ' ').toUpperCase()}</h3>
                        <div class="url">${app.url}</div>
                        <span class="status-badge status-${app.status}">
                            ${app.status.toUpperCase()}
                        </span>
                    </div>
                    <div class="app-details">
                        <div class="metric">
                            <span class="metric-label">Title</span>
                            <span class="metric-value">${app.title || 'N/A'}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Load Time</span>
                            <span class="metric-value">${app.load_time || 'N/A'}ms</span>
                        </div>
                        ${app.performance ? `
                        <div class="metric">
                            <span class="metric-label">First Paint</span>
                            <span class="metric-value">${app.performance.first_paint || 'N/A'}ms</span>
                        </div>
                        ` : ''}
                        
                        ${app.tests && app.tests.accessibility ? `
                        <h4 style="margin: 15px 0 10px 0; color: #2c3e50;">Accessibility Checks</h4>
                        ${Object.entries(app.tests.accessibility).map(([check, passed]) => `
                        <div class="metric">
                            <span class="metric-label">${check.replace(/_/g, ' ')}</span>
                            <span class="metric-value ${passed ? 'check-passed' : 'check-failed'}">
                                ${passed ? '✅ PASS' : '❌ FAIL'}
                            </span>
                        </div>
                        `).join('')}
                        ` : ''}

                        ${app.tests && app.tests.critical_elements ? `
                        <h4 style="margin: 15px 0 10px 0; color: #2c3e50;">Critical Elements</h4>
                        ${Object.entries(app.tests.critical_elements).map(([element, status]) => `
                        <div class="metric">
                            <span class="metric-label">${element}</span>
                            <span class="metric-value ${status === 'found' ? 'check-passed' : 'check-failed'}">
                                ${status === 'found' ? '✅ FOUND' : '❌ MISSING'}
                            </span>
                        </div>
                        `).join('')}
                        ` : ''}

                        ${app.screenshot ? `
                        <div class="screenshot-info">
                            📸 Screenshot captured: ${path.basename(app.screenshot)}
                        </div>
                        ` : ''}
                    </div>
                </div>
            `).join('')}
        </div>

        ${testData.recommendations && testData.recommendations.length > 0 ? `
        <div class="recommendations">
            <h3>💡 Recommendations</h3>
            ${testData.recommendations.map(rec => `
                <div class="recommendation">
                    <strong>${rec.priority}</strong> ${rec.message}
                </div>
            `).join('')}
        </div>
        ` : ''}

        <div class="timestamp">
            Generated at ${new Date().toLocaleString()} • Test Run ID: ${testData.test_run_id}
        </div>
    </div>
</body>
</html>
`;

fs.writeFileSync(outputPath, html);
console.log(`✅ Visual report generated: ${outputPath}`);
console.log(`🌐 Open in browser: file://${outputPath}`);