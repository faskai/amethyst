"""Runtime execution state."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict
from uuid import uuid4


class TaskType(Enum):
    AMT_AGENT_CALL = "amt_agent_call"
    AMT_FUNCTION_CALL = "amt_function_call"
    STATEMENT_RESULT = "statement_result"


@dataclass
class Task:
    """Executable task."""

    id: str = field(default_factory=lambda: str(f"task-{uuid4()}"))
    resource_name: str = ""
    task_type: TaskType = TaskType.AMT_AGENT_CALL
    input: Dict[str, Any] = field(default_factory=dict)
    result: Any = None
    async_task: Any = field(default=None, init=False)


class Memory:
    """Runtime state storage."""

    def __init__(self):
        self.tasks: Dict[str, Task] = {}

    def get_context(self) -> dict:
        """Get task results for interpreter context."""
        return {
            "tasks": [
                {"id": t.id, "resource_name": t.resource_name, "result": t.result}
                for t in self.tasks.values()
                if t.result
            ]
        }
