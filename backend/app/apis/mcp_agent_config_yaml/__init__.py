"""MCP Agent Configuration YAML API

This module provides a configuration YAML file for the MCP agent system.
It serves the configuration in YAML format that can be consumed by the mcp-agent library.
It also allows updating the configuration to customize the MCP agent behavior.
"""

from fastapi import APIRouter, Response
from typing import Dict, Any
from pydantic import BaseModel
import yaml
import os
import databutton as db
import json
import re

# Create APIRouter
router = APIRouter(prefix="/mcp-agent-config-yaml")

# Configuration storage key for Databutton storage
MCP_CONFIG_STORAGE_KEY = "mcp_agent_config_yaml"

# Default configuration template as a multi-line string
DEFAULT_MCP_CONFIG_YAML = """
$schema: ../../schema/mcp-agent.config.schema.json
execution_engine: asyncio
logger:
  type: console
  level: info
  path: "./mcp-agent.log"
mcp:
  servers:
    fetch:
      command: "uvx"
      args: ["mcp-server-fetch"]
    filesystem:
      command: "npx"
      args: ["-y", "@modelcontextprotocol/server-filesystem", "."]
"""

# Models for config endpoints
class ConfigUpdateRequest(BaseModel):
    config_yaml: str

class ConfigResponse(BaseModel):
    message: str
    status: str

def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

@router.get("/")
def get_mcp_config_yaml():
    """Get the MCP agent configuration YAML
    
    This endpoint returns the MCP agent configuration in YAML format,
    which can be used by the mcp-agent library for configuration.
    """
    try:
        # Try to get stored configuration
        stored_config = db.storage.text.get(sanitize_storage_key(MCP_CONFIG_STORAGE_KEY), default=None)
        
        if stored_config:
            return Response(
                content=stored_config.strip(),
                media_type="application/x-yaml"
            )
        else:
            # Return default config if no stored config exists
            return Response(
                content=DEFAULT_MCP_CONFIG_YAML.strip(),
                media_type="application/x-yaml"
            )
    except Exception as e:
        print(f"Error retrieving MCP config: {e}")
        # Fallback to default config on error
        return Response(
            content=DEFAULT_MCP_CONFIG_YAML.strip(),
            media_type="application/x-yaml"
        )

@router.post("/", response_model=ConfigResponse)
def update_mcp_config_yaml(request: ConfigUpdateRequest):
    """Update the MCP agent configuration YAML
    
    This endpoint allows updating the MCP agent configuration in YAML format.
    The new configuration will be validated before being applied.
    """
    try:
        # Parse the YAML to validate it
        config_dict = yaml.safe_load(request.config_yaml)
        
        # Validate required fields
        if 'execution_engine' not in config_dict:
            return ConfigResponse(
                message="Configuration must include 'execution_engine' field",
                status="error"
            )
        
        if 'mcp' not in config_dict or 'servers' not in config_dict['mcp']:
            return ConfigResponse(
                message="Configuration must include 'mcp.servers' section",
                status="error"
            )
        
        # Store the validated configuration in Databutton storage
        try:
            db.storage.text.put(sanitize_storage_key(MCP_CONFIG_STORAGE_KEY), request.config_yaml)
            
            # Also store a timestamp of when this was updated
            import time
            db.storage.json.put(
                sanitize_storage_key(f"{MCP_CONFIG_STORAGE_KEY}_metadata"),
                {"last_updated": time.time(), "version": "1.0"}
            )
            
            return ConfigResponse(
                message="Configuration updated and saved successfully",
                status="success"
            )
        except Exception as storage_error:
            print(f"Error storing MCP config: {storage_error}")
            return ConfigResponse(
                message=f"Error storing configuration: {str(storage_error)}",
                status="error"
            )
    except yaml.YAMLError as e:
        return ConfigResponse(
            message=f"Invalid YAML format: {str(e)}",
            status="error"
        )
    except Exception as e:
        print(f"Error updating MCP config: {e}")
        return ConfigResponse(
            message=f"Error updating configuration: {str(e)}",
            status="error"
        )
