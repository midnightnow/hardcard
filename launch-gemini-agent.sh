#!/bin/bash
# Launch Gemini CLI with agent-specific context

echo "🤖 Gemini CLI Agent Launcher"
echo "==========================="
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
echo "Working directory: $worktree"
echo ""

# Create context prompt
context="You are the $name AI Agent for HardCard.
Working directory: $worktree
Focus on: $name tasks only
First, check STATUS.md and AI_AGENT_TASKS.md"

echo "📋 Quick Start Commands:"
echo ""
echo "cd $worktree"
echo "gemini -p \"$context. What should I work on?\""
echo ""

# Copy context to clipboard if available
if command -v pbcopy >/dev/null 2>&1; then
    echo "$context" | pbcopy
    echo "✅ Context copied to clipboard!"
fi

# Change to agent directory
cd "$worktree"
echo "Current directory: $(pwd)"
echo ""
echo "📄 See GEMINI.md for detailed commands"
