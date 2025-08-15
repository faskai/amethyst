# Amethyst Cognitive Engine Tests

This directory contains a unified server hosting multiple A2A agents and MCP tools for testing the Amethyst cognitive execution engine.

## 🚀 Quick Start

### Prerequisites
```bash
# From the compiler/ directory
cd ../  # Go to compiler/ root

# Install dependencies with Poetry
poetry install
```

### Start Unified Server
```bash
# Start unified server with all agents and tools (Terminal 1)
cd tests/
poetry run python unified_server.py
```

### Run Cognitive Engine Test
```bash
# Run cognitive engine test with real GPT-4 orchestrator (Terminal 2)
cd tests/
poetry run python test_cognitive_engine.py
```

### Environment Setup
Make sure you have your OpenAI API key configured:
```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API key
OPENAI_API_KEY=your_actual_openai_api_key_here
```

## 🤖 Available Resources

All resources are hosted on a single server at **http://localhost:9998**

### A2A Agents
| Agent | Endpoint | Purpose |
|-------|----------|---------|
| **hello_world_agent** | `/agents/hello_world_agent` | Basic test agent |
| **all_trails** | `/agents/all_trails` | Hiking trail finder |
| **open_table** | `/agents/open_table` | Restaurant booking |
| **browser** | `/agents/browser` | Web browsing/booking |
| **todoist** | `/agents/todoist` | Task management |

### MCP Tools
| Tool | Endpoint | Purpose |
|------|----------|---------|
| **get_weather** | `/tools/get_weather` | Weather information |
| **email** | `/tools/email` | Send emails |

## 📁 Project Structure

```
compiler/
├── 📄 pyproject.toml               # 🔧 Poetry dependencies & config
├── 📄 .env                         # 🔑 Environment variables (API keys)
├── 📄 .env.example                 # 📝 Example environment file
│
├── 📁 src/amethyst_compiler/       # 🧠 Core cognitive engine
│   ├── 📄 runtime.py               # 🎯 AmethystEngine (main entry point)
│   ├── 📄 orchestrator.py          # 🤖 GPT-4 orchestrator
│   ├── 📄 memory.py                # 💾 Task memory system
│   └── 📄 amethyst_types.py        # 📋 Type definitions
│
└── 📁 tests/                       # 🧪 Test suite
    ├── 📄 test_cognitive_engine.py # 🌟 Main cognitive engine test
    ├── 📄 unified_server.py        # 🏃 Unified agents & tools server
    ├── 📄 a2a_agents.py            # 🤖 A2A agent management
    ├── 📄 mcp_tools.py             # 🛠️ MCP protocol wrapper
    │
    ├── 📁 agents/                  # 🤖 A2A Agent implementations
    │   ├── 📄 __init__.py          # 📋 Agent registry
    │   ├── 📄 hello_world_agent.py # 🤖 Simple test agent
    │   ├── 📄 all_trails_agent.py  # 🤖 Hiking trail finder
    │   ├── 📄 open_table_agent.py  # 🤖 Restaurant booking
    │   ├── 📄 browser_agent.py     # 🤖 Web browsing/booking
    │   └── 📄 todoist_agent.py     # 🤖 Task management
    │
    ├── 📁 tools/                   # 🛠️ MCP Tool implementations
    │   ├── 📄 __init__.py          # 📋 Tool registry
    │   ├── 📄 get_weather.py       # 🛠️ Weather information tool
    │   └── 📄 email.py             # 🛠️ Email sending tool
    │
    ├── 📄 readme_example.amt       # 📝 Day planner test scenario
    └── 📄 README.md                # 📚 This file
```

## 🔧 Resource Details

### A2A Agents
Each agent is implemented in a separate file and imported by the unified server:

- **hello_world_agent**: Simple greeting for testing
- **all_trails**: Hiking trail recommendations with distances, elevation, views
- **open_table**: Restaurant booking with PNW cuisine and waterfront locations  
- **browser**: Web browsing and booking (parking, rides, research)
- **todoist**: Todo list management with checklists and reminders

### MCP Tools
Lightweight tools implemented using Python MCP SDK:

- **get_weather**: Returns current weather conditions and forecasts for specified locations
- **email**: Sends emails with specified recipients, subjects, and content

The tools are implemented as proper MCP tools and integrated into the unified server for seamless access alongside A2A agents.

## 💡 Complete Usage Example

```bash
# 1. Setup (one time)
cd compiler/
poetry install
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 2. Terminal 1: Start unified server
cd tests/
poetry run python unified_server.py

# 3. Terminal 2: Run cognitive engine test  
cd tests/
poetry run python test_cognitive_engine.py
```

## 🧠 How the Cognitive Engine Works

The test demonstrates Amethyst's **cognitive execution engine**:

1. **📝 Natural Language Input**: Reads `readme_example.amt` with day planning instructions
2. **🤖 GPT-4 Orchestrator**: Interprets each line and plans appropriate tasks  
3. **🎯 Smart Execution**: 
   - Calls `@get_weather` tool first
   - Based on weather, chooses rainy day path → `@open_table` 
   - Understands "go do a/b" → runs parallel async tasks
   - Sends final `@email` with results
4. **💾 Memory**: Stores task results for the orchestrator to reference

**No rigid parsing** - the LLM understands natural language and plans execution dynamically!

## 🏗️ Architecture

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
    "name": "new_tool",
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