#!/bin/bash

echo "🔍 VetSorcery Quick Analysis with Gemini"
echo "========================================"

# Create results directory
mkdir -p gemini-results

# Quick comprehensive analysis
echo -e "\n📋 Running Comprehensive Analysis..."

cat << 'EOF' > gemini-results/comprehensive-prompt.txt
Analyze the VetSorcery veterinary management system and provide:

1. TOP 5 CRITICAL ISSUES:
   - Security vulnerabilities
   - Performance problems
   - Missing critical features
   - Architecture flaws
   - Compliance gaps

2. QUICK WINS (can fix in 1 day):
   - Simple improvements
   - Easy optimizations
   - Quick bug fixes

3. RECOMMENDED NEXT STEPS:
   - Priority order
   - Effort estimates
   - Dependencies

Keep the analysis concise and actionable.
EOF

# Run analysis
head -5000 HARDCARDSUITE/vetsorcery_extracted/frontend/vetsorcery-complete.html | gemini -p "$(cat gemini-results/comprehensive-prompt.txt)" > gemini-results/quick-analysis.md

echo -e "\n✅ Analysis Complete!"
echo "Report saved to: gemini-results/quick-analysis.md"

# Display the report
echo -e "\n📄 Analysis Report:"
echo "=================="
cat gemini-results/quick-analysis.md