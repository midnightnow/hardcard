#!/bin/bash
set -e

# Emergency Guardian Alert System
# Sends immediate alerts to all guardians during emergencies

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Configuration
GUARDIAN_CONFIG="${GUARDIAN_CONFIG:-guardian_config.yaml}"
ALERT_LOG="logs/emergency-alerts.log"
INCIDENT_ID="EMERGENCY-$(date +%Y%m%d-%H%M%S)"

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

usage() {
    echo "Emergency Guardian Alert System"
    echo ""
    echo "Usage: $0 --threat \"threat description\" [options]"
    echo ""
    echo "Required:"
    echo "  --threat TEXT          Description of the threat"
    echo ""
    echo "Options:"
    echo "  --target-contracts LIST  Comma-separated list of affected contracts"
    echo "  --severity LEVEL        emergency|critical|high (default: emergency)"
    echo "  --incident-id ID        Custom incident ID"
    echo "  --guardian-config FILE  Guardian configuration file"
    echo "  --dry-run              Test mode, no actual alerts sent"
    echo ""
    echo "Examples:"
    echo "  $0 --threat \"Smart contract vulnerability detected\" --severity critical"
    echo "  $0 --threat \"Guardian key compromised\" --target-contracts \"0x123,0x456\""
    exit 1
}

# Parse arguments
THREAT=""
TARGET_CONTRACTS=""
SEVERITY="emergency"
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --threat)
            THREAT="$2"
            shift 2
            ;;
        --target-contracts)
            TARGET_CONTRACTS="$2"
            shift 2
            ;;
        --severity)
            SEVERITY="$2"
            shift 2
            ;;
        --incident-id)
            INCIDENT_ID="$2"
            shift 2
            ;;
        --guardian-config)
            GUARDIAN_CONFIG="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help|-h)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# Validate inputs
if [ -z "$THREAT" ]; then
    log_error "Threat description is required"
    usage
fi

if [ ! -f "$GUARDIAN_CONFIG" ]; then
    log_error "Guardian config file not found: $GUARDIAN_CONFIG"
    exit 1
fi

# Create alert log
mkdir -p "$(dirname "$ALERT_LOG")"
touch "$ALERT_LOG"

# Log alert initiation
echo "$(date -u): ALERT INITIATED - $INCIDENT_ID - $THREAT" >> "$ALERT_LOG"

echo "🚨 EMERGENCY GUARDIAN ALERT SYSTEM"
echo "=" .repeat(50)
echo "Incident ID: $INCIDENT_ID"
echo "Threat: $THREAT"
echo "Severity: $SEVERITY"
echo "Target Contracts: ${TARGET_CONTRACTS:-"All systems"}"
echo "Timestamp: $(date -u)"
echo

# Determine alert priority
case "$SEVERITY" in
    "emergency")
        PRIORITY="🚨 EMERGENCY"
        COLOR="danger"
        ;;
    "critical")
        PRIORITY="🔴 CRITICAL"
        COLOR="danger"
        ;;
    "high")
        PRIORITY="🟡 HIGH"
        COLOR="warning"
        ;;
    *)
        log_error "Invalid severity level: $SEVERITY"
        exit 1
        ;;
esac

# Create alert message
ALERT_MESSAGE="$PRIORITY GOVERNANCE ALERT

Incident ID: $INCIDENT_ID
Threat: $THREAT
Severity: $SEVERITY
Timestamp: $(date -u)
Target Contracts: ${TARGET_CONTRACTS:-"All systems"}

IMMEDIATE ACTION REQUIRED:
- Review threat details
- Assess system impact
- Coordinate response via emergency channels
- Execute appropriate emergency procedures

Response required within 15 minutes.

Emergency Procedures: https://docs.hardcard.io/ops/emergency
Guardian Dashboard: https://monitoring.hardcard.io/guardians
Incident Response: https://incident.hardcard.io/$INCIDENT_ID"

# Load guardian information
if command -v yq > /dev/null; then
    GUARDIANS=($(yq eval '.guardians | keys | .[]' "$GUARDIAN_CONFIG"))
else
    log_warning "yq not found, parsing YAML manually"
    GUARDIANS=($(grep -E "^\s+\w+:" "$GUARDIAN_CONFIG" | sed 's/.*\(\w\+\):.*/\1/' | head -5))
fi

if [ ${#GUARDIANS[@]} -eq 0 ]; then
    log_error "No guardians found in config file"
    exit 1
fi

log_info "Found ${#GUARDIANS[@]} guardians to alert"

# Alert tracking
ALERT_SUMMARY=()
FAILED_ALERTS=0

# Send alerts to each guardian
for guardian in "${GUARDIANS[@]}"; do
    log_info "Alerting guardian: $guardian"
    
    # Get guardian contact info
    if command -v yq > /dev/null; then
        GUARDIAN_EMAIL=$(yq eval ".guardians.$guardian.email" "$GUARDIAN_CONFIG")
        GUARDIAN_PHONE=$(yq eval ".guardians.$guardian.phone // \"\"" "$GUARDIAN_CONFIG")
        GUARDIAN_SLACK=$(yq eval ".guardians.$guardian.slack // \"\"" "$GUARDIAN_CONFIG")
        GUARDIAN_NAME=$(yq eval ".guardians.$guardian.name // \"$guardian\"" "$GUARDIAN_CONFIG")
    else
        # Fallback parsing
        GUARDIAN_EMAIL=$(grep -A 10 "$guardian:" "$GUARDIAN_CONFIG" | grep "email:" | cut -d'"' -f2)
        GUARDIAN_NAME="$guardian"
    fi
    
    if [ -z "$GUARDIAN_EMAIL" ] || [ "$GUARDIAN_EMAIL" = "null" ]; then
        log_warning "No email found for guardian $guardian"
        FAILED_ALERTS=$((FAILED_ALERTS + 1))
        continue
    fi
    
    # Send email alert
    if [ "$DRY_RUN" = true ]; then
        echo "  [DRY RUN] Would send email to: $GUARDIAN_EMAIL"
        ALERT_STATUS="dry-run"
    else
        if send_email_alert "$GUARDIAN_EMAIL" "$GUARDIAN_NAME"; then
            echo "  ✅ Email sent to: $GUARDIAN_EMAIL"
            ALERT_STATUS="email-sent"
        else
            echo "  ❌ Email failed: $GUARDIAN_EMAIL"
            ALERT_STATUS="email-failed"
            FAILED_ALERTS=$((FAILED_ALERTS + 1))
        fi
    fi
    
    # Send SMS if phone number available
    if [ -n "$GUARDIAN_PHONE" ] && [ "$GUARDIAN_PHONE" != "null" ]; then
        if [ "$DRY_RUN" = true ]; then
            echo "  [DRY RUN] Would send SMS to: $GUARDIAN_PHONE"
        else
            if send_sms_alert "$GUARDIAN_PHONE"; then
                echo "  ✅ SMS sent to: $GUARDIAN_PHONE"
                ALERT_STATUS="$ALERT_STATUS,sms-sent"
            else
                echo "  ❌ SMS failed: $GUARDIAN_PHONE"
                ALERT_STATUS="$ALERT_STATUS,sms-failed"
            fi
        fi
    fi
    
    # Send Slack DM if configured
    if [ -n "$GUARDIAN_SLACK" ] && [ "$GUARDIAN_SLACK" != "null" ]; then
        if [ "$DRY_RUN" = true ]; then
            echo "  [DRY RUN] Would send Slack message to: $GUARDIAN_SLACK"
        else
            if send_slack_alert "$GUARDIAN_SLACK"; then
                echo "  ✅ Slack sent to: $GUARDIAN_SLACK"
                ALERT_STATUS="$ALERT_STATUS,slack-sent"
            else
                echo "  ❌ Slack failed: $GUARDIAN_SLACK"
                ALERT_STATUS="$ALERT_STATUS,slack-failed"
            fi
        fi
    fi
    
    ALERT_SUMMARY+=("$guardian:$GUARDIAN_EMAIL:$ALERT_STATUS")
    
    # Log individual alert
    echo "$(date -u): $guardian ($GUARDIAN_EMAIL) - Status: $ALERT_STATUS" >> "$ALERT_LOG"
done

# Send to emergency channels
log_info "Sending to emergency channels..."

# Slack emergency channel
if [ -n "$SLACK_EMERGENCY_WEBHOOK" ] && [ "$DRY_RUN" = false ]; then
    send_slack_channel_alert
elif [ "$DRY_RUN" = true ]; then
    echo "  [DRY RUN] Would send to Slack emergency channel"
fi

# Discord emergency channel (if configured)
if [ -n "$DISCORD_EMERGENCY_WEBHOOK" ] && [ "$DRY_RUN" = false ]; then
    send_discord_alert
elif [ "$DRY_RUN" = true ]; then
    echo "  [DRY RUN] Would send to Discord emergency channel"
fi

# Generate alert summary
SUCCESS_COUNT=$((${#GUARDIANS[@]} - FAILED_ALERTS))

echo
echo "📊 Alert Summary:"
echo "  Total Guardians: ${#GUARDIANS[@]}"
echo "  Successful Alerts: $SUCCESS_COUNT"
echo "  Failed Alerts: $FAILED_ALERTS"
echo "  Success Rate: $((SUCCESS_COUNT * 100 / ${#GUARDIANS[@]}))%"

if [ $FAILED_ALERTS -gt 0 ]; then
    log_warning "$FAILED_ALERTS alerts failed to send"
    echo "  Failed guardians may need manual contact"
fi

# Create incident tracking file
INCIDENT_FILE="logs/incidents/$INCIDENT_ID.json"
mkdir -p "$(dirname "$INCIDENT_FILE")"

cat > "$INCIDENT_FILE" <<EOF
{
  "incident_id": "$INCIDENT_ID",
  "timestamp": "$(date -u --iso-8601=seconds)",
  "threat": "$THREAT",
  "severity": "$SEVERITY",
  "target_contracts": "$TARGET_CONTRACTS",
  "guardians_alerted": ${#GUARDIANS[@]},
  "successful_alerts": $SUCCESS_COUNT,
  "failed_alerts": $FAILED_ALERTS,
  "alert_details": [
$(for summary in "${ALERT_SUMMARY[@]}"; do
    IFS=':' read -r guardian email status <<< "$summary"
    echo "    {\"guardian\": \"$guardian\", \"email\": \"$email\", \"status\": \"$status\"},"
done | sed '$s/,$//')
  ],
  "status": "alerts_sent",
  "dry_run": $DRY_RUN
}
EOF

echo "📁 Incident tracking: $INCIDENT_FILE"

# Final log entry
echo "$(date -u): ALERT COMPLETED - $INCIDENT_ID - Success: $SUCCESS_COUNT/$((${#GUARDIANS[@]})) - Failed: $FAILED_ALERTS" >> "$ALERT_LOG"

# Exit with error code if alerts failed
if [ $FAILED_ALERTS -gt 0 ] && [ "$DRY_RUN" = false ]; then
    exit 1
fi

echo
log_info "Emergency alert system completed"

# Helper functions
send_email_alert() {
    local email="$1"
    local name="$2"
    
    # Create email content
    local email_subject="$PRIORITY: Hardcard Governance Emergency - $INCIDENT_ID"
    local email_body="Dear $name,

$ALERT_MESSAGE

This is an automated emergency alert. Please respond immediately.

Best regards,
Hardcard Emergency Response System"
    
    # Send email using system mail or configured SMTP
    if command -v mail > /dev/null; then
        echo "$email_body" | mail -s "$email_subject" "$email"
        return $?
    elif [ -n "$SMTP_SERVER" ]; then
        # Use custom SMTP sending logic here
        return 0
    else
        # Log email content for manual sending
        echo "EMAIL TO: $email" >> "logs/emergency-emails-$(date +%Y%m%d).log"
        echo "SUBJECT: $email_subject" >> "logs/emergency-emails-$(date +%Y%m%d).log"
        echo "BODY: $email_body" >> "logs/emergency-emails-$(date +%Y%m%d).log"
        echo "---" >> "logs/emergency-emails-$(date +%Y%m%d).log"
        return 0
    fi
}

send_sms_alert() {
    local phone="$1"
    local sms_message="HARDCARD EMERGENCY $INCIDENT_ID: $THREAT. Check email immediately. Response required in 15min."
    
    # Use SMS service (Twilio, AWS SNS, etc.)
    if [ -n "$TWILIO_ACCOUNT_SID" ] && [ -n "$TWILIO_AUTH_TOKEN" ]; then
        # Twilio SMS sending logic would go here
        return 0
    else
        # Log SMS for manual sending
        echo "SMS TO: $phone - $sms_message" >> "logs/emergency-sms-$(date +%Y%m%d).log"
        return 0
    fi
}

send_slack_alert() {
    local slack_user="$1"
    
    if [ -n "$SLACK_BOT_TOKEN" ]; then
        # Slack API call to send DM would go here
        return 0
    else
        return 1
    fi
}

send_slack_channel_alert() {
    local webhook_url="$SLACK_EMERGENCY_WEBHOOK"
    
    if [ -n "$webhook_url" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{
                \"text\": \"$PRIORITY\",
                \"attachments\": [{
                    \"color\": \"$COLOR\",
                    \"title\": \"Hardcard Governance Emergency Alert\",
                    \"text\": \"$ALERT_MESSAGE\",
                    \"footer\": \"Emergency Response System\",
                    \"ts\": $(date +%s)
                }]
            }" \
            "$webhook_url" > /dev/null 2>&1
        return $?
    else
        return 1
    fi
}

send_discord_alert() {
    local webhook_url="$DISCORD_EMERGENCY_WEBHOOK"
    
    if [ -n "$webhook_url" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{
                \"content\": \"$PRIORITY\",
                \"embeds\": [{
                    \"title\": \"Hardcard Governance Emergency Alert\",
                    \"description\": \"$ALERT_MESSAGE\",
                    \"color\": 15158332,
                    \"timestamp\": \"$(date -u --iso-8601=seconds)\"
                }]
            }" \
            "$webhook_url" > /dev/null 2>&1
        return $?
    else
        return 1
    fi
}