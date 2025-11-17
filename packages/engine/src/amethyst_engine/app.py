"""Amethyst app and resource types."""

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel


class Statement(BaseModel):
    """Single statement in a function block."""

    text: str
    is_parallel: bool = False


class AmtBlock(BaseModel):
    """Function execution block."""

    type: Literal["sequence", "repeat", "wait"]
    statements: List[Statement] = []


class Resource(BaseModel):
    """Lightweight resource for interpreter (sent to LLM)."""

    type: str
    name: str
    provider: str
    key: Optional[str] = None


class ResourceExpanded(Resource):
    """Extended resource with execution details (internal processing)."""

    is_main: bool = False
    code: Optional[str] = None
    blocks: List[AmtBlock] = []
    connection_status: Optional[str] = None
    auth_url: Optional[str] = None


@dataclass
class AmtFile:
    """AMT file containing Amethyst code."""

    content: str


@dataclass
class App:
    """Application containing multiple AMT files and resources."""

    files: List[AmtFile]
    resources: Dict[str, Resource] = field(default_factory=dict)
    resources_expanded: List[ResourceExpanded] = field(default_factory=list)
    workspaceId: str = ""

    def list_resources_as_dict(self) -> List[Dict]:
        """Serialize resources to dicts for JSON output."""
        return [r.model_dump() for r in self.resources.values()]
