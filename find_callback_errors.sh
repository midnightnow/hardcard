#!/bin/bash

# Find all files that might have useCallback issues
echo "Finding files with potential useCallback issues..."

cd /Users/studio/hardcard/hardcard-suite/apps/vetsorcery

# Search for useCallback patterns that might be missing dependency arrays
grep -r "useCallback" src/ --include="*.tsx" --include="*.ts" | grep -v "}, \[" | grep -v "useCallback from" > callback_issues.txt

echo "Files with potential issues:"
cat callback_issues.txt

# Also check for missing useCallback imports
echo -e "\n\nChecking for missing useCallback imports..."
grep -r "useCallback(" src/ --include="*.tsx" --include="*.ts" | while read -r line; do
  file=$(echo "$line" | cut -d: -f1)
  if ! grep -q "import.*useCallback" "$file"; then
    echo "Missing useCallback import in: $file"
  fi
done