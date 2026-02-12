#!/bin/bash
# Git Worktree Manager for HardCard
# Simplifies worktree creation and management

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Base directory for worktrees
WORKTREE_BASE_DIR="../"

echo -e "${BLUE}🌳 HardCard Git Worktree Manager${NC}"
echo "================================"

# Function to list worktrees
list_worktrees() {
    echo -e "\n${GREEN}Current Worktrees:${NC}"
    git worktree list | while read -r line; do
        echo "  📁 $line"
    done
}

# Function to create worktree
create_worktree() {
    local worktree_type=$1
    local branch_name=$2
    local worktree_dir=""
    
    case $worktree_type in
        "hotfix")
            worktree_dir="${WORKTREE_BASE_DIR}hardcard-hotfix-${branch_name}"
            branch_name="hotfix/${branch_name}"
            ;;
        "feature")
            worktree_dir="${WORKTREE_BASE_DIR}hardcard-feature-${branch_name}"
            branch_name="feature/${branch_name}"
            ;;
        "typescript")
            worktree_dir="${WORKTREE_BASE_DIR}hardcard-ts-${branch_name}"
            branch_name="typescript/${branch_name}"
            ;;
        "experiment")
            worktree_dir="${WORKTREE_BASE_DIR}hardcard-exp-${branch_name}"
            branch_name="exp/${branch_name}"
            ;;
        *)
            echo -e "${RED}Unknown worktree type: $worktree_type${NC}"
            return 1
            ;;
    esac
    
    echo -e "${YELLOW}Creating worktree...${NC}"
    echo "  Type: $worktree_type"
    echo "  Branch: $branch_name"
    echo "  Directory: $worktree_dir"
    
    if git worktree add "$worktree_dir" -b "$branch_name"; then
        echo -e "${GREEN}✅ Worktree created successfully!${NC}"
        echo -e "\n${BLUE}Next steps:${NC}"
        echo "  cd $worktree_dir"
        echo "  code .  # Open in VS Code"
        echo "  npm install  # Install dependencies if needed"
    else
        echo -e "${RED}❌ Failed to create worktree${NC}"
        return 1
    fi
}

# Function to switch to worktree
switch_to_worktree() {
    echo -e "\n${GREEN}Available worktrees:${NC}"
    local i=1
    local worktrees=()
    
    while IFS= read -r line; do
        dir=$(echo "$line" | awk '{print $1}')
        branch=$(echo "$line" | awk '{print $3}' | tr -d '[]')
        worktrees+=("$dir")
        echo "  $i) $dir [$branch]"
        ((i++))
    done < <(git worktree list)
    
    echo ""
    read -p "Select worktree number: " selection
    
    if [[ "$selection" =~ ^[0-9]+$ ]] && [ "$selection" -ge 1 ] && [ "$selection" -le "${#worktrees[@]}" ]; then
        selected_dir="${worktrees[$((selection-1))]}"
        echo -e "${GREEN}Switching to: $selected_dir${NC}"
        cd "$selected_dir"
        exec $SHELL
    else
        echo -e "${RED}Invalid selection${NC}"
    fi
}

# Function to clean up worktrees
cleanup_worktrees() {
    echo -e "\n${YELLOW}Cleaning up worktrees...${NC}"
    
    # First, prune any worktrees that were deleted manually
    git worktree prune
    
    echo -e "${GREEN}Stale worktrees removed (if any)${NC}"
    
    # List worktrees that can be removed
    echo -e "\n${BLUE}Current worktrees:${NC}"
    list_worktrees
    
    echo -e "\n${YELLOW}To remove a specific worktree:${NC}"
    echo "  git worktree remove <path>"
    echo "  # or"
    echo "  rm -rf <worktree-directory>"
    echo "  git worktree prune"
}

# Function to setup standard worktrees
setup_standard_worktrees() {
    echo -e "\n${BLUE}Setting up standard HardCard worktrees...${NC}"
    
    # Check if they already exist
    existing=$(git worktree list | wc -l)
    if [ "$existing" -gt 1 ]; then
        echo -e "${YELLOW}⚠️  You already have worktrees set up${NC}"
        list_worktrees
        read -p "Continue anyway? (y/n): " confirm
        if [ "$confirm" != "y" ]; then
            return 0
        fi
    fi
    
    echo -e "\n${GREEN}Creating standard worktrees:${NC}"
    
    # TypeScript migration worktree
    if ! git worktree list | grep -q "typescript-migration"; then
        echo "1. TypeScript migration worktree..."
        git worktree add "${WORKTREE_BASE_DIR}hardcard-typescript" -b typescript/strict-mode
    fi
    
    # Hotfix worktree
    if ! git worktree list | grep -q "hotfix"; then
        echo "2. Hotfix worktree..."
        git worktree add "${WORKTREE_BASE_DIR}hardcard-hotfix" -b hotfix/standby
    fi
    
    # Feature development worktree
    if ! git worktree list | grep -q "feature"; then
        echo "3. Feature development worktree..."
        git worktree add "${WORKTREE_BASE_DIR}hardcard-feature" -b feature/development
    fi
    
    echo -e "\n${GREEN}✅ Standard worktrees created!${NC}"
    list_worktrees
}

# Main menu
show_menu() {
    echo ""
    echo "What would you like to do?"
    echo "1) List all worktrees"
    echo "2) Create new worktree"
    echo "3) Switch to worktree"
    echo "4) Setup standard worktrees"
    echo "5) Clean up worktrees"
    echo "6) Show worktree guide"
    echo "7) Exit"
    echo ""
}

# Main loop
while true; do
    show_menu
    read -p "Select option (1-7): " choice
    
    case $choice in
        1)
            list_worktrees
            ;;
        2)
            echo -e "\n${BLUE}Create new worktree${NC}"
            echo "Select type:"
            echo "  1) hotfix    - For emergency fixes"
            echo "  2) feature   - For new features"
            echo "  3) typescript - For TypeScript migration"
            echo "  4) experiment - For testing ideas"
            read -p "Type (1-4): " type_choice
            
            case $type_choice in
                1) type="hotfix" ;;
                2) type="feature" ;;
                3) type="typescript" ;;
                4) type="experiment" ;;
                *) echo -e "${RED}Invalid choice${NC}"; continue ;;
            esac
            
            read -p "Enter branch name (e.g., payment-fix): " branch_name
            if [ -n "$branch_name" ]; then
                create_worktree "$type" "$branch_name"
            else
                echo -e "${RED}Branch name required${NC}"
            fi
            ;;
        3)
            switch_to_worktree
            ;;
        4)
            setup_standard_worktrees
            ;;
        5)
            cleanup_worktrees
            ;;
        6)
            if [ -f "GIT_WORKTREE_GUIDE.md" ]; then
                less GIT_WORKTREE_GUIDE.md
            else
                echo -e "${RED}Guide not found${NC}"
            fi
            ;;
        7)
            echo -e "${GREEN}Goodbye!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            ;;
    esac
done