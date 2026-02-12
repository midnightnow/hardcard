#!/bin/bash
set -e

COMMAND=$1
SCENARIO=${2:-"compromised-guardian"}
NETWORK=${3:-"sepolia"}

case $COMMAND in
  start)
    echo "🚨 FIRE DRILL INITIATED"
    echo "=" .repeat(50)
    echo "Scenario: $SCENARIO"
    echo "Network: $NETWORK"
    echo "Start Time: $(date -u)"
    INCIDENT_ID="DRILL-$(date +%Y-%m-%d-%H%M)"
    echo "Incident ID: $INCIDENT_ID"
    
    # Create drill directory
    DRILL_DIR="./drill-$INCIDENT_ID"
    mkdir -p "$DRILL_DIR"
    echo "$INCIDENT_ID" > "$DRILL_DIR/incident-id"
    echo "$SCENARIO" > "$DRILL_DIR/scenario"
    echo "$NETWORK" > "$DRILL_DIR/network"
    echo "$(date -u)" > "$DRILL_DIR/start-time"
    
    # Deploy test contracts if needed
    if [ ! -f "deployments/$NETWORK/GuardianCouncil.json" ]; then
      echo "📜 Deploying contracts to $NETWORK..."
      npx hardhat run scripts/deploy.ts --network $NETWORK
    fi
    
    # Load contract addresses
    if [ -f "deployments/$NETWORK/GuardianCouncil.json" ]; then
      GUARDIAN_COUNCIL=$(jq -r '.address' "deployments/$NETWORK/GuardianCouncil.json")
      echo "GUARDIAN_COUNCIL=$GUARDIAN_COUNCIL" > "$DRILL_DIR/contracts"
    fi
    
    # Start monitoring if available
    if [ -f "./scripts/monitoring/start-monitoring.sh" ]; then
      ./scripts/monitoring/start-monitoring.sh --drill-mode --incident-id "$INCIDENT_ID" &
      echo $! > "$DRILL_DIR/monitoring-pid"
    fi
    
    # Notify participants
    echo "📢 Notifying participants..."
    if command -v curl > /dev/null && [ ! -z "$SLACK_WEBHOOK" ]; then
      curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"🚨 **Fire Drill Started**\\nScenario: $SCENARIO\\nIncident ID: $INCIDENT_ID\\nNetwork: $NETWORK\"}" \
        "$SLACK_WEBHOOK" || echo "Slack notification failed"
    fi
    
    # Create initial drill log
    cat > "$DRILL_DIR/drill-log.md" <<EOF
# Fire Drill Log: $INCIDENT_ID

**Scenario**: $SCENARIO  
**Network**: $NETWORK  
**Start Time**: $(date -u)  

## Timeline

- **$(date -u)**: Drill initiated
EOF
    
    echo "✅ Fire drill setup complete"
    echo "📁 Drill directory: $DRILL_DIR"
    echo "📝 Log updates with: ./fire-drill.sh log [message]"
    echo "🛑 End drill with: ./fire-drill.sh complete $INCIDENT_ID"
    ;;
    
  log)
    # Find active drill
    ACTIVE_DRILL=$(find . -name "drill-DRILL-*" -type d | head -1)
    if [ -z "$ACTIVE_DRILL" ]; then
      echo "❌ No active drill found"
      exit 1
    fi
    
    MESSAGE="$2"
    if [ -z "$MESSAGE" ]; then
      echo "Usage: $0 log \"Your log message\""
      exit 1
    fi
    
    INCIDENT_ID=$(cat "$ACTIVE_DRILL/incident-id")
    echo "- **$(date -u)**: $MESSAGE" >> "$ACTIVE_DRILL/drill-log.md"
    echo "📝 [$INCIDENT_ID] $MESSAGE"
    ;;
    
  status)
    # Find active drill
    ACTIVE_DRILL=$(find . -name "drill-DRILL-*" -type d | head -1)
    if [ -z "$ACTIVE_DRILL" ]; then
      echo "❌ No active drill found"
      exit 1
    fi
    
    INCIDENT_ID=$(cat "$ACTIVE_DRILL/incident-id")
    SCENARIO=$(cat "$ACTIVE_DRILL/scenario")
    START_TIME=$(cat "$ACTIVE_DRILL/start-time")
    
    echo "🔍 DRILL STATUS"
    echo "=" .repeat(30)
    echo "Incident ID: $INCIDENT_ID"
    echo "Scenario: $SCENARIO"
    echo "Start Time: $START_TIME"
    echo "Duration: $(( $(date +%s) - $(date -d "$START_TIME" +%s) )) seconds"
    
    if [ -f "$ACTIVE_DRILL/contracts" ]; then
      echo ""
      echo "📜 Contracts:"
      cat "$ACTIVE_DRILL/contracts"
    fi
    
    echo ""
    echo "📝 Recent log entries:"
    tail -5 "$ACTIVE_DRILL/drill-log.md"
    ;;
    
  complete)
    INCIDENT_ID=$2
    if [ -z "$INCIDENT_ID" ]; then
      # Find active drill
      ACTIVE_DRILL=$(find . -name "drill-DRILL-*" -type d | head -1)
      if [ ! -z "$ACTIVE_DRILL" ]; then
        INCIDENT_ID=$(cat "$ACTIVE_DRILL/incident-id")
      else
        echo "❌ No active drill found and no incident ID provided"
        exit 1
      fi
    fi
    
    DRILL_DIR="./drill-$INCIDENT_ID"
    if [ ! -d "$DRILL_DIR" ]; then
      echo "❌ Drill directory not found: $DRILL_DIR"
      exit 1
    fi
    
    END_TIME=$(date -u)
    START_TIME=$(cat "$DRILL_DIR/start-time")
    DURATION=$(( $(date +%s) - $(date -d "$START_TIME" +%s) ))
    
    echo "✅ FIRE DRILL COMPLETE"
    echo "=" .repeat(50)
    echo "Incident ID: $INCIDENT_ID"
    echo "End Time: $END_TIME"
    echo "Duration: ${DURATION}s ($(( DURATION / 60 ))m $(( DURATION % 60 ))s)"
    
    # Complete the drill log
    cat >> "$DRILL_DIR/drill-log.md" <<EOF

## Summary

- **End Time**: $END_TIME
- **Total Duration**: ${DURATION}s ($(( DURATION / 60 ))m $(( DURATION % 60 ))s)

## Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Total Time | < 30 min | $(( DURATION / 60 ))m | $([ $DURATION -lt 1800 ] && echo "✅ PASS" || echo "❌ FAIL") |

## Action Items

- [ ] Review performance metrics
- [ ] Update procedures based on lessons learned
- [ ] Schedule next drill

## Files Generated

$(find "$DRILL_DIR" -type f | sed 's/^/- /')
EOF
    
    # Stop monitoring if running
    if [ -f "$DRILL_DIR/monitoring-pid" ]; then
      MONITORING_PID=$(cat "$DRILL_DIR/monitoring-pid")
      if kill -0 "$MONITORING_PID" 2>/dev/null; then
        kill "$MONITORING_PID"
        echo "🔌 Monitoring stopped"
      fi
      rm -f "$DRILL_DIR/monitoring-pid"
    fi
    
    # Generate summary report
    ./fire-drills/generate-drill-report.sh "$DRILL_DIR" > "reports/drill-$INCIDENT_ID-summary.md"
    
    # Notify completion
    if command -v curl > /dev/null && [ ! -z "$SLACK_WEBHOOK" ]; then
      curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"✅ **Fire Drill Complete**\\nIncident ID: $INCIDENT_ID\\nDuration: $(( DURATION / 60 ))m $(( DURATION % 60 ))s\\nStatus: $([ $DURATION -lt 1800 ] && echo "PASS" || echo "FAIL")\"}" \
        "$SLACK_WEBHOOK" || echo "Slack notification failed"
    fi
    
    # Archive drill directory
    ARCHIVE_DIR="./drill-archives"
    mkdir -p "$ARCHIVE_DIR"
    mv "$DRILL_DIR" "$ARCHIVE_DIR/"
    
    echo "📁 Drill archived to: $ARCHIVE_DIR/drill-$INCIDENT_ID"
    echo "📊 Summary report: reports/drill-$INCIDENT_ID-summary.md"
    ;;
    
  list)
    echo "🗂️  DRILL HISTORY"
    echo "=" .repeat(30)
    
    if [ -d "./drill-archives" ]; then
      for drill_dir in ./drill-archives/drill-DRILL-*; do
        if [ -d "$drill_dir" ]; then
          INCIDENT_ID=$(basename "$drill_dir" | sed 's/drill-//')
          if [ -f "$drill_dir/scenario" ] && [ -f "$drill_dir/start-time" ]; then
            SCENARIO=$(cat "$drill_dir/scenario")
            START_TIME=$(cat "$drill_dir/start-time")
            echo "$INCIDENT_ID - $SCENARIO - $START_TIME"
          fi
        fi
      done
    else
      echo "No drill history found"
    fi
    ;;
    
  clean)
    echo "🧹 Cleaning up drill artifacts..."
    
    # Remove active drills (with confirmation)
    if find . -name "drill-DRILL-*" -type d | grep -q .; then
      echo "Found active drill directories:"
      find . -name "drill-DRILL-*" -type d
      echo "This will remove all active drills. Continue? (y/N)"
      read -r response
      if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
        find . -name "drill-DRILL-*" -type d -exec rm -rf {} +
        echo "✅ Active drills cleaned up"
      else
        echo "Cleanup cancelled"
      fi
    else
      echo "No active drills to clean"
    fi
    ;;
    
  *)
    echo "Hardcard Guardian Fire Drill Manager"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  start [scenario] [network]  - Start a new fire drill"
    echo "  log \"message\"               - Add entry to active drill log"
    echo "  status                      - Show current drill status"
    echo "  complete [incident-id]      - End the drill and generate report"
    echo "  list                        - Show drill history"
    echo "  clean                       - Clean up drill artifacts"
    echo ""
    echo "Scenarios:"
    echo "  compromised-guardian        - Guardian key compromised"
    echo "  unresponsive-guardian       - Guardian not responding"
    echo "  multiple-rotation           - Multiple guardians need rotation"
    echo "  planned-rotation            - Scheduled key rotation"
    echo ""
    echo "Examples:"
    echo "  $0 start compromised-guardian sepolia"
    echo "  $0 log \"Guardian 3 key generated\""
    echo "  $0 complete"
    echo ""
    exit 1
    ;;
esac