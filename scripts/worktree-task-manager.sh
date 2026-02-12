#!/bin/bash
# 🤖 Worktree Task Manager for HardCard Multi-Agent System
# Manages task assignments and completion tracking across AI agent worktrees

set -e

PROJECT_ROOT="/Users/studio/hardcard"
TASK_FILE="$PROJECT_ROOT/AI_AGENT_TASKS.md"
STATUS_DIR="$PROJECT_ROOT/agent-status"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Emojis for better UX
ROBOT="🤖"
CHECK="✅"
WARNING="⚠️"
FIRE="🔥"
TARGET="🎯"
CHART="📊"

# Ensure status directory exists
mkdir -p "$STATUS_DIR"

show_help() {
    echo -e "${BLUE}${ROBOT} Worktree Task Manager${NC}"
    echo "=================================="
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "COMMANDS:"
    echo "  analyze          - Run page completion analysis"
    echo "  assign           - Assign tasks to AI agents"
    echo "  status           - Show all agent statuses"
    echo "  agent <name>     - Show specific agent status"
    echo "  update <agent>   - Update agent task progress"
    echo "  dashboard        - Show completion dashboard"
    echo "  critical         - Show critical issues only"
    echo "  production       - Show production-ready pages"
    echo "  help             - Show this help"
    echo ""
    echo "AGENT NAMES:"
    echo "  frontend-ai, backend-ai, testing-ai, docs-ai, security-ai"
    echo ""
    echo "EXAMPLES:"
    echo "  $0 analyze                    # Run completion analysis"
    echo "  $0 assign frontend-ai         # Assign tasks to frontend agent"
    echo "  $0 status                     # Show all agent statuses"
    echo "  $0 agent frontend-ai          # Show frontend agent details"
    echo "  $0 dashboard                  # Show completion dashboard"
}

run_analysis() {
    echo -e "${BLUE}${CHART} Running Page Completion Analysis...${NC}"
    echo ""
    
    if ! python3 "$PROJECT_ROOT/scripts/page-completion-tracker.py" --output "$STATUS_DIR/completion-report.json"; then
        echo -e "${RED}${WARNING} Analysis failed!${NC}"
        exit 1
    fi
    
    echo ""
    echo -e "${GREEN}${CHECK} Analysis complete! Report saved to $STATUS_DIR/completion-report.json${NC}"
}

assign_tasks() {
    local agent=$1
    
    if [[ -z "$agent" ]]; then
        echo -e "${YELLOW}${WARNING} Assigning tasks to all agents...${NC}"
        python3 "$PROJECT_ROOT/scripts/page-completion-tracker.py" --assignments > "$STATUS_DIR/all-assignments.txt"
        echo -e "${GREEN}${CHECK} Task assignments saved to $STATUS_DIR/all-assignments.txt${NC}"
        return
    fi
    
    echo -e "${BLUE}${TARGET} Assigning tasks to $agent...${NC}"
    
    # Generate assignments and filter for specific agent
    local agent_upper=$(echo "$agent" | tr '[:lower:]' '[:upper:]')
    python3 "$PROJECT_ROOT/scripts/page-completion-tracker.py" --assignments | \
    awk "/^${agent_upper}:/{flag=1; next} /^[A-Z-]+:/{flag=0} flag" > "$STATUS_DIR/${agent}-tasks.txt"
    
    # Update agent's STATUS.md file
    local agent_dir="$PROJECT_ROOT/../hardcard-${agent}"
    if [[ -d "$agent_dir" ]]; then
        echo -e "${PURPLE}${ROBOT} Updating $agent_dir/STATUS.md...${NC}"
        
        local agent_title=$(echo "$agent" | tr '[:lower:]' '[:upper:]')
        cat > "$agent_dir/STATUS.md" << EOF
# ${agent_title} Status Report
**Last Updated:** $(date)
**Completion Analysis:** $(date)

## 🎯 Current Priority Tasks

$(cat "$STATUS_DIR/${agent}-tasks.txt" | head -10)

## 📊 Task Summary
- **Critical Tasks:** $(grep -c "🔴 URGENT" "$STATUS_DIR/${agent}-tasks.txt" 2>/dev/null || echo "0")
- **High Priority:** $(grep -c "🟠 HIGH" "$STATUS_DIR/${agent}-tasks.txt" 2>/dev/null || echo "0")
- **Medium Priority:** $(grep -c "🟡 MEDIUM" "$STATUS_DIR/${agent}-tasks.txt" 2>/dev/null || echo "0")
- **Testing Tasks:** $(grep -c "🧪" "$STATUS_DIR/${agent}-tasks.txt" 2>/dev/null || echo "0")
- **Security Issues:** $(grep -c "🚨" "$STATUS_DIR/${agent}-tasks.txt" 2>/dev/null || echo "0")

## 📋 Full Task List
See: $STATUS_DIR/${agent}-tasks.txt

## 🔄 Progress Updates
<!-- Update this section as you complete tasks -->

## 🚫 Blockers
<!-- List any blockers or dependencies -->

## 📝 Notes
<!-- Add any additional notes or observations -->
EOF
        
        echo -e "${GREEN}${CHECK} Updated $agent STATUS.md with $(wc -l < "$STATUS_DIR/${agent}-tasks.txt") tasks${NC}"
    else
        echo -e "${YELLOW}${WARNING} Agent directory $agent_dir not found${NC}"
    fi
}

show_status() {
    echo -e "${BLUE}${CHART} Agent Status Dashboard${NC}"
    echo "=================================="
    echo ""
    
    # Run completion analysis first
    if [[ ! -f "$STATUS_DIR/completion-report.json" ]] || [[ $(find "$STATUS_DIR/completion-report.json" -mmin +60) ]]; then
        echo -e "${YELLOW}${WARNING} Running fresh analysis (report is >1 hour old)...${NC}"
        run_analysis > /dev/null
    fi
    
    # Show overall project status
    local total_files=$(jq -r '.total_files' "$STATUS_DIR/completion-report.json" 2>/dev/null || echo "unknown")
    local avg_completion=$(jq -r '.summary.average_completion' "$STATUS_DIR/completion-report.json" 2>/dev/null || echo "unknown")
    local prod_ready=$(jq -r '.summary.ready_for_production' "$STATUS_DIR/completion-report.json" 2>/dev/null || echo "unknown")
    local critical_issues=$(jq -r '.summary.critical_issues | length' "$STATUS_DIR/completion-report.json" 2>/dev/null || echo "unknown")
    
    echo -e "${PURPLE}📊 PROJECT OVERVIEW${NC}"
    echo -e "Total Files: ${CYAN}$total_files${NC}"
    echo -e "Average Completion: ${CYAN}$avg_completion%${NC}"
    echo -e "Production Ready: ${CYAN}$prod_ready${NC}"
    echo -e "Critical Issues: ${RED}$critical_issues${NC}"
    echo ""
    
    # Show each agent status
    for agent in frontend-ai backend-ai testing-ai docs-ai security-ai; do
        local agent_dir="$PROJECT_ROOT/../hardcard-${agent}"
        
        local agent_display=$(echo "$agent" | tr '[:lower:]' '[:upper:]')
        echo -e "${BLUE}${ROBOT} ${agent_display}${NC}"
        echo "-------------------"
        
        if [[ -d "$agent_dir" ]]; then
            cd "$agent_dir"
            
            # Git status
            local branch=$(git branch --show-current 2>/dev/null || echo "unknown")
            local changes=$(git status --porcelain 2>/dev/null | wc -l)
            local last_commit=$(git log -1 --format="%h %s" 2>/dev/null || echo "No commits")
            
            echo -e "Branch: ${CYAN}$branch${NC}"
            echo -e "Uncommitted Changes: ${YELLOW}$changes${NC}"
            echo -e "Last Commit: ${CYAN}$last_commit${NC}"
            
            # Task summary from STATUS.md
            if [[ -f "STATUS.md" ]]; then
                local critical_tasks=$(grep -c "🔴 URGENT" "STATUS.md" 2>/dev/null || echo "0")
                local high_tasks=$(grep -c "🟠 HIGH" "STATUS.md" 2>/dev/null || echo "0")
                local medium_tasks=$(grep -c "🟡 MEDIUM" "STATUS.md" 2>/dev/null || echo "0")
                
                echo -e "Critical Tasks: ${RED}$critical_tasks${NC}"
                echo -e "High Priority: ${YELLOW}$high_tasks${NC}"
                echo -e "Medium Priority: ${GREEN}$medium_tasks${NC}"
            else
                echo -e "${YELLOW}No STATUS.md found${NC}"
            fi
            
            cd "$PROJECT_ROOT"
        else
            echo -e "${RED}Agent directory not found${NC}"
        fi
        
        echo ""
    done
}

show_agent_details() {
    local agent=$1
    
    if [[ -z "$agent" ]]; then
        echo -e "${RED}${WARNING} Please specify an agent name${NC}"
        exit 1
    fi
    
    local agent_dir="$PROJECT_ROOT/../hardcard-${agent}"
    
    local agent_display=$(echo "$agent" | tr '[:lower:]' '[:upper:]')
    echo -e "${BLUE}${ROBOT} ${agent_display} Detailed Status${NC}"
    echo "=================================="
    echo ""
    
    if [[ ! -d "$agent_dir" ]]; then
        echo -e "${RED}${WARNING} Agent directory $agent_dir not found${NC}"
        exit 1
    fi
    
    cd "$agent_dir"
    
    # Git information
    echo -e "${PURPLE}🔧 Git Status${NC}"
    echo "Branch: $(git branch --show-current)"
    echo "Last Commit: $(git log -1 --format='%h - %s (%cr)')"
    echo "Changes: $(git status --porcelain | wc -l) files modified"
    echo ""
    
    # Show STATUS.md content
    if [[ -f "STATUS.md" ]]; then
        echo -e "${PURPLE}📋 Current Tasks${NC}"
        cat "STATUS.md"
    else
        echo -e "${YELLOW}${WARNING} No STATUS.md found. Run 'assign $agent' to create one.${NC}"
    fi
    
    cd "$PROJECT_ROOT"
}

show_dashboard() {
    echo -e "${BLUE}${CHART} VetSorcery Completion Dashboard${NC}"
    echo "===================================="
    echo ""
    
    # Run fresh analysis
    run_analysis > /dev/null
    
    # Show completion levels with visual bars
    echo -e "${PURPLE}📊 COMPLETION LEVELS${NC}"
    
    local complete=$(jq -r '.summary.completion_levels.COMPLETE' "$STATUS_DIR/completion-report.json")
    local mostly=$(jq -r '.summary.completion_levels.MOSTLY_COMPLETE' "$STATUS_DIR/completion-report.json")
    local partial=$(jq -r '.summary.completion_levels.PARTIALLY_COMPLETE' "$STATUS_DIR/completion-report.json")
    local basic=$(jq -r '.summary.completion_levels.BASIC_STRUCTURE' "$STATUS_DIR/completion-report.json")
    local placeholder=$(jq -r '.summary.completion_levels.PLACEHOLDER' "$STATUS_DIR/completion-report.json")
    
    echo -e "${GREEN}✅ Complete (90-100%):        $complete${NC}"
    echo -e "${CYAN}🟢 Mostly Complete (75-89%):  $mostly${NC}"
    echo -e "${YELLOW}🟡 Partially Complete (50-74%): $partial${NC}"
    echo -e "${YELLOW}🟠 Basic Structure (25-49%):  $basic${NC}"
    echo -e "${RED}🔴 Placeholder (0-24%):       $placeholder${NC}"
    echo ""
    
    # Show critical issues
    local critical_count=$(jq -r '.summary.critical_issues | length' "$STATUS_DIR/completion-report.json")
    if [[ "$critical_count" -gt 0 ]]; then
        echo -e "${RED}🚨 CRITICAL ISSUES ($critical_count)${NC}"
        jq -r '.summary.critical_issues[] | "  • \(.file): \(.issue)"' "$STATUS_DIR/completion-report.json"
        echo ""
    fi
    
    # Show lowest completion pages
    echo -e "${RED}🔴 PAGES NEEDING IMMEDIATE ATTENTION${NC}"
    python3 "$PROJECT_ROOT/scripts/page-completion-tracker.py" | grep "🔴" | head -5
    echo ""
    
    echo -e "${GREEN}${CHECK} Use 'assign' command to distribute tasks to agents${NC}"
}

show_critical() {
    echo -e "${RED}🚨 Critical Issues Report${NC}"
    echo "========================="
    echo ""
    
    if [[ ! -f "$STATUS_DIR/completion-report.json" ]]; then
        run_analysis > /dev/null
    fi
    
    # Security issues
    local security_count=$(jq -r '.summary.critical_issues | length' "$STATUS_DIR/completion-report.json")
    if [[ "$security_count" -gt 0 ]]; then
        echo -e "${RED}🔐 SECURITY ISSUES ($security_count)${NC}"
        jq -r '.summary.critical_issues[] | "  • \(.file): \(.issue)"' "$STATUS_DIR/completion-report.json"
        echo ""
    fi
    
    # Placeholder pages
    echo -e "${RED}📄 PLACEHOLDER PAGES${NC}"
    python3 "$PROJECT_ROOT/scripts/page-completion-tracker.py" | grep "  •  0%" | head -10
    echo ""
    
    # Pages with lowest completion
    echo -e "${YELLOW}📉 LOWEST COMPLETION PAGES${NC}"
    python3 "$PROJECT_ROOT/scripts/page-completion-tracker.py" | grep -E "  • [0-9][0-9]?%" | head -10
}

show_production() {
    echo -e "${GREEN}🚀 Production-Ready Pages${NC}"
    echo "=========================="
    echo ""
    
    if [[ ! -f "$STATUS_DIR/completion-report.json" ]]; then
        run_analysis > /dev/null
    fi
    
    echo -e "${GREEN}✅ COMPLETE PAGES (90-100%)${NC}"
    python3 "$PROJECT_ROOT/scripts/page-completion-tracker.py" | grep -E "  • (9[0-9]|100)%" | head -15
    echo ""
    
    echo -e "${CYAN}🟢 MOSTLY COMPLETE PAGES (75-89%)${NC}"
    python3 "$PROJECT_ROOT/scripts/page-completion-tracker.py" | grep -E "  • [78][0-9]%" | head -10
    echo ""
    
    local total_ready=$(jq -r '.summary.ready_for_production' "$STATUS_DIR/completion-report.json")
    local total_files=$(jq -r '.total_files' "$STATUS_DIR/completion-report.json")
    local percentage=$(( total_ready * 100 / total_files ))
    
    echo -e "${GREEN}📊 PRODUCTION READINESS: $total_ready/$total_files ($percentage%)${NC}"
}

# Main command dispatch
case "${1:-help}" in
    "analyze")
        run_analysis
        ;;
    "assign")
        assign_tasks "$2"
        ;;
    "status")
        show_status
        ;;
    "agent")
        show_agent_details "$2"
        ;;
    "update")
        echo -e "${BLUE}${TARGET} Update feature coming soon...${NC}"
        echo "For now, manually edit the STATUS.md file in the agent's worktree."
        ;;
    "dashboard")
        show_dashboard
        ;;
    "critical")
        show_critical
        ;;
    "production")
        show_production
        ;;
    "help"|*)
        show_help
        ;;
esac