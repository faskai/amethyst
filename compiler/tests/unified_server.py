#!/usr/bin/env python3
"""
Unified server hosting multiple agents and MCP tools.
Single server with multiple endpoints for better resource management.
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from typing import Dict, Any

# Import A2A agent manager
from a2a_agents import A2AAgentManager

# Import MCP tools
from mcp_tools import AVAILABLE_TOOLS, call_tool_function


class UnifiedAgentServer:
    """Unified server hosting multiple agents and MCP tools."""
    
    def __init__(self, port: int = 9998):
        self.port = port
        self.agent_manager = A2AAgentManager(port=port)
        self.tools = {}
        self.app = FastAPI(title="Amethyst Unified Server")
        self._setup_routes()
        self._setup_resources()
        
    def _setup_routes(self):
        """Setup FastAPI routes for MCP tools and agent discovery."""
        
        @self.app.get("/")
        async def root():
            return {
                "name": "Amethyst Unified Server",
                "version": "1.0.0",
                "agents": self.agent_manager.get_agent_names(),
                "tools": list(self.tools.keys()),
                "endpoints": {
                    "agents": "/agents/{agent_name}",
                    "tools": "/tools/{tool_name}",
                    "agent_cards": "/agents/{agent_name}/.well-known/agent.json"
                }
            }
        
        @self.app.get("/agents")
        async def list_agents():
            return {"agents": self.agent_manager.get_agent_names()}
            
        @self.app.get("/tools")
        async def list_tools():
            return {"tools": list(self.tools.keys())}
            
        @self.app.post("/tools/{tool_name}")
        async def call_tool(tool_name: str, request: Dict[str, Any]):
            """MCP tool calling endpoint."""
            if tool_name not in self.tools:
                raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found")
            
            # Route to MCP tool implementation
            result = await self._call_tool(tool_name, request)
            return {"result": result}
            
        @self.app.get("/tools/{tool_name}")
        async def get_tool_info(tool_name: str):
            """Get tool information."""
            if tool_name not in self.tools:
                raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found")
            
            return self.tools[tool_name]
    
    async def _call_tool(self, tool_name: str, request: Dict[str, Any]) -> str:
        """Route MCP tool calls."""
        
        # Use the MCP tool implementation
        if tool_name in AVAILABLE_TOOLS:
            # Extract parameters from request
            params = {}
            for param_name, param_info in AVAILABLE_TOOLS[tool_name]["parameters"].items():
                if param_name in request:
                    params[param_name] = request[param_name]
                elif "default" in param_info:
                    params[param_name] = param_info["default"]
            
            # Call the tool function
            return call_tool_function(tool_name, **params)
        else:
            return f"Unknown tool: {tool_name}"
    
    def _setup_resources(self):
        """Setup all A2A agents and MCP tools."""
        
        # Setup A2A agents using the agent manager
        self.agent_manager.setup_agents(self.app)
        
        # Setup MCP tools from imported configuration
        self.tools = AVAILABLE_TOOLS
    
    def run(self):
        """Start the unified server."""
        print("🚀 Starting Amethyst Unified Server")
        print(f"📡 Server running on http://localhost:{self.port}")
        print("\n🤖 Available Agents:")
        for agent_name in self.agent_manager.get_agent_names():
            print(f"  • {agent_name}: http://localhost:{self.port}/agents/{agent_name}")
        print("\n🔧 Available Tools:")
        for tool_name in self.tools.keys():
            print(f"  • {tool_name}: http://localhost:{self.port}/tools/{tool_name}")
        print("\n⏹️  Press Ctrl+C to stop")
        
        uvicorn.run(self.app, host='0.0.0.0', port=self.port)


if __name__ == '__main__':
    server = UnifiedAgentServer(port=9998)
    server.run()
