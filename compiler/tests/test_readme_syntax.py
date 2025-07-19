#!/usr/bin/env python3
"""Test runner for README syntax example."""

import sys
import os
import asyncio

# Add parent src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import from the new package structure
from amethyst_compiler import AmethystCompiler


async def main():
    """Run the README syntax test."""
    compiler_instance = AmethystCompiler()
    
    # Read the README example file
    try:
        with open(os.path.join(os.path.dirname(__file__), 'readme_example.amt'), 'r') as f:
            test_code = f.read()
    except FileNotFoundError:
        print("Error: readme_example.amt file not found")
        return
    
    print("=== README Syntax Test ===")
    print("Input code:")
    print(test_code)
    print("\nOutput:")
    
    result = await compiler_instance.compile_and_execute(test_code)
    print(result)


if __name__ == "__main__":
    asyncio.run(main()) 