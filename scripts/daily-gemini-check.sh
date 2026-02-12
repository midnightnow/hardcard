#!/bin/bash
# Daily Gemini Health Check and Analysis

PROJECT_ROOT="/Users/studio/00 Constellation/hardcard"
REPORT_DIR="$PROJECT_ROOT/reports/gemini"
DATE=$(date '+%Y-%m-%d')

mkdir -p "$REPORT_DIR"

echo "🧠 Starting daily Gemini analysis..."

# Code quality analysis
echo "📊 Running code quality analysis..."
gemini analyze --directory src/ --output "$REPORT_DIR/quality-$DATE.json" --threshold 85

# Security scan
echo "🔒 Running security scan..."
gemini security-scan --directory src/ --severity high --output "$REPORT_DIR/security-$DATE.json"

# Performance analysis
echo "⚡ Running performance analysis..."
gemini performance --directory src/ --output "$REPORT_DIR/performance-$DATE.json"

# Documentation check
echo "📚 Checking documentation coverage..."
gemini docs-coverage --directory src/ --output "$REPORT_DIR/docs-coverage-$DATE.json"

echo "✅ Daily Gemini analysis complete. Reports saved to $REPORT_DIR"
