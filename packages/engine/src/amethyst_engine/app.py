"""Amethyst app and resource types."""

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


class AmtFile(BaseModel):
    """AMT file containing Amethyst code."""

    content: str


class App(BaseModel):
    """Application containing multiple AMT files and resources."""

    files: List[AmtFile] = []
    resources: List[Resource] = []
    resources_expanded: List[ResourceExpanded] = []
    workspaceId: str = ""
    memory: Memory = Field(default_factory=Memory)

    class Config:
        arbitrary_types_allowed = True
