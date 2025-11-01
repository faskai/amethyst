#!/usr/bin/env python3
"""Weather tool implementation for Amethyst testing."""

import mcp.types as types
from typing import Any


def get_weather_tool(location: str = "Seattle, WA") -> str:
    """Get weather information for a location."""
    return f"""
🌦️ **Current Weather for {location}:**
- Condition: Light Rain
- Temperature: 52°F (11°C)
- Humidity: 85%
- Wind: 8 mph SW
- Forecast: Rain continuing through evening
- Perfect day for indoor dining! 🌧️
    """.strip()


# Tool metadata for MCP protocol
TOOL_INFO = {
    "name": "get-weather",
    "description": "Get current weather information for a location",
    "function": get_weather_tool,
    "parameters": {
        "location": {
            "type": "string", 
            "description": "Location to get weather for", 
            "default": "Seattle, WA"
        }
    },
    "mcp_schema": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The location to get weather for (e.g., 'Seattle, WA')"
            }
        },
        "required": ["location"]
    }
}


async def handle_mcp_call(arguments: dict[str, Any]) -> list[types.TextContent]:
    """Handle MCP tool call for get weather."""
    location = arguments.get("location", "Seattle, WA")
    
    # Mock weather data
    weather_response = f"""
🌦️ **Current Weather for {location}:**
- Condition: Light Rain
- Temperature: 52°F (11°C)
- Humidity: 85%
- Wind: 8 mph SW
- Pressure: 30.15 inHg
- Visibility: 6 miles
- UV Index: 2 (Low)

**📅 3-Day Forecast:**
- Today: Light rain, High 54°F, Low 45°F
- Tomorrow: Partly cloudy, High 58°F, Low 42°F  
- Day 3: Sunny, High 62°F, Low 46°F

**💡 Recommendations:**
- Perfect day for indoor dining! 🌧️
- Bring an umbrella if going out
- Great weather for cozy restaurant visits
    """
    
    return [types.TextContent(type="text", text=weather_response.strip())]
