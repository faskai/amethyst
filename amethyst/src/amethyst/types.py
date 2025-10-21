"""Amethyst resource types.

Resources are agents and tools available for execution.
"""

from typing import Dict, List, Optional, Literal
from dataclasses import dataclass, asdict


@dataclass
class Resource:
    """Agent or tool resource definition."""
    type: Literal["agent", "tool"]
    name: str
    provider: Literal["amethyst", "external"]
    url: str = None
    connection_status: str = None
    auth_url: str = None
    parameters: Dict = None
    capabilities: List[Dict] = None


class ResourceRegistry:
    """Runtime registry for available resources."""
    
    def __init__(self):
        self._resources: Dict[str, Resource] = {}
    
    def register_resource(self, resource: Resource) -> None:
        self._resources[resource.name] = resource
    
    def get_resource(self, name: str) -> Resource:
        return self._resources[name]
    
    def list_resources(self) -> List[Dict]:
        return [asdict(r) for r in self._resources.values()]