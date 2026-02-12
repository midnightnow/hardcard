from typing import Dict, Any, List, Optional
import os
import yaml
import databutton as db
from fastapi import APIRouter, Body
from pydantic import BaseModel

# Create a router
router = APIRouter()

def get_mcp_config():
    """Get the MCP configuration as a dictionary"""
    try:
        config = db.storage.text.get("mcp_config.yaml", "")
        if not config:
            # Return default config
            return get_default_config()
        return yaml.safe_load(config)
    except Exception as e:
        print(f"Error loading MCP config: {e}")
        return get_default_config()

def get_default_config():
    """Get the default MCP configuration"""
    return {
        "$schema": "../../schema/mcp-agent.config.schema.json",
        "execution_engine": "asyncio",
        "logger": {
            "type": "console",
            "level": "info",
            "path": "./mcp-agent.log"
        },
        "mcp": {
            "servers": {
                "fetch": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-fetch"]
                },
                "filesystem": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
                },
                "legacyvault": {
                    "command": "uvicorn",
                    "args": ["src.app.apis.legacyvault_proxy:router", "--host", "0.0.0.0", "--port", "8001"]
                }
            }
        }
    }

def get_server_names():
    """Get the names of MCP servers configured in the config"""
    config = get_mcp_config()
    try:
        return list(config.get("mcp", {}).get("servers", {}).keys())
    except Exception as e:
        print(f"Error getting server names: {e}")
        return []

def get_llm_config():
    """Get the LLM configuration from the MCP config"""
    config = get_mcp_config()
    return config.get("llm", {})

def save_mcp_config(config_yaml: str) -> Dict[str, Any]:
    """Save the MCP configuration"""
    try:
        # Validate the YAML
        # Just parse the YAML to validate it, we don't need to store the result
        yaml.safe_load(config_yaml)
        
        # Save the configuration
        db.storage.text.put("mcp_config.yaml", config_yaml)
        
        return {"status": "success", "message": "Configuration saved successfully"}
    except Exception as e:
        return {"status": "error", "message": f"Error saving configuration: {str(e)}"}


# Define API models
class MCPConfigResponse(BaseModel):
    server_names: List[str]
    config: Dict[str, Any]


class MCPConfigUpdateRequest(BaseModel):
    config: str


class MCPConfigUpdateResponse(BaseModel):
    status: str
    message: str


# API endpoints
@router.get("/get_mcp_configuration")
def get_mcp_configuration_v2() -> MCPConfigResponse:
    """Get the current MCP configuration including server names and full config"""
    return MCPConfigResponse(
        server_names=get_server_names(),
        config=get_mcp_config()
    )


@router.get("/get_mcp_config_yaml")
def get_mcp_config_yaml_v2() -> str:
    """Get the MCP configuration as YAML"""
    return db.storage.text.get("mcp_config.yaml", yaml.dump(get_default_config()))


@router.post("/update_mcp_config_yaml")
def update_mcp_config_yaml_v2(request: MCPConfigUpdateRequest) -> MCPConfigUpdateResponse:
    """Update the MCP configuration with provided YAML"""
    result = save_mcp_config(request.config)
    return MCPConfigUpdateResponse(
        status=result["status"],
        message=result["message"]
    )
