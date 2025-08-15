#!/usr/bin/env python3
"""Test the Amethyst cognitive execution engine."""

import sys
import os
import asyncio

# Add parent src to path for amethyst_compiler imports
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from amethyst_compiler import AmethystEngine, AgentDefinition, ToolDefinition, ResourceDefinition, ResourceType, Step, StepType


async def main():
    """Test the cognitive engine."""
    
    print("🧠 === Amethyst Cognitive Engine Test ===")
    
    # Create engine
    engine = AmethystEngine()
    
    # Register all agents from unified server
    agents = [
        ("hello_world_agent", "Just a hello world agent", "http://localhost:9998/agents/hello_world_agent"),
        ("all_trails", "Find hiking trails based on criteria", "http://localhost:9998/agents/all_trails"), 
        ("open_table", "Find and book restaurant reservations", "http://localhost:9998/agents/open_table"),
        ("browser", "Web browsing agent for bookings and research", "http://localhost:9998/agents/browser"),
        ("todoist", "Task management and todo list creation", "http://localhost:9998/agents/todoist"),
    ]

    for name, description, url in agents:
        agent_def = AgentDefinition(name=name, url=url)
        resource = ResourceDefinition(resource_type=ResourceType.AGENT, definition=agent_def)
        engine.register_resource(resource)

    # Register MCP tools 
    tools = [
        ("get_weather", {"type": "object", "properties": {"location": {"type": "string"}}}, "http://localhost:9998/tools/get_weather"),
        ("email", {"type": "object", "properties": {"recipient": {"type": "string"}, "subject": {"type": "string"}, "content": {"type": "string"}}}, "http://localhost:9998/tools/email"),
    ]

    for name, schema, url in tools:
        tool_def = ToolDefinition(name=name, url=url)
        resource = ResourceDefinition(resource_type=ResourceType.TOOL, definition=tool_def)
        engine.register_resource(resource)
    
    # Read the test file
    try:
        with open(os.path.join(os.path.dirname(__file__), 'readme_example.amt'), 'r') as f:
            test_code = f.read()
    except FileNotFoundError:
        print("❌ Error: readme_example.amt file not found")
        return

    print("📝 Input instructions:")
    print(test_code)
    print("\n🤖 Processing with GPT-4 Orchestrator...")
    print("=" * 60)

    try:
        result = await engine.execute(test_code)
        print(result)
    except Exception as e:
        print(f"❌ Error during execution: {e}")

    print("\n✅ Cognitive execution completed!")


if __name__ == "__main__":
    asyncio.run(main())
