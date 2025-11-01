#!/usr/bin/env python3
"""Agents package for Amethyst testing."""

from .hello_world_agent import get_hello_world_config
from .all_trails_agent import get_all_trails_config
from .open_table_agent import get_open_table_config
from .browser_agent import get_browser_config
from .todoist_agent import get_todoist_config

# Export all agent configurations for easy import
__all__ = [
    'get_hello_world_config',
    'get_all_trails_config', 
    'get_open_table_config',
    'get_browser_config',
    'get_todoist_config',
    'AGENT_CONFIGS'
]

# Agent registry for unified server
AGENT_CONFIGS = {
    "hello-world-agent": get_hello_world_config,
    "all-trails": get_all_trails_config,
    "open-table": get_open_table_config,
    "browser": get_browser_config,
    "todoist": get_todoist_config
}
