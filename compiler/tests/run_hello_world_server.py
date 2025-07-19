#!/usr/bin/env python3
"""Run the hello world agent server."""

import sys
import os

# Add parent src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Run the server directly from the module
if __name__ == "__main__":
    print("Starting Hello World Agent Server on http://localhost:9998")
    exec(open('hello_world_agent.py').read()) 