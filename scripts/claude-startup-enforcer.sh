#!/bin/bash
# 🚀 Claude Startup Enforcer - Automatic Worktree System Initialization
# This script runs automatically when Claude starts to ensure the multi-agent system is active

set -e

PROJECT_ROOT="/Users/studio/hardcard"
STARTUP_LOG="$PROJECT_ROOT/logs/claude-startup.log"
MONITORING_DIR="$PROJECT_ROOT/monitoring"
PERFORMANCE_DIR="$PROJECT_ROOT/performance"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Emojis
ROCKET="🚀"
CHECK="✅"
WARNING="⚠️"
ROBOT="🤖"
CHART="📊"
GEAR="⚙️"

# Ensure directories exist
mkdir -p "$PROJECT_ROOT/logs" "$MONITORING_DIR" "$PERFORMANCE_DIR"

# Log with timestamp
log() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $message" >> "$STARTUP_LOG"
    echo -e "$message"
}

# Performance tracking
track_performance() {
    local operation="$1"
    local start_time=$(date +%s.%N)
    
    # Execute the operation
    shift
    "$@"
    local exit_code=$?
    
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc)
    
    # Log performance metrics
    echo "{\"operation\": \"$operation\", \"duration\": $duration, \"timestamp\": \"$(date -Iseconds)\", \"exit_code\": $exit_code}" >> "$PERFORMANCE_DIR/startup-metrics.jsonl"
    
    return $exit_code
}

# Check system health
check_system_health() {
    log "${GEAR} Checking system health..."
    
    local health_report="$MONITORING_DIR/system-health.json"
    local timestamp=$(date -Iseconds)
    
    # Check Git status
    local git_status="healthy"
    if ! git status > /dev/null 2>&1; then
        git_status="error"
    fi
    
    # Check worktrees
    local worktree_count=$(git worktree list 2>/dev/null | wc -l || echo "0")
    local expected_worktrees=6  # Main + 5 agents
    
    # Check disk space
    local disk_usage=$(df "$PROJECT_ROOT" | tail -1 | awk '{print $5}' | sed 's/%//')
    local disk_status="healthy"
    if [ "$disk_usage" -gt 90 ]; then
        disk_status="critical"
    elif [ "$disk_usage" -gt 80 ]; then
        disk_status="warning"
    fi
    
    # Check memory usage
    local memory_usage=$(vm_stat | grep "Pages active" | awk '{print $3}' | sed 's/\.//')
    
    # Generate health report
    cat > "$health_report" << EOF
{
  "timestamp": "$timestamp",
  "git_status": "$git_status",
  "worktree_count": $worktree_count,
  "expected_worktrees": $expected_worktrees,
  "disk_usage_percent": $disk_usage,
  "disk_status": "$disk_status",
  "memory_active_pages": ${memory_usage:-0},
  "project_root": "$PROJECT_ROOT",
  "claude_session_id": "${CLAUDE_SESSION_ID:-unknown}"
}
EOF
    
    log "${CHECK} System health report generated: $health_report"
    
    # Alert on critical issues
    if [ "$git_status" = "error" ]; then
        log "${WARNING} CRITICAL: Git repository issues detected"
        return 1
    fi
    
    if [ "$worktree_count" -lt "$expected_worktrees" ]; then
        log "${WARNING} WARNING: Missing worktrees (found: $worktree_count, expected: $expected_worktrees)"
    fi
    
    if [ "$disk_status" = "critical" ]; then
        log "${WARNING} CRITICAL: Disk usage critical ($disk_usage%)"
        return 1
    fi
    
    return 0
}

# Validate worktree configuration
validate_worktrees() {
    log "${ROBOT} Validating worktree configuration..."
    
    local validation_report="$MONITORING_DIR/worktree-validation.json"
    local timestamp=$(date -Iseconds)
    local issues=()
    local agents=("frontend-ai" "backend-ai" "testing-ai" "docs-ai" "security-ai")
    
    echo "{\"timestamp\": \"$timestamp\", \"validations\": [" > "$validation_report"
    
    for i in "${!agents[@]}"; do
        local agent="${agents[$i]}"
        local agent_dir="/Users/studio/hardcard-${agent}"
        local branch="ai/${agent%-ai}-specialist"
        if [ "$agent" = "docs-ai" ]; then
            branch="ai/documentation"
        elif [ "$agent" = "security-ai" ]; then
            branch="ai/security-audit"
        fi
        
        local status="healthy"
        local error_message=""
        
        # Check if directory exists
        if [ ! -d "$agent_dir" ]; then
            status="missing_directory"
            error_message="Agent directory not found: $agent_dir"
            issues+=("$agent: missing directory")
        else
            cd "$agent_dir"
            
            # Check if it's a git repository
            if ! git status > /dev/null 2>&1; then
                status="git_error"
                error_message="Not a git repository or git error"
                issues+=("$agent: git error")
            else
                # Check branch
                local current_branch=$(git branch --show-current)
                if [ "$current_branch" != "$branch" ]; then
                    status="wrong_branch"
                    error_message="Expected branch $branch, found $current_branch"
                    issues+=("$agent: wrong branch")
                fi
                
                # Check for STATUS.md
                if [ ! -f "STATUS.md" ]; then
                    status="missing_status"
                    error_message="STATUS.md file not found"
                    issues+=("$agent: missing STATUS.md")
                fi
            fi
            cd "$PROJECT_ROOT"
        fi
        
        # Add validation entry
        if [ $i -gt 0 ]; then
            echo "," >> "$validation_report"
        fi
        echo "    {\"agent\": \"$agent\", \"directory\": \"$agent_dir\", \"expected_branch\": \"$branch\", \"status\": \"$status\", \"error\": \"$error_message\"}" >> "$validation_report"
    done
    
    echo "  ], \"issues_count\": ${#issues[@]}, \"issues\": [" >> "$validation_report"
    for i in "${!issues[@]}"; do
        local issue="${issues[$i]}"
        if [ $i -gt 0 ]; then
            echo "," >> "$validation_report"
        fi
        echo "    \"${issue}\"" >> "$validation_report"
    done
    echo "  ]}" >> "$validation_report"
    
    if [ ${#issues[@]} -eq 0 ]; then
        log "${CHECK} All worktrees validated successfully"
        return 0
    else
        log "${WARNING} Worktree validation issues found: ${#issues[@]}"
        for issue in "${issues[@]}"; do
            log "  - $issue"
        done
        return 1
    fi
}

# Auto-repair worktree issues
auto_repair_worktrees() {
    log "${GEAR} Auto-repairing worktree issues..."
    
    local agents=("frontend-ai" "backend-ai" "testing-ai" "docs-ai" "security-ai")
    local repairs_made=0
    
    for agent in "${agents[@]}"; do
        local agent_dir="/Users/studio/hardcard-${agent}"
        local branch="ai/${agent%-ai}-specialist"
        if [ "$agent" = "docs-ai" ]; then
            branch="ai/documentation"
        elif [ "$agent" = "security-ai" ]; then
            branch="ai/security-audit"
        fi
        
        # Create worktree if missing
        if [ ! -d "$agent_dir" ]; then
            log "${GEAR} Creating missing worktree for $agent..."
            if git worktree add "$agent_dir" -b "$branch" 2>/dev/null; then
                log "${CHECK} Created worktree: $agent_dir"
                repairs_made=$((repairs_made + 1))
            else
                log "${WARNING} Failed to create worktree for $agent"
            fi
        fi
        
        # Create STATUS.md if missing
        if [ -d "$agent_dir" ] && [ ! -f "$agent_dir/STATUS.md" ]; then
            log "${GEAR} Creating STATUS.md for $agent..."
            cat > "$agent_dir/STATUS.md" << EOF
# ${agent^^} Status Report
**Last Updated:** $(date)
**Auto-generated:** By Claude startup enforcer

## 🎯 Current Priority Tasks
No tasks assigned yet. Run task assignment to get started.

## 📊 Task Summary
- **Critical Tasks:** 0
- **High Priority:** 0
- **Medium Priority:** 0

## 🔄 Progress Updates
Agent initialized and ready for work.

## 🚫 Blockers
None

## 📝 Notes
Agent workspace created automatically.
EOF
            repairs_made=$((repairs_made + 1))
            log "${CHECK} Created STATUS.md for $agent"
        fi
    done
    
    log "${CHECK} Auto-repair completed. Repairs made: $repairs_made"
    return 0
}

# Initialize monitoring
initialize_monitoring() {
    log "${CHART} Initializing continuous monitoring..."
    
    # Create monitoring configuration
    cat > "$MONITORING_DIR/config.json" << EOF
{
  "monitoring_enabled": true,
  "check_interval_seconds": 300,
  "performance_tracking": true,
  "auto_repair": true,
  "alerts": {
    "disk_usage_threshold": 85,
    "completion_threshold": 70,
    "security_issues_threshold": 0
  },
  "retention": {
    "logs_days": 30,
    "metrics_days": 90,
    "reports_days": 365
  }
}
EOF
    
    # Start background monitoring (if not already running)
    local monitor_pid=$(pgrep -f "claude-continuous-monitor" || echo "")
    if [ -z "$monitor_pid" ]; then
        log "${GEAR} Starting background monitoring..."
        nohup "$PROJECT_ROOT/scripts/claude-continuous-monitor.sh" > "$MONITORING_DIR/monitor.log" 2>&1 &
        echo $! > "$MONITORING_DIR/monitor.pid"
        log "${CHECK} Background monitoring started (PID: $!)"
    else
        log "${CHECK} Background monitoring already running (PID: $monitor_pid)"
    fi
}

# Run completion analysis
run_startup_analysis() {
    log "${CHART} Running startup completion analysis..."
    
    local analysis_start=$(date +%s.%N)
    
    # Run page completion tracker
    if python3 "$PROJECT_ROOT/scripts/page-completion-tracker.py" --output "$MONITORING_DIR/startup-completion-report.json" > /dev/null 2>&1; then
        log "${CHECK} Completion analysis completed"
        
        # Extract key metrics
        local total_files=$(jq -r '.total_files' "$MONITORING_DIR/startup-completion-report.json" 2>/dev/null || echo "unknown")
        local avg_completion=$(jq -r '.summary.average_completion' "$MONITORING_DIR/startup-completion-report.json" 2>/dev/null || echo "unknown")
        local critical_issues=$(jq -r '.summary.critical_issues | length' "$MONITORING_DIR/startup-completion-report.json" 2>/dev/null || echo "unknown")
        
        log "${CHART} Project status: $total_files files, $avg_completion% avg completion, $critical_issues critical issues"
    else
        log "${WARNING} Completion analysis failed"
    fi
    
    local analysis_end=$(date +%s.%N)
    local analysis_duration=$(echo "$analysis_end - $analysis_start" | bc)
    
    # Log performance
    echo "{\"operation\": \"startup_analysis\", \"duration\": $analysis_duration, \"timestamp\": \"$(date -Iseconds)\"}" >> "$PERFORMANCE_DIR/startup-metrics.jsonl"
}

# Assign tasks to agents
auto_assign_tasks() {
    log "${ROBOT} Auto-assigning tasks to agents..."
    
    # Run task assignment for all agents
    if "$PROJECT_ROOT/scripts/worktree-task-manager.sh" assign > "$MONITORING_DIR/task-assignment.log" 2>&1; then
        log "${CHECK} Tasks assigned to all agents"
    else
        log "${WARNING} Task assignment failed"
    fi
}

# Generate startup report
generate_startup_report() {
    log "${CHART} Generating startup report..."
    
    local report_file="$MONITORING_DIR/claude-startup-report.json"
    local timestamp=$(date -Iseconds)
    local session_id="${CLAUDE_SESSION_ID:-$(date +%s)}"
    
    # Get system info
    local total_files=$(jq -r '.total_files' "$MONITORING_DIR/startup-completion-report.json" 2>/dev/null || echo "0")
    local avg_completion=$(jq -r '.summary.average_completion' "$MONITORING_DIR/startup-completion-report.json" 2>/dev/null || echo "0")
    local worktree_count=$(git worktree list 2>/dev/null | wc -l || echo "0")
    
    cat > "$report_file" << EOF
{
  "session_id": "$session_id",
  "timestamp": "$timestamp",
  "startup_duration": "$(grep "Startup completed" "$STARTUP_LOG" | tail -1 | grep -o '[0-9.]*s' || echo "unknown")",
  "system_status": {
    "project_root": "$PROJECT_ROOT",
    "total_files": $total_files,
    "average_completion": $avg_completion,
    "worktree_count": $worktree_count,
    "monitoring_enabled": true,
    "auto_repair_enabled": true
  },
  "agents": [
    {"name": "frontend-ai", "status": "active", "directory": "/Users/studio/hardcard-frontend-ai"},
    {"name": "backend-ai", "status": "active", "directory": "/Users/studio/hardcard-backend-ai"},
    {"name": "testing-ai", "status": "active", "directory": "/Users/studio/hardcard-testing-ai"},
    {"name": "docs-ai", "status": "active", "directory": "/Users/studio/hardcard-docs-ai"},
    {"name": "security-ai", "status": "active", "directory": "/Users/studio/hardcard-security-ai"}
  ],
  "next_analysis": "$(date -d '+5 minutes' -Iseconds 2>/dev/null || date -v+5M -Iseconds 2>/dev/null || echo "unknown")"
}
EOF
    
    log "${CHECK} Startup report generated: $report_file"
}

# Main startup sequence
main() {
    local startup_start=$(date +%s.%N)
    
    log "${ROCKET} Claude Multi-Agent System Startup Enforcer"
    log "=================================="
    
    # Step 1: System Health Check
    if ! track_performance "system_health_check" check_system_health; then
        log "${WARNING} System health issues detected, attempting repairs..."
    fi
    
    # Step 2: Validate Worktrees
    if ! track_performance "worktree_validation" validate_worktrees; then
        log "${GEAR} Worktree issues detected, auto-repairing..."
        track_performance "auto_repair" auto_repair_worktrees
        
        # Re-validate after repair
        if ! validate_worktrees; then
            log "${WARNING} Some worktree issues persist after auto-repair"
        fi
    fi
    
    # Step 3: Initialize Monitoring
    track_performance "monitoring_init" initialize_monitoring
    
    # Step 4: Run Analysis
    track_performance "startup_analysis" run_startup_analysis
    
    # Step 5: Auto-assign Tasks
    track_performance "task_assignment" auto_assign_tasks
    
    # Step 6: Generate Report
    track_performance "report_generation" generate_startup_report
    
    local startup_end=$(date +%s.%N)
    local startup_duration=$(echo "$startup_end - $startup_start" | bc)
    
    log "${CHECK} Claude startup enforcement completed in ${startup_duration}s"
    log "${ROCKET} Multi-agent worktree system is now active and monitored"
    
    # Display quick status
    echo -e "\n${BLUE}📊 QUICK STATUS${NC}"
    echo -e "Files Analyzed: ${CYAN}$(jq -r '.total_files' "$MONITORING_DIR/startup-completion-report.json" 2>/dev/null || echo "unknown")${NC}"
    echo -e "Avg Completion: ${CYAN}$(jq -r '.summary.average_completion' "$MONITORING_DIR/startup-completion-report.json" 2>/dev/null || echo "unknown")%${NC}"
    echo -e "Worktrees Active: ${CYAN}$(git worktree list 2>/dev/null | wc -l || echo "0")${NC}"
    echo -e "Monitoring: ${GREEN}ACTIVE${NC}"
    echo ""
    echo -e "${GREEN}${CHECK} Use './scripts/worktree-task-manager.sh status' for detailed information${NC}"
}

# Run main function
main "$@"