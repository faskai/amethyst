"""Amethyst execution engine - main interpreter and coordinator."""

import asyncio
from typing import Dict, List, Any, Optional

from . import types
from .memory import Memory, Task, Step, TaskType, StepType
from .planner import CognitivePlanner
from .executor import call_tool, call_agent
from .compiler import convert_acl_to_afl


class AmethystEngine:
    """Main execution engine - interprets and coordinates AI-powered execution."""
    
    def __init__(self):
        self.memory = Memory()
        self.registry = types.ResourceRegistry()
        try:
            self.planner = CognitivePlanner()
        except ValueError as e:
            print(f"Warning: {e}")
            self.planner = None
    
    def register_resource(self, resource: types.ResourceDefinition) -> None:
        """Register resource."""
        self.registry.register_resource(resource)
    
    async def execute(self, instructions: str) -> str:
        """Execute instructions using cognitive planning."""
        
        if not self.planner:
            return "Error: No OpenAI API key"
        
        lines = [line.strip() for line in instructions.split('\n') if line.strip()]
        results = [f"🧠 Cognitive Engine Processing: {len(lines)} lines"]
        
        position = 0
        while position < len(lines) and position != -1:
            # Skip agent/end lines  
            while position < len(lines) and (lines[position].startswith('agent ') or lines[position].startswith('end ')):
                position += 1
            
            if position >= len(lines):
                break
                
            # Get execution plan from cognitive planner
            memory_summary = self._get_memory_summary()
            plan = await self.planner.plan_execution(
                instructions=instructions,
                memory_summary=memory_summary,
                current_position=position,
                available_resources=self.registry.list_resources()
            )
            
            tasks = plan.get("tasks", [])
            steps = plan.get("steps", [])
            position = plan.get("next_position", -1)
            
            # Execute tasks
            for task in tasks:
                try:
                    # Add task to memory immediately for tracking
                    self.memory.add_task(task)
                    
                    # Create coroutine based on task type
                    if task.task_type == TaskType.TOOL_CALL:
                        async_task = call_tool(task.resource_name, task.parameters, self.registry)
                    elif task.task_type == TaskType.AGENT_CALL:
                        async_task = call_agent(task.resource_name, task.parameters, self.registry)
                    else:
                        # Future task types can be added here
                        results.append(f"❌ Unknown task type: {task.task_type}")
                        continue
                    
                    # Store coroutine for awaiting
                    task.async_task = self._execute_task(task, async_task)
                    
                    if task.is_async:
                        # Don't await, just store for later
                        results.append(f"🚀 Started async {task.task_type.value} {task.resource_name}")
                    else:
                        # Execute sync immediately
                        await task.async_task
                        results.append(f"✅ {task.task_type.value} {task.resource_name}: Success")
                        
                except Exception as e:
                    results.append(f"❌ {task.task_type.value} {task.resource_name}: {e}")
            
            # Execute steps
            for step in steps:
                try:
                    if step.step_type == StepType.AWAIT:
                        await self._await_tasks(step.task_ids)
                        results.append(f"⏳ Awaited tasks: {step.task_ids}")
                        
                except Exception as e:
                    results.append(f"❌ Step {step.step_type.value}: {e}")
        
        # Add final memory summary
        results.append("\n📋 Final Memory:")
        results.append(self._get_memory_summary())
        
        return "\n".join(results)
    
    async def _execute_task(self, task: Task, async_task) -> None:
        """Execute async task and store result."""
        try:
            task.result = await async_task
        except Exception as e:
            task.result = f"Error: {e}"
    
    async def _await_tasks(self, task_ids: List[str]) -> None:
        """Wait for specific async tasks."""
        
        tasks_to_await = []
        for task_id in task_ids:
            task = self.memory.get_task(task_id)
            if task and task.async_task:
                tasks_to_await.append(task.async_task)
        
        if tasks_to_await:
            await asyncio.gather(*tasks_to_await)
    
    def _get_memory_summary(self) -> str:
        """Get memory summary."""
        tasks = self.memory.get_tasks()
        if not tasks:
            return "No previous tasks"
        
        summary = []
        for task in tasks[-3:]:  # Last 3 tasks
            result_preview = str(task.result)[:100] + "..." if len(str(task.result)) > 100 else str(task.result)
            summary.append(f"{task.task_type.value} {task.resource_name}: {result_preview}")
        
        return "\n".join(summary)
    
    async def execute_acl(self, acl_text: str, save_afl_path: Optional[str] = None) -> str:
        """Execute ACL by converting to AFL first.
        
        Converts ACL (Casual) → AFL (Formal) → execution.
        """
        
        if not self.planner:
            return "Error: No OpenAI API key"
        
        # Convert ACL to ASL/AFL using compiler
        afl_code = await convert_acl_to_afl(
            client=self.planner.client,
            acl_text=acl_text,
            available_resources=self.registry.list_resources()
        )
        
        # Optionally save AFL to file
        if save_afl_path:
            with open(save_afl_path, 'w') as f:
                f.write(afl_code)
        
        # Execute the AFL
        return await self.execute(afl_code)
