#!/bin/bash

echo "Updating all HARDCARDSUITE references to hardcard..."

# Update all text files
find . -type f \( -name "*.js" -o -name "*.ts" -o -name "*.tsx" -o -name "*.json" -o -name "*.md" -o -name "*.sh" -o -name "*.py" -o -name "*.yml" -o -name "*.yaml" \) -exec grep -l "HARDCARDSUITE" {} \; | while read file; do
    echo "Updating $file..."
    sed -i '' 's|/HARDCARDSUITE/|/hardcard/|g' "$file" 2>/dev/null || true
    sed -i '' 's|HARDCARDSUITE|hardcard|g' "$file" 2>/dev/null || true
done

echo "Path updates complete!"