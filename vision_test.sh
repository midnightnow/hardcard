#!/bin/bash

# Vision Testing Protocol for HardCard Suite
# Tests web applications and generates assessment reports

set -e

# Configuration
SCREENSHOT_DIR="/Users/studio/hardcard/screenshots"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="$SCREENSHOT_DIR/test_report_$TIMESTAMP.md"

# URLs to test
URLS_main_app="http://localhost:5173"
URLS_databutton_app="http://localhost:3001" 
URLS_hardcard_suite="http://localhost:3002"

URL_NAMES="main_app databutton_app hardcard_suite"

# Create screenshots directory
mkdir -p "$SCREENSHOT_DIR"

echo "=== HardCard Suite Vision Testing Protocol ===" | tee "$REPORT_FILE"
echo "Started at: $(date)" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# Function to test URL
test_url() {
    local name="$1"
    local url="$2"
    
    echo "Testing $name ($url)..." | tee -a "$REPORT_FILE"
    
    # Test HTTP response
    if response=$(curl -s -w "%{http_code}:%{time_total}" --connect-timeout 10 "$url" 2>/dev/null); then
        http_code="${response##*:}"
        response_time="${response%:*}"
        response_time="${response_time##*:}"
        content="${response%:*:*}"
        
        echo "  ✓ HTTP Status: $http_code" | tee -a "$REPORT_FILE"
        echo "  ✓ Response Time: ${response_time}s" | tee -a "$REPORT_FILE"
        
        # Extract title
        title=$(echo "$content" | grep -o '<title[^>]*>[^<]*</title>' | sed 's/<[^>]*>//g' || echo "No title found")
        echo "  ✓ Title: $title" | tee -a "$REPORT_FILE"
        
        # Check content length
        content_length=${#content}
        echo "  ✓ Content Length: $content_length bytes" | tee -a "$REPORT_FILE"
        
        # Basic health checks
        if [[ $http_code == "200" ]]; then
            echo "  ✅ Status: ONLINE" | tee -a "$REPORT_FILE"
            
            # Check for common issues
            if echo "$content" | grep -qi "error\|exception"; then
                echo "  ⚠️  Warning: Error messages detected in HTML" | tee -a "$REPORT_FILE"
            fi
            
            if [[ $content_length -lt 100 ]]; then
                echo "  ⚠️  Warning: Very little content detected" | tee -a "$REPORT_FILE"
            fi
            
            return 0
        else
            echo "  ❌ Status: ERROR (HTTP $http_code)" | tee -a "$REPORT_FILE"
            return 1
        fi
    else
        echo "  ❌ Status: OFFLINE (Connection failed)" | tee -a "$REPORT_FILE"
        return 1
    fi
}

# Function to take screenshot using AppleScript (for macOS)
take_screenshot() {
    local name="$1"
    local url="$2"
    
    echo "Taking screenshot of $name..." | tee -a "$REPORT_FILE"
    
    # Open URL in default browser and take screenshot
    screenshot_file="$SCREENSHOT_DIR/${name}_${TIMESTAMP}.png"
    
    # Use AppleScript to open URL and take screenshot
    osascript <<EOF
tell application "Safari"
    activate
    set myTab to make new document with properties {URL:"$url"}
    delay 3
end tell

tell application "System Events"
    do shell script "screencapture -x '$screenshot_file'"
end tell
EOF
    
    if [[ -f "$screenshot_file" ]]; then
        echo "  ✓ Screenshot saved: $screenshot_file" | tee -a "$REPORT_FILE"
    else
        echo "  ❌ Screenshot failed" | tee -a "$REPORT_FILE"
    fi
}

# Test all applications
online_count=0
total_count=3

echo "## Application Status" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

for app_name in $URL_NAMES; do
    eval "url=\$URLS_$app_name"
    echo "" | tee -a "$REPORT_FILE"
    
    if test_url "$app_name" "$url"; then
        ((online_count++))
    fi
    
    echo "" | tee -a "$REPORT_FILE"
done

# Generate summary
echo "" | tee -a "$REPORT_FILE"
echo "## Summary" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"
echo "- Total Applications: $total_count" | tee -a "$REPORT_FILE"
echo "- Online: $online_count" | tee -a "$REPORT_FILE"
echo "- Offline: $((total_count - online_count))" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# Generate recommendations
echo "## Recommendations" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

if [[ $online_count -eq $total_count ]]; then
    echo "✅ All applications are online and responding properly." | tee -a "$REPORT_FILE"
elif [[ $online_count -gt 0 ]]; then
    echo "⚠️  $((total_count - online_count)) of $total_count applications need attention." | tee -a "$REPORT_FILE"
    echo "- Check server logs for offline applications" | tee -a "$REPORT_FILE"
    echo "- Verify port configurations and dependencies" | tee -a "$REPORT_FILE"
else
    echo "🔴 All applications are offline - check development environment." | tee -a "$REPORT_FILE"
    echo "- Verify all services are running" | tee -a "$REPORT_FILE"
    echo "- Check for port conflicts" | tee -a "$REPORT_FILE"
    echo "- Review startup scripts and dependencies" | tee -a "$REPORT_FILE"
fi

echo "" | tee -a "$REPORT_FILE"
echo "Report saved to: $REPORT_FILE" | tee -a "$REPORT_FILE"

# Make screenshots accessible
echo "" | tee -a "$REPORT_FILE"
echo "Screenshots saved in: $SCREENSHOT_DIR" | tee -a "$REPORT_FILE"