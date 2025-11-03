"""Amethyst: AI-native programming language runtime."""

# High-level API
from .app import Resource
from .engine import Engine

# Legacy alias
AmethystEngine = Engine

__version__ = "0.1.0"

__all__ = [
    "Engine",
    "AmethystEngine",
    "Resource",
]
