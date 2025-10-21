#!/usr/bin/env python3
"""Test ACL to AFL conversion and execution."""

import sys
import os
import asyncio

# Add parent src to path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'src'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from amethyst_engine import AmethystEngine, AgentDefinition, ToolDefinition, ResourceDefinition, ResourceType


async def test_acl_to_afl_conversion():
    """Test converting ACL to AFL and executing it."""
    
    print("🧠 === Amethyst ACL to AFL Conversion Test ===\n")
    
    # Create engine
    engine = AmethystEngine()
    
    # Register agents (using space case for resource names)
    agents = [
        ("all trails", "http://localhost:9998/agents/all_trails"),
        ("open table", "http://localhost:9998/agents/open_table"),
        ("browser", "http://localhost:9998/agents/browser"),
        ("todoist", "http://localhost:9998/agents/todoist"),
    ]
    
    for name, url in agents:
        agent_def = AgentDefinition(name=name, url=url)
        resource = ResourceDefinition(resource_type=ResourceType.AGENT, definition=agent_def)
        engine.register_resource(resource)
    
    # Register tools (using space case for resource names)
    tools = [
        ("get weather", "http://localhost:9998/tools/get_weather"),
        ("email", "http://localhost:9998/tools/email"),
    ]
    
    for name, url in tools:
        tool_def = ToolDefinition(name=name, url=url)
        resource = ResourceDefinition(resource_type=ResourceType.TOOL, definition=tool_def)
        engine.register_resource(resource)
    
    # Read ACL from example.txt
    acl_file = os.path.join(os.path.dirname(__file__), 'example.txt')
    afl_file = os.path.join(os.path.dirname(__file__), 'example.amt')
    
    try:
        with open(acl_file, 'r') as f:
            acl_text = f.read()
    except FileNotFoundError:
        print(f"❌ Error: {acl_file} not found")
        return
    
    print("📝 Input ACL (Casual Language):")
    print("-" * 60)
    print(acl_text)
    print("-" * 60)
    
    print("\n🔄 Converting ACL to AFL...")
    print("=" * 60)
    
    try:
        # Execute ACL and save AFL
        result = await engine.execute_acl(acl_text, save_afl_path=afl_file)
        
        print("\n🤖 Execution Results:")
        print("=" * 60)
        print(result)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Test completed!")


if __name__ == "__main__":
    asyncio.run(test_acl_to_afl_conversion())

