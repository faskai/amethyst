# Amethyst

AI-native programming language runtime.

## What is Amethyst?

Amethyst reads like English and compiles to executable code.

## Quick Start

```bash
# Install
poetry install

# Configure
cp .env.example .env
# Add to .env:
# - OPENAI_API_KEY
# - PIPEDREAM_PROJECT_ID
# - PIPEDREAM_PROJECT_ENVIRONMENT
# - PIPEDREAM_CLIENT_ID
# - PIPEDREAM_CLIENT_SECRET
# - PIPEDREAM_EXTERNAL_USER_ID (optional, defaults to "default_user")

# Run test
cd tests
poetry run python unified_server.py  # Terminal 1
poetry run python cognitive_engine/test_cognitive_engine.py  # Terminal 2
```

## Usage

```python
from amethyst import Engine, Resource

engine = Engine(verbose=True)
resources = [
    Resource(type="agent", name="all trails", url="..."),
    Resource(type="tool", name="get weather", url="..."),
]

result = await engine.run("""
use get weather to check forecast
if sunny
    use all trails to find hikes
end if
""", resources=resources)
```

## Architecture

- `engine.py` - Execution runtime
- `planner.py` - Casual lang → Amethyst Language (AL) compilation
- `interpreter.py` - AL interpretation
- `executor.py` - Task execution
- `memory.py` - Runtime state

See `tests/README.md` for testing details.
