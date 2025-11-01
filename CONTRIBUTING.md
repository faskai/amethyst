# Contributing to Amethyst

Welcome! We're building the first AI-native programming language.

## Quick Setup

### 1. Environment Setup
```bash
# Clone repo
git clone https://github.com/fask/amethyst
cd amethyst

# Install engine dependencies
cd packages/engine
poetry install
cp .env.example .env
# Edit .env and add:
# - OPENAI_API_KEY
# - PIPEDREAM_PROJECT_ID, PIPEDREAM_CLIENT_ID, PIPEDREAM_CLIENT_SECRET

# Install API dependencies
cd ../../apps/api
poetry install
```

### 2. Run Tests
```bash
# Terminal 1: Start test server (provides agents & tools)
cd packages/engine/tests
poetry run python unified_server.py

# Terminal 2: Run engine tests
poetry run python cognitive_engine/test_cognitive_engine.py
```

### 3. Run API Server
```bash
cd apps/api
poetry run uvicorn main:app --reload --port 8000

# Visit http://localhost:8000/docs for API documentation
```

## Architecture

```
amethyst/
├── apps/                 # Deployable applications
│   ├── api/             # FastAPI server
│   ├── web/             # Future: Next.js (free tier)
│   ├── web-pro/         # Future: Next.js (paid tier)
│   └── ios/             # Future: React Native
│
└── packages/            # Libraries and SDKs
    ├── engine/          # Execution engine (internal)
    ├── python/          # Future: Python SDK → "amethyst" on PyPI
    ├── node/            # Future: Node SDK → "amethyst" on npm
    ├── react/           # Future: React SDK → "@amethyst/react" on npm
    └── ui/              # Future: Shared UI components
```

### How It Works
1. **Planner** - Compiles casual language to formal Amethyst Language (AL)
2. **Interpreter** - Reads AL and determines execution steps
3. **Executor** - Executes agent calls, tool calls
4. **Memory** - Tracks runtime state and results

## Contributing

### Code
1. Fork and create a branch
2. Make changes following existing patterns
3. Keep changes minimal and focused
4. Submit a PR with clear description

### Areas to Contribute
- Engine features (conditionals, loops, error handling)
- Agent integrations (using a2a-sdk)
- Tool integrations (using MCP)
- API endpoints
- Documentation
- Tests

## Code Style
- Python: Follow existing style, use ruff for linting
- Keep functions small and focused
- Add docstrings for public APIs
- No unnecessary abstractions

## Communication
- GitHub Issues for bugs and features
- Discussions for questions
- PRs for code contributions

---

Thank you for contributing to Amethyst!