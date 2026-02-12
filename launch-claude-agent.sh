#!/bin/bash
# Launch Claude Code with agent-specific context

echo "🤖 Claude Code Agent Launcher"
echo "============================"
echo ""
echo "Select agent to launch:"
echo "1) Frontend Agent"
echo "2) Backend Agent"
echo "3) Testing Agent"
echo "4) Documentation Agent"
echo "5) Security Agent"
echo ""
read -p "Choice (1-5): " choice

case $choice in
    1) 
        agent="frontend-ai"
        name="Frontend"
        ;;
    2) 
        agent="backend-ai"
        name="Backend"
        ;;
    3) 
        agent="testing-ai"
        name="Testing"
        ;;
    4) 
        agent="docs-ai"
        name="Documentation"
        ;;
    5) 
        agent="security-ai"
        name="Security"
        ;;
    *) 
        echo "Invalid choice"
        exit 1
        ;;
esac

worktree="/Users/studio/hardcard-$agent"

echo ""
echo "🚀 Launching $name Agent..."
echo ""
echo "Working directory: $worktree"
echo "Configuration: $worktree/CLAUDE.md"
echo ""

# Copy agent context to clipboard
if [ -f "$worktree/CLAUDE.md" ]; then
    echo "📋 Agent context copied to clipboard!"
    cat "$worktree/CLAUDE.md" | pbcopy
fi

# Change to agent directory
cd "$worktree"

# If Claude Code is installed, launch it
if command -v claude >/dev/null 2>&1; then
    echo "Starting Claude Code in agent workspace..."
    claude code
else
    echo "Claude Code CLI not found. Opening directory..."
    if command -v code >/dev/null 2>&1; then
        code .
    fi
    echo ""
    echo "Remember to check CLAUDE.md for your agent instructions!"
fi
