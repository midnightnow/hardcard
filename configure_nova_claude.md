# Configure Nova for Claude Desktop

## Step 1: Locate Claude Configuration

Open Claude Desktop settings and find the MCP configuration file:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

## Step 2: Add Nova Configuration

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "nova": {
      "command": "node",
      "args": [
        "/Users/studio/.nvm/versions/node/v20.19.3/lib/node_modules/@nova-mcp/mcp-nova/nova-memory-mcp.mjs"
      ],
      "env": {
        "NODE_ENV": "production"
      }
    }
  }
}
```

## Step 3: Restart Claude

1. Quit Claude Desktop completely
2. Restart Claude Desktop
3. Look for "nova" in the MCP servers list

## Step 4: Test Nova

In your first message, try:
```
Store this in Nova: VetSorcery uses FastAPI backend with Firebase Firestore database, Twilio WebRTC for voice, and OpenAI GPT-4o for AI phone agents.
```

Then test retrieval:
```
What do you remember about VetSorcery?
```