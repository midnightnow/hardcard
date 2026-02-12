#!/bin/bash
# 🔥 Auto-Startup Integration - Runs the complete system automatically when Claude starts
# This script is designed to be called from CLAUDE.md or startup hooks

set -e

PROJECT_ROOT="/Users/studio/hardcard"
INTEGRATION_LOG="$PROJECT_ROOT/logs/auto-startup.log"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Emojis
ROCKET="🚀"
CHECK="✅"
GEAR="⚙️"
FIRE="🔥"

# Ensure log directory exists
mkdir -p "$PROJECT_ROOT/logs"

# Log function
log_startup() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $message" >> "$INTEGRATION_LOG"
    echo -e "$message"
}

# Check if already running
check_already_running() {
    local pid_file="$PROJECT_ROOT/monitoring/startup-integration.pid"
    
    if [ -f "$pid_file" ]; then
        local existing_pid=$(cat "$pid_file")
        if ps -p "$existing_pid" > /dev/null 2>&1; then
            log_startup "${YELLOW}System already running (PID: $existing_pid). Skipping startup.${NC}"
            return 0
        else
            # Stale PID file, remove it
            rm -f "$pid_file"
        fi
    fi
    
    # Write current PID
    echo $$ > "$pid_file"
    return 1
}

# Quick system validation
quick_validation() {
    log_startup "${GEAR} Running quick system validation..."
    
    # Check if we're in the right directory
    if [ ! -f "$PROJECT_ROOT/CLAUDE.md" ]; then
        log_startup "${RED}Error: Not in HardCard project root${NC}"
        return 1
    fi
    
    # Check if core scripts exist
    local required_scripts=(
        "scripts/claude-startup-enforcer.sh"
        "scripts/worktree-task-manager.sh"
        "scripts/page-completion-tracker.py"
        "scripts/quality-gates-enforcer.sh"
    )
    
    for script in "${required_scripts[@]}"; do
        if [ ! -f "$PROJECT_ROOT/$script" ]; then
            log_startup "${RED}Error: Required script missing: $script${NC}"
            return 1
        fi
    done
    
    log_startup "${CHECK} Quick validation passed"
    return 0
}

# Run background startup (non-blocking)
run_background_startup() {
    log_startup "${ROCKET} Starting background system initialization..."
    
    # Run best practices enforcer first
    log_startup "${GEAR} Enforcing best practices..."
    "$PROJECT_ROOT/scripts/best-practices-enforcer.sh" > "$PROJECT_ROOT/logs/best-practices.log" 2>&1 &
    local bp_pid=$!
    
    # Run startup enforcer in background
    nohup "$PROJECT_ROOT/scripts/claude-startup-enforcer.sh" > "$PROJECT_ROOT/logs/background-startup.log" 2>&1 &
    local startup_pid=$!
    
    log_startup "${CHECK} Background startup initiated (PID: $startup_pid)"
    log_startup "${CHECK} Best practices enforcement initiated (PID: $bp_pid)"
    
    # Give it a moment to start
    sleep 3
    
    # Check if processes are still running
    if ps -p "$startup_pid" > /dev/null 2>&1; then
        log_startup "${CHECK} Background startup is running successfully"
    else
        log_startup "${YELLOW}Background startup completed quickly or failed${NC}"
    fi
    
    if ps -p "$bp_pid" > /dev/null 2>&1; then
        log_startup "${CHECK} Best practices enforcement is running"
    else
        log_startup "${CHECK} Best practices enforcement completed"
    fi
}

# Show immediate status
show_immediate_status() {
    log_startup "${BLUE}📊 IMMEDIATE STATUS CHECK${NC}"
    
    # Show worktree count
    local worktree_count=$(git worktree list 2>/dev/null | wc -l || echo "0")
    log_startup "Worktrees: ${BLUE}$worktree_count${NC} active"
    
    # Show if monitoring is running
    local monitor_pid=$(pgrep -f "claude-continuous-monitor" || echo "")
    if [ -n "$monitor_pid" ]; then
        log_startup "Monitoring: ${GREEN}ACTIVE${NC} (PID: $monitor_pid)"
    else
        log_startup "Monitoring: ${YELLOW}STARTING${NC}"
    fi
    
    # Show last completion report
    if [ -f "$PROJECT_ROOT/monitoring/startup-completion-report.json" ]; then
        local total_files=$(jq -r '.total_files' "$PROJECT_ROOT/monitoring/startup-completion-report.json" 2>/dev/null || echo "unknown")
        local avg_completion=$(jq -r '.summary.average_completion' "$PROJECT_ROOT/monitoring/startup-completion-report.json" 2>/dev/null || echo "unknown")
        log_startup "Files: ${BLUE}$total_files${NC} | Completion: ${BLUE}$avg_completion%${NC}"
    else
        log_startup "Analysis: ${YELLOW}RUNNING${NC}"
    fi
}

# Main integration function
main() {
    log_startup "${FIRE} Claude Auto-Startup Integration"
    log_startup "======================================="
    
    # Change to project directory
    cd "$PROJECT_ROOT" || {
        echo "Error: Cannot change to project root: $PROJECT_ROOT"
        exit 1
    }
    
    # Check if already running
    if check_already_running; then
        return 0
    fi
    
    # Quick validation
    if ! quick_validation; then
        log_startup "${RED}Validation failed. System may not be properly configured.${NC}"
        return 1
    fi
    
    # Run comprehensive startup orchestrator
    log_startup "${ROCKET} Launching Comprehensive AI Development Ecosystem..."
    if [ -f "$PROJECT_ROOT/scripts/comprehensive-startup-orchestrator.py" ]; then
        nohup python3 "$PROJECT_ROOT/scripts/comprehensive-startup-orchestrator.py" --project-root "$PROJECT_ROOT" > "$PROJECT_ROOT/logs/comprehensive-startup.log" 2>&1 &
        local orchestrator_pid=$!
        log_startup "${CHECK} Comprehensive startup orchestrator launched (PID: $orchestrator_pid)"
        
        # Give it a moment to start
        sleep 3
        
        if ps -p "$orchestrator_pid" > /dev/null 2>&1; then
            log_startup "${CHECK} Comprehensive AI ecosystem startup is running"
            log_startup "${BLUE}Initializing: Claude Code + Claude Engineer + Gemini CLI + MOEX${NC}"
        else
            log_startup "${YELLOW}Comprehensive startup orchestrator completed quickly${NC}"
        fi
    elif [ -f "$PROJECT_ROOT/scripts/unified-startup-orchestrator.py" ]; then
        log_startup "${YELLOW}Using fallback unified startup orchestrator${NC}"
        nohup python3 "$PROJECT_ROOT/scripts/unified-startup-orchestrator.py" --project-root "$PROJECT_ROOT" > "$PROJECT_ROOT/logs/unified-startup.log" 2>&1 &
        local orchestrator_pid=$!
        log_startup "${CHECK} Unified startup orchestrator launched (PID: $orchestrator_pid)"
        
        # Give it a moment to start
        sleep 2
        
        if ps -p "$orchestrator_pid" > /dev/null 2>&1; then
            log_startup "${CHECK} Unified startup orchestrator is running"
        else
            log_startup "${YELLOW}Unified startup orchestrator completed quickly${NC}"
        fi
    else
        log_startup "${YELLOW}Startup orchestrators not found - running individual systems${NC}"
        # Fallback to individual startup
        run_background_startup
        show_immediate_status
        initialize_gemini
        initialize_moex
    fi
    
    log_startup ""
    log_startup "${CHECK} Auto-startup integration completed"
    log_startup "${BLUE}Use './scripts/worktree-task-manager.sh status' for detailed information${NC}"
    log_startup ""
    
    # Wait a moment for background processes to settle
    sleep 1
    
    # Clean up PID file after a delay (in background)
    (sleep 30; rm -f "$PROJECT_ROOT/monitoring/startup-integration.pid") &
}

# Initialize Gemini CLI integration
initialize_gemini() {
    log_startup "${GEAR} Initializing Gemini CLI integration..."
    
    if [ -f "$PROJECT_ROOT/scripts/gemini-cli-setup.sh" ]; then
        "$PROJECT_ROOT/scripts/gemini-cli-setup.sh" > /dev/null 2>&1 &
        log_startup "${CHECK} Gemini CLI initialization started"
    else
        log_startup "${YELLOW} Gemini CLI setup script not found${NC}"
    fi
}

# Initialize MOEX coordinator
initialize_moex() {
    log_startup "${GEAR} Initializing MOEX coordinator..."
    
    if [ -f "$PROJECT_ROOT/scripts/moex-coordinator.sh" ]; then
        "$PROJECT_ROOT/scripts/moex-coordinator.sh" init > /dev/null 2>&1
        log_startup "${CHECK} MOEX coordinator initialized"
    else
        log_startup "${YELLOW} MOEX coordinator script not found${NC}"
    fi
}

# Run main function
main "$@"

# Initialize Gemini CLI integration
initialize_gemini() {
    log_startup "${GEAR} Initializing Gemini CLI integration..."
    
    if [ -f "$PROJECT_ROOT/scripts/gemini-cli-setup.sh" ]; then
        "$PROJECT_ROOT/scripts/gemini-cli-setup.sh" > /dev/null 2>&1 &
        log_startup "${CHECK} Gemini CLI initialization started"
    else
        log_startup "${YELLOW} Gemini CLI setup script not found${NC}"
    fi
}

# Initialize MOEX coordinator
initialize_moex() {
    log_startup "${GEAR} Initializing MOEX coordinator..."
    
    if [ -f "$PROJECT_ROOT/scripts/moex-coordinator.sh" ]; then
        "$PROJECT_ROOT/scripts/moex-coordinator.sh" init > /dev/null 2>&1
        log_startup "${CHECK} MOEX coordinator initialized"
    else
        log_startup "${YELLOW} MOEX coordinator script not found${NC}"
    fi
}

# Add to main function after show_immediate_status
# initialize_gemini
# initialize_moex
