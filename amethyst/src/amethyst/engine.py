"""Amethyst execution engine.

The Engine orchestrates the compilation and execution of Amethyst code:
- Planner: Compiles ACL (casual) to AFL (formal) 
- Interpreter: Interprets AFL and determines execution steps
- Executor: Executes tasks (agent calls, tool calls)
- Memory: Tracks runtime state and results
"""

import asyncio
import os
from dotenv import load_dotenv

from . import types
from .memory import Memory, TaskType, StepType, Task
from .interpreter import Interpreter
from .executor import call_tool, call_agent, execute_asl_block
from .hydrator import ResourceHydrator


class Engine:
    """Amethyst execution engine.
    
    Orchestrates compilation and execution:
    Planner → Interpreter → Executor
    
    Example:
        >>> engine = Engine(verbose=True)
        >>> resources = [Resource(type="tool", name="weather", url="...")]
        >>> result = await engine.run("get the weather", resources=resources)
    """
    
    def __init__(self, verbose: bool = False):
        load_dotenv()
        
        self.memory = Memory()
        self.registry = types.ResourceRegistry()
        self.verbose = verbose
        
        from .providers.pipedream import PipedreamProvider
        self.provider = PipedreamProvider(verbose=verbose)
        
        from .planner import Planner
        self.planner = Planner(self.provider, verbose=verbose)
        
        self.hydrator = ResourceHydrator()
    
    async def run(self, acl: str, resources: list[types.Resource]) -> dict:
        """Run Amethyst code."""
        await self.hydrator.hydrate_resources(resources)
        for resource in resources:
            self.registry.register_resource(resource)
        
        plan = self.planner.compile(acl, self.registry.list_resources())
        
        for r in plan["resources"]:
            self.registry.register_resource(types.Resource(**r))
        
        needs_oauth = [r for r in plan["resources"] if r.get("connection_status") == "needs_oauth"]
        if needs_oauth:
            return {"status": "oauth_required", "code": plan["code"], "resources": plan["resources"]}
        
        result = await self.execute(plan["code"])
        return {"status": "completed", "code": plan["code"], "result": result}
    
    async def execute(self, instructions: str) -> str:
        """Execute compiled AFL code."""
        interpreter = Interpreter(verbose=self.verbose)
        mcp_tools = self.provider.get_execution_mcp_config(self.registry.list_resources())
        position = 0
        
        while position >= 0:
            plan = await interpreter.interpret(
                instructions=instructions,
                memory=self.memory.get_full_context(),
                current_position=position,
                available_resources=self.registry.list_resources(),
                mcp_tools=mcp_tools
            )
            
            for task in plan["tasks"]:
                self.memory.add_task(task)
                
                if task.task_type == TaskType.AGENT_CALL:
                    coro = call_agent(task.resource_name, task.parameters, self.registry)
                elif task.task_type == TaskType.TOOL_CALL:
                    coro = call_tool(task.resource_name, task.parameters, self.registry)
                else:
                    continue
                
                if task.is_async:
                    task.async_task = asyncio.create_task(coro)
                else:
                    task.result = await coro
            
            for step in plan["steps"]:
                if step.step_type == StepType.AWAIT:
                    await self._await_tasks(step.task_ids)
                    self.memory.add_step(step)
            
            position = plan["next_position"]
        
        return self.memory.get_summary()
    
    async def _await_tasks(self, task_ids):
        """Wait for tasks and store results."""
        for task_id in task_ids:
            task = self.memory.get_task(task_id)
            task.result = await task.async_task
