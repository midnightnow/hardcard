#!/bin/bash
# Setup Gemini CLI configurations for each AI agent
# Free alternative to Claude Code

set -e

echo "🤖 Setting up Gemini CLI configurations for AI agents..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to create agent-specific GEMINI.md
create_agent_gemini_config() {
    local agent_type=$1
    local agent_dir=$2
    local branch=$3
    local focus_area=$4
    local specific_tasks=$5
    
    cat > "$agent_dir/GEMINI.md" << EOF
# Gemini CLI Configuration - $agent_type Agent

## 🤖 Agent Identity

**You are the $agent_type Specialist AI Agent**
- **Working Directory**: \`$agent_dir\`
- **Branch**: \`$branch\`
- **Focus Area**: $focus_area

## 🎯 Your Mission

You specialize in $focus_area. Your primary responsibilities:
$specific_tasks

## 🛠️ Gemini CLI Commands

### Essential Commands for $agent_type
EOF

    # Add agent-specific commands
    case $agent_type in
        "Frontend")
            cat >> "$agent_dir/GEMINI.md" << 'EOF'

```bash
# Analyze all TypeScript files
gemini -a -p "Analyze TypeScript code for strict mode compatibility"

# Review specific component
gemini -p "Review and improve this React component" src/components/Example.tsx

# Performance analysis
gemini -a -p "Identify performance bottlenecks in React components"

# Generate tests
gemini -p "Generate comprehensive tests for this component" src/components/Example.tsx

# Accessibility audit
gemini -a -p "Audit components for WCAG compliance"
```

### Common Tasks
1. **TypeScript Migration**
   ```bash
   gemini -p "Migrate to TypeScript strict mode" src/components/Dashboard.tsx
   ```

2. **Component Optimization**
   ```bash
   gemini -a -p "Optimize React components for performance"
   ```

3. **Code Review**
   ```bash
   gemini -p "Review this code for best practices" $(git diff --name-only)
   ```
EOF
            ;;
            
        "Backend")
            cat >> "$agent_dir/GEMINI.md" << 'EOF'

```bash
# Analyze Python code
gemini -a -p "Review Python code for type hints and best practices"

# API documentation
gemini -p "Generate OpenAPI documentation" app/apis/

# Database optimization
gemini -a -p "Analyze and optimize database queries"

# Security review
gemini -p "Security audit for API endpoints" app/apis/

# Add Pydantic models
gemini -p "Create Pydantic models for data validation" app/models/
```

### Common Tasks
1. **Type Hints**
   ```bash
   gemini -p "Add comprehensive type hints" app/apis/users.py
   ```

2. **API Design**
   ```bash
   gemini -a -p "Review API design for RESTful best practices"
   ```

3. **Performance**
   ```bash
   gemini -p "Optimize this endpoint for performance" app/apis/data.py
   ```
EOF
            ;;
            
        "Testing")
            cat >> "$agent_dir/GEMINI.md" << 'EOF'

```bash
# Generate test suites
gemini -a -p "Generate comprehensive test suites for uncovered code"

# E2E scenarios
gemini -p "Create E2E test scenarios" tests/e2e/

# Coverage analysis
gemini -a -p "Analyze test coverage and suggest improvements"

# Test optimization
gemini -p "Optimize slow tests" tests/

# Mock generation
gemini -p "Generate mocks for external dependencies" tests/mocks/
```

### Common Tasks
1. **Unit Tests**
   ```bash
   gemini -p "Generate unit tests with high coverage" src/utils/
   ```

2. **Integration Tests**
   ```bash
   gemini -p "Create integration tests for API" tests/integration/
   ```

3. **Test Refactoring**
   ```bash
   gemini -a -p "Refactor tests for better maintainability"
   ```
EOF
            ;;
            
        "Documentation")
            cat >> "$agent_dir/GEMINI.md" << 'EOF'

```bash
# Generate documentation
gemini -a -p "Generate comprehensive documentation from code"

# README updates
gemini -p "Update README with current information" README.md

# API docs
gemini -p "Create API documentation" backend/

# Tutorials
gemini -p "Create step-by-step setup tutorial" docs/

# Architecture docs
gemini -a -p "Document system architecture"
```

### Common Tasks
1. **Doc Generation**
   ```bash
   gemini -p "Generate docs from code comments" src/
   ```

2. **Guide Creation**
   ```bash
   gemini -p "Create user guide for new feature" docs/guides/
   ```

3. **Doc Review**
   ```bash
   gemini -a -p "Review docs for accuracy and completeness"
   ```
EOF
            ;;
            
        "Security")
            cat >> "$agent_dir/GEMINI.md" << 'EOF'

```bash
# Security audit
gemini -a -p "Perform comprehensive security audit"

# Vulnerability scan
gemini -p "Scan for security vulnerabilities" .

# OWASP check
gemini -a -p "Check OWASP top 10 compliance"

# Dependency audit
gemini -p "Audit dependencies for vulnerabilities" package.json

# Code review
gemini -p "Security-focused code review" src/auth/
```

### Common Tasks
1. **Auth Audit**
   ```bash
   gemini -p "Audit authentication implementation" src/auth/
   ```

2. **Data Security**
   ```bash
   gemini -a -p "Review data handling for security issues"
   ```

3. **Penetration Test**
   ```bash
   gemini -p "Suggest penetration test scenarios" .
   ```
EOF
            ;;
    esac
    
    # Add common footer
    cat >> "$agent_dir/GEMINI.md" << EOF

## 📋 Working Protocol with Gemini

### Starting a Session
1. Navigate to your directory: \`cd $agent_dir\`
2. Check status: \`git status\`
3. Review tasks: \`cat /Users/studio/hardcard/AI_AGENT_TASKS.md\`
4. Update status: \`echo "Working on: [task]" >> STATUS.md\`

### During Work
- Use specific file paths when possible (saves tokens)
- Commit frequently with clear messages
- Test changes before committing
- Document significant decisions

### Ending a Session
1. Commit all changes
2. Update STATUS.md with progress
3. Note any blockers
4. Push to remote if ready

## 💰 Cost Optimization Tips

1. **Target Specific Files**
   \`\`\`bash
   gemini -p "Review this file" specific-file.ts
   \`\`\`

2. **Avoid -a Flag When Possible**
   The \`-a\` flag includes all files (expensive)

3. **Batch Similar Tasks**
   \`\`\`bash
   find . -name "*.test.ts" | xargs -I {} gemini -p "Add tests" {}
   \`\`\`

4. **Use Incremental Processing**
   Process large tasks in chunks

## 🚫 Restrictions

**You MUST NOT:**
- Modify files outside your focus area
- Switch to other agent directories
- Use -a flag unnecessarily (wastes tokens)
- Include sensitive data in prompts

## 💡 Gemini-Specific Tips

1. **Clear Prompts** = Better results + fewer tokens
2. **Structured Output** - Request JSON/Markdown
3. **Context Setting** - Include role in prompt
4. **Iterative Refinement** - Small focused prompts

Remember: You're part of a specialized agent team. Stay focused on your area!
EOF
}

# Create configurations for each agent
echo "Creating Frontend agent Gemini configuration..."
create_agent_gemini_config "Frontend" \
    "/Users/studio/hardcard-frontend-ai" \
    "ai/frontend-specialist" \
    "React, TypeScript, and UI development" \
    "- Component development and optimization
- TypeScript strict mode migration
- Performance improvements
- Accessibility compliance
- Test generation"

echo "Creating Backend agent Gemini configuration..."
create_agent_gemini_config "Backend" \
    "/Users/studio/hardcard-backend-ai" \
    "ai/backend-specialist" \
    "Python, FastAPI, and database development" \
    "- API endpoint development
- Type hints and validation
- Database optimization
- Security implementation
- Documentation generation"

echo "Creating Testing agent Gemini configuration..."
create_agent_gemini_config "Testing" \
    "/Users/studio/hardcard-testing-ai" \
    "ai/testing-specialist" \
    "Comprehensive testing and quality assurance" \
    "- Test suite generation
- Coverage improvement
- E2E scenario creation
- Performance testing
- Test optimization"

echo "Creating Documentation agent Gemini configuration..."
create_agent_gemini_config "Documentation" \
    "/Users/studio/hardcard-docs-ai" \
    "ai/documentation" \
    "Technical documentation and guides" \
    "- README maintenance
- API documentation
- User guides
- Architecture docs
- Tutorial creation"

echo "Creating Security agent Gemini configuration..."
create_agent_gemini_config "Security" \
    "/Users/studio/hardcard-security-ai" \
    "ai/security-audit" \
    "Security analysis and vulnerability assessment" \
    "- Security audits
- Vulnerability scanning
- OWASP compliance
- Dependency analysis
- Penetration testing"

# Create Gemini launcher script
cat > launch-gemini-agent.sh << 'EOF'
#!/bin/bash
# Launch Gemini CLI with agent-specific context

echo "🤖 Gemini CLI Agent Launcher"
echo "==========================="
echo ""
echo "Select agent to launch:"
echo "1) Frontend Agent"
echo "2) Backend Agent"
echo "3) Testing Agent"
echo "4) Documentation Agent"
echo "5) Security Agent"
echo ""
read -p "Choice (1-5): " choice

case $choice in
    1) 
        agent="frontend-ai"
        name="Frontend"
        ;;
    2) 
        agent="backend-ai"
        name="Backend"
        ;;
    3) 
        agent="testing-ai"
        name="Testing"
        ;;
    4) 
        agent="docs-ai"
        name="Documentation"
        ;;
    5) 
        agent="security-ai"
        name="Security"
        ;;
    *) 
        echo "Invalid choice"
        exit 1
        ;;
esac

worktree="/Users/studio/hardcard-$agent"

echo ""
echo "🚀 Launching $name Agent..."
echo "Working directory: $worktree"
echo ""

# Create context prompt
context="You are the $name AI Agent for HardCard.
Working directory: $worktree
Focus on: $name tasks only
First, check STATUS.md and AI_AGENT_TASKS.md"

echo "📋 Quick Start Commands:"
echo ""
echo "cd $worktree"
echo "gemini -p \"$context. What should I work on?\""
echo ""

# Copy context to clipboard if available
if command -v pbcopy >/dev/null 2>&1; then
    echo "$context" | pbcopy
    echo "✅ Context copied to clipboard!"
fi

# Change to agent directory
cd "$worktree"
echo "Current directory: $(pwd)"
echo ""
echo "📄 See GEMINI.md for detailed commands"
EOF
chmod +x launch-gemini-agent.sh

# Create batch processing script
cat > scripts/gemini-batch-process.sh << 'EOF'
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
EOF
chmod +x scripts/gemini-batch-process.sh

# Create cost tracking script
cat > scripts/gemini-usage-tracker.sh << 'EOF'
#!/bin/bash
# Track Gemini CLI usage for cost management

LOG_FILE="gemini-usage.log"

# Log usage
log_usage() {
    local agent=$1
    local command=$2
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    echo "$timestamp | $agent | $command" >> "$LOG_FILE"
}

# Estimate tokens (rough approximation)
estimate_tokens() {
    local files=$1
    local chars=$(wc -c $files 2>/dev/null | tail -1 | awk '{print $1}')
    local tokens=$((chars / 4))  # Rough estimate: 1 token ≈ 4 chars
    echo "$tokens"
}

# Usage report
generate_report() {
    echo "📊 Gemini Usage Report"
    echo "===================="
    echo ""
    
    # By agent
    echo "Usage by Agent:"
    for agent in frontend backend testing docs security; do
        count=$(grep -c "$agent" "$LOG_FILE" 2>/dev/null || echo "0")
        echo "  $agent: $count requests"
    done
    
    echo ""
    echo "Recent activity:"
    tail -10 "$LOG_FILE"
}

# Main
case "$1" in
    "log")
        log_usage "$2" "$3"
        ;;
    "estimate")
        estimate_tokens "$2"
        ;;
    "report")
        generate_report
        ;;
    *)
        echo "Usage: $0 {log|estimate|report}"
        ;;
esac
EOF
chmod +x scripts/gemini-usage-tracker.sh

# Create comparison guide
cat > GEMINI_VS_CLAUDE_COMPARISON.md << 'EOF'
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
EOF

echo ""
echo -e "${GREEN}✅ Gemini CLI Agent Configurations Complete!${NC}"
echo ""
echo -e "${BLUE}📁 Created:${NC}"
echo "  - GEMINI.md in main directory (overview)"
echo "  - GEMINI.md in each agent worktree (specific)"
echo "  - launch-gemini-agent.sh (unified launcher)"
echo "  - gemini-batch-process.sh (batch operations)"
echo "  - gemini-usage-tracker.sh (cost tracking)"
echo "  - GEMINI_VS_CLAUDE_COMPARISON.md (comparison guide)"
echo ""
echo -e "${YELLOW}🚀 To use:${NC}"
echo "  1. Install Gemini CLI: npm install -g @google/gemini-cli"
echo "  2. Set API key: export GEMINI_API_KEY=your-key"
echo "  3. Run: ./launch-gemini-agent.sh"
echo "  4. Select your agent"
echo "  5. Start working!"
echo ""
echo -e "${GREEN}💡 Gemini CLI is now configured for multi-agent development!${NC}"