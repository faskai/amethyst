# Amethyst Compiler

This directory contains the Python-based compiler for the Amethyst language.

## Structure

- `src/`: Source code for the language and compiler
  - `types.py`: Type definitions for Agent and Tool (model-agnostic)
  - `parser.py`: Simple parser for Amethyst syntax
  - `compiler.py`: Main compiler implementation with A2A communication
- `tests/`: Test files and examples
  - `test.amt`: Test file with sample Amethyst code
  - `run_test.py`: Test runner
  - `run_hello_world_server.py`: Script to run the hello world agent server
  - `hello_world_agent.py`: Hello world agent using A2A SDK
- `pyproject.toml`: Poetry project configuration and dependencies

## Usage

1. Install dependencies:
   ```bash
   poetry install
   ```

2. Start the hello world agent server (in one terminal):
   ```bash
   cd tests
   poetry run python run_hello_world_server.py
   ```

3. Run the test (in another terminal):
   ```bash
   cd tests
   poetry run python run_test.py
   ```

## Current Features

- Basic agent parsing from `.amt` files
- Agent registry for storing and retrieving agents
- Simple invoke call parsing using `@` syntax
- A2A (Agent-to-Agent) communication using a2a-sdk
- Hello world agent implementation
- Model-agnostic design (no hard dependencies on specific providers)

## Example

The test file `tests/test.amt` contains:
```
agent test
What's your favorite thing to say, @hello_world_agent?
end test
```

This creates an agent named "test" that communicates with the "hello_world_agent" via A2A protocol. The full agent prompt (`@hello_world_agent.`) is sent to the hello_world_agent.

## A2A Communication

The compiler uses the A2A SDK to enable agent-to-agent communication. The hello world agent runs as a server on `http://localhost:9998` and the compiler acts as a client to communicate with it.

## Syntax

- `agent <name>`: Define an agent
- `@<agent_name>`: Invoke another agent
- `end <name>`: End agent definition
- All syntax is case-insensitive 