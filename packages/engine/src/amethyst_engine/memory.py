"""Runtime execution state."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List
from uuid import uuid4


@dataclass
class AiCall:
    """AI input / output for tracing and debugging."""

    input_messages: List[Dict[str, str]] = field(default_factory=list)
    intermediate_outputs: List[Dict[str, Any]] = field(default_factory=list)


class TaskType(Enum):
    AMT_AGENT = "amt_agent"
    AMT_FUNCTION = "amt_function"
    STATEMENT = "statement"


@dataclass
class Task:
    """Basic task for LLM (lightweight, serializable)."""

    id: str = field(default_factory=lambda: str(f"task-{uuid4()}"))
    parent_task_id: str | None = None
    resource_name: str = ""
    task_type: TaskType = TaskType.AMT_AGENT
    input: Dict[str, Any] = field(default_factory=dict)
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


@dataclass
class TaskExpanded(Task):
    """Expanded task for internal processing with tracing."""

    async_task: Any = field(default=None, init=False, repr=False)
    ai_calls: List[AiCall] = field(default_factory=list, repr=False)

    def to_dict(self, include_ai_calls: bool = False) -> dict:
        """Serialize task to dict, optionally including ai_calls for tracing."""
        data = super().to_dict()
        if include_ai_calls and self.ai_calls:
            data["ai_calls"] = [
                {
                    "input_messages": ac.input_messages,
                    "intermediate_outputs": ac.intermediate_outputs,
                }
                for ac in self.ai_calls
            ]
        return data


class Memory:
    """Runtime state storage."""

    def __init__(self):
        self.tasks: Dict[str, TaskExpanded] = {}

    def get_scoped_context(self, current_task_id: str) -> dict:
        """Get immediate children as context (for LLM)."""
        children = [t for t in self.tasks.values() if t.parent_task_id == current_task_id]
        return {"tasks": [t.to_dict(include_ai_calls=False) for t in children if t.result]}

    def get_context(self) -> dict:
        """Get all task results for final context."""
        return {
            "tasks": [t.to_dict(include_ai_calls=False) for t in self.tasks.values() if t.result]
        }
