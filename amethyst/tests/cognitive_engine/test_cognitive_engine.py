#!/usr/bin/env python3
"""Test ACL to AFL conversion and execution."""

import sys
import os
import asyncio
import httpx
import json

# Add parent src to path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'src'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from amethyst import Engine, Resource


async def check_server(url: str, timeout: float = 2.0) -> bool:
    """Check if server is running."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=timeout)
            return response.status_code == 200
    except:
        return False


async def test_acl_to_afl_conversion():
    """Test converting ACL to AFL and executing it."""
    
    print("🧠 === Amethyst ACL to AFL Conversion Test ===\n")
    
    # Check if unified server is running - FAIL FAST
    server_url = "http://localhost:9998"
    if not await check_server(server_url):
        print(f"\n❌ ERROR: Unified server is not running at {server_url}")
        sys.exit(1)
    
    print("✅ Server is running\n")
    
    # Create engine
    engine = Engine(verbose=True)
    
    # Prepare resources (agents and tools)
    resources = [
        Resource(type="agent", name="all-trails", provider="amethyst", url="http://localhost:9998/agents/all-trails"),
        Resource(type="agent", name="open-table", provider="amethyst", url="http://localhost:9998/agents/open-table"),
        Resource(type="agent", name="browser", provider="amethyst", url="http://localhost:9998/agents/browser"),
        Resource(type="agent", name="todoist", provider="amethyst", url="http://localhost:9998/agents/todoist"),
        Resource(type="tool", name="get-weather", provider="amethyst", url="http://localhost:9998/tools/get-weather"),
        Resource(type="tool", name="email", provider="amethyst", url="http://localhost:9998/tools/email"),
    ]
    
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
    
     # Run ACL with resources
    response = await engine.run(acl_text, resources=resources)
    
    # Save AFL+ASL code (caller's responsibility)
    with open(afl_file, 'w') as f:
        f.write(response["code"])
    
    print(f"\n✅ Execution Results:\n{json.dumps(response, indent=2)}")

if __name__ == "__main__":
    asyncio.run(test_acl_to_afl_conversion())

