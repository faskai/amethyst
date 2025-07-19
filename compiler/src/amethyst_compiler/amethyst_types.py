from typing import Dict, List, Optional, Any, Literal
from dataclasses import dataclass
from enum import Enum


class ResourceType(Enum):
    """Type of resource (agent or tool)."""
    AGENT = "agent"
    TOOL = "tool"


@dataclass
class AgentDefinition:
    """Represents an Amethyst agent definition."""
    name: str
    instructions: str
    url: Optional[str] = None  # URL for remote agent
    model: Optional[str] = None  # Model to use (e.g., "gpt-4", "gemini-2.0-flash", etc.)
    
    def __post_init__(self):
        if self.model is None:
            # Default model if none specified
            self.model = "gpt-4"


@dataclass
class ToolDefinition:
    """Represents an Amethyst tool definition."""
    name: str
    schema: Dict[str, Any]
    url: Optional[str] = None  # URL for remote tool
    function: Optional[Any] = None  # The actual function to call (for local tools)


@dataclass
class ResourceDefinition:
    """Generic resource definition that can be either an agent or tool."""
    resource_type: ResourceType
    definition: AgentDefinition | ToolDefinition
    
    @property
    def name(self) -> str:
        """Get the name from the definition."""
        return self.definition.name
    
    @property
    def url(self) -> Optional[str]:
        """Get the URL from the definition."""
        return self.definition.url


class ResourceRegistry:
    """Registry to store and retrieve resource definitions."""
    
    def __init__(self):
        self._resources: Dict[str, ResourceDefinition] = {}
    
    def register_resource(self, resource: ResourceDefinition) -> None:
        """Register a resource in the registry."""
        self._resources[resource.name] = resource
    
    def get_resource(self, name: str) -> Optional[ResourceDefinition]:
        """Get a resource by name."""
        return self._resources.get(name)
    
    def list_resources(self) -> List[str]:
        """List all registered resource names."""
        return list(self._resources.keys())
    
    def get_agent_definition(self, name: str) -> Optional[AgentDefinition]:
        """Get an agent definition by name."""
        resource = self.get_resource(name)
        if resource and resource.resource_type == ResourceType.AGENT:
            return resource.definition
        return None
    
    def get_tool_definition(self, name: str) -> Optional[ToolDefinition]:
        """Get a tool definition by name."""
        resource = self.get_resource(name)
        if resource and resource.resource_type == ResourceType.TOOL:
            return resource.definition
        return None 