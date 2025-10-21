"""Memory system for cognitive execution."""

import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class TaskType(Enum):
    TOOL_CALL = "tool_call"
    AGENT_CALL = "agent_call"


class StepType(Enum):
    AWAIT = "await"


@dataclass
class Task:
    """A task to execute."""
    
    id: str
    resource_name: str
    task_type: TaskType
    parameters: Dict[str, Any]
    is_async: bool = False
    result: Any = None
    async_task: Any = field(default=None, init=False)  # Coroutine for awaiting


@dataclass 
class Step:
    """A system step like await."""
    
    step_type: StepType
    task_ids: List[str]


class Memory:
    """Simple storage."""
    
    def __init__(self):
        self.tasks_by_id: Dict[str, Task] = {}
        
    def add_task(self, task: Task) -> None:
        """Add task."""
        self.tasks_by_id[task.id] = task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        return self.tasks_by_id.get(task_id)
    
    def get_tasks(self) -> List[Task]:
        """Get all tasks as list."""
        return list(self.tasks_by_id.values())
