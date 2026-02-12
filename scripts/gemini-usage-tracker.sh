#!/bin/bash
# Track Gemini CLI usage for cost management

LOG_FILE="gemini-usage.log"

# Log usage
log_usage() {
    local agent=$1
    local command=$2
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    echo "$timestamp | $agent | $command" >> "$LOG_FILE"
}

# Estimate tokens (rough approximation)
estimate_tokens() {
    local files=$1
    local chars=$(wc -c $files 2>/dev/null | tail -1 | awk '{print $1}')
    local tokens=$((chars / 4))  # Rough estimate: 1 token ≈ 4 chars
    echo "$tokens"
}

# Usage report
generate_report() {
    echo "📊 Gemini Usage Report"
    echo "===================="
    echo ""
    
    # By agent
    echo "Usage by Agent:"
    for agent in frontend backend testing docs security; do
        count=$(grep -c "$agent" "$LOG_FILE" 2>/dev/null || echo "0")
        echo "  $agent: $count requests"
    done
    
    echo ""
    echo "Recent activity:"
    tail -10 "$LOG_FILE"
}

# Main
case "$1" in
    "log")
        log_usage "$2" "$3"
        ;;
    "estimate")
        estimate_tokens "$2"
        ;;
    "report")
        generate_report
        ;;
    *)
        echo "Usage: $0 {log|estimate|report}"
        ;;
esac
