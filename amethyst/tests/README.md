# Amethyst Tests

Test server hosting A2A agents and MCP tools.

## Quick Start

```bash
# From amethyst/ root
poetry install
cp .env.example .env  # Add OPENAI_API_KEY

# Terminal 1: Start server
cd tests
poetry run python unified_server.py

# Terminal 2: Run tests
poetry run python cognitive_engine/test_cognitive_engine.py
```

## Available Resources (http://localhost:9998)

**Agents:** all_trails, open_table, browser, todoist
**Tools:** get_weather, email

## Server Architecture

- **FastAPI** server on port 9998
- **A2A Agents** at `/agents/{name}`
- **MCP Tools** at `/tools/{name}`

## Debugging

```bash
# Check server
curl http://localhost:9998/

# Test agent
curl http://localhost:9998/agents/browser/.well-known/agent.json

# Test tool
curl -X POST http://localhost:9998/tools/get_weather \
  -H "Content-Type: application/json" \
  -d '{"query": "Seattle"}'
```

## Adding Resources

**Agents:** Create in `agents/`, register in `agents/__init__.py`
**Tools:** Create in `tools/`, register in `tools/__init__.py`