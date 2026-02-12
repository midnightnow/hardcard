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
