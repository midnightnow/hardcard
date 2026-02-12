#!/bin/bash
# Setup Claude Code configurations for each AI agent
# This ensures each agent knows their specific context and capabilities

set -e

echo "🤖 Setting up Claude Code configurations for AI agents..."
echo ""

# Function to create agent-specific CLAUDE.md
create_agent_claude_config() {
    local agent_type=$1
    local agent_dir=$2
    local branch=$3
    local focus_area=$4
    local specific_tools=$5
    
    cat > "$agent_dir/CLAUDE.md" << EOF
# Claude Code Configuration - $agent_type Agent

## 🤖 Agent Identity

**You are the $agent_type Specialist AI Agent**
- **Working Directory**: \`$agent_dir\`
- **Branch**: \`$branch\`
- **Focus Area**: $focus_area

## 🎯 Your Mission

You specialize in $focus_area. Your primary responsibilities include:
$specific_tools

## 🛠️ Available Tools

### Core Tools (Always Available)
- **File Operations**: Read, Write, Edit, MultiEdit
- **Search**: Grep, Glob (use within your directory)
- **Terminal**: Bash (for your focus area commands)
- **Git**: Commit frequently on your branch

### Recommended MCP Extensions for $agent_type
EOF

    # Add agent-specific MCP recommendations
    case $agent_type in
        "Frontend")
            cat >> "$agent_dir/CLAUDE.md" << 'EOF'
- **MCP Vision**: Analyze UI screenshots and designs
- **MCP Browser**: Test UI interactions and flows
- **MCP Accessibility**: Check WCAG compliance
- **MCP Performance**: Monitor bundle sizes and load times

### Your Specific Commands
```bash
# Start development
npm run dev

# Type checking
npm run type-check

# Run tests
npm test

# Build production
npm run build

# Check bundle size
npm run analyze
```

### Focus Areas
1. React component development
2. TypeScript migration (strict mode)
3. UI/UX implementation
4. Performance optimization
5. Accessibility compliance
EOF
            ;;
            
        "Backend")
            cat >> "$agent_dir/CLAUDE.md" << 'EOF'
- **MCP PostgreSQL**: Database queries and migrations
- **MCP Redis**: Cache management
- **MCP HTTP Client**: API testing
- **MCP Docker**: Container management

### Your Specific Commands
```bash
# Start API server
uvicorn main:app --reload

# Run migrations
alembic upgrade head

# Run tests
pytest

# Type checking
mypy .

# Format code
black .
```

### Focus Areas
1. API endpoint development
2. Database schema design
3. Authentication/Authorization
4. Performance optimization
5. Data validation (Pydantic)
EOF
            ;;
            
        "Testing")
            cat >> "$agent_dir/CLAUDE.md" << 'EOF'
- **MCP Browser**: E2E test automation
- **MCP Vision**: Visual regression testing
- **MCP Performance**: Load testing
- **MCP Accessibility**: Automated accessibility testing

### Your Specific Commands
```bash
# Unit tests
npm run test:unit

# E2E tests
npm run test:e2e

# Coverage report
npm run test:coverage

# Visual regression
npm run test:visual

# Performance tests
npm run test:perf
```

### Focus Areas
1. Unit test creation
2. Integration testing
3. E2E test scenarios
4. Performance testing
5. Test coverage improvement
EOF
            ;;
            
        "Documentation")
            cat >> "$agent_dir/CLAUDE.md" << 'EOF'
- **MCP Markdown**: Enhanced markdown processing
- **MCP Diagram**: Create architecture diagrams
- **MCP OpenAPI**: Generate API documentation
- **MCP Screenshot**: Capture UI for docs

### Your Specific Commands
```bash
# Build documentation
npm run docs:build

# Serve documentation
npm run docs:serve

# Check links
npm run docs:check-links

# Generate API docs
npm run docs:api
```

### Focus Areas
1. README updates
2. API documentation
3. Setup guides
4. Architecture docs
5. Troubleshooting guides
EOF
            ;;
            
        "Security")
            cat >> "$agent_dir/CLAUDE.md" << 'EOF'
- **MCP Security Scanner**: Vulnerability detection
- **MCP Secrets**: Secret scanning
- **MCP OWASP**: Security best practices
- **MCP Audit**: Dependency auditing

### Your Specific Commands
```bash
# Security scan
npm audit

# Dependency check
npm run security:check

# Secret scanning
git secrets --scan

# OWASP dependency check
dependency-check.sh

# Static analysis
semgrep --config=auto
```

### Focus Areas
1. Vulnerability assessment
2. Authentication audit
3. Authorization review
4. Dependency security
5. Security best practices
EOF
            ;;
    esac
    
    # Add common footer
    cat >> "$agent_dir/CLAUDE.md" << EOF

## 📋 Working Protocol

### Starting a Session
1. **Always** start with: \`cd $agent_dir\`
2. Check status: \`git status\`
3. Review tasks: \`cat /Users/studio/hardcard/AI_AGENT_TASKS.md\`
4. Update status: \`echo "Working on: [task]" >> STATUS.md\`

### During Work
- Commit frequently with descriptive messages
- Test changes before committing
- Document significant decisions
- Leave notes for other agents if needed

### Ending a Session
1. Commit all changes
2. Update STATUS.md with progress
3. Note any blockers in agent-communication/
4. Push to remote if ready

## 🚫 Restrictions

**You MUST NOT:**
- Modify files outside your focus area
- Switch to other agent directories
- Merge branches (coordinator handles this)
- Delete or rename core project files
- Modify other agents' work

## 💡 Tips for Success

1. **Small, focused commits** - Easy to review and merge
2. **Clear commit messages** - Include agent name prefix
3. **Test everything** - Don't break the build
4. **Communicate** - Use agent-communication/ directory
5. **Stay in scope** - Focus on your specialty

## 🆘 Getting Help

- Blocked? Create a note in \`/Users/studio/hardcard/agent-communication/blockers.md\`
- Need another agent? Leave a request in \`agent-communication/requests.md\`
- Coordination issues? The main coordinator (Claude) will help

Remember: You're part of a team of specialized agents working together to improve HardCard!
EOF
}

# Create configurations for each agent
echo "Creating Frontend agent configuration..."
create_agent_claude_config "Frontend" \
    "/Users/studio/hardcard-frontend-ai" \
    "ai/frontend-specialist" \
    "React, TypeScript, and UI development" \
    "- Component architecture and development
- TypeScript strict mode migration
- UI/UX implementation
- Performance optimization
- Accessibility compliance"

echo "Creating Backend agent configuration..."
create_agent_claude_config "Backend" \
    "/Users/studio/hardcard-backend-ai" \
    "ai/backend-specialist" \
    "Python, FastAPI, and database development" \
    "- API endpoint development
- Database schema design
- Authentication and authorization
- Performance optimization
- Data validation and serialization"

echo "Creating Testing agent configuration..."
create_agent_claude_config "Testing" \
    "/Users/studio/hardcard-testing-ai" \
    "ai/testing-specialist" \
    "Comprehensive testing and quality assurance" \
    "- Unit test development
- Integration testing
- End-to-end test scenarios
- Performance testing
- Test coverage improvement"

echo "Creating Documentation agent configuration..."
create_agent_claude_config "Documentation" \
    "/Users/studio/hardcard-docs-ai" \
    "ai/documentation" \
    "Technical documentation and guides" \
    "- README maintenance
- API documentation
- Setup and installation guides
- Architecture documentation
- Troubleshooting guides"

echo "Creating Security agent configuration..."
create_agent_claude_config "Security" \
    "/Users/studio/hardcard-security-ai" \
    "ai/security-audit" \
    "Security analysis and vulnerability assessment" \
    "- Security vulnerability scanning
- Authentication audit
- Authorization review
- Dependency security
- OWASP compliance"

# Create MCP extension recommendations
cat > MCP_RECOMMENDATIONS.md << 'EOF'
# 🔌 Recommended MCP Extensions for HardCard

## Essential MCPs for All Agents

### 1. Core Development
- **mcp-git**: Enhanced git operations
- **mcp-filesystem**: Advanced file operations
- **mcp-terminal**: Extended terminal capabilities

### 2. Quality & Testing
- **mcp-prettier**: Code formatting
- **mcp-eslint**: Linting integration
- **mcp-jest**: Test runner integration

### 3. Communication
- **mcp-slack**: Team notifications
- **mcp-github**: PR and issue management
- **mcp-webhook**: External integrations

## Agent-Specific MCPs

### Frontend Agent
```json
{
  "mcps": {
    "vision": {
      "command": "npx @modelcontextprotocol/mcp-vision",
      "description": "Analyze UI screenshots and mockups"
    },
    "browser": {
      "command": "npx @modelcontextprotocol/mcp-browser",
      "description": "Browser automation for testing"
    },
    "figma": {
      "command": "npx @modelcontextprotocol/mcp-figma",
      "description": "Design system integration"
    }
  }
}
```

### Backend Agent
```json
{
  "mcps": {
    "postgresql": {
      "command": "npx @modelcontextprotocol/mcp-postgresql",
      "env": {
        "DATABASE_URL": "${DATABASE_URL}"
      }
    },
    "redis": {
      "command": "npx @modelcontextprotocol/mcp-redis",
      "env": {
        "REDIS_URL": "${REDIS_URL}"
      }
    },
    "openapi": {
      "command": "npx @modelcontextprotocol/mcp-openapi",
      "description": "API documentation generation"
    }
  }
}
```

### Testing Agent
```json
{
  "mcps": {
    "playwright": {
      "command": "npx @modelcontextprotocol/mcp-playwright",
      "description": "E2E testing automation"
    },
    "lighthouse": {
      "command": "npx @modelcontextprotocol/mcp-lighthouse",
      "description": "Performance testing"
    },
    "axe": {
      "command": "npx @modelcontextprotocol/mcp-axe",
      "description": "Accessibility testing"
    }
  }
}
```

## Installation

Add to your Claude Code configuration:
```json
{
  "mcpServers": {
    // Add the MCPs from above based on your agent role
  }
}
```

Or install globally:
```bash
npm install -g @modelcontextprotocol/mcp-vision
npm install -g @modelcontextprotocol/mcp-browser
# etc...
```
EOF

# Create a unified agent launcher with Claude context
cat > launch-claude-agent.sh << 'EOF'
#!/bin/bash
# Launch Claude Code with agent-specific context

echo "🤖 Claude Code Agent Launcher"
echo "============================"
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
echo ""
echo "Working directory: $worktree"
echo "Configuration: $worktree/CLAUDE.md"
echo ""

# Copy agent context to clipboard
if [ -f "$worktree/CLAUDE.md" ]; then
    echo "📋 Agent context copied to clipboard!"
    cat "$worktree/CLAUDE.md" | pbcopy
fi

# Change to agent directory
cd "$worktree"

# If Claude Code is installed, launch it
if command -v claude >/dev/null 2>&1; then
    echo "Starting Claude Code in agent workspace..."
    claude code
else
    echo "Claude Code CLI not found. Opening directory..."
    if command -v code >/dev/null 2>&1; then
        code .
    fi
    echo ""
    echo "Remember to check CLAUDE.md for your agent instructions!"
fi
EOF
chmod +x launch-claude-agent.sh

echo ""
echo "✅ Claude Code Agent Configurations Complete!"
echo ""
echo "📁 Created:"
echo "  - CLAUDE.md in main directory (overview)"
echo "  - CLAUDE.md in each agent worktree (specific)"
echo "  - MCP_RECOMMENDATIONS.md (extension guide)"
echo "  - launch-claude-agent.sh (unified launcher)"
echo ""
echo "🚀 To use:"
echo "  1. Run: ./launch-claude-agent.sh"
echo "  2. Select your agent"
echo "  3. Claude Code starts with context"
echo ""
echo "📋 Each agent now has:"
echo "  - Clear identity and mission"
echo "  - Specific tool recommendations"
echo "  - Working protocols"
echo "  - Restrictions and guidelines"
echo ""
echo "💡 The CLAUDE.md files will be automatically read by Claude Code!"