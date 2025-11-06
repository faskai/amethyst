"""Amethyst app and resource types."""

from dataclasses import asdict, dataclass, field
from typing import Dict, List, Literal


@dataclass
class Resource:
    """Agent, tool, or function resource definition."""

    type: Literal["agent", "tool", "function"]
    name: str
    provider: Literal["amethyst", "pipedream"]
    key: str = None
    url: str = None
    connection_status: str = None
    auth_url: str = None
    parameters: Dict = None
    skills: List[Dict] = None


@dataclass
class AmtFile:
    """AMT file containing Amethyst code."""

    content: str
    amt_agents: List = field(default_factory=list)
    functions: List = field(default_factory=list)


@dataclass
class App:
    """Application containing multiple AMT files and resources."""

    files: List[AmtFile]
    resources: Dict[str, Resource] = field(default_factory=dict)

    def list_resources(self) -> List[Dict]:
        return [asdict(r) for r in self.resources.values()]
