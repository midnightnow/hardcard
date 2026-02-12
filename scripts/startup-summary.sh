#!/bin/bash
# Startup Summary - Shows comprehensive status of all best practices and integrations

PROJECT_ROOT="/Users/studio/hardcard"

# Colors and emojis
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'
ROCKET="🚀"
CHECK="✅"
BRAIN="🧠"
SHIELD="🛡️"
GEAR="⚙️"

echo -e "${ROCKET} ${BLUE}HardCard Multi-Agent System - Startup Summary${NC}"
echo "=================================================================="
echo "📅 $(date)"
echo ""

# Claude Code Status
echo -e "${BLUE}🤖 CLAUDE CODE STATUS${NC}"
echo "--------------------"

if [ -f "$PROJECT_ROOT/CLAUDE.md" ]; then
    echo -e "${CHECK} CLAUDE.md configuration: ${GREEN}Active${NC}"
else
    echo -e "❌ CLAUDE.md configuration: ${RED}Missing${NC}"
fi

if [ -f "$PROJECT_ROOT/.claude/settings.json" ]; then
    echo -e "${CHECK} Claude settings: ${GREEN}Configured${NC}"
    tools_count=$(jq -r '.allowedTools | length' "$PROJECT_ROOT/.claude/settings.json" 2>/dev/null || echo "0")
    echo -e "   📋 Pre-approved tools: ${tools_count}"
else
    echo -e "❌ Claude settings: ${RED}Missing${NC}"
fi

if [ -d "$PROJECT_ROOT/.claude/commands" ]; then
    commands_count=$(ls "$PROJECT_ROOT/.claude/commands"/*.md 2>/dev/null | wc -l)
    echo -e "${CHECK} Custom slash commands: ${GREEN}${commands_count} available${NC}"
else
    echo -e "❌ Custom slash commands: ${RED}Not configured${NC}"
fi

if [ -f "$PROJECT_ROOT/.mcp.json" ]; then
    mcp_servers=$(jq -r '.mcpServers | keys | length' "$PROJECT_ROOT/.mcp.json" 2>/dev/null || echo "0")
    echo -e "${CHECK} MCP servers: ${GREEN}${mcp_servers} configured${NC}"
else
    echo -e "❌ MCP servers: ${RED}Not configured${NC}"
fi

echo ""

# Gemini CLI Status
echo -e "${BLUE}🧠 GEMINI CLI STATUS${NC}"
echo "---------------------"

if command -v gemini &> /dev/null; then
    echo -e "${CHECK} Gemini CLI: ${GREEN}Installed${NC} ($(gemini --version 2>/dev/null || echo 'Unknown version'))"
else
    echo -e "❌ Gemini CLI: ${RED}Not installed${NC}"
fi

if [ -f "$PROJECT_ROOT/gemini.yaml" ]; then
    echo -e "${CHECK} Gemini configuration: ${GREEN}Active${NC}"
    gemini_agents=$(yq eval '.agents | keys | length' "$PROJECT_ROOT/gemini.yaml" 2>/dev/null || echo "0")
    echo -e "   🤖 Configured agents: ${gemini_agents}"
else
    echo -e "❌ Gemini configuration: ${RED}Missing${NC}"
fi

if [ -f "$PROJECT_ROOT/.claude/gemini-integration.json" ]; then
    echo -e "${CHECK} Claude-Gemini integration: ${GREEN}Configured${NC}"
else
    echo -e "❌ Claude-Gemini integration: ${RED}Not configured${NC}"
fi

gemini_scripts=$(ls "$PROJECT_ROOT/scripts/gemini-"*.sh 2>/dev/null | wc -l)
echo -e "${CHECK} Gemini automation scripts: ${GREEN}${gemini_scripts} available${NC}"

echo ""

# MOEX Coordinator Status
echo -e "${BLUE}🔄 MOEX COORDINATOR STATUS${NC}"
echo "---------------------------"

if [ -f "$PROJECT_ROOT/moex-config.yaml" ]; then
    echo -e "${CHECK} MOEX configuration: ${GREEN}Active${NC}"
else
    echo -e "❌ MOEX configuration: ${RED}Missing${NC}"
fi

if [ -f "$PROJECT_ROOT/scripts/moex-coordinator.sh" ]; then
    echo -e "${CHECK} MOEX coordinator: ${GREEN}Available${NC}"
else
    echo -e "❌ MOEX coordinator: ${RED}Missing${NC}"
fi

if [ -d "$PROJECT_ROOT/moex-workspace" ]; then
    echo -e "${CHECK} MOEX workspace: ${GREEN}Initialized${NC}"
    
    # Check coordination files
    if [ -f "$PROJECT_ROOT/moex-workspace/claude-status.json" ]; then
        claude_status=$(jq -r '.status' "$PROJECT_ROOT/moex-workspace/claude-status.json" 2>/dev/null || echo "unknown")
        echo -e "   🤖 Claude status: ${claude_status}"
    fi
    
    if [ -f "$PROJECT_ROOT/moex-workspace/gemini-status.json" ]; then
        gemini_status=$(jq -r '.status' "$PROJECT_ROOT/moex-workspace/gemini-status.json" 2>/dev/null || echo "unknown")
        echo -e "   🧠 Gemini status: ${gemini_status}"
    fi
else
    echo -e "❌ MOEX workspace: ${RED}Not initialized${NC}"
fi

echo ""

# Health Monitoring Status
echo -e "${BLUE}🏥 HEALTH MONITORING STATUS${NC}"
echo "----------------------------"

monitoring_scripts=(
    "comprehensive-health-dashboard.py"
    "automated-stability-monitor.py"
    "enhanced-resilience-system.py"
    "fail-safe-deployment-system.py"
    "resilient-error-recovery.py"
)

for script in "${monitoring_scripts[@]}"; do
    if [ -f "$PROJECT_ROOT/scripts/$script" ]; then
        echo -e "${CHECK} ${script}: ${GREEN}Available${NC}"
    else
        echo -e "❌ ${script}: ${RED}Missing${NC}"
    fi
done

# Check if monitoring is running
dashboard_running=$(pgrep -f "comprehensive-health-dashboard" || echo "")
if [ -n "$dashboard_running" ]; then
    echo -e "${CHECK} Health dashboard: ${GREEN}Running (PID: $dashboard_running)${NC}"
else
    echo -e "⏸️ Health dashboard: ${YELLOW}Not running${NC}"
fi

echo ""

# Quality Gates Status
echo -e "${BLUE}🛡️ QUALITY GATES STATUS${NC}"
echo "------------------------"

if [ -f "$PROJECT_ROOT/.git/hooks/pre-commit" ]; then
    echo -e "${CHECK} Pre-commit hooks: ${GREEN}Installed${NC}"
else
    echo -e "❌ Pre-commit hooks: ${RED}Not installed${NC}"
fi

if [ -f "$PROJECT_ROOT/scripts/quality-gates-enforcer.sh" ]; then
    echo -e "${CHECK} Quality gates enforcer: ${GREEN}Available${NC}"
else
    echo -e "❌ Quality gates enforcer: ${RED}Missing${NC}"
fi

# Check recent quality reports
if [ -f "$PROJECT_ROOT/reports/best-practices-validation-"*.json ]; then
    latest_report=$(ls -t "$PROJECT_ROOT/reports/best-practices-validation-"*.json 2>/dev/null | head -1)
    if [ -n "$latest_report" ]; then
        report_score=$(jq -r '.best_practices_score.overall' "$latest_report" 2>/dev/null || echo "0")
        echo -e "${CHECK} Latest validation score: ${GREEN}${report_score}/100${NC}"
    fi
else
    echo -e "⚠️ Validation reports: ${YELLOW}None found${NC}"
fi

echo ""

# Git Worktree Status
echo -e "${BLUE}🌳 GIT WORKTREE STATUS${NC}"
echo "----------------------"

worktree_count=$(git worktree list 2>/dev/null | wc -l || echo "0")
echo -e "${CHECK} Active worktrees: ${GREEN}${worktree_count}${NC}"

if [ "$worktree_count" -gt 1 ]; then
    echo "   Available agent workspaces:"
    git worktree list 2>/dev/null | tail -n +2 | while read -r line; do
        workspace=$(echo "$line" | awk '{print $1}')
        branch=$(echo "$line" | awk '{print $2}' | tr -d '[]')
        echo -e "   🤖 $(basename "$workspace"): ${branch}"
    done
fi

echo ""

# Best Practices Summary
echo -e "${BLUE}📋 BEST PRACTICES SUMMARY${NC}"
echo "--------------------------"

# Calculate overall implementation score
total_checks=0
passed_checks=0

# Claude Code checks (4 checks)
total_checks=$((total_checks + 4))
[ -f "$PROJECT_ROOT/CLAUDE.md" ] && passed_checks=$((passed_checks + 1))
[ -f "$PROJECT_ROOT/.claude/settings.json" ] && passed_checks=$((passed_checks + 1))
[ -d "$PROJECT_ROOT/.claude/commands" ] && passed_checks=$((passed_checks + 1))
[ -f "$PROJECT_ROOT/.mcp.json" ] && passed_checks=$((passed_checks + 1))

# Gemini CLI checks (3 checks)
total_checks=$((total_checks + 3))
command -v gemini &> /dev/null && passed_checks=$((passed_checks + 1))
[ -f "$PROJECT_ROOT/gemini.yaml" ] && passed_checks=$((passed_checks + 1))
[ -f "$PROJECT_ROOT/.claude/gemini-integration.json" ] && passed_checks=$((passed_checks + 1))

# MOEX checks (3 checks)
total_checks=$((total_checks + 3))
[ -f "$PROJECT_ROOT/moex-config.yaml" ] && passed_checks=$((passed_checks + 1))
[ -f "$PROJECT_ROOT/scripts/moex-coordinator.sh" ] && passed_checks=$((passed_checks + 1))
[ -d "$PROJECT_ROOT/moex-workspace" ] && passed_checks=$((passed_checks + 1))

# Quality & monitoring checks (3 checks)
total_checks=$((total_checks + 3))
[ -f "$PROJECT_ROOT/scripts/comprehensive-health-dashboard.py" ] && passed_checks=$((passed_checks + 1))
[ -f "$PROJECT_ROOT/.git/hooks/pre-commit" ] && passed_checks=$((passed_checks + 1))
[ -f "$PROJECT_ROOT/scripts/quality-gates-enforcer.sh" ] && passed_checks=$((passed_checks + 1))

percentage=$(( (passed_checks * 100) / total_checks ))

echo -e "📊 Implementation Status: ${passed_checks}/${total_checks} (${percentage}%)"

if [ "$percentage" -ge 90 ]; then
    echo -e "🏆 Status: ${GREEN}Excellent - All best practices implemented${NC}"
elif [ "$percentage" -ge 80 ]; then
    echo -e "👍 Status: ${GREEN}Good - Minor improvements needed${NC}"
elif [ "$percentage" -ge 70 ]; then
    echo -e "⚠️ Status: ${YELLOW}Moderate - Several improvements needed${NC}"
else
    echo -e "🔧 Status: ${RED}Needs Work - Major improvements required${NC}"
fi

echo ""

# Quick Commands Reference
echo -e "${BLUE}🚀 QUICK COMMANDS${NC}"
echo "-----------------"
echo "Health check:     /project:health-check"
echo "Agent setup:      /project:agent-setup <agent-name>"
echo "Fix GitHub issue: /project:fix-issue <issue-number>"
echo "TDD workflow:     /project:tdd <feature>"
echo ""
echo "Health dashboard: ./scripts/comprehensive-health-dashboard.py"
echo "MOEX monitor:     ./scripts/moex-coordinator.sh monitor"
echo "Best practices:   ./scripts/best-practices-enforcer.sh"
echo ""

echo "=================================================================="
echo -e "${ROCKET} ${GREEN}Multi-Agent Development Environment Ready!${NC}"
echo "🎯 Follow the workflow: Explore → Plan → Code → Commit"
echo "💡 Use /clear frequently to optimize context"
echo "🤝 Let Claude, Gemini, and MOEX work together seamlessly"
echo "=================================================================="