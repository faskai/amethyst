# Amethyst Engine Tests

Unified server hosting A2A agents and MCP tools for testing the Amethyst cognitive execution engine.

## Quick Start

```bash
# 1. Install dependencies (from engine/ root)
poetry install

# 2. Set up environment
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=your_key_here

# 3. Start unified server (Terminal 1)
cd tests
poetry run python unified_server.py

# 4. Run cognitive engine test (Terminal 2)
cd tests/cognitive_engine
poetry run python test_cognitive_engine.py
```

## Available Resources

Server: **http://localhost:9998**

**A2A Agents:**
- `all_trails` - Find hiking trails
- `open_table` - Restaurant booking  
- `browser` - Web browsing/booking
- `todoist` - Task management
- `hello_world_agent` - Basic test

**MCP Tools:**
- `get_weather` - Weather information
- `email` - Send emails

## How It Works

1. Compiler converts ACL → AFL
2. Planner uses AI to decide what runs
3. Executor calls agents/tools
4. Memory stores results

## Server Architecture

### Unified Server
- **FastAPI**: Main server framework with routing
- **A2A Agents**: Mounted at `/agents/{agent_name}` endpoints  
- **MCP Tools**: Available at `/tools/{tool_name}` endpoints
- **Single Port**: All resources accessible on port 9998

### Server Architecture
- **Unified Server**: Main server orchestrating both agents and tools
- **A2A Agent Manager**: Handles A2A agent setup and mounting (in `a2a_agents.py`)
- **MCP Tools**: Tool implementations and protocol wrapper (in `mcp_tools.py` and `tools/`)

### Agent Pattern
Each agent follows a clean separation:
- **Agent File**: Located in `agents/` directory, contains executor class and configuration function
- **Executor**: Implements the agent logic (extends `AgentExecutor`)
- **Configuration**: Returns metadata (name, description, skills, executor class)
- **Manager**: A2A agent manager handles instantiation and mounting

### Tool Pattern
Each tool follows a modular structure:
- **Tool File**: Located in `tools/` directory, contains both MCP and direct function implementations
- **MCP Handler**: Implements the MCP protocol for tool integration
- **Direct Function**: Standalone function for direct usage
- **Registry**: Tools are registered in `tools/__init__.py` for easy access

## 🔍 Debugging

### Check Server Status
```bash
# From tests/ directory with Poetry environment

# Server overview
curl http://localhost:9998/

# List all agents
curl http://localhost:9998/agents

# List all tools  
curl http://localhost:9998/tools

# Test specific agent
curl http://localhost:9998/agents/browser/.well-known/agent.json

# Test MCP tool
curl -X POST http://localhost:9998/tools/get_weather \
  -H "Content-Type: application/json" \
  -d '{"query": "Seattle weather"}'
```

### View Logs
The unified server logs all activity to console:
- ✅ Successful agent responses
- ❌ Error messages and stack traces
- 🔍 Request/response details
- 📡 Server startup and agent mounting

## 📝 Adding New Resources

### Adding New Agents

1. **Create agent file** in `agents/` (e.g., `agents/new_agent.py`):
```python
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import AgentSkill, TaskArtifactUpdateEvent, TaskStatus, TaskStatusUpdateEvent
from a2a.utils import new_task, new_text_artifact

class NewAgentExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        # Agent implementation here
        pass
    
    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise Exception('cancel not supported')

def get_new_agent_config():
    return {
        "name": "New Agent",
        "description": "Description of what the agent does",
        "skills": [AgentSkill(...)],
        "executor_class": NewAgentExecutor
    }
```

2. **Register in agents package** by updating `agents/__init__.py`:
```python
from .new_agent import get_new_agent_config

# Add to AGENT_CONFIGS
"new_agent": get_new_agent_config,
```

### Adding New Tools

1. **Create tool file** in `tools/` (e.g., `tools/new_tool.py`):
```python
import mcp.types as types
from typing import Any

def new_tool_function(param: str = "default") -> str:
    """Tool implementation."""
    return f"Result: {param}"

TOOL_INFO = {
    "name": "new tool",
    "description": "Description of what the tool does",
    "function": new_tool_function,
    "parameters": {
        "param": {"type": "string", "description": "Parameter description", "default": "default"}
    },
    "mcp_schema": {
        "type": "object",
        "properties": {
            "param": {"type": "string", "description": "Parameter for the tool"}
        },
        "required": ["param"]
    }
}

async def handle_mcp_call(arguments: dict[str, Any]) -> list[types.TextContent]:
    """Handle MCP tool call."""
    param = arguments.get("param", "default")
    result = new_tool_function(param)
    return [types.TextContent(type="text", text=result)]
```

2. **Register in tools package** by updating `tools/__init__.py`:
```python
from .new_tool import TOOL_INFO as NEW_TOOL_INFO, new_tool_function, handle_mcp_call as new_tool_mcp_call

# Add to AVAILABLE_TOOLS
"new_tool": NEW_TOOL_INFO,
```

3. **Update MCP handler** in `mcp_tools.py` if needed for the new tool.

### Test New Resources

```bash
# Restart server
poetry run python unified_server.py

# Test new agent
curl http://localhost:9998/agents/new_agent/.well-known/agent.json

# Test new tool
curl -X POST http://localhost:9998/tools/new_tool \
  -H "Content-Type: application/json" \
  -d '{"param": "test_value"}'
```