#!/bin/bash

echo "🔍 Running Detailed VetSorcery Analysis with Gemini..."
echo "=================================================="

# Create analysis directory
mkdir -p gemini-analysis-results

# 1. Code Quality Analysis
echo -e "\n📊 Analyzing Code Quality..."
cat > gemini-analysis-results/code-quality-prompt.txt << 'EOF'
Analyze the code quality of vetsorcery-complete.html:
1. Identify code duplication
2. Find performance bottlenecks
3. Check JavaScript best practices
4. Review CSS optimization opportunities
5. Assess HTML semantic structure
6. Find memory leaks or inefficient patterns
7. Check for unused code
8. Review error handling
EOF

cat HARDCARDSUITE/vetsorcery_extracted/frontend/vetsorcery-complete.html | gemini -p "$(cat gemini-analysis-results/code-quality-prompt.txt)" > gemini-analysis-results/code-quality-report.md

# 2. Security Analysis
echo -e "\n🔒 Analyzing Security..."
cat > gemini-analysis-results/security-prompt.txt << 'EOF'
Perform a security analysis of vetsorcery-complete.html:
1. Check for XSS vulnerabilities
2. Review data validation practices
3. Assess encryption implementation
4. Check for hardcoded secrets
5. Review authentication patterns
6. Identify HIPAA compliance gaps
7. Check for injection vulnerabilities
8. Review session management
EOF

cat HARDCARDSUITE/vetsorcery_extracted/frontend/vetsorcery-complete.html | gemini -p "$(cat gemini-analysis-results/security-prompt.txt)" > gemini-analysis-results/security-report.md

# 3. Performance Analysis
echo -e "\n⚡ Analyzing Performance..."
cat > gemini-analysis-results/performance-prompt.txt << 'EOF'
Analyze performance issues in vetsorcery-complete.html:
1. Identify render-blocking resources
2. Check for unnecessary DOM manipulation
3. Review animation performance
4. Find memory-intensive operations
5. Check for inefficient event handlers
6. Review image optimization needs
7. Identify bundle size issues
8. Check for unnecessary re-renders
EOF

cat HARDCARDSUITE/vetsorcery_extracted/frontend/vetsorcery-complete.html | gemini -p "$(cat gemini-analysis-results/performance-prompt.txt)" > gemini-analysis-results/performance-report.md

# 4. Feature Gap Analysis
echo -e "\n🚀 Analyzing Feature Gaps..."
cat > gemini-analysis-results/feature-gaps-prompt.txt << 'EOF'
Identify missing features for a complete veterinary practice management system:
1. What critical features are missing?
2. Which integrations need to be added?
3. What reporting capabilities are lacking?
4. Which workflows are incomplete?
5. What mobile features are missing?
6. Which accessibility features need improvement?
7. What automation opportunities exist?
8. Which compliance features are missing?
EOF

cat HARDCARDSUITE/vetsorcery_extracted/frontend/vetsorcery-complete.html | gemini -p "$(cat gemini-analysis-results/feature-gaps-prompt.txt)" > gemini-analysis-results/feature-gaps-report.md

# 5. UI/UX Analysis
echo -e "\n🎨 Analyzing UI/UX..."
cat > gemini-analysis-results/ui-ux-prompt.txt << 'EOF'
Analyze the UI/UX of vetsorcery-complete.html:
1. Review consistency of design patterns
2. Check accessibility compliance
3. Assess mobile responsiveness
4. Review navigation patterns
5. Check form usability
6. Assess visual hierarchy
7. Review error messaging
8. Check loading states
EOF

cat HARDCARDSUITE/vetsorcery_extracted/frontend/vetsorcery-complete.html | gemini -p "$(cat gemini-analysis-results/ui-ux-prompt.txt)" > gemini-analysis-results/ui-ux-report.md

# Create summary report
echo -e "\n📝 Creating Summary Report..."
cat > gemini-analysis-results/create-summary.txt << 'EOF'
Based on all the analysis reports, create a prioritized action plan with:
1. Top 5 critical fixes needed immediately
2. Quick wins that can be implemented in 1-2 days
3. Medium-term improvements (1-2 weeks)
4. Long-term architectural changes
5. Estimated effort for each item
6. Dependencies between items
EOF

# Combine all reports for summary
cat gemini-analysis-results/*.md | gemini -p "$(cat gemini-analysis-results/create-summary.txt)" > gemini-analysis-results/SUMMARY_REPORT.md

echo -e "\n✅ Analysis Complete!"
echo "Results saved in: gemini-analysis-results/"
echo ""
echo "Reports generated:"
ls -la gemini-analysis-results/*.md | awk '{print "  - " $9}'