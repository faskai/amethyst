# Cognitive Engine Tests

Tests for ACL→AFL conversion and AI-powered execution.

## Quick Start

```bash
# From engine/ root
poetry install

# Terminal 1: Start server
cd tests
poetry run python unified_server.py

# Terminal 2: Run test
cd tests/cognitive_engine
poetry run python test_cognitive_engine.py
```

## What This Tests

1. ACL → AFL conversion
2. AI planning (decides what runs next)
3. Agent & tool calls (A2A/MCP)
4. Parallel execution
5. Memory/state management

## Files

- `example.txt` - ACL input
- `example.amt` - AFL output (generated)
- `test_cognitive_engine.py` - Test script

## Flow

```
ACL input (example.txt)
  ↓
Compiler → AFL (example.amt)
  ↓
Planner → decides tasks
  ↓
Executor → runs tasks
  ↓
Results
```

## Resources

Server at `http://localhost:9998` provides:

**Agents:** all_trails, open_table, browser, todoist  
**Tools:** get_weather, email

## Setup

Create `.env` in `engine/`:
```bash
OPENAI_API_KEY=your_key_here
```

## Example Output

```
📝 Input ACL:
Plan a day depending on the weather...

🔄 Converting ACL to AFL...
✅ AFL Generated

🤖 Execution Results:
✅ tool_call get_weather: Success
✅ agent_call all_trails: Success
✅ tool_call email: Success
```

