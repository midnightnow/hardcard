#!/bin/bash
# Post-attach script for devcontainer
# Runs each time VS Code attaches to the container

set -e

echo "👋 Welcome to HardCard Development Environment!"

# Set up terminal
echo "🎨 Configuring terminal..."

# Check if we're in VS Code terminal
if [ "$TERM_PROGRAM" = "vscode" ]; then
    # Set up powerline fonts if available
    if fc-list | grep -q "MesloLGS"; then
        echo "✅ Powerline fonts detected"
    else
        echo "💡 Consider installing MesloLGS NF font for better terminal experience"
    fi
fi

# Display current git branch and status
if [ -d ".git" ]; then
    echo ""
    echo "📌 Git Status:"
    git branch --show-current | xargs echo "  Branch:"
    git status --short | head -5
    
    # Check for uncommitted changes
    if ! git diff --quiet; then
        echo "  ⚠️  You have uncommitted changes"
    fi
fi

# Show running services
echo ""
echo "🏃 Running Services:"
docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "(postgres|redis|mailhog)" | head -5

# Check for TODO items
echo ""
if command -v rg >/dev/null 2>&1; then
    TODO_COUNT=$(rg -c "TODO|FIXME|HACK" --type py --type js --type ts 2>/dev/null | wc -l)
    if [ "$TODO_COUNT" -gt 0 ]; then
        echo "📝 You have $TODO_COUNT files with TODO/FIXME items"
    fi
fi

# Check test status
echo ""
echo "🧪 Test Status:"
if [ -f ".coverage" ]; then
    coverage report | tail -1
else
    echo "  No coverage data found. Run 'test-all' to generate."
fi

# Reminders
echo ""
echo "🔔 Reminders:"
echo "  • Run 'pre-commit install' if you haven't already"
echo "  • Use 'quality' to run all code quality checks"
echo "  • Use 'security' to run security scans"

# Check for updates
if [ -f "requirements.txt" ]; then
    echo ""
    echo "📦 Checking for outdated packages..."
    pip list --outdated 2>/dev/null | head -5 || echo "  All packages up to date!"
fi

# Set custom prompt for this session
export PS1='🔐 \[\033[1;36m\]\w\[\033[0m\]$(__git_ps1 " (%s)") \$ '

echo ""
echo "Ready to code! 🚀"
echo ""