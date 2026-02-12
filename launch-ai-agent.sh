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
