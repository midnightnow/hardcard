#!/bin/bash
# 🚀 Launch AI Development Ecosystem
# Simple launcher for the comprehensive multi-agent AI system

set -e

PROJECT_ROOT="/Users/studio/00 Constellation/hardcard"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Change to project directory
cd "$PROJECT_ROOT" || {
    echo -e "${RED}Error: Cannot change to project root: $PROJECT_ROOT${NC}"
    exit 1
}

echo -e "${BLUE}🚀 Launching AI Development Ecosystem${NC}"
echo -e "${BLUE}====================================${NC}"
echo ""

# Check for required files
if [ ! -f "scripts/comprehensive-startup-orchestrator.py" ]; then
    echo -e "${RED}❌ Comprehensive startup orchestrator not found${NC}"
    echo -e "${YELLOW}Available options:${NC}"
    
    if [ -f "scripts/unified-startup-orchestrator.py" ]; then
        echo -e "  ${GREEN}✅ Unified startup orchestrator${NC}"
        echo -e "${YELLOW}Running unified startup instead...${NC}"
        python3 scripts/unified-startup-orchestrator.py --project-root "$PROJECT_ROOT"
    elif [ -f "scripts/auto-startup-integration.sh" ]; then
        echo -e "  ${GREEN}✅ Auto-startup integration${NC}"
        echo -e "${YELLOW}Running auto-startup instead...${NC}"
        bash scripts/auto-startup-integration.sh
    else
        echo -e "${RED}❌ No startup orchestrators found${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Found comprehensive startup orchestrator${NC}"
    echo -e "${BLUE}🤖 Initializing agents: Claude Code + Claude Engineer + Gemini CLI + MOEX${NC}"
    echo ""
    
    # Run comprehensive startup
    python3 scripts/comprehensive-startup-orchestrator.py --project-root "$PROJECT_ROOT"
fi

echo ""
echo -e "${GREEN}🎉 AI Development Ecosystem launch completed!${NC}"
echo ""
echo -e "${BLUE}📊 Check status with:${NC}"
echo -e "  ./scripts/worktree-task-manager.sh status"
echo -e "  ./scripts/comprehensive-health-dashboard.py"
echo ""
echo -e "${BLUE}🚀 Available tools:${NC}"
echo -e "  ${GREEN}Claude Code:${NC} Primary development and implementation"
echo -e "  ${GREEN}Claude Engineer:${NC} Self-improving AI with dynamic tool creation"
echo -e "  ${GREEN}Gemini CLI:${NC} Code analysis and documentation"
echo -e "  ${GREEN}MOEX:${NC} Multi-agent coordination and orchestration"
echo ""