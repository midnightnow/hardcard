#!/bin/bash
# Setup Multi-AI Agent Worktrees for HardCard
# Each agent gets their own workspace

set -e

echo "🤖 Setting up Multi-AI Agent Worktrees for HardCard"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if we're in the right directory
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Base directory
BASE_DIR=$(dirname "$(pwd)")

echo -e "${BLUE}Creating AI Agent Worktrees in: $BASE_DIR${NC}"
echo ""

# Function to create agent worktree
create_agent_worktree() {
    local agent_name=$1
    local branch_name=$2
    local description=$3
    local worktree_path="${BASE_DIR}/hardcard-${agent_name}"
    
    echo -e "${YELLOW}Setting up $agent_name agent...${NC}"
    echo "  Description: $description"
    
    if [ -d "$worktree_path" ]; then
        echo "  ⚠️  Worktree already exists, skipping"
    else
        if git worktree add "$worktree_path" -b "$branch_name" 2>/dev/null; then
            echo -e "  ${GREEN}✅ Created at: $worktree_path${NC}"
            
            # Create agent config
            echo "{
  \"agent\": \"$agent_name\",
  \"purpose\": \"$description\",
  \"branch\": \"$branch_name\",
  \"created\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\",
  \"guidelines\": {
    \"focus_areas\": [],
    \"restrictions\": [],
    \"communication\": \"Update STATUS.md after each session\"
  }
}" > "$worktree_path/.agent-config.json"
            
            # Create status file
            echo "# $agent_name Agent Status

## Current Task
None assigned yet

## Progress
- [ ] Awaiting assignment

## Notes
Ready for work!

Last Updated: $(date)" > "$worktree_path/STATUS.md"
            
        else
            echo "  ❌ Failed to create worktree"
        fi
    fi
    echo ""
}

# Create main agent worktrees
echo -e "${BLUE}Creating specialized AI agent worktrees...${NC}"
echo ""

create_agent_worktree "frontend-ai" "ai/frontend-specialist" \
    "Frontend development - React, TypeScript, UI/UX"

create_agent_worktree "backend-ai" "ai/backend-specialist" \
    "Backend development - Python, FastAPI, Database"

create_agent_worktree "testing-ai" "ai/testing-specialist" \
    "Testing & QA - Unit tests, E2E, Performance"

create_agent_worktree "docs-ai" "ai/documentation" \
    "Documentation - API docs, guides, README files"

create_agent_worktree "security-ai" "ai/security-audit" \
    "Security analysis - Vulnerability scanning, Best practices"

# Create task distribution file
echo -e "${YELLOW}Creating task distribution system...${NC}"

cat > AI_AGENT_TASKS.md << 'EOF'
# 🤖 AI Agent Task Distribution

**Last Updated:** $(date)
**Coordinator:** Claude (Main Worktree)

---

## 🎯 Current Sprint: TypeScript Migration & Security

### Frontend Agent Tasks
- [ ] Enable TypeScript strict mode in tsconfig.json
- [ ] Fix type errors in Dashboard component
- [ ] Add proper types to all API calls
- [ ] Create interfaces for all props
- [ ] Remove all 'any' types

### Backend Agent Tasks  
- [ ] Add type hints to all Python functions
- [ ] Create Pydantic models for API responses
- [ ] Implement input validation
- [ ] Add OpenAPI schema generation
- [ ] Type all database queries

### Testing Agent Tasks
- [ ] Create unit tests for migrated components
- [ ] Add type checking to test suite
- [ ] Create E2E tests for critical paths
- [ ] Set up performance benchmarks
- [ ] Add security test cases

### Documentation Agent Tasks
- [ ] Document TypeScript migration guide
- [ ] Update API documentation
- [ ] Create component usage examples
- [ ] Write troubleshooting guide
- [ ] Update README with new setup

### Security Agent Tasks
- [ ] Audit authentication flows
- [ ] Check for exposed secrets
- [ ] Review API security
- [ ] Analyze dependencies for vulnerabilities
- [ ] Create security best practices guide

---

## 📊 Progress Tracking

| Agent | Current Task | Progress | Status |
|-------|-------------|----------|---------|
| Frontend AI | Not started | 0% | 🟡 Ready |
| Backend AI | Not started | 0% | 🟡 Ready |
| Testing AI | Not started | 0% | 🟡 Ready |
| Docs AI | Not started | 0% | 🟡 Ready |
| Security AI | Not started | 0% | 🟡 Ready |

---

## 🔄 Communication Protocol

1. Check this file for assigned tasks
2. Update STATUS.md in your worktree
3. Commit regularly with descriptive messages
4. Request merge when task complete
5. Note any blockers or dependencies
EOF

# Create communication directory
mkdir -p agent-communication
cat > agent-communication/README.md << 'EOF'
# Agent Communication Hub

This directory facilitates communication between AI agents.

## Files:
- `requests.md` - Inter-agent requests
- `blockers.md` - Current blockers
- `decisions.md` - Architectural decisions
- `handoffs.md` - Work handoff notes

## Protocol:
1. Agents check this directory before starting work
2. Leave notes for other agents when needed
3. Mark items as resolved when complete
EOF

# Create the agent coordinator script
cat > scripts/agent-coordinator.sh << 'EOF'
#!/bin/bash
# Multi-AI Agent Coordinator for HardCard

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# List all agent worktrees
list_agents() {
    echo -e "${BLUE}🤖 Active AI Agent Worktrees:${NC}"
    git worktree list | grep -E "ai/|agent" | while IFS= read -r line; do
        dir=$(echo "$line" | awk '{print $1}')
        branch=$(echo "$line" | awk '{print $3}' | tr -d '[]')
        agent_name=$(basename "$dir" | sed 's/hardcard-//')
        echo -e "  ${GREEN}→${NC} $agent_name (branch: $branch)"
        echo "     Path: $dir"
    done
}

# Check agent status
check_status() {
    echo -e "${BLUE}📊 Agent Status Report:${NC}"
    echo ""
    
    for worktree in ../hardcard-*-ai; do
        if [ -d "$worktree" ]; then
            agent_name=$(basename "$worktree" | sed 's/hardcard-//')
            echo -e "${YELLOW}$agent_name:${NC}"
            
            cd "$worktree"
            
            # Git status
            changes=$(git status --porcelain | wc -l | tr -d ' ')
            branch=$(git branch --show-current)
            
            echo "  Branch: $branch"
            echo "  Changes: $changes uncommitted"
            
            # Check STATUS.md
            if [ -f "STATUS.md" ]; then
                current_task=$(grep -A 1 "## Current Task" STATUS.md | tail -1)
                echo "  Task: $current_task"
            fi
            
            # Check last commit
            last_commit=$(git log -1 --oneline 2>/dev/null || echo "No commits yet")
            echo "  Last: $last_commit"
            
            echo ""
            cd - > /dev/null
        fi
    done
}

# Merge agent work
merge_agent() {
    local agent=$1
    if [ -z "$agent" ]; then
        echo -e "${RED}Error: Please specify agent name${NC}"
        echo "Usage: $0 merge <agent-name>"
        return 1
    fi
    
    cd "$(git rev-parse --show-toplevel)"
    branch="ai/${agent}-specialist"
    
    echo -e "${YELLOW}Merging $agent work...${NC}"
    
    # Check if branch exists
    if ! git show-ref --quiet refs/heads/"$branch"; then
        branch="ai/${agent}"
        if ! git show-ref --quiet refs/heads/"$branch"; then
            echo -e "${RED}Error: Branch $branch not found${NC}"
            return 1
        fi
    fi
    
    # Show what will be merged
    echo "Changes to be merged:"
    git log --oneline main.."$branch" | head -10
    
    echo ""
    read -p "Proceed with merge? (y/n): " confirm
    if [ "$confirm" = "y" ]; then
        git merge "$branch" --no-ff -m "Merge $agent AI agent work

- Agent: $agent
- Branch: $branch
- Timestamp: $(date)"
        echo -e "${GREEN}✅ Merge complete!${NC}"
    else
        echo "Merge cancelled"
    fi
}

# Assign task to agent
assign_task() {
    local agent=$1
    local task=$2
    
    if [ -z "$agent" ] || [ -z "$task" ]; then
        echo -e "${RED}Error: Usage: $0 assign <agent> <task>${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}Assigning task to $agent...${NC}"
    echo ""
    echo "Task: $task"
    echo ""
    echo "This will update AI_AGENT_TASKS.md"
    echo "The agent should check their assigned tasks there."
}

# Show help
show_help() {
    echo "Multi-AI Agent Coordinator"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  list           - List all AI agent worktrees"
    echo "  status         - Check status of all agents"
    echo "  merge <agent>  - Merge agent's work into main"
    echo "  assign <agent> <task> - Assign task to agent"
    echo "  help           - Show this help"
}

# Main command dispatcher
case "$1" in
    "list")
        list_agents
        ;;
    "status")
        check_status
        ;;
    "merge")
        merge_agent "$2"
        ;;
    "assign")
        assign_task "$2" "$3"
        ;;
    "help"|"")
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        show_help
        exit 1
        ;;
esac
EOF

chmod +x scripts/agent-coordinator.sh

# Create agent launcher script
cat > scripts/launch-agent.sh << 'EOF'
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
EOF

chmod +x scripts/launch-agent.sh

# Summary
echo ""
echo -e "${GREEN}✅ Multi-AI Agent Setup Complete!${NC}"
echo ""
echo -e "${BLUE}📁 Created Worktrees:${NC}"
git worktree list | grep -E "ai/" | while IFS= read -r line; do
    echo "  $line"
done

echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo "1. Add each worktree to GitHub Desktop:"
echo "   - File → Add Local Repository"
echo "   - Browse to each agent directory"
echo ""
echo "2. Assign tasks to agents:"
echo "   - Edit AI_AGENT_TASKS.md"
echo "   - Or use: ./scripts/agent-coordinator.sh assign <agent> <task>"
echo ""
echo "3. Launch agent workspace:"
echo "   ./scripts/launch-agent.sh frontend-ai"
echo ""
echo "4. Monitor progress:"
echo "   ./scripts/agent-coordinator.sh status"
echo ""
echo -e "${YELLOW}💡 Pro Tip:${NC} Each agent can work independently without conflicts!"