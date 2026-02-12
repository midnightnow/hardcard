#!/bin/bash
# MOEX Intelligence Coordinator

PROJECT_ROOT="/Users/studio/00 Constellation/hardcard"
MOEX_CONFIG="$PROJECT_ROOT/moex-config.yaml"
MOEX_WORKSPACE="$PROJECT_ROOT/moex-workspace"
MOEX_LOG="$PROJECT_ROOT/logs/moex-coordination.log"

# Create workspace and logs
mkdir -p "$MOEX_WORKSPACE" "$PROJECT_ROOT/logs"

# Log function
log_moex() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $message" >> "$MOEX_LOG"
    echo "$message"
}

case "$1" in
    "init")
        log_moex "🧠 Initializing MOEX coordinator..."
        # Initialize coordination workspace
        touch "$MOEX_WORKSPACE/claude-status.json"
        touch "$MOEX_WORKSPACE/gemini-status.json"
        touch "$MOEX_WORKSPACE/coordination-queue.json"
        log_moex "✅ MOEX coordinator initialized"
        ;;
        
    "coordinate")
        if [ -z "$2" ]; then
            echo "Usage: $0 coordinate <task-description>"
            exit 1
        fi
        
        TASK="$2"
        log_moex "🔀 Coordinating task: $TASK"
        
        # Route task based on type
        if [[ "$TASK" =~ (implement|feature|bug|fix) ]]; then
            log_moex "📝 Routing to Claude for implementation"
            # Route to Claude
        elif [[ "$TASK" =~ (analyze|review|optimize|docs) ]]; then
            log_moex "🧠 Routing to Gemini for analysis"
            # Route to Gemini
        else
            log_moex "🤔 Task requires both agents - initiating workflow"
            # Start coordinated workflow
        fi
        ;;
        
    "status")
        log_moex "📊 MOEX Coordination Status:"
        log_moex "  Claude: $(cat $MOEX_WORKSPACE/claude-status.json 2>/dev/null || echo 'Unknown')"
        log_moex "  Gemini: $(cat $MOEX_WORKSPACE/gemini-status.json 2>/dev/null || echo 'Unknown')"
        ;;
        
    "monitor")
        log_moex "👁️ Starting MOEX monitoring dashboard..."
        # Start monitoring loop
        while true; do
            clear
            echo "🧠 MOEX Intelligence Coordinator Dashboard"
            echo "=========================================="
            echo "📅 $(date)"
            echo ""
            echo "🤖 Agent Status:"
            echo "  Claude: $(cat $MOEX_WORKSPACE/claude-status.json 2>/dev/null || echo 'Unknown')"
            echo "  Gemini: $(cat $MOEX_WORKSPACE/gemini-status.json 2>/dev/null || echo 'Unknown')"
            echo ""
            echo "📋 Active Tasks:"
            cat "$MOEX_WORKSPACE/coordination-queue.json" 2>/dev/null || echo "  No active tasks"
            echo ""
            echo "Press Ctrl+C to exit..."
            sleep 5
        done
        ;;
        
    *)
        echo "MOEX Intelligence Coordinator"
        echo "Usage: $0 {init|coordinate|status|monitor}"
        echo ""
        echo "Commands:"
        echo "  init                 - Initialize MOEX coordinator"
        echo "  coordinate <task>    - Coordinate a task between agents"
        echo "  status              - Show current agent status"
        echo "  monitor             - Start monitoring dashboard"
        ;;
esac
