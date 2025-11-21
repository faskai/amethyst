"""Amethyst app and resource types."""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from .memory import Memory


class Statement(BaseModel):
    """Single statement in a function block."""

    text: str
    is_parallel: bool = False


class AmtBlock(BaseModel):
    """Function execution block."""

    type: Literal["sequence", "repeat", "wait"]
    statements: List[Statement] = []


class ResourceLite(BaseModel):
    """Lightweight resource for interpreter (sent to LLM)."""

    type: str
    name: str
    provider: str
    id: Optional[str] = None


class Resource(ResourceLite):
    """Lightweight resource for interpreter (sent to LLM)."""

    img_url: Optional[str] = None


class ResourceExpanded(Resource):
    """Extended resource with execution details (internal processing)."""

    is_main: bool = False
    code: Optional[str] = None
    blocks: List[AmtBlock] = []
    connection_status: Optional[str] = None
    auth_url: Optional[str] = None

    def to_lite(self) -> ResourceLite:
        return ResourceLite(type=self.type, name=self.name, provider=self.provider, id=self.id)


class AmtFile(BaseModel):
    """AMT file containing Amethyst code."""

    content: str


class App(BaseModel):
    files: List[AmtFile] = []
    resource_ids: List[str] = []
    workspaceId: str = ""
    memory: Memory = Field(default_factory=Memory)
    updated_at: Optional[datetime] = None


class AppExpanded(App):
    """Application containing multiple AMT files and resources."""

    resources: List[ResourceExpanded] = []
