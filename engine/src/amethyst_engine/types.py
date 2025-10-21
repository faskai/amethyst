from typing import Dict, List, Optional, Any, Literal
from dataclasses import dataclass
from enum import Enum


class ResourceType(Enum):
    """Type of resource (agent or tool)."""
    AGENT = "agent"
    TOOL = "tool"


@dataclass
class AgentDefinition:
    """Remote A2A agent."""
    name: str
    url: str


@dataclass 
class ToolDefinition:
    """Remote MCP tool."""
    name: str
    url: str


@dataclass
class ResourceDefinition:
    """Generic resource definition that can be either an agent or tool."""
    resource_type: ResourceType
    definition: AgentDefinition | ToolDefinition


class ResourceRegistry:
    """Simple resource storage."""
    
    def __init__(self):
        self._resources: Dict[str, ResourceDefinition] = {}
    
    def register_resource(self, resource: ResourceDefinition) -> None:
        """Register a resource."""
        self._resources[resource.definition.name] = resource
    
    def get_resource(self, name: str) -> Optional[ResourceDefinition]:
        """Get a resource by name."""
        return self._resources.get(name)
    
    def list_resources(self) -> List[str]:
        """List resources with types."""
        result = []
        for name, resource in self._resources.items():
            if resource.resource_type == ResourceType.AGENT:
                result.append(f"agent:{name}")
            elif resource.resource_type == ResourceType.TOOL:
                result.append(f"tool:{name}")
        return result 