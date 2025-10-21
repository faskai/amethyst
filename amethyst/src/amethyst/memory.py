"""Runtime execution state.

Tracks tasks, steps, and results during execution.
"""

from typing import List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class TaskType(Enum):
    TOOL_CALL = "tool_call"
    AGENT_CALL = "agent_call"


class StepType(Enum):
    AWAIT = "await"
    CONDITIONAL = "conditional"
    LOOP = "loop"


@dataclass
class Task:
    """Executable task (agent call or tool call)."""
    id: str
    resource_name: str
    task_type: TaskType
    parameters: Dict[str, Any]
    is_async: bool = False
    result: Any = None
    async_task: Any = field(default=None, init=False)


@dataclass 
class Step:
    """Control flow step (await, conditional, loop)."""
    step_type: StepType
    task_ids: List[str]


class Memory:
    """Runtime state storage."""
    
    def __init__(self):
        self.tasks_by_id: Dict[str, Task] = {}
        self.completed_steps: List[Step] = []
        
    def add_task(self, task: Task) -> None:
        self.tasks_by_id[task.id] = task
    
    def add_step(self, step: Step) -> None:
        self.completed_steps.append(step)
    
    def get_task(self, task_id: str) -> Task:
        return self.tasks_by_id[task_id]
    
    def get_full_context(self) -> str:
        """Get full memory context for interpreter."""
        lines = []
        
        completed_tasks = [t for t in self.tasks_by_id.values() if t.result]
        if completed_tasks:
            lines.append("Completed tasks:")
            for t in completed_tasks:
                lines.append(f"  - {t.resource_name}: {str(t.result)}")
        
        if self.completed_steps:
            lines.append("\nCompleted steps:")
            for s in self.completed_steps:
                lines.append(f"  - {s.step_type.value} for tasks: {', '.join(s.task_ids)}")
        
        return "\n".join(lines) if lines else "No tasks or steps completed yet"
    
    def get_summary(self) -> str:
        """Get summary of completed tasks."""
        completed = [t for t in self.tasks_by_id.values() if t.result]
        return "\n".join([f"- {t.resource_name}: {t.result}" for t in completed])
