"""Abstract provider interface."""

from abc import ABC, abstractmethod
from typing import List

from amethyst.planner import ExternalResource


class ToolProvider(ABC):
    """Base interface for tool providers."""

    @abstractmethod
    def get_discovery_mcp_config(self) -> dict:
        """Get MCP config for app discovery (planning phase)."""
        pass

    @abstractmethod
    def get_execution_mcp_config(self, available_resources: list) -> list[dict]:
        """Get MCP configs for execution phase."""
        pass

    @abstractmethod
    def enrich_resources(self, resources: List[ExternalResource]) -> list[dict]:
        """
        Enrich discovered resources with connection status and auth URLs.

        Args:
            resources: List of resource dicts from MCP discovery

        Returns:
            List of enriched resource dicts with connection_status and auth_url
        """
        pass
