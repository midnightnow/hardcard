#!/bin/bash
# Create default context files for AI agents
# Simple solution that works with worktrees

set -e

echo "🤖 Creating AI Agent Default Contexts..."
echo ""

# Function to create context card
create_context_card() {
    local agent_name=$1
    local agent_dir=$2
    local branch=$3
    local focus=$4
    
    # Create a context card that can be copied
    cat > "$agent_dir/START_HERE.md" << EOF
# 🤖 $agent_name AI Agent

## COPY THIS ENTIRE BLOCK TO START:

\`\`\`
I am the $agent_name AI Agent for HardCard.
My working directory is: $agent_dir
My branch is: $branch
My focus is: $focus

I'll start by initializing my workspace:
\`\`\`

\`\`\`bash
cd $agent_dir
pwd
git status
ls -la
\`\`\`

## MY RULES:
1. I work ONLY in $agent_dir
2. I focus ONLY on $focus
3. I update STATUS.md regularly
4. I commit with clear messages
5. I check AI_AGENT_TASKS.md for my tasks

## QUICK COMMANDS:
- See my tasks: \`grep -A 20 "$agent_name" /Users/studio/hardcard/AI_AGENT_TASKS.md\`
- Update status: \`echo "Working on: [task]" >> STATUS.md\`
- Commit work: \`git add -A && git commit -m "$agent_name: [description]"\`
EOF

    # Create a one-liner file
    echo "cd $agent_dir && echo 'I am the $agent_name AI in $(pwd) on branch $branch'" > "$agent_dir/COPY_THIS_FIRST.txt"
}

# Create for each agent
create_context_card "Frontend" "/Users/studio/hardcard-frontend-ai" "ai/frontend-specialist" "frontend/ files only"
create_context_card "Backend" "/Users/studio/hardcard-backend-ai" "ai/backend-specialist" "backend/ files only"
create_context_card "Testing" "/Users/studio/hardcard-testing-ai" "ai/testing-specialist" "test files only"
create_context_card "Documentation" "/Users/studio/hardcard-docs-ai" "ai/documentation" "*.md files only"
create_context_card "Security" "/Users/studio/hardcard-security-ai" "ai/security-audit" "security analysis"

# Create quick launcher with clipboard support
cat > quick-launch-agent.sh << 'EOF'
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
EOF
chmod +x quick-launch-agent.sh

# Create all-in-one reference file
cat > AI_AGENT_DIRECTORY.md << 'EOF'
# 📁 AI Agent Directory & Quick Reference

## 🤖 Agent Workspaces

### Frontend AI
- **Directory**: `/Users/studio/hardcard-frontend-ai`
- **Branch**: `ai/frontend-specialist`
- **Focus**: React, TypeScript, UI components
- **Start**: `cat /Users/studio/hardcard-frontend-ai/START_HERE.md`

### Backend AI
- **Directory**: `/Users/studio/hardcard-backend-ai`
- **Branch**: `ai/backend-specialist`
- **Focus**: Python, FastAPI, Database
- **Start**: `cat /Users/studio/hardcard-backend-ai/START_HERE.md`

### Testing AI
- **Directory**: `/Users/studio/hardcard-testing-ai`
- **Branch**: `ai/testing-specialist`
- **Focus**: Unit tests, E2E tests, QA
- **Start**: `cat /Users/studio/hardcard-testing-ai/START_HERE.md`

### Documentation AI
- **Directory**: `/Users/studio/hardcard-docs-ai`
- **Branch**: `ai/documentation`
- **Focus**: README files, API docs, guides
- **Start**: `cat /Users/studio/hardcard-docs-ai/START_HERE.md`

### Security AI
- **Directory**: `/Users/studio/hardcard-security-ai`
- **Branch**: `ai/security-audit`
- **Focus**: Security analysis, vulnerability scanning
- **Start**: `cat /Users/studio/hardcard-security-ai/START_HERE.md`

## 🚀 Quick Launch

Run: `./quick-launch-agent.sh`

## 📋 Manual Copy Commands

```bash
# Frontend
cat /Users/studio/hardcard-frontend-ai/START_HERE.md | pbcopy

# Backend
cat /Users/studio/hardcard-backend-ai/START_HERE.md | pbcopy

# Testing
cat /Users/studio/hardcard-testing-ai/START_HERE.md | pbcopy

# Documentation
cat /Users/studio/hardcard-docs-ai/START_HERE.md | pbcopy

# Security
cat /Users/studio/hardcard-security-ai/START_HERE.md | pbcopy
```
EOF

echo "✅ AI Agent Default Contexts Created!"
echo ""
echo "📁 Created in each worktree:"
echo "  - START_HERE.md (full context)"
echo "  - COPY_THIS_FIRST.txt (one-liner)"
echo ""
echo "🚀 To use:"
echo "  1. Run: ./quick-launch-agent.sh"
echo "  2. Select agent"
echo "  3. Paste the copied context to AI"
echo ""
echo "📋 Or manually copy:"
echo "  cat ../hardcard-frontend-ai/START_HERE.md | pbcopy"