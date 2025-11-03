"""Amethyst app and resource types."""

from dataclasses import asdict, dataclass, field
from typing import Dict, List, Literal


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


@dataclass
class AmtFile:
    """AMT file containing Amethyst code."""

    content: str


@dataclass
class App:
    """Application containing multiple AMT files and resources."""

    files: List[AmtFile]
    resources: Dict[str, Resource] = field(default_factory=dict)

    def list_resources(self) -> List[Dict]:
        return [asdict(r) for r in self.resources.values()]
