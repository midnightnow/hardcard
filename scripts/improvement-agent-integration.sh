#!/bin/bash
# HardCard Improvement Agent Integration
# Integrates improvement agents with the existing multi-agent worktree system

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🤖 HardCard Improvement Agent Integration${NC}"
echo "========================================"

# Function to assign improvement tasks to agents
assign_improvement_tasks() {
    echo -e "${YELLOW}📋 Assigning improvement tasks to agents...${NC}"
    
    # Get latest improvement report
    LATEST_REPORT=$(ls -t improvement_report_*.json 2>/dev/null | head -1)
    
    if [[ -z "$LATEST_REPORT" ]]; then
        echo -e "${YELLOW}⚠️ No improvement report found. Running analysis...${NC}"
        python scripts/improvement-agent-framework.py \
            --root HARDCARDSUITE/vetsorcery_extracted \
            --auto-fix \
            --output improvement_report_$(date +%Y%m%d_%H%M%S).json
        LATEST_REPORT=$(ls -t improvement_report_*.json | head -1)
    fi
    
    echo -e "${GREEN}✅ Using report: $LATEST_REPORT${NC}"
    
    # Extract critical files and assign to agents
    python3 <<EOF
import json
import os

with open('$LATEST_REPORT', 'r') as f:
    report = json.load(f)

# Assign tasks based on file type and issues
frontend_tasks = []
backend_tasks = []
security_tasks = []
test_tasks = []

for file_data in report['critical_files'][:50]:  # Top 50 critical files
    path = file_data['path']
    
    if 'frontend' in path and ('.tsx' in path or '.ts' in path):
        frontend_tasks.append(path)
    elif 'backend' in path and '.py' in path:
        backend_tasks.append(path)
    elif any(issue['type'].startswith('security_') for issue in file_data['issues']):
        security_tasks.append(path)
    elif 'test' in path.lower():
        test_tasks.append(path)

# Write task files for each agent
task_assignments = {
    'frontend-ai': frontend_tasks,
    'backend-ai': backend_tasks,
    'security-ai': security_tasks,
    'testing-ai': test_tasks
}

for agent, tasks in task_assignments.items():
    if tasks:
        worktree_path = f'$PROJECT_ROOT/../hardcard-{agent}'
        if os.path.exists(worktree_path):
            task_file = os.path.join(worktree_path, 'IMPROVEMENT_TASKS.md')
            with open(task_file, 'w') as f:
                f.write(f"# Improvement Tasks for {agent}\n\n")
                f.write(f"Generated from: {os.path.basename('$LATEST_REPORT')}\n\n")
                f.write("## Critical Files to Fix\n\n")
                for i, task in enumerate(tasks[:10], 1):  # Top 10 per agent
                    f.write(f"{i}. {task}\n")
            print(f"✅ Assigned {len(tasks[:10])} tasks to {agent}")

print("\n📊 Task Assignment Summary:")
print(f"- Frontend: {len(frontend_tasks)} critical files")
print(f"- Backend: {len(backend_tasks)} critical files")
print(f"- Security: {len(security_tasks)} critical files")
print(f"- Testing: {len(test_tasks)} critical files")
EOF
}

# Function to create improvement dashboard
create_improvement_dashboard() {
    echo -e "${YELLOW}📊 Creating improvement dashboard...${NC}"
    
    cat > "$PROJECT_ROOT/IMPROVEMENT_DASHBOARD.md" <<EOF
# HardCard Improvement Dashboard
Generated: $(date)

## 📈 Overall Progress

### Codebase Statistics
$(python scripts/page-completion-tracker.py | grep -E "Total Files|Average Completion|Production Ready|Critical Issues")

### Recent Improvements
- Auto-fixes applied: $(grep -c "Fixed:" improvement_report_*.md 2>/dev/null || echo "0")
- Files analyzed: $(grep "Total Files Analyzed" improvement_report_*.md 2>/dev/null | tail -1 | awk '{print $5}')
- Critical issues: $(grep "Critical Issues:" improvement_report_*.md 2>/dev/null | tail -1 | awk '{print $3}')

## 🤖 Agent Assignments

### Frontend Agent
- Worktree: \`hardcard-frontend-ai\`
- Branch: \`ai/frontend-specialist\`
- Tasks: See \`IMPROVEMENT_TASKS.md\` in worktree

### Backend Agent  
- Worktree: \`hardcard-backend-ai\`
- Branch: \`ai/backend-specialist\`
- Tasks: See \`IMPROVEMENT_TASKS.md\` in worktree

### Security Agent
- Worktree: \`hardcard-security-ai\`
- Branch: \`ai/security-audit\`
- Tasks: See \`IMPROVEMENT_TASKS.md\` in worktree

### Testing Agent
- Worktree: \`hardcard-testing-ai\`
- Branch: \`ai/testing-specialist\`
- Tasks: See \`IMPROVEMENT_TASKS.md\` in worktree

## 🔧 Improvement Commands

\`\`\`bash
# Run full analysis with auto-fix
./scripts/improvement-agent-integration.sh analyze

# Assign tasks to agents
./scripts/improvement-agent-integration.sh assign

# Monitor improvements
./scripts/improvement-agent-integration.sh monitor

# Generate report
./scripts/improvement-agent-integration.sh report
\`\`\`

## 📋 Next Steps

1. Each agent should check their \`IMPROVEMENT_TASKS.md\`
2. Focus on critical security issues first
3. Run tests after each fix
4. Update completion scores
5. Commit improvements to agent branches

EOF
    
    echo -e "${GREEN}✅ Dashboard created: IMPROVEMENT_DASHBOARD.md${NC}"
}

# Function to monitor improvements
monitor_improvements() {
    echo -e "${YELLOW}👀 Starting improvement monitor...${NC}"
    python scripts/improvement-agent-monitor.py
}

# Function to generate comprehensive report
generate_report() {
    echo -e "${YELLOW}📊 Generating comprehensive improvement report...${NC}"
    
    # Combine all agent work
    REPORT_FILE="IMPROVEMENT_REPORT_$(date +%Y%m%d_%H%M%S).md"
    
    cat > "$REPORT_FILE" <<EOF
# HardCard Comprehensive Improvement Report
Generated: $(date)

## Executive Summary

EOF
    
    # Add statistics from latest analysis
    if [[ -f improvement_report_*.md ]]; then
        latest_md=$(ls -t improvement_report_*.md | head -1)
        grep -A 20 "Summary Statistics" "$latest_md" >> "$REPORT_FILE"
    fi
    
    # Add agent progress
    echo -e "\n## Agent Progress\n" >> "$REPORT_FILE"
    
    for agent in frontend backend security testing; do
        worktree="../hardcard-${agent}-ai"
        if [[ -d "$worktree" ]]; then
            echo "### $agent Agent" >> "$REPORT_FILE"
            echo "\`\`\`" >> "$REPORT_FILE"
            (cd "$worktree" && git log --oneline -10) >> "$REPORT_FILE" 2>/dev/null || echo "No commits yet"
            echo "\`\`\`" >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
        fi
    done
    
    echo -e "${GREEN}✅ Report saved: $REPORT_FILE${NC}"
}

# Main command handler
case "${1:-help}" in
    analyze)
        echo -e "${BLUE}🔍 Running full codebase analysis...${NC}"
        python scripts/improvement-agent-framework.py \
            --root HARDCARDSUITE/vetsorcery_extracted \
            --auto-fix \
            --output improvement_report_$(date +%Y%m%d_%H%M%S).json
        ;;
    
    assign)
        assign_improvement_tasks
        create_improvement_dashboard
        ;;
    
    monitor)
        monitor_improvements
        ;;
    
    report)
        generate_report
        ;;
    
    full)
        echo -e "${BLUE}🚀 Running full improvement workflow...${NC}"
        $0 analyze
        $0 assign
        create_improvement_dashboard
        echo -e "${GREEN}✅ Full workflow complete!${NC}"
        echo -e "${YELLOW}💡 Run '$0 monitor' to start real-time monitoring${NC}"
        ;;
    
    help|*)
        echo "Usage: $0 {analyze|assign|monitor|report|full|help}"
        echo ""
        echo "Commands:"
        echo "  analyze  - Run improvement analysis on codebase"
        echo "  assign   - Assign improvement tasks to agents"
        echo "  monitor  - Start real-time improvement monitoring"
        echo "  report   - Generate comprehensive report"
        echo "  full     - Run complete improvement workflow"
        echo "  help     - Show this help message"
        ;;
esac