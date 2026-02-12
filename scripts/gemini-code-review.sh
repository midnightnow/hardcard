#!/bin/bash
# Gemini-powered code review automation

if [ -z "$1" ]; then
    echo "Usage: $0 <file-or-directory>"
    exit 1
fi

TARGET="$1"
PROJECT_ROOT="/Users/studio/00 Constellation/hardcard"
REVIEW_DIR="$PROJECT_ROOT/reviews"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')

mkdir -p "$REVIEW_DIR"

echo "🧠 Starting Gemini code review for: $TARGET"

# Comprehensive code review
gemini review \
    --input "$TARGET" \
    --focus "security,performance,maintainability,best-practices" \
    --output "$REVIEW_DIR/review_${TIMESTAMP}.md" \
    --format markdown \
    --include-suggestions \
    --include-examples

echo "✅ Code review complete. Report saved to $REVIEW_DIR/review_${TIMESTAMP}.md"
