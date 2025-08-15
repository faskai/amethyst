#!/usr/bin/env python3
"""MCP Tools implementation for Amethyst testing."""

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
)
import mcp.types as types
import json
from typing import Any, Sequence

# Import from tools package
from tools import AVAILABLE_TOOLS, call_tool_function, get_weather_mcp_call, email_mcp_call

# Initialize MCP server for tools
mcp_server = Server("amethyst-tools")


@mcp_server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available MCP tools."""
    tools = []
    for tool_name, tool_info in AVAILABLE_TOOLS.items():
        tools.append(types.Tool(
            name=tool_name,
            description=tool_info["description"],
            inputSchema=tool_info["mcp_schema"]
        ))
    return tools


@mcp_server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle MCP tool calls."""
    
    if name == "get_weather":
        return await get_weather_mcp_call(arguments)
    elif name == "email":
        return await email_mcp_call(arguments)
    else:
        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


# Legacy compatibility - AVAILABLE_TOOLS and call_tool_function are imported from tools package
