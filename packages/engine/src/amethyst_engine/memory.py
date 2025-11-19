"""Runtime execution state."""

from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class AiCall(BaseModel):
    """AI input / output for tracing and debugging."""

    input_messages: List[Dict[str, str]] = []
    intermediate_outputs: List[Dict[str, Any]] = []


class TaskType(str, Enum):
    AMT_AGENT = "amt_agent"
    AMT_FUNCTION = "amt_function"
    STATEMENT = "statement"


class Task(BaseModel):
    """Basic task for LLM (lightweight, serializable)."""

    id: str = Field(default_factory=lambda: f"task-{uuid4()}")
    parent_task_id: Optional[str] = None
    resource_name: str = ""
    task_type: TaskType = TaskType.AMT_AGENT
    input: List[Dict[str, Any]] = Field(default_factory=list)
    result: Any = None

    def to_dict(self) -> dict:
        """Serialize task to dict for LLM."""
        return {
            "id": self.id,
            "parent_task_id": self.parent_task_id,
            "resource_name": self.resource_name,
            "task_type": self.task_type.value,
            "input": self.input,
            "result": self.result,
        }


class TaskExpanded(Task):
    """Expanded task for internal processing with tracing."""

    ai_calls: List[AiCall] = []
    async_task: Any = None

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self, include_ai_calls: bool = False) -> dict:
        """Serialize task to dict, optionally including ai_calls for tracing."""
        data = super().to_dict()
        if include_ai_calls and self.ai_calls:
            data["ai_calls"] = [ac.model_dump() for ac in self.ai_calls]
        return data


class Memory(BaseModel):
    """Runtime state storage."""

    tasks: Dict[str, TaskExpanded] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True

    def get_context(self) -> dict:
        """Get all task results for final context."""
        return {"tasks": [t.to_dict() for t in self.tasks.values() if t.result]}
