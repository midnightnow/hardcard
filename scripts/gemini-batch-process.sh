#!/bin/bash
# Batch process files with Gemini CLI

echo "🔄 Gemini Batch Processor"
echo "======================="
echo ""
echo "Select task:"
echo "1) Add TypeScript types to all components"
echo "2) Generate tests for all components"
echo "3) Add documentation to all functions"
echo "4) Security audit all files"
echo "5) Performance review all components"
echo ""
read -p "Choice (1-5): " choice

case $choice in
    1)
        prompt="Add comprehensive TypeScript types"
        pattern="*.tsx"
        ;;
    2)
        prompt="Generate comprehensive unit tests"
        pattern="*.tsx"
        ;;
    3)
        prompt="Add JSDoc documentation"
        pattern="*.ts"
        ;;
    4)
        prompt="Security audit this file"
        pattern="*"
        ;;
    5)
        prompt="Review for performance issues"
        pattern="*.tsx"
        ;;
esac

echo ""
echo "Processing files matching: $pattern"
echo "Prompt: $prompt"
echo ""

# Process files
find . -name "$pattern" -type f | while read -r file; do
    echo "Processing: $file"
    gemini -p "$prompt" "$file" > "${file}.gemini-output.md"
    echo "Output saved to: ${file}.gemini-output.md"
done

echo ""
echo "✅ Batch processing complete!"
