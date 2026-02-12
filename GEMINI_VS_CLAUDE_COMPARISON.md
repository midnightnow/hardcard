# 🔄 Gemini CLI vs Claude Code Comparison

## Quick Reference

| Feature | Claude Code | Gemini CLI |
|---------|------------|------------|
| Cost | Paid subscription | Free tier available |
| Context Window | Large | Very large |
| File Access | Automatic | Manual with -a flag |
| IDE Integration | Native | Command line only |
| Speed | Fast | Fast |
| Code Understanding | Excellent | Excellent |

## When to Use Each

### Use Claude Code for:
- Integrated development experience
- Complex multi-file refactoring
- Real-time code assistance
- Native file system access

### Use Gemini CLI for:
- Batch processing
- Cost-sensitive operations
- Scriptable workflows
- CI/CD integration

## Equivalent Commands

### Claude Code
```
"Please analyze all TypeScript files and fix errors"
```

### Gemini CLI
```bash
gemini -a -p "Analyze all TypeScript files and provide fixes"
```

### File-Specific Work

**Claude Code**: Automatically sees current file
**Gemini CLI**: Must specify file path
```bash
gemini -p "Review this component" src/Component.tsx
```

## Cost Optimization Strategies

### Gemini CLI Tips:
1. **Avoid -a flag** when possible (includes all files)
2. **Target specific files** to reduce token usage
3. **Batch similar operations** together
4. **Use incremental processing** for large tasks

### Free Tier Management:
- Track usage with `gemini-usage-tracker.sh`
- Process critical files first
- Use specific, focused prompts
- Leverage caching for repeated analysis

## Workflow Integration

### Morning Routine
```bash
# Check agent status
./scripts/agent-coordinator.sh status

# Launch Gemini agent
./launch-gemini-agent.sh

# Run focused analysis
cd ../hardcard-frontend-ai
gemini -p "Review STATUS.md and continue work"
```

### Batch Operations
```bash
# Process all test files
find . -name "*.test.ts" | xargs -I {} gemini -p "Add missing tests" {}

# Generate documentation
gemini -a -p "Generate comprehensive documentation"
```

## Best Practices

1. **Context Setting**: Always include agent role in prompts
2. **Output Format**: Request structured output (JSON/Markdown)
3. **Incremental Work**: Process in chunks to manage costs
4. **Version Control**: Commit frequently
5. **Documentation**: Update STATUS.md after each session

---

Both tools are excellent - choose based on your needs and budget!
