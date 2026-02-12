# 🎯 Gemini CLI Cheat Sheet for Agents

## Basic Commands

### Review Current Work
```bash
gemini -p "Review STATUS.md and current tasks"
```

### Analyze Specific File
```bash
gemini -p "Analyze and improve this file" path/to/file.ts
```

### Analyze All Files (Expensive!)
```bash
gemini -a -p "Perform comprehensive analysis"
```

### Generate Code
```bash
gemini -p "Generate TypeScript interface for this API response" api-response.json
```

## Agent-Specific Commands

### Frontend
```bash
# TypeScript migration
gemini -p "Convert to TypeScript with strict mode" component.jsx

# Performance optimization  
gemini -p "Optimize this component for performance" heavy-component.tsx

# Accessibility
gemini -p "Add ARIA labels and keyboard navigation" form.tsx
```

### Backend
```bash
# Add type hints
gemini -p "Add Python type hints" module.py

# API design
gemini -p "Create RESTful API endpoints for user management" 

# Database optimization
gemini -p "Optimize this SQL query" slow-query.sql
```

### Testing
```bash
# Generate tests
gemini -p "Generate Jest tests with 100% coverage" component.tsx

# E2E scenarios
gemini -p "Create Playwright E2E test for checkout flow"

# Test optimization
gemini -p "Optimize slow tests" slow-test.spec.ts
```

### Documentation
```bash
# README update
gemini -p "Update README with current project state" README.md

# API docs
gemini -p "Generate OpenAPI documentation" api-routes.ts

# Tutorials
gemini -p "Create step-by-step tutorial for new developers"
```

### Security
```bash
# Security audit
gemini -p "Audit for OWASP top 10 vulnerabilities" auth-module/

# Dependency check
gemini -p "Check dependencies for known vulnerabilities" package.json

# Secret scanning
gemini -p "Scan for hardcoded secrets and credentials" .
```

## Cost-Saving Patterns

### Process Multiple Files Efficiently
```bash
# Instead of using -a flag
find . -name "*.tsx" -type f | head -10 | xargs -I {} gemini -p "Quick review" {}
```

### Incremental Processing
```bash
# Process in chunks
gemini -p "List all files needing TypeScript migration" > todo.txt
cat todo.txt | head -5 | xargs -I {} gemini -p "Migrate to TypeScript" {}
```

### Focused Analysis
```bash
# Target specific concerns
gemini -p "Only look for security issues" sensitive-file.ts
```

## Workflow Commands

### Start of Day
```bash
gemini -p "Review yesterday's STATUS.md and plan today's work"
```

### Before Commit
```bash
gemini -p "Review changes for quality and security" $(git diff --name-only)
```

### End of Day
```bash
gemini -p "Summarize today's progress for STATUS.md"
```

## Advanced Usage

### Structured Output
```bash
gemini -p "Analyze code and return results as JSON" file.ts
```

### Chain Operations
```bash
gemini -p "List all components without tests" | \
  xargs -I {} gemini -p "Generate tests for {}" {}
```

### Parallel Processing
```bash
# Run multiple analyses simultaneously
for file in *.ts; do
  gemini -p "Review $file" "$file" > "reviews/$file.md" &
done
wait
```

Remember: Specific prompts = Better results + Lower costs!
