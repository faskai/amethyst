#!/usr/bin/env python3
"""Simple test runner for the Amethyst compiler."""

import sys
import os
import asyncio

# Add parent src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import from the new package structure
from amethyst_compiler import AmethystCompiler, AgentDefinition, ResourceDefinition, ResourceType


async def main():
    """Run the test."""
    compiler_instance = AmethystCompiler()
    
    # Register the hello world agent
    hello_world_agent = AgentDefinition(
        name="hello_world_agent",
        instructions="Just a hello world agent",
        url="http://localhost:9998"
    )
    
    resource = ResourceDefinition(
        resource_type=ResourceType.AGENT,
        definition=hello_world_agent
    )
    
    compiler_instance.register_resource(resource)
    
    # Read the test file from tests directory
    try:
        with open(os.path.join(os.path.dirname(__file__), 'test_agent.amt'), 'r') as f:
            test_code = f.read()
    except FileNotFoundError:
        print("Error: test_agent.amt file not found")
        return
    
    print("=== Amethyst Compiler Test ===")
    print("Input code:")
    print(test_code)
    print("\nOutput:")
    
    result = await compiler_instance.compile_and_execute(test_code)
    print(result)


if __name__ == "__main__":
    asyncio.run(main()) 