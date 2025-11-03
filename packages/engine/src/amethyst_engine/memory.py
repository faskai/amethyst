"""Runtime execution state.

Tracks tasks, steps, and results during execution.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class TaskType(Enum):
    TOOL_CALL = "tool_call"
    AGENT_CALL = "agent_call"
    AMT_AGENT_RESULT = "amt_agent_result"


class StepType(Enum):
    AWAIT = "await"
    CONDITIONAL = "conditional"
    LOOP = "loop"


@dataclass
class Task:
    """Executable task (agent call or tool call)."""

    id: str = None
    resource_name: str = None
    task_type: TaskType = None
    parameters: Dict[str, Any] = None
    is_async: bool = False
    result: Any = None
    async_task: Any = field(default=None, init=False)


@dataclass
class Step:
    """Control flow step (await, conditional, loop)."""

    step_type: StepType
    task_ids: List[str]


class Memory:
    """Runtime state storage - simple data container."""

    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.steps: List[Step] = []
        self.files: List[Dict[str, Any]] = []

    def get_context(self) -> dict:
        """Get tasks and steps for interpreter context."""
        return {
            "tasks": [
                {
                    "id": t.id,
                    "resource_name": t.resource_name,
                    "task_type": t.task_type.value,
                    "result": t.result,
                }
                for t in self.tasks.values()
                if t.result
            ],
            "files": self.files,
        }
