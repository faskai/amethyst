"""Abstract provider interface."""

from abc import ABC, abstractmethod
from typing import List

from ..app import Resource, ResourceExpanded


class ToolProvider(ABC):
    """Base interface for tool providers."""

    @abstractmethod
    def get_discovery_mcp_config(self) -> dict:
        """Get MCP config for app discovery (planning phase)."""
        pass

    @abstractmethod
    def get_execution_mcp_config(self, available_resources: List[Resource]) -> list[dict]:
        """Get MCP configs for execution phase."""
        pass

    @abstractmethod
    def enrich_resources(self, resources: List[ResourceExpanded]):
        """Enrich ResourceExpanded objects in place with connection status and auth URLs."""
        pass
