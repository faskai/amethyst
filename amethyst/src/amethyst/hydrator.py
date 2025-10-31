"""Resource hydration for A2A and MCP support."""

import os
from typing import Dict, List

import httpx

from .types import Resource


class ResourceHydrator:
    """Hydrates resources with schemas and capabilities."""

    def __init__(self):
        self.base_url = os.getenv("AMETHYST_SERVER_URL", "http://localhost:9998").rstrip("/")

    async def hydrate_resources(self, resources: List[Resource]) -> None:
        """Hydrate resources with their schemas and capabilities."""
        for resource in resources:
            if resource.provider == "amethyst":
                await self._hydrate_amethyst_resource(resource)

    async def _hydrate_amethyst_resource(self, resource: Resource) -> None:
        """Hydrate an Amethyst resource with its schema/capabilities."""
        if resource.type == "tool":
            resource.parameters = await self._fetch_tool_schema(resource.name)
        elif resource.type == "agent":
            resource.capabilities = await self._fetch_agent_capabilities(resource.name)

    async def _fetch_tool_schema(self, tool_name: str) -> Dict:
        """Fetch tool schema from unified server."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/tools/{tool_name}")
            response.raise_for_status()
            tool_info = response.json()
            return tool_info["parameters"]

    async def _fetch_agent_capabilities(self, agent_name: str) -> List[Dict]:
        """Fetch agent capabilities from unified server."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/agents/{agent_name}/.well-known/agent.json"
            )
            response.raise_for_status()
            agent_card = response.json()
            return agent_card["skills"]
