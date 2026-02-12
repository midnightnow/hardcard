#!/bin/bash
# 🔄 Claude Continuous Monitor - Real-time system monitoring and performance tracking
# Runs in background to continuously monitor the multi-agent worktree system

set -e

PROJECT_ROOT="/Users/studio/hardcard"
MONITORING_DIR="$PROJECT_ROOT/monitoring"
PERFORMANCE_DIR="$PROJECT_ROOT/performance"
ALERTS_DIR="$PROJECT_ROOT/alerts"
LOG_FILE="$MONITORING_DIR/continuous-monitor.log"

# Ensure directories exist
mkdir -p "$MONITORING_DIR" "$PERFORMANCE_DIR" "$ALERTS_DIR"

# Configuration
MONITOR_INTERVAL=300  # 5 minutes
PERFORMANCE_SAMPLE_INTERVAL=60  # 1 minute
ALERT_COOLDOWN=1800  # 30 minutes

# Colors for logging
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Emojis
MONITOR="👁️"
ALERT="🚨"
CHECK="✅"
WARNING="⚠️"
CHART="📊"

# Log with timestamp
log_monitor() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $message" >> "$LOG_FILE"
    if [ "${2:-}" = "echo" ]; then
        echo -e "[$timestamp] $message"
    fi
}

# Performance metrics collection
collect_performance_metrics() {
    local timestamp=$(date -Iseconds)
    local metrics_file="$PERFORMANCE_DIR/metrics-$(date +%Y%m%d).jsonl"
    
    # System metrics
    local cpu_usage=$(top -l 1 -s 0 | grep "CPU usage" | awk '{print $3}' | sed 's/%//' || echo "0")
    local memory_pressure=$(memory_pressure | grep "System-wide memory free percentage" | awk '{print $5}' | sed 's/%//' || echo "100")
    local disk_usage=$(df "$PROJECT_ROOT" | tail -1 | awk '{print $5}' | sed 's/%//')
    
    # Git worktree metrics
    local worktree_count=$(git worktree list 2>/dev/null | wc -l || echo "0")
    local total_changes=0
    
    # Count uncommitted changes across all worktrees
    for agent in frontend-ai backend-ai testing-ai docs-ai security-ai; do
        local agent_dir="/Users/studio/hardcard-${agent}"
        if [ -d "$agent_dir" ]; then
            cd "$agent_dir"
            local changes=$(git status --porcelain 2>/dev/null | wc -l || echo "0")
            total_changes=$((total_changes + changes))
            cd "$PROJECT_ROOT"
        fi
    done
    
    # Project metrics (if completion report exists)
    local completion_avg="null"
    local critical_issues="null"
    local production_ready="null"
    
    if [ -f "$MONITORING_DIR/startup-completion-report.json" ]; then
        completion_avg=$(jq -r '.summary.average_completion' "$MONITORING_DIR/startup-completion-report.json" 2>/dev/null || echo "null")
        critical_issues=$(jq -r '.summary.critical_issues | length' "$MONITORING_DIR/startup-completion-report.json" 2>/dev/null || echo "null")
        production_ready=$(jq -r '.summary.ready_for_production' "$MONITORING_DIR/startup-completion-report.json" 2>/dev/null || echo "null")
    fi
    
    # Write metrics
    cat >> "$metrics_file" << EOF
{"timestamp": "$timestamp", "type": "performance", "cpu_usage": $cpu_usage, "memory_free": $memory_pressure, "disk_usage": $disk_usage, "worktree_count": $worktree_count, "uncommitted_changes": $total_changes, "completion_avg": $completion_avg, "critical_issues": $critical_issues, "production_ready": $production_ready}
EOF
    
    log_monitor "${CHART} Metrics collected: CPU $cpu_usage%, Memory ${memory_pressure}% free, Disk $disk_usage%, $total_changes changes"
}

# Check for alerts
check_alerts() {
    local timestamp=$(date -Iseconds)
    local alert_file="$ALERTS_DIR/alerts-$(date +%Y%m%d).jsonl"
    local config_file="$MONITORING_DIR/config.json"
    
    # Load configuration
    local disk_threshold=85
    local completion_threshold=70
    local security_threshold=0
    
    if [ -f "$config_file" ]; then
        disk_threshold=$(jq -r '.alerts.disk_usage_threshold' "$config_file" 2>/dev/null || echo "85")
        completion_threshold=$(jq -r '.alerts.completion_threshold' "$config_file" 2>/dev/null || echo "70")
        security_threshold=$(jq -r '.alerts.security_issues_threshold' "$config_file" 2>/dev/null || echo "0")
    fi
    
    # Check disk usage
    local disk_usage=$(df "$PROJECT_ROOT" | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$disk_usage" -gt "$disk_threshold" ]; then
        local alert_id="disk_usage_high"
        if ! recent_alert "$alert_id"; then
            log_monitor "${ALERT} ALERT: Disk usage $disk_usage% exceeds threshold $disk_threshold%" echo
            cat >> "$alert_file" << EOF
{"timestamp": "$timestamp", "type": "disk_usage", "severity": "warning", "message": "Disk usage $disk_usage% exceeds threshold $disk_threshold%", "value": $disk_usage, "threshold": $disk_threshold}
EOF
            mark_alert_sent "$alert_id"
        fi
    fi
    
    # Check completion metrics (if available)
    if [ -f "$MONITORING_DIR/startup-completion-report.json" ]; then
        local avg_completion=$(jq -r '.summary.average_completion' "$MONITORING_DIR/startup-completion-report.json" 2>/dev/null || echo "100")
        local critical_issues=$(jq -r '.summary.critical_issues | length' "$MONITORING_DIR/startup-completion-report.json" 2>/dev/null || echo "0")
        
        # Low completion alert
        if [ "$(echo "$avg_completion < $completion_threshold" | bc)" -eq 1 ]; then
            local alert_id="completion_low"
            if ! recent_alert "$alert_id"; then
                log_monitor "${ALERT} ALERT: Average completion $avg_completion% below threshold $completion_threshold%" echo
                cat >> "$alert_file" << EOF
{"timestamp": "$timestamp", "type": "completion", "severity": "warning", "message": "Average completion $avg_completion% below threshold $completion_threshold%", "value": $avg_completion, "threshold": $completion_threshold}
EOF
                mark_alert_sent "$alert_id"
            fi
        fi
        
        # Security issues alert
        if [ "$critical_issues" -gt "$security_threshold" ]; then
            local alert_id="security_issues"
            if ! recent_alert "$alert_id"; then
                log_monitor "${ALERT} ALERT: $critical_issues critical security issues found" echo
                cat >> "$alert_file" << EOF
{"timestamp": "$timestamp", "type": "security", "severity": "critical", "message": "$critical_issues critical security issues found", "value": $critical_issues, "threshold": $security_threshold}
EOF
                mark_alert_sent "$alert_id"
            fi
        fi
    fi
    
    # Check for stuck agents (no commits in 24 hours)
    for agent in frontend-ai backend-ai testing-ai docs-ai security-ai; do
        local agent_dir="/Users/studio/hardcard-${agent}"
        if [ -d "$agent_dir" ]; then
            cd "$agent_dir"
            local last_commit_time=$(git log -1 --format="%ct" 2>/dev/null || echo "0")
            local current_time=$(date +%s)
            local hours_since=$((( current_time - last_commit_time ) / 3600))
            
            if [ "$hours_since" -gt 24 ] && [ "$last_commit_time" -gt 0 ]; then
                local alert_id="agent_inactive_$agent"
                if ! recent_alert "$alert_id"; then
                    log_monitor "${WARNING} ALERT: Agent $agent inactive for $hours_since hours" echo
                    cat >> "$alert_file" << EOF
{"timestamp": "$timestamp", "type": "agent_inactive", "severity": "info", "message": "Agent $agent inactive for $hours_since hours", "agent": "$agent", "hours": $hours_since}
EOF
                    mark_alert_sent "$alert_id"
                fi
            fi
            cd "$PROJECT_ROOT"
        fi
    done
}

# Check if alert was recently sent
recent_alert() {
    local alert_id="$1"
    local alert_file="$ALERTS_DIR/recent-alerts.txt"
    local current_time=$(date +%s)
    
    if [ -f "$alert_file" ]; then
        while IFS= read -r line; do
            if [ -n "$line" ]; then
                local stored_id=$(echo "$line" | cut -d: -f1)
                local stored_time=$(echo "$line" | cut -d: -f2)
                
                if [ "$stored_id" = "$alert_id" ]; then
                    local time_diff=$((current_time - stored_time))
                    if [ "$time_diff" -lt "$ALERT_COOLDOWN" ]; then
                        return 0  # Alert was recent
                    fi
                fi
            fi
        done < "$alert_file"
    fi
    
    return 1  # Alert was not recent
}

# Mark alert as sent
mark_alert_sent() {
    local alert_id="$1"
    local alert_file="$ALERTS_DIR/recent-alerts.txt"
    local current_time=$(date +%s)
    
    # Remove old entry if exists
    if [ -f "$alert_file" ]; then
        grep -v "^$alert_id:" "$alert_file" > "$alert_file.tmp" 2>/dev/null || true
        mv "$alert_file.tmp" "$alert_file" 2>/dev/null || true
    fi
    
    # Add new entry
    echo "$alert_id:$current_time" >> "$alert_file"
}

# Health check for all components
health_check() {
    local timestamp=$(date -Iseconds)
    local health_file="$MONITORING_DIR/health-check.json"
    local overall_status="healthy"
    local issues=()
    
    # Check worktrees
    local expected_worktrees=6
    local actual_worktrees=$(git worktree list 2>/dev/null | wc -l || echo "0")
    if [ "$actual_worktrees" -ne "$expected_worktrees" ]; then
        overall_status="degraded"
        issues+=("Missing worktrees: expected $expected_worktrees, found $actual_worktrees")
    fi
    
    # Check agent directories and STATUS files
    for agent in frontend-ai backend-ai testing-ai docs-ai security-ai; do
        local agent_dir="/Users/studio/hardcard-${agent}"
        if [ ! -d "$agent_dir" ]; then
            overall_status="degraded"
            issues+=("Agent directory missing: $agent_dir")
        elif [ ! -f "$agent_dir/STATUS.md" ]; then
            overall_status="degraded"
            issues+=("STATUS.md missing for agent: $agent")
        fi
    done
    
    # Check script availability
    local required_scripts=("page-completion-tracker.py" "worktree-task-manager.sh" "agent-coordinator.sh")
    for script in "${required_scripts[@]}"; do
        if [ ! -f "$PROJECT_ROOT/scripts/$script" ]; then
            overall_status="critical"
            issues+=("Required script missing: $script")
        fi
    done
    
    # Generate health report
    local issues_json=$(printf '%s\n' "${issues[@]}" | jq -R . | jq -s .)
    cat > "$health_file" << EOF
{
  "timestamp": "$timestamp",
  "overall_status": "$overall_status",
  "components": {
    "worktrees": {
      "expected": $expected_worktrees,
      "actual": $actual_worktrees,
      "status": "$([ "$actual_worktrees" -eq "$expected_worktrees" ] && echo "healthy" || echo "degraded")"
    },
    "monitoring": {
      "status": "healthy",
      "uptime_seconds": $(ps -o etime= -p $$ | tr -d ' ' | awk -F: '{if (NF==2) print $1*60+$2; else if (NF==3) print $1*3600+$2*60+$3}')
    }
  },
  "issues": $issues_json,
  "issues_count": ${#issues[@]}
}
EOF
    
    log_monitor "${CHECK} Health check completed: $overall_status (${#issues[@]} issues)"
    
    return $([ "$overall_status" = "healthy" ] && echo 0 || echo 1)
}

# Cleanup old files
cleanup_old_files() {
    local days_to_keep=30
    
    # Clean old log files
    find "$MONITORING_DIR" -name "*.log" -mtime +$days_to_keep -delete 2>/dev/null || true
    
    # Clean old metric files (keep 90 days)
    find "$PERFORMANCE_DIR" -name "metrics-*.jsonl" -mtime +90 -delete 2>/dev/null || true
    
    # Clean old alert files (keep 365 days)
    find "$ALERTS_DIR" -name "alerts-*.jsonl" -mtime +365 -delete 2>/dev/null || true
    
    log_monitor "${CHECK} Cleanup completed: removed files older than $days_to_keep days"
}

# Performance optimization suggestions
analyze_performance() {
    local perf_file="$PERFORMANCE_DIR/performance-analysis.json"
    local timestamp=$(date -Iseconds)
    
    # Analyze recent metrics
    local today_metrics="$PERFORMANCE_DIR/metrics-$(date +%Y%m%d).jsonl"
    if [ -f "$today_metrics" ]; then
        # Calculate averages
        local avg_cpu=$(cat "$today_metrics" | jq -r '.cpu_usage' | awk '{sum+=$1} END {print sum/NR}' 2>/dev/null || echo "0")
        local avg_disk=$(cat "$today_metrics" | jq -r '.disk_usage' | awk '{sum+=$1} END {print sum/NR}' 2>/dev/null || echo "0")
        local max_changes=$(cat "$today_metrics" | jq -r '.uncommitted_changes' | sort -n | tail -1 || echo "0")
        
        # Generate recommendations
        local recommendations=()
        if [ "$(echo "$avg_cpu > 80" | bc)" -eq 1 ]; then
            recommendations+=("High CPU usage detected ($avg_cpu%). Consider reducing background processes.")
        fi
        if [ "$(echo "$avg_disk > 85" | bc)" -eq 1 ]; then
            recommendations+=("High disk usage ($avg_disk%). Consider cleaning up old files or increasing storage.")
        fi
        if [ "$max_changes" -gt 50 ]; then
            recommendations+=("High number of uncommitted changes ($max_changes). Agents should commit more frequently.")
        fi
        
        # Generate performance report
        local recommendations_json=$(printf '%s\n' "${recommendations[@]}" | jq -R . | jq -s .)
        cat > "$perf_file" << EOF
{
  "timestamp": "$timestamp",
  "analysis_period": "today",
  "metrics": {
    "average_cpu_usage": $avg_cpu,
    "average_disk_usage": $avg_disk,
    "max_uncommitted_changes": $max_changes
  },
  "recommendations": $recommendations_json,
  "performance_score": $(echo "100 - ($avg_cpu * 0.4) - ($avg_disk * 0.4) - ($max_changes * 0.2)" | bc | cut -d. -f1)
}
EOF
        
        log_monitor "${CHART} Performance analysis completed. Score: $(jq -r '.performance_score' "$perf_file")/100"
    fi
}

# Signal handlers
cleanup_and_exit() {
    log_monitor "${WARNING} Continuous monitor stopping..." echo
    rm -f "$MONITORING_DIR/monitor.pid"
    exit 0
}

trap cleanup_and_exit SIGTERM SIGINT

# Main monitoring loop
main() {
    log_monitor "${MONITOR} Claude Continuous Monitor started (PID: $$)" echo
    
    local cycle_count=0
    local last_performance_sample=0
    local last_cleanup=$(date +%s)
    
    while true; do
        cycle_count=$((cycle_count + 1))
        local current_time=$(date +%s)
        
        # Performance sampling (every minute)
        if [ $((current_time - last_performance_sample)) -ge $PERFORMANCE_SAMPLE_INTERVAL ]; then
            collect_performance_metrics
            last_performance_sample=$current_time
        fi
        
        # Full monitoring cycle (every 5 minutes)
        if [ $((cycle_count % 5)) -eq 0 ]; then
            log_monitor "${MONITOR} Running monitoring cycle $cycle_count"
            
            # Health check
            health_check
            
            # Check for alerts
            check_alerts
            
            # Performance analysis
            analyze_performance
        fi
        
        # Daily cleanup (once per day)
        if [ $((current_time - last_cleanup)) -ge 86400 ]; then
            cleanup_old_files
            last_cleanup=$current_time
        fi
        
        # Sleep for 1 minute
        sleep 60
    done
}

# Start monitoring
main "$@"