#!/bin/bash
# Universal AI Agent Launcher - Works with Claude Code and Gemini CLI

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${PURPLE}🤖 Universal AI Agent Launcher${NC}"
echo "=============================="
echo ""

# Step 1: Choose AI System
echo "Select AI system:"
echo "1) Claude Code"
echo "2) Gemini CLI (Free)"
echo ""
read -p "Choice (1-2): " ai_choice

case $ai_choice in
    1) ai_system="claude" ;;
    2) ai_system="gemini" ;;
    *) echo "Invalid choice"; exit 1 ;;
esac

# Step 2: Choose Agent
echo ""
echo "Select agent:"
echo "1) Frontend Agent"
echo "2) Backend Agent"
echo "3) Testing Agent"
echo "4) Documentation Agent"
echo "5) Security Agent"
echo ""
read -p "Choice (1-5): " agent_choice

case $agent_choice in
    1) 
        agent="frontend-ai"
        name="Frontend"
        focus="React, TypeScript, UI"
        ;;
    2) 
        agent="backend-ai"
        name="Backend"
        focus="Python, FastAPI, Database"
        ;;
    3) 
        agent="testing-ai"
        name="Testing"
        focus="Tests, QA, E2E"
        ;;
    4) 
        agent="docs-ai"
        name="Documentation"
        focus="Markdown, Guides"
        ;;
    5) 
        agent="security-ai"
        name="Security"
        focus="Security Analysis"
        ;;
    *) 
        echo "Invalid choice"
        exit 1
        ;;
esac

worktree="/Users/studio/hardcard-$agent"

echo ""
echo -e "${CYAN}🚀 Launching $name Agent with $ai_system${NC}"
echo "========================================"
echo ""

# Generate appropriate context
if [ "$ai_system" = "claude" ]; then
    echo -e "${BLUE}Claude Code Context:${NC}"
    echo ""
    cat << EOF
You are the $name AI Agent for HardCard.
Working directory: $worktree
Branch: ai/$agent
Focus: $focus

Check CLAUDE.md for detailed instructions.
Review STATUS.md and AI_AGENT_TASKS.md.
Work only in your assigned directory.
EOF
    echo ""
    echo -e "${YELLOW}Commands:${NC}"
    echo "cd $worktree"
    echo "# Claude Code will automatically see CLAUDE.md"
    echo ""
    
    # Copy context if possible
    if command -v pbcopy >/dev/null 2>&1; then
        echo "cd $worktree" | pbcopy
        echo -e "${GREEN}✅ Directory command copied to clipboard!${NC}"
    fi
    
else
    echo -e "${BLUE}Gemini CLI Commands:${NC}"
    echo ""
    
    # Show specific Gemini commands
    case $name in
        "Frontend")
            cat << 'EOF'
cd /Users/studio/hardcard-frontend-ai
gemini -p "I am the Frontend Agent. Review STATUS.md and suggest next tasks"

# Common tasks:
gemini -p "Enable TypeScript strict mode" frontend/tsconfig.json
gemini -p "Migrate component to TypeScript" frontend/src/components/Example.tsx
gemini -a -p "Find and fix all TypeScript any types"
EOF
            ;;
        "Backend")
            cat << 'EOF'
cd /Users/studio/hardcard-backend-ai
gemini -p "I am the Backend Agent. Review STATUS.md and suggest next tasks"

# Common tasks:
gemini -p "Add type hints to Python functions" backend/app/
gemini -p "Create Pydantic models" backend/app/models/
gemini -a -p "Optimize database queries"
EOF
            ;;
        "Testing")
            cat << 'EOF'
cd /Users/studio/hardcard-testing-ai
gemini -p "I am the Testing Agent. Review STATUS.md and suggest next tasks"

# Common tasks:
gemini -p "Generate tests for component" frontend/src/components/Example.tsx
gemini -a -p "Analyze test coverage and fill gaps"
gemini -p "Create E2E test scenarios" tests/e2e/
EOF
            ;;
        "Documentation")
            cat << 'EOF'
cd /Users/studio/hardcard-docs-ai
gemini -p "I am the Documentation Agent. Review STATUS.md and suggest next tasks"

# Common tasks:
gemini -p "Update README.md" README.md
gemini -a -p "Generate API documentation"
gemini -p "Create setup guide" docs/SETUP.md
EOF
            ;;
        "Security")
            cat << 'EOF'
cd /Users/studio/hardcard-security-ai
gemini -p "I am the Security Agent. Review STATUS.md and suggest next tasks"

# Common tasks:
gemini -a -p "Perform security audit"
gemini -p "Check for exposed secrets" .
gemini -p "OWASP compliance check" backend/app/auth/
EOF
            ;;
    esac
    
    echo ""
    echo -e "${YELLOW}💡 Tips:${NC}"
    echo "- Use specific files to save tokens"
    echo "- Check GEMINI.md for more commands"
    echo "- Update STATUS.md after work"
fi

echo ""
echo -e "${GREEN}📁 Key Files:${NC}"
echo "- Tasks: /Users/studio/hardcard/AI_AGENT_TASKS.md"
echo "- Status: $worktree/STATUS.md"
echo "- Guide: $worktree/${ai_system^^}.md"
echo ""

# Offer to open in editor
read -p "Open in VS Code? (y/n): " open_code
if [ "$open_code" = "y" ] && command -v code >/dev/null 2>&1; then
    code "$worktree"
fi

echo ""
echo -e "${PURPLE}🚀 Happy coding with $ai_system!${NC}"