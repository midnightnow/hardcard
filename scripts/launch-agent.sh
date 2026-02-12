#!/bin/bash
# Launch specific AI agent workspace

agent=$1
if [ -z "$agent" ]; then
    echo "Usage: $0 <agent-name>"
    echo "Available agents: frontend-ai, backend-ai, testing-ai, docs-ai, security-ai"
    exit 1
fi

worktree_path="../hardcard-$agent"
if [ ! -d "$worktree_path" ]; then
    echo "Error: Agent worktree not found at $worktree_path"
    exit 1
fi

echo "🚀 Launching $agent workspace..."
cd "$worktree_path"

# Open in VS Code if available
if command -v code >/dev/null 2>&1; then
    code .
fi

# Start new shell in worktree
exec $SHELL
