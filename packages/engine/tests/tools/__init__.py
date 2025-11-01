#!/usr/bin/env python3
"""Tools package for Amethyst testing."""

from .get_weather import TOOL_INFO as GET_WEATHER_TOOL, get_weather_tool, handle_mcp_call as get_weather_mcp_call
from .email import TOOL_INFO as EMAIL_TOOL, email_tool, handle_mcp_call as email_mcp_call

# Export all tools for easy import
__all__ = [
    'GET_WEATHER_TOOL',
    'EMAIL_TOOL', 
    'get_weather_tool',
    'email_tool',
    'get_weather_mcp_call',
    'email_mcp_call',
    'AVAILABLE_TOOLS',
    'call_tool_function'
]

# Tool registry for unified server
AVAILABLE_TOOLS = {
    "get-weather": GET_WEATHER_TOOL,
    "email": EMAIL_TOOL
}


def call_tool_function(tool_name: str, **kwargs) -> str:
    """Call a tool function directly."""
    if tool_name not in AVAILABLE_TOOLS:
        return f"Unknown tool: {tool_name}"
    
    tool_func = AVAILABLE_TOOLS[tool_name]["function"]
    try:
        return tool_func(**kwargs)
    except Exception as e:
        return f"Error calling {tool_name}: {str(e)}"
