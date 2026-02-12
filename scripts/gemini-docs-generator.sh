#!/bin/bash
# Gemini-powered documentation generation

PROJECT_ROOT="/Users/studio/00 Constellation/hardcard"
DOCS_DIR="$PROJECT_ROOT/docs/generated"
SRC_DIR="$PROJECT_ROOT/src"

mkdir -p "$DOCS_DIR"

echo "🧠 Generating documentation with Gemini..."

# API documentation
echo "📝 Generating API documentation..."
gemini docs \
    --input "$SRC_DIR" \
    --output "$DOCS_DIR/api" \
    --type api \
    --format markdown \
    --include-examples

# Component documentation
echo "🧩 Generating component documentation..."
gemini docs \
    --input "$SRC_DIR/components" \
    --output "$DOCS_DIR/components" \
    --type components \
    --format markdown \
    --include-props

# Architecture documentation
echo "🏗️ Generating architecture documentation..."
gemini docs \
    --input "$SRC_DIR" \
    --output "$DOCS_DIR/architecture" \
    --type architecture \
    --format markdown \
    --include-diagrams

echo "✅ Documentation generation complete. Files saved to $DOCS_DIR"
