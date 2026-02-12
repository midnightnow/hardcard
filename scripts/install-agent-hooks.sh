#!/bin/bash
# Install Git Hooks for AI Agent Context
# This ensures agents always know their context

set -e

echo "🔧 Installing AI Agent Git Hooks..."
echo ""

# Function to create post-checkout hook
create_post_checkout_hook() {
    local worktree=$1
    local agent_name=$2
    local hook_file="$worktree/.git/hooks/post-checkout"
    
    mkdir -p "$worktree/.git/hooks"
    
    cat > "$hook_file" << EOF
#!/bin/bash
# Auto-generated hook for $agent_name AI agent

echo ""
echo "🤖 =========================================="
echo "🤖 $agent_name AI AGENT CONTEXT"
echo "🤖 =========================================="
echo "📁 Working Directory: \$(pwd)"
echo "🌿 Branch: \$(git branch --show-current)"
echo "📋 Focus Area: Check .ai-context for rules"
echo ""
echo "⚠️  REMEMBER: You must work ONLY in this directory!"
echo "📄 Your context is in: PASTE_THIS_TO_AI.txt"
echo "🤖 =========================================="
echo ""
EOF
    chmod +x "$hook_file"
}

# Function to create prompt file for each agent
create_agent_prompt_file() {
    local worktree=$1
    local agent_type=$2
    local branch=$3
    
    cat > "$worktree/AI_AGENT_PROMPT.md" << EOF
# 🤖 $agent_type AI Agent - System Prompt

## COPY THIS ENTIRE BLOCK AS YOUR FIRST MESSAGE:

\`\`\`
I am the $agent_type Specialist AI for HardCard.

MY WORKSPACE: $worktree
MY BRANCH: $branch

I will now initialize my workspace:
\`\`\`

\`\`\`bash
cd $worktree && pwd
git status
cat STATUS.md
\`\`\`

After initialization, I will check my assigned tasks in AI_AGENT_TASKS.md and begin work.

## RULES I FOLLOW:
1. I work ONLY in $worktree
2. I focus ONLY on my designated files
3. I update STATUS.md with my progress
4. I commit with descriptive messages
5. I never modify files outside my scope

## MY CURRENT SESSION:
Starting work session at $(date)
EOF
}

# Install for each agent
for agent_dir in ../hardcard-*-ai; do
    if [ -d "$agent_dir" ]; then
        agent_name=$(basename "$agent_dir" | sed 's/hardcard-//' | sed 's/-ai//' | sed 's/.*/\u&/')
        echo "Installing hooks for $agent_name agent..."
        
        create_post_checkout_hook "$agent_dir" "$agent_name"
        create_agent_prompt_file "$agent_dir" "$agent_name" "$(cd $agent_dir && git branch --show-current)"
        
        # Create a shell wrapper that includes context
        cat > "$agent_dir/start-agent-session.sh" << EOF
#!/bin/bash
echo "Starting $agent_name AI Agent Session"
echo "===================================="
echo ""
echo "📋 Copy the following to start your AI session:"
echo ""
cat AI_AGENT_PROMPT.md
echo ""
echo "===================================="
if command -v pbcopy >/dev/null 2>&1; then
    cat AI_AGENT_PROMPT.md | pbcopy
    echo "✅ Prompt copied to clipboard!"
fi
EOF
        chmod +x "$agent_dir/start-agent-session.sh"
    fi
done

# Create VS Code workspace files with agent context
echo ""
echo "Creating VS Code workspace configurations..."

for agent_dir in ../hardcard-*-ai; do
    if [ -d "$agent_dir" ]; then
        agent_name=$(basename "$agent_dir")
        cat > "$agent_dir/.vscode/settings.json" << EOF
{
    "window.title": "🤖 $agent_name - \${activeEditorShort}",
    "terminal.integrated.cwd": "$agent_dir",
    "terminal.integrated.env.osx": {
        "AI_AGENT": "$agent_name",
        "AI_WORKTREE": "$agent_dir"
    },
    "terminal.integrated.shellArgs.osx": [
        "-c",
        "echo '🤖 $agent_name workspace' && echo 'Directory: $agent_dir' && echo '' && exec \$SHELL"
    ]
}
EOF
        mkdir -p "$agent_dir/.vscode"
    fi
done

# Create browser bookmarks file
cat > ~/Desktop/AI-Agent-Bookmarks.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>HardCard AI Agent Bookmarks</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .agent { margin: 20px 0; padding: 20px; border: 2px solid #007bff; border-radius: 10px; }
        .agent h2 { margin-top: 0; }
        .context { background: #f0f0f0; padding: 10px; border-radius: 5px; }
        button { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
        button:hover { background: #0056b3; }
    </style>
</head>
<body>
    <h1>🤖 HardCard AI Agent Quick Launch</h1>
    <p>Click any button to copy the agent context to clipboard</p>
EOF

# Add each agent to the bookmarks
for agent_dir in ../hardcard-*-ai; do
    if [ -d "$agent_dir" ]; then
        agent_name=$(basename "$agent_dir" | sed 's/hardcard-//' | sed 's/-ai//')
        agent_context=$(cat "$agent_dir/.ai-context" | sed 's/"/\\"/g' | sed ':a;N;$!ba;s/\n/\\n/g')
        
        cat >> ~/Desktop/AI-Agent-Bookmarks.html << EOF
    <div class="agent">
        <h2>$agent_name Agent</h2>
        <div class="context">
            <pre id="${agent_name}-context">$(cat "$agent_dir/.ai-context")</pre>
        </div>
        <button onclick="copyContext('${agent_name}-context')">Copy $agent_name Context</button>
    </div>
EOF
    fi
done

cat >> ~/Desktop/AI-Agent-Bookmarks.html << 'EOF'
    <script>
        function copyContext(elementId) {
            const text = document.getElementById(elementId).textContent;
            navigator.clipboard.writeText(text).then(() => {
                alert('Context copied to clipboard!');
            });
        }
    </script>
</body>
</html>
EOF

echo ""
echo "✅ AI Agent Automation Complete!"
echo ""
echo "🎯 What's been set up:"
echo "  1. Git hooks in each worktree"
echo "  2. AI_AGENT_PROMPT.md in each directory"
echo "  3. start-agent-session.sh scripts"
echo "  4. VS Code workspace settings"
echo "  5. Desktop HTML bookmark file"
echo ""
echo "🚀 Three ways to use:"
echo ""
echo "  Option 1: Run start script"
echo "  cd ../hardcard-frontend-ai && ./start-agent-session.sh"
echo ""
echo "  Option 2: Use launcher"
echo "  ./launch-ai-agent.sh"
echo ""
echo "  Option 3: Open bookmarks"
echo "  open ~/Desktop/AI-Agent-Bookmarks.html"
echo ""