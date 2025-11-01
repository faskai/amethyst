"""Amethyst: AI-native programming language runtime."""

# High-level API
from .engine import Engine
from .types import Resource

# Legacy alias
AmethystEngine = Engine

__version__ = "0.1.0"

__all__ = [
    'Engine',
    'AmethystEngine',
    'Resource',
]
