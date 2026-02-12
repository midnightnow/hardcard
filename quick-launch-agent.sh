#!/bin/bash
# Quick AI Agent Launcher with Clipboard

AGENTS=(
    "frontend-ai|Frontend development"
    "backend-ai|Backend development"
    "testing-ai|Testing and QA"
    "docs-ai|Documentation"
    "security-ai|Security audit"
)

echo "🤖 Quick AI Agent Launcher"
echo "========================"
echo ""

# Show menu
i=1
for agent in "${AGENTS[@]}"; do
    name=$(echo $agent | cut -d'|' -f2)
    echo "$i) $name"
    ((i++))
done

echo ""
read -p "Select agent (1-5): " choice

# Get selected agent
agent_info="${AGENTS[$((choice-1))]}"
agent_id=$(echo $agent_info | cut -d'|' -f1)
agent_dir="/Users/studio/hardcard-$agent_id"

if [ ! -d "$agent_dir" ]; then
    echo "Error: Agent directory not found"
    exit 1
fi

# Show context
echo ""
echo "📋 COPY THIS TO YOUR AI:"
echo "======================="
cat "$agent_dir/START_HERE.md"
echo "======================="

# Copy to clipboard
if command -v pbcopy >/dev/null 2>&1; then
    cat "$agent_dir/START_HERE.md" | pbcopy
    echo ""
    echo "✅ Context copied to clipboard!"
    echo "📌 Just paste into your AI chat!"
fi

# Optionally open directory
echo ""
read -p "Open in VS Code? (y/n): " open_code
if [ "$open_code" = "y" ] && command -v code >/dev/null 2>&1; then
    code "$agent_dir"
fi
