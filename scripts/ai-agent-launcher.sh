#!/bin/bash
# AI Agent Launcher with Built-in Context
# Automatically sets up the correct context for each agent

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Function to generate agent context
generate_agent_context() {
    local agent_type=$1
    local worktree_path=$2
    local branch=$3
    local focus_area=$4
    
    cat << EOF
SYSTEM CONTEXT:
==============
You are the $agent_type Specialist AI for the HardCard project.

WORKING DIRECTORY: $worktree_path
BRANCH: $branch
FOCUS: $focus_area

CRITICAL RULES:
1. Your FIRST command must be: cd $worktree_path
2. You work ONLY in this directory
3. You focus ONLY on $focus_area
4. Update STATUS.md after each work session
5. Commit regularly with descriptive messages
6. Check AI_AGENT_TASKS.md for your assigned tasks

FORBIDDEN:
- Do NOT modify files outside your focus area
- Do NOT switch to other directories
- Do NOT merge or modify other branches

START EVERY SESSION WITH:
cd $worktree_path && pwd && git status

Your tasks are listed in: /Users/studio/hardcard/AI_AGENT_TASKS.md
Look for the "$agent_type Agent Tasks" section.
EOF
}

# Function to create agent startup file
create_agent_startup() {
    local agent=$1
    local worktree_path=$2
    local startup_file="$worktree_path/.ai-agent-startup"
    
    cat > "$startup_file" << 'EOF'
#!/bin/bash
# Auto-generated startup script for AI agent

echo "🤖 AI Agent Workspace Initialized"
echo "================================"
pwd
echo ""
echo "Branch: $(git branch --show-current)"
echo "Status: $(git status --porcelain | wc -l) uncommitted changes"
echo ""
echo "📋 Your tasks:"
grep -A 20 "$(basename $(pwd) | sed 's/hardcard-//' | sed 's/-ai//')" /Users/studio/hardcard/AI_AGENT_TASKS.md | grep "^- \["
echo ""
echo "💡 Remember: Work only in this directory!"
EOF
    chmod +x "$startup_file"
}

# Function to create agent launcher URL
create_agent_url() {
    local agent=$1
    local context=$2
    local worktree_path=$3
    
    # Create a custom URL file that can be opened
    local url_file="$HOME/Desktop/Launch-${agent}-Agent.url"
    
    cat > "$url_file" << EOF
[InternetShortcut]
URL=file://$worktree_path/.ai-agent-context.md
EOF
    
    # Also create a markdown file with the context
    cat > "$worktree_path/.ai-agent-context.md" << EOF
# 🤖 $agent AI Agent Context

\`\`\`bash
$context
\`\`\`

## Quick Start Commands

\`\`\`bash
cd $worktree_path
./ai-agent-startup
\`\`\`

## Your Current Tasks

Check AI_AGENT_TASKS.md for assignments.
EOF
}

# Function to setup agent
setup_agent() {
    local agent_type=$1
    local agent_id=$2
    local worktree_dir=$3
    local branch=$4
    local focus=$5
    
    echo -e "${BLUE}Setting up $agent_type agent...${NC}"
    
    # Generate context
    local context=$(generate_agent_context "$agent_type" "$worktree_dir" "$branch" "$focus")
    
    # Save context to file
    echo "$context" > "$worktree_dir/.ai-context"
    
    # Create startup script
    create_agent_startup "$agent_type" "$worktree_dir"
    
    # Create URL launcher
    create_agent_url "$agent_type" "$context" "$worktree_dir"
    
    # Create clipboard-ready file
    echo "$context" > "$worktree_dir/PASTE_THIS_TO_AI.txt"
    
    echo -e "${GREEN}✅ $agent_type agent configured${NC}"
}

# Main setup
echo -e "${YELLOW}🤖 Configuring AI Agent Defaults...${NC}"
echo ""

# Setup each agent
setup_agent "Frontend" "frontend-ai" "/Users/studio/hardcard-frontend-ai" "ai/frontend-specialist" "frontend/ directory only"
setup_agent "Backend" "backend-ai" "/Users/studio/hardcard-backend-ai" "ai/backend-specialist" "backend/ directory only"
setup_agent "Testing" "testing-ai" "/Users/studio/hardcard-testing-ai" "ai/testing-specialist" "test files only"
setup_agent "Documentation" "docs-ai" "/Users/studio/hardcard-docs-ai" "ai/documentation" "*.md files only"
setup_agent "Security" "security-ai" "/Users/studio/hardcard-security-ai" "ai/security-audit" "security analysis"

# Create master launcher
cat > launch-ai-agent.sh << 'EOF'
#!/bin/bash
# Master AI Agent Launcher

echo "🤖 HardCard AI Agent Launcher"
echo "============================"
echo ""
echo "Select an agent to launch:"
echo "1) Frontend AI"
echo "2) Backend AI"
echo "3) Testing AI"
echo "4) Documentation AI"
echo "5) Security AI"
echo ""
read -p "Choice (1-5): " choice

case $choice in
    1) agent="frontend-ai" ;;
    2) agent="backend-ai" ;;
    3) agent="testing-ai" ;;
    4) agent="docs-ai" ;;
    5) agent="security-ai" ;;
    *) echo "Invalid choice"; exit 1 ;;
esac

worktree="/Users/studio/hardcard-$agent"

echo ""
echo "📋 Copy this context to your AI agent:"
echo "======================================"
cat "$worktree/.ai-context"
echo ""
echo "======================================"
echo ""
echo "Context saved to: $worktree/PASTE_THIS_TO_AI.txt"
echo ""

# Copy to clipboard if possible
if command -v pbcopy >/dev/null 2>&1; then
    cat "$worktree/.ai-context" | pbcopy
    echo "✅ Context copied to clipboard!"
fi

# Open in VS Code if available
if command -v code >/dev/null 2>&1; then
    code "$worktree"
fi
EOF
chmod +x launch-ai-agent.sh

echo ""
echo -e "${GREEN}✅ AI Agent Default Contexts Created!${NC}"
echo ""
echo -e "${BLUE}📁 What's been created:${NC}"
echo "  - Each worktree has .ai-context file"
echo "  - Each worktree has PASTE_THIS_TO_AI.txt"
echo "  - Desktop shortcuts for each agent"
echo "  - Master launcher script"
echo ""
echo -e "${YELLOW}🚀 How to use:${NC}"
echo "1. Run: ./launch-ai-agent.sh"
echo "2. Select the agent"
echo "3. Copy the displayed context"
echo "4. Paste as first message to AI"
echo ""
echo -e "${GREEN}💡 Pro tip: Context is auto-copied to clipboard!${NC}"