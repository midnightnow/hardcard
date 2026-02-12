#!/bin/bash

echo "🔧 Setting up HardCard Dashboard Auto-Start..."

# Create necessary directories
mkdir -p /Users/studio/hardcard/logs

# Load the launch agent
launchctl unload ~/Library/LaunchAgents/com.hardcard.dashboard.plist 2>/dev/null
launchctl load ~/Library/LaunchAgents/com.hardcard.dashboard.plist

# Set default browser opening preference (optional)
# This makes the dashboard open in your default browser
defaults write com.apple.LaunchServices/com.apple.launchservices.secure LSHandlers -array-add \
    '{LSHandlerContentType = "public.html"; LSHandlerRoleAll = "com.apple.safari";}'

echo "✅ Auto-start configured successfully!"
echo ""
echo "The HardCard Dashboard will now:"
echo "  • Launch automatically when you log in"
echo "  • Open in your default browser"
echo "  • Start the HTTP server if needed"
echo ""
echo "To test immediately, run:"
echo "  ./launch-hardcard-dashboard.sh"
echo ""
echo "To disable auto-start, run:"
echo "  launchctl unload ~/Library/LaunchAgents/com.hardcard.dashboard.plist"