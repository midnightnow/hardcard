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
