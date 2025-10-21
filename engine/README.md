# Amethyst Engine

The Python-based cognitive execution engine for the Amethyst language.

## What is Amethyst?

Amethyst is an AI-native programming language that reads like English. Write code in three levels:

* **ACL (Casual)** – free-flowing chat with no grammar rules
* **ASL (Semi-formal)** – structured natural English for agent instructions  
* **AFL (Formal)** – fully structured and precise

## Quick Start

```bash
# Install dependencies
poetry install

# Set your OpenAI API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run the cognitive engine test
cd tests/cognitive_engine
poetry run python test_cognitive_engine.py
```

## Files

- `engine.py` - Main interpreter
- `planner.py` - AI planner  
- `compiler.py` - ACL→AFL conversion
- `executor.py` - Runs tasks
- `memory.py` - State storage

## How It Works

1. **Write in natural language** (ACL) - no syntax needed
2. **Compiler converts to AFL** - structured but readable
3. **Planner uses AI** - decides what to execute next
4. **Executor runs tasks** - calls agents and tools

## Example

**Input (ACL):**
```
Plan my day based on weather
```

**Converted to (AFL):**
```
agent day planner
use get weather to check forecast
if weather is sunny
use all trails to find good hikes nearby under 10k with views
else if rainy
use open table to find nice waterfront restaurant with PNW food
end if
use email to send the final plan
end agent
```

**Engine executes:** Calls weather → chooses agent → sends email

AI plans dynamically - no rigid parsing!

## Key Features

- Natural conditionals: `if weather is sunny`
- Parallel execution: `a: in parallel ...` + `wait for a, b`
- Agent composition: agents call other agents/tools
- Standard protocols: A2A (agents) & MCP (tools)

## Testing

See `tests/cognitive_engine/README.md` for details.
